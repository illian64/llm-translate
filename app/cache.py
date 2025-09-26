import hashlib
import os
import sqlite3

import pyway.info
import pyway.migrate
import pyway.validate

from app import log
from app.dto import TranslateCommonRequest, Part
from app.params import CacheParams

logger = log.logger()


class Cache:
    params: CacheParams

    def __init__(self, params: CacheParams):
        self.params = params
        self.init_pybase_migration()
        self.init_delete_expired_values()

    def get_connection(self):
        return sqlite3.connect(self.params.file)

    def init_pybase_migration(self):
        os.environ["PYWAY_TYPE"] = "sqlite"
        os.environ["PYWAY_TABLE"] = "pyway_migrations"
        os.environ["PYWAY_DATABASE_NAME"] = self.params.file
        migration_path = self.params.migration_path if self.params.migration_path else "resources/migrations"
        os.environ["PYWAY_DATABASE_MIGRATION_DIR"] = migration_path
        migrate = pyway.migrate.Migrate(pyway.migrate.ConfigFile())
        logger.info("Result apply migrations: %s", migrate.run())

    def init_delete_expired_values(self) -> None:
        if not self.params.enabled:
            return None

        connection = self.get_connection()
        cursor = connection.cursor()

        if self.params.expire_days > 0:
            delete_expired_values = "DELETE FROM cache_translate WHERE created < date('now', '-{0} day')".format(
                self.params.expire_days)
            cursor.execute(delete_expired_values)

        connection.commit()

    def get(self, req: TranslateCommonRequest, text: str, model_name: str):
        select = ("SELECT value FROM cache_translate "
                  "WHERE key = ? AND from_lang = ? AND to_lang = ? AND plugin = ? AND model = ? AND context_hash = ?")
        cursor = self.get_connection().cursor()
        cursor.execute(select, (text, req.from_lang, req.to_lang, req.translator_plugin, model_name,
                                self.context_hash(req.context)))
        value = cursor.fetchone()
        if value:
            return value[0]
        else:
            return None

    def put(self, req: TranslateCommonRequest, text: str, value: str, model_name: str):
        try:
            insert_connection = self.get_connection()
            cursor = insert_connection.cursor()
            insert = 'INSERT INTO cache_translate (KEY, from_lang, to_lang, plugin, model, context_hash, VALUE) VALUES (?, ?, ?, ?, ?, ?, ?)'
            cursor.execute(insert,(text, req.from_lang, req.to_lang, req.translator_plugin, model_name,
                                   self.context_hash(req.context), value))
            insert_connection.commit()
            insert_connection.close()
        except Exception as e:
            log.log_exception("Error save cache entry, text = {0}, req = {1}".format(text, req), e)

    def cache_read(self, req: TranslateCommonRequest, parts: list[Part], params: CacheParams, model_name: str):
        if params.enabled and req.translator_plugin not in params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate():
                    cached_translate = self.get(req, part.text, model_name)
                    if cached_translate:
                        part.cache_found = True
                        part.translate = cached_translate
                    else:
                        part.cache_found = False

    def cache_write(self, req: TranslateCommonRequest, parts: list[Part], params: CacheParams, model_name: str):
        if params.enabled and req.translator_plugin not in params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate() and not part.cache_found:
                    self.put(req, part.text, part.translate, model_name)

    def context_hash(self, context: str | None) -> int:
        if context and len(context.strip()) > 0:
            return int(hashlib.sha1(context.encode("utf-8")).hexdigest(), 16) % 100000000
        else:
            return 0

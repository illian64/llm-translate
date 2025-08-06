import logging
import sqlite3

from app.dto import TranslateCommonRequest, Part
from app.params import CacheParams

logger = logging.getLogger('uvicorn')


class Cache:
    cache_table_name = "cache_translate"
    params: CacheParams
    connection: sqlite3.Connection

    def __init__(self, params: CacheParams):
        self.params = params
        self.connection = self.get_connection()
        self.init()

    def get_connection(self):
        return sqlite3.connect(self.params.file)

    def init(self):
        if not self.params.enabled:
            return None

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(self.cache_table_name))
        table_exists = cursor.fetchall()

        if len(table_exists) == 0:
            logger.info("Init cache table: %s, file db: %s", self.cache_table_name, self.params.file)
            create_table = """
                CREATE TABLE IF NOT EXISTS {0} 
                (key TEXT NOT NULL, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                from_lang TEXT NOT NULL, to_lang TEXT NOT NULL, plugin TEXT NOT NULL,
                model TEXT NOT NULL, value TEXT NOT NULL) 
            """.format(self.cache_table_name)
            create_idx_translate_cols = ('CREATE UNIQUE INDEX IF NOT EXISTS idx_translate_cols '
                                         'ON {0} (key, from_lang, to_lang, plugin, model)').format(self.cache_table_name)
            create_idx_created = ('CREATE INDEX IF NOT EXISTS idx_created '
                                  'ON {0} (created)').format(self.cache_table_name)

            with cursor:
                cursor.execute(create_table)
                cursor.execute(create_idx_translate_cols)
                cursor.execute(create_idx_created)
        else:
            if (self.params.expire_days > 0):
                delete_expired_values = "DELETE FROM {0} WHERE created < date('now', '-{1} day')".format(
                    self.cache_table_name, self.params.expire_days)
                cursor.execute(delete_expired_values)

        self.connection.commit()

    def get(self, req: TranslateCommonRequest, text: str):
        select = "SELECT value FROM {0} WHERE key = ? AND from_lang = ? AND to_lang = ? AND plugin = ?".format(
            self.cache_table_name)
        cursor = self.connection.cursor()
        cursor.execute(select, (text, req.from_lang, req.to_lang, req.translator_plugin))
        value = cursor.fetchone()
        if value:
            return value[0]
        else:
            return None

    def put(self, req: TranslateCommonRequest, text: str, value: str):
        try:
            insert_connection = self.get_connection()
            cursor = insert_connection.cursor()
            cursor.execute('INSERT INTO {0} (KEY, from_lang, to_lang, plugin, VALUE) VALUES (?, ?, ?, ?, ?)'.format(
                self.cache_table_name),(text, req.from_lang, req.to_lang, req.translator_plugin, value))
            insert_connection.commit()
            insert_connection.close()
        except Exception as e:
            logger.error("Error save cache entry, text = %s, req = %s, error=%s", text, req, e)

    def cache_read(self, req: TranslateCommonRequest, parts: list[Part], params: CacheParams):
        if params.enabled and req.translator_plugin not in params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate():
                    cached_translate = self.get(req, part.text)
                    if cached_translate:
                        part.cache_found = True
                        part.translate = cached_translate
                    else:
                        part.cache_found = False

    def cache_write(self, req: TranslateCommonRequest, parts: list[Part], params: CacheParams):
        if params.enabled and req.translator_plugin not in params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate() and not part.cache_found:
                    self.put(req, part.text, part.translate)

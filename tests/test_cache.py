import os
from pathlib import Path
from unittest import TestCase

from app.cache import Cache
from app.dto import TranslateCommonRequest
from app.params import CacheParams


class CacheTest(TestCase):
    test_dir = Path(__file__).parent.absolute()

    params = CacheParams(enabled=True, file=str(test_dir / "files/test.db"), disable_for_plugins=[], expire_days=20,
                         migration_path=str(test_dir / "../cache/migrations"))

    req = TranslateCommonRequest(text="all text", from_lang="fr", to_lang="to", translator_plugin="plugin1")

    def test_operations(self):
        print("Absolute path: " + os.path.abspath(self.params.migration_path))

        cache = Cache(self.params)
        cache.put(req=self.req, text="part1 text 1", value="translate 1", model_name="model 1")
        cache.put(req=self.req, text="part1 text 1", value="translate 2", model_name="model 2")

        value1 = cache.get(req=self.req, text="part1 text 1", model_name="model 1")
        self.assertEqual("translate 1", value1)
        value2 = cache.get(req=self.req, text="part1 text 1", model_name="model 2")
        self.assertEqual("translate 2", value2)

        os.remove(self.params.file)

    def test_delete_expired_values(self):
        cache = Cache(self.params)
        cache.put(req=self.req, text="part1 text 1", value="translate 1", model_name="model 1")
        cache.put(req=self.req, text="part1 text 1", value="translate 2", model_name="model 2")

        connection = cache.get_connection()
        cursor = connection.cursor()
        sql1 = "UPDATE cache_translate SET created = date('now', '-30 day') WHERE model='model 1'"
        sql2 = "UPDATE cache_translate SET created = date('now', '-10 day') WHERE model='model 2'"

        cursor.execute(sql1)
        cursor.execute(sql2)

        connection.commit()
        connection.close()

        cache = Cache(self.params)

        value1 = cache.get(req=self.req, text="part1 text 1", model_name="model 1")
        self.assertEqual(None, value1)
        value2 = cache.get(req=self.req, text="part1 text 1", model_name="model 2")
        self.assertEqual("translate 2", value2)

        os.remove(self.params.file)



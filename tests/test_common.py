"""
Test common classes and functions for vcdb.
"""
import datetime
import os
import unittest

from vcdb import common

import tests


class OrmTest(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(tests.TEMP_FOLDER, 'ormtest.db')
        common.ensure_is_removed(self.database_path)
        engine_uri = 'sqlite:///' + self.database_path
        self.session = common.vcdb_session(engine_uri)

    def test_can_create_change(self):
        repository = common.Repository(
            repository_id=1,
            uri='file://localhost/tmp/tmp',
        )
        self.session.add(repository)
        self.session.commit()

        import sqlite3
        with sqlite3.connect(self.database_path) as db:
            repository_count = len(list(db.cursor().execute('select 1 from repositories')))
        self.assertEqual(1, repository_count)


if __name__ == '__main__':
    unittest.main()

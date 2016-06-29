"""
Tests for vcdb command line interface.
"""
import os.path
import sqlite3
import unittest
from contextlib import closing

from vcdb import command
from vcdb import common
from vcdb import subversion

import tests
from tests import test_subversion


class CommandTest(unittest.TestCase):
    def test_can_show_help(self):
        try:
            command.vcdb_command(['--help'])
            self.fail()
        except SystemExit as error:
            self.assertEqual(error.code, 0)

    def test_can_show_version(self):
        try:
            command.vcdb_command(['--version'])
            self.fail()
        except SystemExit as error:
            self.assertEqual(error.code, 0)

    def test_can_build_database(self):
        def assert_table_has_rows(cursor, table):
            sql_statement = 'select 1 from ' + table + ' limit 1'
            has_data = len(list(cursor.execute(sql_statement))) != 0
            self.assertTrue(has_data, 'table ' + table + ' must contain data')

        repository_builder = test_subversion.TestRepositoryBuilder(common.func_name())
        repository_builder.build()

        database_path = os.path.join(tests.TEMP_FOLDER, common.func_name() + '.db')
        common.ensure_is_removed(database_path)
        engine_uri = 'sqlite:///' + database_path
        exit_code = command.vcdb_command([repository_builder.repository_uri, engine_uri])
        self.assertEqual(exit_code, 0)

        with sqlite3.connect(database_path) as database:
            with closing(database.cursor()) as cursor:
                assert_table_has_rows(cursor, 'repositories')
                assert_table_has_rows(cursor, 'changes')
                assert_table_has_rows(cursor, 'paths')


if __name__ == '__main__':
    unittest.main()

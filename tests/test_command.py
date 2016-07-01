"""
Tests for vcdb command line interface.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
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

    def assert_table_has_rows(self, cursor, table):
        sql_statement = 'select 1 from ' + table + ' limit 1'
        has_data = len(list(cursor.execute(sql_statement))) != 0
        self.assertTrue(has_data, 'table ' + table + ' must contain data')

    def assert_has_vcdb_rows(self, database_path):
        with sqlite3.connect(database_path) as database:
            with closing(database.cursor()) as cursor:
                self.assert_table_has_rows(cursor, 'repositories')
                self.assert_table_has_rows(cursor, 'changes')
                self.assert_table_has_rows(cursor, 'paths')

    def test_can_build_database_for_test_subversion_repository(self):
        repository_builder = test_subversion.TestRepositoryBuilder(common.func_name())
        repository_builder.build()

        database_path = os.path.join(tests.TEMP_FOLDER, common.func_name() + '.db')
        common.ensure_is_removed(database_path)
        engine_uri = 'sqlite:///' + database_path
        exit_code = command.vcdb_command([repository_builder.repository_uri, engine_uri])
        self.assertEqual(exit_code, 0)
        self.assert_has_vcdb_rows(database_path)

    def test_can_build_database_for_vcdb_github_repository(self):
        repository_uri = 'https://github.com/roskakori/vcdb/trunk'
        database_path = os.path.join(tests.TEMP_FOLDER, common.func_name() + '.db')
        engine_uri = 'sqlite:////' + database_path
        common.ensure_is_removed(database_path)

        exit_code = command.vcdb_command([repository_uri, engine_uri])
        self.assertEqual(exit_code, 0)
        self.assert_has_vcdb_rows(database_path)

    def test_can_rebuild_database(self):
        repository_builder = test_subversion.TestRepositoryBuilder(common.func_name())
        repository_builder.build()

        database_path = os.path.join(tests.TEMP_FOLDER, common.func_name() + '.db')
        common.ensure_is_removed(database_path)
        engine_uri = 'sqlite:///' + database_path
        for _ in range(2):
            exit_code = command.vcdb_command([repository_builder.repository_uri, engine_uri])
            self.assertEqual(exit_code, 0)
            self.assert_has_vcdb_rows(database_path)


if __name__ == '__main__':
    unittest.main()

"""
Tests for Subversion repository.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
import logging
import os
import pathlib
import subprocess
import unittest
import urllib

from vcdb.subversion import run_svn, write_svn_log_xml
from vcdb import common
from vcdb import subversion

import tests


def _write_source(path, lines=None):
    assert path is not None
    with open(path, 'w', encoding='utf-8') as target_file:
        if lines is not None:
            for line in lines:
                target_file.write(line + '\n')


def _svnadmin(args):
    subprocess.check_call(['svnadmin'] + args)


class TestRepositoryBuilder():
    def __init__(self, project):
        assert project is not None
        self.project = project
        self.project_path = os.path.join(tests.TEMP_FOLDER, self.project)
        self.repo_path = os.path.abspath(os.path.join(self.project_path, 'repo'))
        self.work_path = os.path.join(self.project_path, 'work')
        self.repository_uri = pathlib.Path(self.repo_path).as_uri() + '/'
        self.project_trunk_uri = urllib.parse.urljoin(self.repository_uri, self.project + '/trunk')

    def build(self):
        common.ensure_folder_is_empty(self.project_path)

        # Create repository and check it out.
        _svnadmin(['create', self.repo_path])
        run_svn('mkdir', '--message', 'Added project folder.', '--parents', self.project_trunk_uri)
        run_svn('checkout', self.project_trunk_uri, self.work_path)

        # Write empty.txt.
        empty_txt_path = os.path.join(self.work_path, 'empty.txt')
        _write_source(empty_txt_path)

        # Write useless.txt.
        useless_txt_path = os.path.join(self.work_path, 'useless.txt')
        _write_source(useless_txt_path)

        # Write hello.py.
        hello_py_path = os.path.join(self.work_path, 'hello.py')
        _write_source(hello_py_path, [
            '# The classic hello world.'
            'print("hello world")',
        ])

        # Add and commit files.
        run_svn('add', empty_txt_path, hello_py_path, useless_txt_path)
        run_svn('commit', '--message', 'Added tool to greet.', self.work_path)

        # Remove useless file.
        run_svn('remove', useless_txt_path)
        run_svn('commit', '--message', 'Removed useless file.', useless_txt_path)

        # Modify existing file.
        _write_source(hello_py_path, [
            '# The classic hello world.'
            'print("hello world!")',
        ])
        run_svn('commit', '--message', 'Added exclamation mark.', hello_py_path)

        # Copy a file.
        hello_again_py_path = os.path.join(self.work_path, 'hello_again.py')
        run_svn('copy', hello_py_path, hello_again_py_path)
        run_svn('commit', '--message', 'Added another tool to greet.', hello_again_py_path)

        # Modify and move a file.
        _write_source(hello_py_path, [
            '# Das klassische Hallo Welt.'
            'print("Hallo Welt!")',
        ])
        hallo_py_path = os.path.join(self.work_path, 'hallo.py')
        run_svn('move', '--force', hello_py_path, hallo_py_path)
        run_svn('commit', '--message', 'Translated to German.', hallo_py_path, hello_py_path)

        # Rename a file.
        hallo_welt_py_path = os.path.join(self.work_path, 'hallo_welt.py')
        run_svn('move', hallo_py_path, hallo_welt_py_path)
        run_svn('commit', '--message', 'Renamed to clearer name.', hallo_py_path, hallo_welt_py_path)

        # Revert a file to an older version.
        revision_to_revert_to = subversion.svn_info_revision(self.repository_uri)
        _write_source(hallo_welt_py_path, [
            '# Das klassische Hallo Welt.'
            'print("Hallo Welt!!!")',
        ])
        run_svn('commit', '--message', 'Added extra ohmpf.', hallo_welt_py_path)
        run_svn('update')
        run_svn('merge', '--revision', 'HEAD:' + revision_to_revert_to, hallo_welt_py_path)
        run_svn('commit', '--message', 'Toned things down again.', hallo_welt_py_path)

        # Replace a file.
        run_svn('remove', empty_txt_path)
        _write_source(empty_txt_path)
        run_svn('add', empty_txt_path)
        run_svn('commit', '--message', 'Changed to a different kind of empty.', empty_txt_path)

        # Add a file without commit message.
        pointless_tmp_path = os.path.join(self.work_path, 'pointless.tmp')
        _write_source(pointless_tmp_path)
        run_svn('add', pointless_tmp_path)
        run_svn('commit', '--message', '', pointless_tmp_path)


class SubversionTest(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(tests.TEMP_FOLDER, 'subversiontest.db')
        common.ensure_is_removed(self.database_path)
        engine_uri = 'sqlite:///' + self.database_path
        self.session = common.vcdb_session(engine_uri)

    def test_can_build_database_from_subversion_repository(self):
        repository_builder = TestRepositoryBuilder(common.func_name())
        repository_builder.build()
        subversion.update_repository(self.session, repository_builder.repository_uri)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

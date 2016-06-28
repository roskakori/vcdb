"""
Tests for Subversion repository.
"""
import logging
import os
import pathlib
import subprocess
import unittest
import urllib

from vcdb.subversion import run_svn, write_svn_log_xml
from vcdb import common
from vcdb import subversion

_log = logging.getLogger('vcdb.tests')
_TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(_TEMP_FOLDER, exist_ok=True)


class SubversionTest(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(_TEMP_FOLDER, 'subversiontest.db')
        common.ensure_is_removed(self.database_path)
        engine_uri = 'sqlite:///' + self.database_path
        self.session = common.vcdb_session(engine_uri)

    def _svnadmin(self, args):
        subprocess.check_call(['svnadmin'] + args)

    def _write_source(self, path, lines=None):
        assert path is not None
        with open(path, 'w', encoding='utf-8') as target_file:
            if lines is not None:
                for line in lines:
                    target_file.write(line + '\n')

    def test_can_analyze_subversion_repository(self):
        project = common.func_name()
        project_path = os.path.join(_TEMP_FOLDER, project)
        common.ensure_folder_is_empty(project_path)
        repo_path = os.path.abspath(os.path.join(project_path, 'repo'))
        work_path = os.path.join(project_path, 'work')
        log_xml_path = os.path.join(project_path, project + '_log.xml')
        repository_uri = pathlib.Path(repo_path).as_uri() + '/'
        project_trunk_uri = urllib.parse.urljoin(repository_uri, project + '/trunk')

        # Create repository and check it out.
        self._svnadmin(['create', repo_path])
        run_svn('mkdir', '--message', 'Added project folder.', '--parents', project_trunk_uri)
        run_svn('checkout', project_trunk_uri, work_path)

        # Write empty.txt.
        empty_txt_path = os.path.join(work_path, 'empty.txt')
        self._write_source(empty_txt_path)

        # Write hello.py.
        hello_py_path = os.path.join(work_path, 'hello.py')
        self._write_source(hello_py_path, [
            '# The classic hello world.'
            'print("hello world")',
        ])

        # Add and commit files.
        run_svn('add', empty_txt_path, hello_py_path)
        run_svn('commit', '--message', 'Added tool to greet.', work_path)

        subversion.update_repository(self.session, repository_uri)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()

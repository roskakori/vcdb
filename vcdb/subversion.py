"""
Utility functions to work with Subversion.
"""
import datetime
import logging
import os
import subprocess
import tempfile
from xml.etree import ElementTree

import vcdb.common as common

STRFTIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

_log = logging.getLogger('vcdb.subversion')



class LogEntryPath():
    def __init__(self, logentry, path_element):
        assert logentry is not None
        assert path_element.tag == 'path'

        self.path = path_element.text
        self.kind = path_element.attrib['kind']
        self.action = path_element.attrib['action']
        self._logentry = logentry

    def as_changed_path(self):
        return common.ChangedPath(self._logentry.change_id, self.action, self.kind, self.path)


def add_change_from_logentry(session, repository, logentry_element):
        assert logentry_element.tag == 'logentry'
        author = logentry_element.find('author').text
        change_id = logentry_element.attrib['revision']
        commit_message = logentry_element.find('msg').text
        commit_time_text = logentry_element.find('date').text
        # HACK: Strip the trailing 'Z' which seems to be there for reasons unknown.
        commit_time_text = commit_time_text[:-1]
        commit_time = datetime.datetime.strptime(commit_time_text, STRFTIME_FORMAT)
        # TODO: paths = [LogEntryPath(path_element) for path_element in logentry_element.findall('path/paths')]
        change = common.Change(
            author=author,
            change_id=change_id,
            commit_time=commit_time,
            commit_message=commit_message,
            repository_id=repository.repository_id
        )
        session.add(change)


def svn(command, *options):
    command_parts = [
        'svn',
        command,
        '--no-auth-cache',
        '--non-interactive',
        '--quiet',
    ]
    command_parts.extend(list(options))
    _log.info(' '.join(command_parts))
    subprocess.check_call(command_parts)


def svn_log(target_xml_path, uri, revision=None):
    command_parts = [
        'svn',
        'log',
        '--no-auth-cache',
        '--non-interactive',
        '--verbose',
        '--xml',
        uri,
    ]
    if revision is not None:
        command_parts.extend([
            '--revision',
            revision
        ])
    _log.info(' '.join(command_parts))
    with open(target_xml_path, 'wb') as target_xml_file:
        xml_data = subprocess.check_output(command_parts)
        target_xml_file.write(xml_data)


def repository_for(session, repository_uri):
    assert session is not None
    assert repository_uri is not None

    existing_repositories = session.query(common.Repository).filter_by(uri=repository_uri).all()
    existing_repository_count = len(existing_repositories)
    if existing_repository_count == 0:
        _log.info('add new repository: %r', repository_uri)
        result = common.Repository(uri=repository_uri)
        session.add(result)
    else:
        assert existing_repository_count == 1, "Repository.UniqueConstraint('uri') must avoid duplicates"
        result = existing_repositories[0]
    return result


def update_repository(session, repository_uri):
    assert session is not None
    assert repository_uri is not None

    repository = repository_for(session, repository_uri)
    revision = '0:HEAD' # TODO: Update starting from last change.
    svn_log_xml_path = os.path.join(tempfile.gettempdir(), 'vcdb', 'svn_log.xml')  # TODO: Use a real temporary name.

    # Extract log parse it.
    svn_log(svn_log_xml_path, repository_uri, revision)
    _log.info('read subversion log from %s', svn_log_xml_path)
    log_root = ElementTree.parse(svn_log_xml_path)
    for logentry_element in log_root.findall('logentry[@revision]'):
        add_change_from_logentry(session, repository, logentry_element)

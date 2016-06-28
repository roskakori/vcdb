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

_SUBVERSION_KIND_TO_PATH_KIND_MAP = {
    'dir': 'd',
    'file': 'f',
}
_SUBVERSION_ACTION_TO_PATH_ACTION_MAP = {
    'A': 'a',
    'D': 'd',
}
_log = logging.getLogger('vcdb.subversion')


def path_to_add(change, path_element):
    assert change is not None
    assert path_element is not None

    path = path_element.text
    svn_kind = path_element.attrib['kind']
    try:
        kind = _SUBVERSION_KIND_TO_PATH_KIND_MAP[svn_kind]
    except KeyError:
        assert False, 'kind=%r must be added to _SUBVERSION_KIND_TO_PATH_KIND_MAP' % svn_kind
    svn_action = path_element.attrib['action']
    try:
        action = _SUBVERSION_ACTION_TO_PATH_ACTION_MAP[svn_action]
    except KeyError:
        assert False, 'action=%r must be added to _SUBVERSION_ACTION_TO_PATH_ACTION_MAP' % svn_action
    result = common.Path(
        action=action,
        change_id=change.change_id,
        kind=kind, path=path,
        repository_id=change.repository_id)
    return result


def change_to_add(session, repository, logentry_element):
        assert logentry_element.tag == 'logentry'
        author = logentry_element.find('author').text
        change_id = logentry_element.attrib['revision']
        commit_message = logentry_element.find('msg').text
        commit_time_text = logentry_element.find('date').text
        # HACK: Strip the trailing 'Z' which seems to be there for reasons unknown.
        commit_time_text = commit_time_text[:-1]
        commit_time = datetime.datetime.strptime(commit_time_text, STRFTIME_FORMAT)
        result = common.Change(
            author=author,
            change_id=change_id,
            commit_time=commit_time,
            commit_message=commit_message,
            repository_id=repository.repository_id
        )
        return result

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
        session.commit()
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
        change = change_to_add(session, repository, logentry_element)
        session.add(change)
        for path_element in logentry_element.findall('paths/path'):
            path = path_to_add(change, path_element)
            _log.info('add path: %s', path)
            session.add(path)
    session.commit()


"""
Common classes and functions for vcdb.
"""
import os
import shutil

import sqlalchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


class VcdbError(Exception):
    pass


def func_name():
    import traceback
    return traceback.extract_stack(None, 2)[0][2]


def ensure_is_removed(path):
    try:
        shutil.rmtree(path)
    except NotADirectoryError:
        os.remove(path)
    except FileNotFoundError:
        if os.path.exists(path):
            raise


def ensure_folder_is_empty(empty_path):
    ensure_is_removed(empty_path)
    os.makedirs(empty_path, exist_ok=True)


#: Maximum number of characters to represent a Change.change_id.
CHANGE_ID_LENGTH = 32

#: Maximum number of characters to store in Change.commit_message.
COMMIT_MESSAGE_LENGTH = 1020

DeclarativeBase = declarative_base()


class Repository(DeclarativeBase):
    __tablename__ = 'repositories'
    repository_id = Column(Integer, nullable=False, primary_key=True)
    uri = Column(String(255), nullable=False)
    last_change_id = Column(String(CHANGE_ID_LENGTH))  # NOTE: Not a ForeignKey to avoid circular dependency.

    UniqueConstraint('uri')

    def __repr__(self):
        return '<Repository(repository_id=%r, uri=%r, last_synctime=%r)>' % (
            self.repository_id, self.uri, self.last_synctime
        )


class Change(DeclarativeBase):
    """
    A change that has been taken place in a certain repository.
    """
    __tablename__ = 'changes'
    change_id = Column(String(CHANGE_ID_LENGTH), nullable=False, primary_key=True)
    author = Column(String(16))
    commit_message = Column(String(COMMIT_MESSAGE_LENGTH), nullable=False)
    commit_time = Column(DateTime, nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.repository_id'))
    repository = relationship(
        'Repository',
        back_populates='changes',
        cascade='all, delete, delete-orphan',
        single_parent=True
    )

    def __repr__(self):
        return '<Change(change_id=%r, author=%r, commit_time=%r, commit_message=%r' % (
            self.change_id, self.author, self.commit_time, self.commit_message
        )


Repository.changes = relationship('Change', back_populates='repository')


def vcdb_session(engine_uri):
    assert engine_uri is not None
    engine = sqlalchemy.create_engine(engine_uri)
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

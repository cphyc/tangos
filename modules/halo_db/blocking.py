import sqlalchemy, sqlalchemy.engine, sqlalchemy.event
from . import parallel_tasks as pt
global rlock

__author__ = 'app'

def event_begin(conn):
    rlock.acquire()

def event_commit_or_rollback(conn):
    rlock.release()


def make_engine_blocking(engine):
    global rlock
    assert isinstance(engine, sqlalchemy.engine.Engine)
    rlock = pt.RLock("db_write_lock")

    sqlalchemy.event.listen(engine, 'begin', event_begin )
    sqlalchemy.event.listen(engine, 'commit', event_commit_or_rollback)
    sqlalchemy.event.listen(engine, 'rollback', event_commit_or_rollback)
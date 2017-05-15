#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

# format the log entries
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

handler = RotatingFileHandler('dbl2r.log',
                              mode='a',
                              maxBytes=20*1024*1024,
                              backupCount=5,
                              encoding=None,
                              delay=0)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


from sqlalchemy.orm import sessionmaker
from sql_create_table import engine as local_engine, Data, Base
from sqlalchemy import Column, Integer, String, REAL
from sqlalchemy.ext.declarative import declarative_base

# from sql_remote_create import engine as remote_engine
from sqlalchemy import create_engine, Table, MetaData

url = 'postgresql://{}:{}@{}:{}/{}'
url = url.format('dbraw', ',fpflfyys[', '194.87.99.184', 5432, 'dbraw')
remote_engine = create_engine(url, client_encoding='utf8', echo=False)

logger.debug('creating connection to local db')
local_DBSession = sessionmaker(bind=local_engine)
local_session = local_DBSession()

logger.debug('creating connection to remote db')
remote_DBSession = sessionmaker(bind=remote_engine)
remote_session = remote_DBSession()

logger.debug('Pulling schema from local server')
local_meta = MetaData(bind=local_engine)
tt = Table(Data.__tablename__, local_meta, autoload=True)
columns = tt.columns.keys()

remote_meta = MetaData(bind=remote_engine)
# class rData(Base):
#     __tablename__ = 'web_data'
#     id = Column(Integer, primary_key=True)
#     tag_id = Column(Integer, nullable=False, default=999)
#     value = Column(REAL)
#     stime = Column(String(30))
# rData = Table('web_data', remote_meta,
#     Column('id', Integer, primary_key=True),
#     Column('tag_id', Integer, nullable=False, default=999),
#     Column('value', REAL),
#     Column('stime', String(30))
# )
def quick_mapper(table):
    Base = declarative_base()
    class GenericMapper(Base):
        __table__ = table
    return GenericMapper

rData_table = Table('web_data', remote_meta, autoload=True, autoload_with=remote_engine)
rData = quick_mapper(rData_table)
remote_last_initial = remote_session.query(rData).order_by(rData.id.desc()).first()


if remote_last_initial is None:
    remote_last_initial_id = 1
else:
    remote_last_initial_id = remote_last_initial.id

logger.info('Starting up adding rows')
while 1:
    local_last = local_session.query(Data).order_by(Data.id.desc()).first()
    local_last_id = local_last.id
    remote_last = remote_session.query(rData).order_by(rData.id.desc()).first()
    if remote_last is None:
        remote_last_id = 1
    else:
        remote_last_id = remote_last.id
    logger.debug('db rows remote={}, local={}'.format(remote_last_id, local_last_id))

    if remote_last_id >= local_last_id - 5:
        logger.info('db rows remote={}, local={}'.format(remote_last_id, local_last_id))
        logger.info('Finishing the cycles: {} has been added'.format(remote_last_id-remote_last_initial_id))
        break

    new_records = local_session.query(Data).filter(Data.id>remote_last_id).limit(100).all()
    for record in new_records:
        d = dict(
            [(str(column), getattr(record, column)) for column in columns]
        )
        remote_session.merge(rData(**d))
    logger.debug('Commit remote db')
    remote_session.commit()



'''
http://www.tylerlesmann.com/2009/apr/27/copying-databases-across-platforms-sqlalchemy/

import getopt
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def make_session(connection_string):
    if 'sqlite' in connection_string :
        engine = create_engine(connection_string, echo=True)
    else:
        engine = create_engine(connection_string, echo=True, client_encoding='utf8')
    Session = sessionmaker(bind=engine)
    return Session(), engine

def pull_data(from_db, to_db, tables):
    source, sengine = make_session(from_db)
    smeta = MetaData(bind=sengine)
    destination, dengine = make_session(to_db)

    for table_name in tables:
        print 'Processing', table_name
        print 'Pulling schema from source server'
        table = Table(table_name, smeta, autoload=True)
        # print 'Creating table on destination server'
        # table.metadata.create_all(dengine)    #creates table
        NewRecord = quick_mapper(table)
        columns = table.columns.keys()
        remote_last_row = destination.query(table).order_by(table.id.desc()).first()
        print 'Transferring records'
        for record in source.query(table).filter(table.id>remote_last_row.id).limit(50).all():
            data = dict(
                [(str(column), getattr(record, column)) for column in columns]
            )
            destination.merge(NewRecord(**data))
    print 'Committing changes'
    destination.commit()

def print_usage():
    print """
Usage: %s -f source_server -t destination_server table [table ...]
    -f, -t = driver://user[:password]@host[:port]/database

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting table_one table_two
    """ % (sys.argv[0], sys.argv[0])

def quick_mapper(table):
    Base = declarative_base()
    class GenericMapper(Base):
        __table__ = table
    return GenericMapper

if __name__ == '__main__':
    # optlist, tables = getopt.getopt(sys.argv[1:], 'f:t:')
    #
    # options = dict(optlist)
    # if '-f' not in options or '-t' not in options or not tables:
    #     print_usage()
    #     raise SystemExit, 1
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format('dbraw', ',fpflfyys[', '192.168.201.200', 5432, 'dbraw')
    tables = ['data']
    options = {'-f': 'sqlite:///common.db',
               '-t': url,
               }

    pull_data(
        options['-f'],
        options['-t'],
        tables,
    )

'''
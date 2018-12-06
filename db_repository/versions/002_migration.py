from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
enrollment = Table('enrollment', pre_meta,
    Column('studentId', INTEGER),
    Column('moduleCode', INTEGER),
)

module = Table('module', pre_meta,
    Column('moduleCode', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=250)),
    Column('moduleLeader', INTEGER),
)

staff = Table('staff', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('firstname', VARCHAR(length=250)),
    Column('surname', VARCHAR(length=250)),
    Column('title', VARCHAR(length=10)),
)

student = Table('student', pre_meta,
    Column('studentId', INTEGER, primary_key=True, nullable=False),
    Column('firstname', VARCHAR(length=250)),
    Column('surname', VARCHAR(length=250)),
    Column('year', DATE),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['enrollment'].drop()
    pre_meta.tables['module'].drop()
    pre_meta.tables['staff'].drop()
    pre_meta.tables['student'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['enrollment'].create()
    pre_meta.tables['module'].create()
    pre_meta.tables['staff'].create()
    pre_meta.tables['student'].create()

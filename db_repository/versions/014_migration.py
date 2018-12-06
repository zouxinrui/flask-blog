from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
comments = Table('comments', pre_meta,
    Column('id', VARCHAR(length=45), primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('text', TEXT),
    Column('date', DATETIME),
    Column('post_id', INTEGER),
)

post = Table('post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=225)),
    Column('title', VARCHAR(length=255)),
    Column('timestamp', DATETIME),
    Column('user_id', INTEGER),
)

posts_tags = Table('posts_tags', pre_meta,
    Column('post_id', VARCHAR(length=45)),
    Column('tag_id', VARCHAR(length=45)),
)

roles = Table('roles', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('role_name', VARCHAR(length=30), nullable=False),
)

tags = Table('tags', pre_meta,
    Column('id', VARCHAR(length=45), primary_key=True, nullable=False),
    Column('name', VARCHAR(length=255)),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('about_me', VARCHAR(length=180)),
    Column('username', VARCHAR(length=64)),
    Column('email', VARCHAR(length=100)),
    Column('password_hash', VARCHAR(length=128)),
)

userroles = Table('userroles', pre_meta,
    Column('user_id', INTEGER, primary_key=True, nullable=False),
    Column('role_id', INTEGER, primary_key=True, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comments'].drop()
    pre_meta.tables['post'].drop()
    pre_meta.tables['posts_tags'].drop()
    pre_meta.tables['roles'].drop()
    pre_meta.tables['tags'].drop()
    pre_meta.tables['user'].drop()
    pre_meta.tables['userroles'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comments'].create()
    pre_meta.tables['post'].create()
    pre_meta.tables['posts_tags'].create()
    pre_meta.tables['roles'].create()
    pre_meta.tables['tags'].create()
    pre_meta.tables['user'].create()
    pre_meta.tables['userroles'].create()

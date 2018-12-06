from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
posts_tags = Table('posts_tags', post_meta,
    Column('post_id', String(length=45)),
    Column('tag_id', String(length=45)),
)

tags = Table('tags', post_meta,
    Column('id', String(length=45), primary_key=True, nullable=False),
    Column('name', String(length=255)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['posts_tags'].create()
    post_meta.tables['tags'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['posts_tags'].drop()
    post_meta.tables['tags'].drop()

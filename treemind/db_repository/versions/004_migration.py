from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
branches = Table('branches', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('main', Boolean, default=ColumnDefault('False')),
    Column('folded', Boolean, default=ColumnDefault('False')),
    Column('orderb', Integer, default=ColumnDefault(0)),
    Column('parent_id', Integer),
    Column('text', String, default=ColumnDefault('')),
)

trees = Table('trees', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('rootb_id', Integer),
    Column('owner_id', Integer),
    Column('latestB_id', Integer),
)

users = Table('users', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String),
    Column('passwd', String),
    Column('email', String),
    Column('latestTree_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['branches'].create()
    post_meta.tables['trees'].create()
    post_meta.tables['users'].columns['latestTree_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['branches'].drop()
    post_meta.tables['trees'].drop()
    post_meta.tables['users'].columns['latestTree_id'].drop()

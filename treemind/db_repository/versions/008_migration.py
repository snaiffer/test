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
    Column('tree_id', Integer),
    Column('read', Boolean, default=ColumnDefault('False')),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['branches'].columns['read'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['branches'].columns['read'].drop()

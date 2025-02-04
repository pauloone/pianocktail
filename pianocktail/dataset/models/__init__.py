from peewee import Database
from . import base


def set_database(database: Database):
    base.database_proxy.initialize(database)

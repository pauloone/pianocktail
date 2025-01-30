from peewee import Database
from . import base


def set_database(database: Database):
    base.BaseModel._meta.db = database

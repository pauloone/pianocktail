from peewee import Model


class BaseModel(Model):
    pass

    class Meta:
        database = None

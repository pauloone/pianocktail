from peewee import CharField, ManyToManyField
from .base import BaseModel
from .cocktail import Cocktail


class Genre(BaseModel):
    name = CharField()
    cocktails = ManyToManyField(Cocktail, backref="genres")

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Genre: {self.name} >"

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


# We explicitely import the through model for the autodiscovery of models.
_genre_cocktail = Genre.cocktails.get_through_model()

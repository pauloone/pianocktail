from peewee import CharField, ManyToManyField
from .base import BaseModel
from .genre import Genre
from .cocktail import Cocktail


class Artist(BaseModel):
    name = CharField()
    genres = ManyToManyField(Genre, backref="artists")
    cocktails = ManyToManyField(Cocktail, backref="artists")

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Artist: {self.name} >"


# We explicitely import the through model for the autodiscovery of models.
_artist_genre = Artist.genres.get_through_model()
_artist_cocktail = Artist.cocktails.get_through_model()

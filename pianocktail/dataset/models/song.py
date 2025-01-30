from peewee import CharField, ForeignKeyField, ManyToManyField
from .base import BaseModel
from .artist import Artist
from .cocktail import Cocktail


class Song(BaseModel):
    name = CharField(100)
    artist = ForeignKeyField(Artist, backref="songs")
    cocktails = ManyToManyField(Cocktail, backref="songs")

    def __str__(self):
        return f"{self.name} by {self.artist}"

    def __repr__(self):
        return f"<Song:id={self.id},name={self.name},artist={self.artist})>"

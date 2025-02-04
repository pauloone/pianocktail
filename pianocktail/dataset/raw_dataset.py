import hashlib
import logging
import typing

import peewee
import yaml

from .models.artist import Artist
from .models.cocktail import Cocktail, Ingredient, IngredientLine, Unit
from .models.genre import Genre
from .models.song import Song

module_logger = logging.getLogger("pianocktail.dataset.raw_dataset")


def cocktail_hash(cocktail_data: dict) -> str:
    hash = hashlib.md5()
    for ingredient in sorted(cocktail_data.keys()):
        hash.update(ingredient.encode())
        hash.update(str(cocktail_data[ingredient]).encode())
    return hash.hexdigest()


def get_or_create_unamed_cocktail(cocktail_data: dict) -> Cocktail:
    name = cocktail_hash(cocktail_data)
    cocktail, create = Cocktail.get_or_create(name=name)
    if create:
        module_logger.info(f"Cocktail {name} created")
        for ingredient, quantity in cocktail_data.items():
            ingredient = ingredient.lower().replace(" ", "_")
            try:
                ingredient = Ingredient.get(name=ingredient)
                IngredientLine.create(ingredient=ingredient, cocktail=cocktail, quantity=quantity)
            except peewee.DoesNotExist:
                module_logger.error(f"Ingredient {ingredient} not found")
                raise ValueError(f"Ingredient {ingredient} not found")
    return cocktail


def generate_cocktails(cocktail_data: typing.Iterable[dict]) -> list[Cocktail]:
    cocktail_instances: list[Cocktail] = []
    for cocktail in cocktail_data:
        if isinstance(cocktail, dict):
            cocktail_instances.append(get_or_create_unamed_cocktail(cocktail))
        else:
            cocktail = cocktail.lower().replace(" ", "_")
            try:
                cocktail_instances.append(Cocktail.get(name=cocktail))
            except peewee.DoesNotExist:
                module_logger.error(f"Cocktail {cocktail} not found")
                raise ValueError(f"Cocktail {cocktail} not found")
    return cocktail_instances


def load_dataset(path: str, database: peewee.Database) -> None:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        with database.atomic() as transaction:
            try:
                for unit, ingredients in data["ingredients"].items():
                    unit, _ = Unit.get_or_create(name=unit)
                    for ingredient in ingredients:
                        ingredient = ingredient.lower().replace(" ", "_")
                        ingredient_instance, created = Ingredient.get_or_create(name=ingredient, unit=unit)
                        if not created and ingredient_instance.unit != unit:
                            module_logger.error(f"Ingredient {ingredient} already exists with a different unit")
                            raise ValueError(f"Ingredient {ingredient} already exists with a different unit")
                        module_logger.debug(f"Ingredient {ingredient} {'created' if created else 'already exists'}")

                for cocktail_name, ingredients in data["cocktails"].items():
                    cocktail_name = cocktail_name.lower().replace(" ", "_")
                    cocktail, created = Cocktail.get_or_create(name=cocktail_name)
                    if created:
                        module_logger.debug(f"Cocktail {cocktail_name} created")
                        for ingredient, quantity in ingredients.items():
                            ingredient = ingredient.lower().replace(" ", "_")
                            try:
                                ingredient = Ingredient.get(name=ingredient)
                                IngredientLine.create(ingredient=ingredient, cocktail=cocktail, quantity=quantity)
                            except peewee.DoesNotExist:
                                module_logger.error(f"Ingredient {ingredient} not found")
                                raise ValueError(f"Ingredient {ingredient} not found")

                for genre, cocktails in data["genres"].items():
                    genre = genre.lower().replace(" ", "_")
                    genre_instance, created = Genre.get_or_create(name=genre)
                    module_logger.debug(f"Genre {genre} {'created' if created else 'already exists'}")
                    genre_instance.cocktails = generate_cocktails(cocktails)

                for artist, artist_data in data["artists"].items():
                    artist_instance, created = Artist.get_or_create(name=artist)
                    module_logger.debug(f"Artist {artist} {'created' if created else 'already exists'}")
                    if "general" in artist_data:
                        artist_instance.cocktails = generate_cocktails(artist_data["general"])
                    if "songs" in artist_data:
                        for song, cocktails_data in artist_data["songs"].items():
                            song_instance, created = Song.get_or_create(name=song, artist=artist_instance)
                            module_logger.debug(f"Song {song} {'created' if created else 'already exists'}")
                            song_instance.cocktails = generate_cocktails(cocktails_data)
                    if "genres" in artist_data:
                        genres = []
                        for genre in artist_data["genres"]:
                            genres.append(Genre.get(name=genre.lower().replace(" ", "_")))
                        artist_instance.genres = genres

            except Exception as e:
                transaction.rollback()
                module_logger.error(f"An error occured during the transaction: {e}")
                raise e

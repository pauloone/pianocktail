"""Peewee migrations -- 003_auto.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    
    @migrator.create_model
    class ArtistCocktailThrough(pw.Model):
        id = pw.AutoField()
        artist = pw.ForeignKeyField(column_name='artist_id', field='id', model=migrator.orm['artist'])
        cocktail = pw.ForeignKeyField(column_name='cocktail_id', field='id', model=migrator.orm['cocktail'])

        class Meta:
            table_name = "artist_cocktail_through"
            indexes = [(('artist', 'cocktail'), True)]

    @migrator.create_model
    class ArtistGenreThrough(pw.Model):
        id = pw.AutoField()
        artist = pw.ForeignKeyField(column_name='artist_id', field='id', model=migrator.orm['artist'])
        genre = pw.ForeignKeyField(column_name='genre_id', field='id', model=migrator.orm['genre'])

        class Meta:
            table_name = "artist_genre_through"
            indexes = [(('artist', 'genre'), True)]

    @migrator.create_model
    class GenreCocktailThrough(pw.Model):
        id = pw.AutoField()
        genre = pw.ForeignKeyField(column_name='genre_id', field='id', model=migrator.orm['genre'])
        cocktail = pw.ForeignKeyField(column_name='cocktail_id', field='id', model=migrator.orm['cocktail'])

        class Meta:
            table_name = "genre_cocktail_through"
            indexes = [(('genre', 'cocktail'), True)]

    @migrator.create_model
    class SongCocktailThrough(pw.Model):
        id = pw.AutoField()
        song = pw.ForeignKeyField(column_name='song_id', field='id', model=migrator.orm['song'])
        cocktail = pw.ForeignKeyField(column_name='cocktail_id', field='id', model=migrator.orm['cocktail'])

        class Meta:
            table_name = "song_cocktail_through"
            indexes = [(('song', 'cocktail'), True)]


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
    migrator.remove_model('song_cocktail_through')

    migrator.remove_model('genre_cocktail_through')

    migrator.remove_model('artist_genre_through')

    migrator.remove_model('artist_cocktail_through')

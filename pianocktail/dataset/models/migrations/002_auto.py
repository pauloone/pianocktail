"""Peewee migrations -- 002_auto.py.

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
    class Cocktail(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=100, null=True)

        class Meta:
            table_name = "cocktail"

    @migrator.create_model
    class Genre(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=255)

        class Meta:
            table_name = "genre"

    @migrator.create_model
    class Unit(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=10, unique=True)

        class Meta:
            table_name = "unit"

    @migrator.create_model
    class Ingredient(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=50, unique=True)
        unit = pw.ForeignKeyField(column_name='unit_id', field='id', model=migrator.orm['unit'])

        class Meta:
            table_name = "ingredient"

    @migrator.create_model
    class IngredientLine(pw.Model):
        id = pw.AutoField()
        ingredient = pw.ForeignKeyField(column_name='ingredient_id', field='id', model=migrator.orm['ingredient'])
        cocktail = pw.ForeignKeyField(column_name='cocktail_id', field='id', model=migrator.orm['cocktail'])
        quantity = pw.IntegerField()

        class Meta:
            table_name = "ingredientline"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
    migrator.remove_model('ingredientline')

    migrator.remove_model('ingredient')

    migrator.remove_model('unit')

    migrator.remove_model('genre')

    migrator.remove_model('cocktail')

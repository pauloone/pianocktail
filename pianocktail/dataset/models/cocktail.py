from peewee import CharField, ForeignKeyField, IntegerField, ManyToManyField
from .base import BaseModel


class Unit(BaseModel):
    name = CharField(10, unique=True)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Unit: {self.name} >"


class Ingredient(BaseModel):
    name = CharField(50, unique=True)
    unit = ForeignKeyField(Unit, backref="ingredients")

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Ingredient: {self.name} >"


class Cocktail(BaseModel):
    name = CharField(100, null=True)
    ingredient_line: ManyToManyField

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Cocktail: {self.name} >"


class IngredientLine(BaseModel):
    ingredient = ForeignKeyField(Ingredient)
    cocktail = ForeignKeyField(Cocktail)
    quantity = IntegerField()


Cocktail.ingredient_line = ManyToManyField(Ingredient, through_model=IngredientLine, backref="cocktails")

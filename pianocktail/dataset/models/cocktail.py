from peewee import CharField, ForeignKeyField, IntegerField, ManyToManyField, DeferredThroughModel
from .base import BaseModel


class Unit(BaseModel):
    name = CharField(10, unique=True, index=True)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Unit: {self.name} >"


class Ingredient(BaseModel):
    name = CharField(50, unique=True, index=True)
    unit = ForeignKeyField(Unit, backref="ingredients")

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Ingredient: {self.name} >"


IngredientLineThroughDeferred = DeferredThroughModel()


class Cocktail(BaseModel):
    name = CharField(100, null=True)
    ingredients: ManyToManyField = ManyToManyField(Ingredient, through_model=IngredientLineThroughDeferred)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Cocktail: {self.name} >"


class IngredientLine(BaseModel):
    ingredient = ForeignKeyField(Ingredient, index=True)
    cocktail = ForeignKeyField(Cocktail, index=True)
    quantity = IntegerField()


IngredientLineThroughDeferred.set_model(IngredientLine)

from django.db import models

class FoodType(models.Model):
    name = lambda: models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Ingredient(models.Model):
    food_type = lambda: models.ManyToManyField(FoodType)
    name = lambda: models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class IngredientDetails(models.Model):
    ingredient = lambda: models.ForeignKey(Ingredient)
    name = lambda: models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Meal(models.Model):
    food_type = lambda: models.ForeignKey(FoodType)
    main_ingredient = lambda: models.ForeignKey(Ingredient)
    ingredient_details = lambda: models.ForeignKey(IngredientDetails, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.food_type, self.main_ingredient)

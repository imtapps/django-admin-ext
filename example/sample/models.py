from django.db import models

class FoodType(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Ingredient(models.Model):
    food_type = models.ManyToManyField(FoodType)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class IngredientDetails(models.Model):
    ingredient = models.ForeignKey(Ingredient)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Meal(models.Model):
    food_type = models.ForeignKey(FoodType)
    main_ingredient = models.ForeignKey(Ingredient)
    ingredient_details = models.ForeignKey(IngredientDetails, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.food_type, self.main_ingredient)


from django.contrib import admin
from django import forms

from djadmin_ext.helpers import BaseAjaxModelAdmin
from djadmin_ext.admin_forms import BaseAjaxModelForm
from sample import models

class MealAdminForm(BaseAjaxModelForm):
    ajax_change_field = "food_type"

    @property
    def dynamic_fields(self):
        food_type = models.FoodType.objects.get(pk=self.data.get('food_type') or self.initial.get('food_type'))
        initial_selected = self.data.get('main_ingredient') or (self.instance.pk and self.instance.main_ingredient)

        return {
            'main_ingredient':forms.ModelChoiceField(
                queryset=models.Ingredient.objects.filter(food_type=food_type),
                initial=initial_selected)
        }

    class Meta(object):
        fields = ['food_type']
        model = models.Meal

class MealAdmin(BaseAjaxModelAdmin):
    form = MealAdminForm

admin.site.register(models.FoodType)
admin.site.register(models.Ingredient)
admin.site.register(models.Meal, MealAdmin)
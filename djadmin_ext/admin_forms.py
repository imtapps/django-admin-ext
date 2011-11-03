
from django import forms
from django.core.exceptions import ImproperlyConfigured

__all__ = (
    'BaseAjaxModelForm',
)

class BaseAjaxModelForm(forms.ModelForm):
    """
    ajax_change_field: must be set to the name of the field on
    your model that triggers the ajax call when it is changed.
    """

    ajax_change_field = None
    ajax_change_fields = None

    def __init__(self, *args, **kwargs):
        super(BaseAjaxModelForm, self).__init__(*args, **kwargs)
        if self.ajax_change_field and not self.ajax_change_fields:
            self.ajax_change_fields = [self.ajax_change_field]
        self.setup_dynamic_fields()

    def get_value_from_initial_or_get(self, field):
        return self.data.get(field) or self.initial.get(field)

    def setup_dynamic_fields(self):
        for field_name, field in self.dynamic_fields.items():
            self.fields[field_name] = field

    @property
    def dynamic_fields(self):
        """
        Return a dict where they keys match model fields and values
        are instantiated form fields.
        """
        return {}

    @property
    def change_field_ids(self):
        if not self.ajax_change_fields:
            raise ImproperlyConfigured("Your Admin Ajax form needs an ajax change field")

        fields = []
        for field in self.ajax_change_fields:
            if field in self.fields:
                fields.append(str(self[field].auto_id))

        return fields

    def save(self, *args, **kwargs):
        """
        Because Django's ModelForm only sets fields on the model instance
        based on the form's Meta.fields/Meta.exclude, dynamic fields are
        ignored and need to be set explicity.
        """
        for field_name in self.dynamic_fields:
            setattr(self.instance, field_name, self.cleaned_data.get(field_name))
        return super(BaseAjaxModelForm, self).save(*args, **kwargs)

    def get_selected_value(self, field_name):
        return self.get_value_from_initial_or_get(field_name) or (
        self.instance.pk and getattr(self.instance, field_name).pk)

    def create_field_and_assign_initial_value(self, queryset, selected_value):
        field = forms.ModelChoiceField(queryset=queryset)
        if selected_value in [i.pk for i in queryset]:
            field.initial = selected_value
        return field

    class Media(object):
        js = ('djadmin_ext/admin_ajax.js',)

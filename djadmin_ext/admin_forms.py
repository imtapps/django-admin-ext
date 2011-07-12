
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

    def __init__(self, *args, **kwargs):
        super(BaseAjaxModelForm, self).__init__(*args, **kwargs)
        if self.initial.get(self.ajax_change_field) or self.data.get(self.ajax_change_field):
            self.setup_dynamic_fields()

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
    def change_field_id(self):
        if not self.ajax_change_field:
            raise ImproperlyConfigured("Your Admin Ajax form needs an ajax change field")
        return self[self.ajax_change_field].auto_id

    def save(self, *args, **kwargs):
        """
        Because Django's ModelForm only sets fields on the model instance
        based on the form's Meta.fields/Meta.exclude, dynamic fields are
        ignored and need to be set explicity.
        """
        for field_name in self.dynamic_fields:
            setattr(self.instance, field_name, self.cleaned_data.get(field_name))
        return super(BaseAjaxModelForm, self).save(*args, **kwargs)

    class Media(object):
        js = ('djadmin_ext/admin_ajax.js',)

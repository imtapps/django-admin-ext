Extensions to Django's admin site.

Currently Includes:
 - BaseCustomUrlAdmin: hook to provide additional urls to your model admin.

 - BaseAjaxModelAdmin: hook to have a form that gets some of it's form
                       fields dynamically depending on a certain field choice.

 - BaseAjaxModelForm: form to help setup and save dynamic fields based
                      on other fields chosen.

USAGE:
Take a look at the example project for a more detailed example.

BaseCustomUrlAdmin:
  - in your ModelAdmin, subclass BaseCustomUrlAdmin and implement
    the 'get_custom_urls' function

BaseAjaxModelAdmin:
  - in your ModelAdmin, subclass BaseAjaxModelAdmin and make sure
    your form is pointing to your dynamic form.

  - there will be a new url that ends with /ajax/ that handles the
    ajax request.

  - Django's ModelAdmin will only display fields declared in a fieldset
    so we make sure the Ajax fields don't display when they don't have
    enough data to be present, and that they do display when they do.
    Because of this, we currently are not respecting any fieldsets
    you might have declared in your ModelAdmin. If you know of a
    good way to lift this restriction, please submit a patch.


BaseAjaxModelForm:
  - set the ajax_change_field to be the name of the form field whose
    change triggers the ajax call OR set the ajax_change_fields to a
    list of field names whose change triggers the ajax call

  - in your form, set the dynamic_fields property to return a dictionary
    whose keys are the field names and values are the instantiated fields.

    @property
    def dynamic_fields(self):
        return {
            'my_field': CharField(initial="hello world!", label="Greeting"),
        }

    when the change field is present either in a forms initial data or
    submitted data, the form will add all your dynamic fields to it, and
    when saving, the form will make sure all your dynamic field values
    are saved to the instance.

  - make sure the file in djadmin_ext/static/djadmin_ext/admin_ajax.js
    is available in your static content.

  - The ajax call gets the new form and replaces all
    the elements with the class of '.module' with the updated form.

    NOTE: this will blow out any inline forms you have declared, so
    if you need inline forms, we'd be happy to accept a patch making
    it possible.

Testing:
To test the admin, we wrote selenium tests. The tests will try
to start django's test server, open a firefox browser window,
execute the tests and verify the actions on the page behave as
expected.

python setup.py test


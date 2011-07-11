
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper

class BaseAjaxModelAdmin(admin.ModelAdmin):
    ajax_template_name = None
    add_form_template = 'djadmin_ext/ajax_change_form.html'
    change_form_template = 'djadmin_ext/ajax_change_form.html'

    def get_fieldsets(self, request, obj=None, ajax_form=None):
        """
        Django's Admin normally looks at the form class to find
        fields to display on the page. In a dynamic environment,
        these must come from an instance, so logic can be applied.

        We're not respecting any fieldsets the user may have applied
        on the ModelAdmin... sorry charlie.
        """
        if not ajax_form:
            ajax_form = self.get_ajax_form(request, obj=obj)
        return [(None, {'fields': ajax_form.fields.keys()})]

    def get_ajax_context(self, request):
        ajax_form = self.get_ajax_form(request)
        return {
            'adminform': helpers.AdminForm(
                ajax_form,
                self.get_fieldsets(request, ajax_form=ajax_form),
                self.prepopulated_fields,
                self.get_readonly_fields(request),
                model_admin=self,
            )
        }

    def get_ajax_form(self, request, obj=None):
        form_class = self.get_form(request)
        return form_class(initial=self.query_dict_to_dict(request.REQUEST), instance=obj)

    def query_dict_to_dict(self, query_dict):
        return dict([(k, query_dict.get(k)) for k in query_dict])

    def ajax_view(self, request, *args, **kwargs):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.object_name.lower()

        context = self.get_ajax_context(request)
        return render_to_response(
            self.ajax_template_name or [
                "admin/%s/%s/ajax_form.html" % (app_label, model_name),
                "admin/%s/ajax_form.html" % app_label,
                "admin/ajax_form.html",
                "djadmin_ext/ajax_form.html",
            ],
        context)

    def get_custom_urls(self, wrapper):
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
            url(r'^ajax/$',
                wrapper(self.ajax_view), name='%s_%s_ajax' % info),
        )

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        _patterns = self.get_custom_urls(wrap)
        return _patterns + super(BaseAjaxModelAdmin, self).get_urls()
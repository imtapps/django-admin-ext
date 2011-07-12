
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper

__all__ = (
    'BaseCustomUrlAdmin', 'BaseAjaxModelAdmin',
)

class BaseCustomUrlAdmin(admin.ModelAdmin):
    """
    Provides a hook to unobtrusively give your ModelAdmin
    some custom urls.
    """
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        _patterns = self.get_custom_urls(wrap)
        return _patterns + super(BaseCustomUrlAdmin, self).get_urls()

    def get_custom_urls(self, wrapper):
        """
        Your ModelAdmin should override this method and return
        a django 'patterns' object.

        If your view is a method on the ModelAdmin, it will
        be necessary to wrap the view in the wrapper to make
        sure the view is called properly. If the view is just
        a normal function outside of any class, you won't need
        the wrapper.
        """
        raise NotImplementedError


class BaseAjaxModelAdmin(BaseCustomUrlAdmin):
    ajax_template_name = None
    add_form_template = 'djadmin_ext/ajax_change_form.html'
    change_form_template = 'djadmin_ext/ajax_change_form.html'

    def get_fieldsets(self, request, obj=None, ajax_form=None):
        """
        Django's Admin normally looks at the form class to find
        fields to display on the page. In a dynamic environment,
        the available fields must come from an instance, so logic
        can be applied.

        We're not respecting any fieldsets the user may have applied
        on the ModelAdmin... sorry charlie.

        Additionally, the add_view and change_view don't have nice
        hooks to override how we get the instantiated form and only
        calls the get_fieldsets method with a request and maybe an
        object. When this is the case, we'll be instantiating the form
        twice, but it's a necessary evil because we can't cache the
        for in the Admin and keep thread safety.
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
        """
        We set the request parameters to 'initial' data so the ajax
        form doesn't trigger validation. (it would if we used 'data')
        """
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
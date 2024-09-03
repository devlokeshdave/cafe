from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import redirect, render


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to pages/urls.py file for more pages.
"""


class PagesView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

def error_view(request, exception):
    initial_context = {}
    initial_context = TemplateLayout.init(None, initial_context)
    return render(request, 'pages_misc_error.html',status=404)

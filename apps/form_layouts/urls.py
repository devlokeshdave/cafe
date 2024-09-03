from django.urls import path
from .views import FormLayoutsView, kot_add, kot_list, kot_view, Kot_table



urlpatterns = [
    path(
        "form/layouts_vertical/",
        FormLayoutsView.as_view(template_name="form_layouts_vertical.html"),
        name="form-layouts-vertical",
    ),
    path(
        "form/layouts_horizontal/",
        FormLayoutsView.as_view(template_name="form_layouts_horizontal.html"),
        name="form-layouts-horizontal",
    ),
    path("kot-add",kot_add,name="kot-add"),
    path("kot-add/<str:pk>",kot_add,name="kot-add"),
    path("kot-list",kot_list,name="kot-list"),
    path("kot-list/<str:pk>",kot_list,name="kot-list"),
    path("kot-view/<str:pk>",kot_view,name="kot-view"),
    path("kot-table",Kot_table,name="kot-table"),
]

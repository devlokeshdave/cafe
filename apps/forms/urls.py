from django.urls import path
from .views import FormsView
from .views import add_item, menu, add_order, order_list, tableList, tax_show, inventory, max_order



urlpatterns = [
    path(
        "forms/basic_inputs/",
        FormsView.as_view(template_name="forms_basic_inputs.html"),
        name="forms-basic-inputs",
    ),
    path(
        "forms/input_groups/",
        FormsView.as_view(template_name="forms_input_groups.html"),
        name="forms-input-groups",
    ),
    path("add-item",add_item,name="add-item"),
    path("menu",menu,name="menu"),
    path("menu/<str:pk>",menu,name="menu"),
    path("inventory/<str:pk>",inventory,name="inventory"),
    path("inventory",inventory,name="inventory"),
    path("add-order",add_order,name="add-order"),
    path("add-order/<str:pk>",add_order,name="add-order"),
    path("order-view/<str:pk>",order_list,name="order-view"),
    path("order-list",order_list,name="order-list"),
    path("table-list",tableList,name="table-list"),
    path("tax-show",tax_show,name="tax-show"),
    path("tax-show/<str:pk>",tax_show,name="tax-show"),
    path("max-order",max_order, name="max-order")
]

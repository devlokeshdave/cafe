from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.models import cafe, permission
from apps.forms.models import Menu, Order_list
from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

@login_required(login_url="/")
def dashboard(request):
    user = request.user
    permission_name = permission.objects.get(user=user)
    cafe_name = permission_name.cafe
    menu = Menu.objects.filter(cafe=cafe_name)
    order = Order_list.objects.filter(cafe=cafe_name)
    end_date= datetime.now().date()
    start_date = end_date - timedelta(days=30)
    order = order.filter(date__range=[start_date,end_date])
    qty = {}
    
    for items in order:
        for key in items.items.keys():
            print("key",key)
            if key in qty:
                qty[key] += items.items[key]["qty"]
            else:
                qty[key] = items.items[key]["qty"]
    print("men...",qty)
    sales = sum(qty.values())
    menu = menu.filter(name__in=qty.keys())
    per_item_profit = {}
    per_item_per = {}
    item_original = {}
    item_discount = {}
    total_item = 0
    for menus in menu:
        print("go..>>",)
        total_item += menus.total_pieces 
        original_price = menus.total_pieces * menus.price
        num_item = menus.total_pieces
        # get discount price on total items 
        discount_on = original_price * (menus.discount/100)
        # get original price for per item
        original = menus.price
        # get discount in price
        discount_price = original_price - discount_on
        item_original[menus.name] = menus.price
       
        # discount per items in per
        price_per = discount_price/num_item
        item_discount[menus.name] = price_per
        # get new box price
        new_box_price = original - price_per
        # get per items final discount price or profit
        new_box_per = price_per/original * 100 
        per_item_profit[menus.name] = new_box_price
        per_item_per[menus.name] = new_box_per
    
    profit = 0
    profit_per = 0
    original_ = 0
    discount_ = 0
    profit_am = 0
    total_profit_per = 0
    print("qty", qty,  per_item_profit)
    for items in qty.keys() :
    
        profit += qty[items] * per_item_profit[items]
        original_ += qty[items] * item_original[items]
        print("original",item_original[items], qty[items], item_original[items] *  qty[items])
        discount_ += qty[items] * item_discount[items]
        print("discount",qty[items], item_discount[items], item_discount[items] *  qty[items])
    if original_ != 0:
        total_profit_per = ((original_ - discount_)/original_) * 100
        profit_am = original_ - discount_
    
    sale_per = (sales/total_item) * 100
    initial_context = {"sale": sales, "sale_per":round(sale_per, 2), "profit_am":round(profit_am, 2),
                       "profit_per":round(total_profit_per,2)}
    initial_context = TemplateLayout.init(None, initial_context)
    return render(request, 'dashboard_analytics.html',initial_context )

    
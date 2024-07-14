from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from apps.authentication.models import cafe, permission
from .models import Menu, Order_list, Number_table, tax
import json
from django.http import JsonResponse
from .form import Order
from datetime import datetime, timedelta
from apps.form_layouts.models import Regular_customer, Bill_regular, Account_balance

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to form/urls.py file for more pages.
"""


class FormsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# @login_required(login_url="/")
# def add_item(request):
#     initial_context = {}
#     initial_context = TemplateLayout.init(None, initial_context)

#     # Ensure the layout path is correctly set and updated in the context

#     # Ensure the layout path is correctly set and updated in the context
#     layout_path = initial_context.get("layout_path")

#     if not layout_path:
#         raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

#     return render(request, "addItem.html", initial_context)

@login_required(login_url="/")
def menu(request, pk=None):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    menu = Menu.objects.filter(cafe=cafe_check)
    print("pk",pk)
    if request.method == "GET":
        if pk is not None:
            menu = menu.filter(category=pk)
    arr= ["Beverages","Breakfast","Lunch","Snacks","Desserts","Specialty Items","Salads"]
    try:
        tax_ = tax.objects.get(cafe=cafe_check)
    except tax.DoesNotExist:
        tax_ = None
    initial_context = {"menu":menu, "tax":tax_, "cafe":cafe_check.id,"arr":arr}
    initial_context = TemplateLayout.init(None, initial_context)
    layout_path = initial_context.get("layout_path")

    if not layout_path:
        raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

    if request.method == "DELETE":
        Menu.objects.get(id=pk).delete()
        return JsonResponse({"msg":"Item delete successfully"})

    if request.method == "POST":
        print("go...<<>")
        data = request.POST
        check = Menu.objects.get(id=pk)
        if check.name != data["name"]:
            name_check = menu.filter(name=data["name"])
            if name_check.exists():
                return JsonResponse({"msg":"name already exists"})

        check.name = data["name"]
        check.price = data["price"]
        check.save()
        return JsonResponse({"msg":"Item edit successfully"})
    return render(request, 'menu.html',initial_context )

@login_required(login_url="/")
def add_item(request, pk=None):
    user = request.user
    permission_name = permission.objects.get(user=user)
    cafe_name = permission_name.cafe
    status = 200
    initial_context = {}
    if pk is not None:
        menu = Menu.objects.get(id=pk)
        initial_context["menu"] = menu
    if request.POST.get('_method') == "POST":
        data = json.loads(request.POST.get('data'))
        all_name = []
        for info in data:
            if info["name"] not in all_name:
                all_name.append(info["name"])
        filter_check = {"cafe":cafe_name, "name__in":all_name}
        name_check = Menu.objects.filter(**filter_check)
        existing_names_list = []
        if name_check.exists():
            existing_names = name_check.values_list('name', flat=True)
            existing_names_list = list(existing_names)
        # print("goo..>",existing_names_list,len(name_check),len(existing_names_list) < len(name_check))
        if len(existing_names_list) < len(all_name):
            for info in data:
                if info["name"] not in existing_names_list:
                    total = float(info["total"])
                    given_am = int(int(info["pieces_qty"]) * int(info["qty"]) * float(info["price"]))
                    discount_am = ((given_am - total)/given_am * 100)
                    total_pieces = (float(info["pieces_qty"]) * float(info["qty"]) )
                    menu = Menu(
                        cafe=cafe_name,
                        name = info["name"],
                        price = info["price"],
                        date=info["date"],
                        qty=info["qty"],
                        pieces_qty=info["pieces_qty"],
                        total=info["total"],
                        category=info["category"],
                        discount = discount_am,
                        total_pieces = total_pieces
                    )
                    menu.save()

            if len(existing_names_list) <= 0:
                initial_context = {"msg":"data added successfully"}
                status = 201

            else:
                name = ",".join(existing_names_list)
                initial_context = {"error":f"data {name} already exists"}
                status = 400
        else:
            name = ",".join(existing_names_list)
            initial_context = {"error":f"data {name} already exists"}
            status = 400

        return JsonResponse(initial_context, status=status)

    if request.POST.get('_method') == "PUT":
        data = request.POST
        if pk is not None:
            menu = Menu.objects.get(id=pk)
            filter_ = {"name":data["name"], "cafe":menu.cafe}
            check = Menu.objects.filter(filter_)
            if menu.name != data["name"]:
                if check.exists():
                    status = 400
                    initial_context = {"error":f"{menu.cafe} name already exists"}
                else:
                    menu =  check.update(
                        name = data["name"], price= data["price"]
                    )
                    status = 200
                    initial_context = {"msg":f"{data['name']} edited successfully"}

    if request.POST.get("_method") == "DELETE":
        if pk is not None:
            menu = Menu.objects.get(id=pk)
            name = menu.name
            menu.delete()
            status = 200
            initial_context = {"msg":f"{name} deleted successfully"}


    initial_context = TemplateLayout.init(None, initial_context)

    # Ensure the layout path is correctly set and updated in the context

    # Ensure the layout path is correctly set and updated in the context
    layout_path = initial_context.get("layout_path")

    if not layout_path:
        raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

    return render(request, "addItem.html", initial_context, status=status)


@login_required(login_url="/")
def add_order(request, pk=None):
    user = request.user
    permission_name = permission.objects.get(user=user)
    cafe_name = permission_name.cafe
    menu = Menu.objects.filter(cafe=cafe_name)
    id = menu.first().cafe.id
    try:
        tax_ = tax.objects.get(cafe=cafe_name)
    except tax.DoesNotExist:
        tax_ = None
    tables = ["Table-1","Table-2","Table-3","Table-4","Table-5","Table-6","Table-7"]
    table_no = f"Table-{pk}"
    customer  = Regular_customer.objects.filter(cafe=cafe_name)
    initial_context = {"menu":menu,"tables":tables,"id":id,
                       "table_no":table_no, "tax_":tax_, "customer":customer}
    print("request.method", request.method)
    initial_context = TemplateLayout.init(None, initial_context)

    if request.POST.get('_method') == "POST":
        data = request.POST["data"]
        data = json.loads(data)
        form = Order(data)
        if form.is_valid():
            form.save()

            for item in data["items"].keys():
                menu_get = menu.filter(name=item).first()
                menu_get.total_pieces -= int(data["items"][item]["qty"])
                menu_get.save()
            if data["cust_type"] != "other":
                reg_id = ""
                if "reg_id" not in data:
                    reg_id = Regular_customer(
                        cafe = cafe_name,
                        name = data["regular_name"],
                        mobile = data["mobile"]
                    ).save()
                else:
                    reg_id = Regular_customer.objects.get(id=data["reg_id"])

                bill_reg = Bill_regular(
                    cafe =cafe_name,
                    customer=reg_id,
                    total=data["total"],
                    reaming=data["reaming"],
                    date=data["date"],
                    items=data["items"]
                ).save()



            return JsonResponse({"msg": "Data saved successfully"}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)

    if request.method == "DELETE":
        Order_list.objects.get(id=pk).delete()
        return JsonResponse({"msg":"Order delete successfully"})
    return render(request, "add_order.html",initial_context)


@login_required(login_url="/")
def order_list(request, pk=None):
    user = request.user
    if pk is not None:
        order = Order_list.objects.get(id=pk)
        initial_context = {"order" : order}
        initial_context = TemplateLayout.init(None, initial_context)
        layout_path = initial_context.get("layout_path")

        if not layout_path:
            raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

        return render(request, 'order_view.html',initial_context )
    else:
        end_date= datetime.now().date()
        start_date = end_date - timedelta(days=1)
        start_date_get = request.GET.get('start_date')
        end_date_get = request.GET.get('end_date')
        cafe_check = permission.objects.get(user=user).cafe
        order = Order_list.objects.filter(cafe=cafe_check)
        if start_date_get and end_date_get:
            order = order.filter(date__range=[start_date_get,end_date_get])
        else:
            order = order.filter(date__range=[start_date,end_date])
        initial_context = {"order":order}
        initial_context = TemplateLayout.init(None, initial_context)
        layout_path = initial_context.get("layout_path")

        if not layout_path:
            raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

        return render(request, 'order_list.html',initial_context )


@login_required(login_url="/")
def tableList(request):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    table = Number_table.objects.get(cafe=cafe_check)
    tables = []
    k = 1
    for i in range(table.number):
        tables.append(f"table {k}")
        k += 1
    initial_context = {"tables":tables}
    initial_context = TemplateLayout.init(None, initial_context)
    layout_path = initial_context.get("layout_path")
    if not layout_path:
        raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

    if request.method == 'POST':
        data = request.POST
        if data["type"] == "add":
            table.number += 1

        else:
            table.number -= 1
        table.save()
        return JsonResponse({"msg":"data added successfully"})
    return render(request, 'tableLIst.html',initial_context )

@login_required(login_url="/")
def tax_show(request, pk=None):
    if request.method == "POST":
        data = json.loads(request.body)
        print("data",data)
        cafe_ = cafe.objects.get(id=data["cafe"])
        if pk is None:
            tax(
                cafe = cafe_,
                name = data["name"],
                tax = data["tax"]
            ).save()
        else:
            tax_ = tax.objects.get(id=pk)
            tax_.name = data["name"]
            tax_.tax = data["tax"]
            tax_.save()

        return JsonResponse({"msg":"Data save successfully"})

@login_required(login_url="/")
def inventory(request, pk=None):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    menu = Menu.objects.filter(cafe=cafe_check)
    try:
        tax_ = tax.objects.get(cafe=cafe_check)
    except tax.DoesNotExist:
        tax_ = None
    initial_context = {"menu":menu, "tax":tax_, "cafe":cafe_check.id}
    initial_context = TemplateLayout.init(None, initial_context)
    layout_path = initial_context.get("layout_path")

    if not layout_path:
        raise ValueError("The layout path is empty. Please check the TemplateHelper.set_layout method.")

    if request.method == "DELETE":
        Menu.objects.get(id=pk).delete()
        return JsonResponse({"msg":"Item delete successfully"})

    if request.method == "POST":
        print("go...<<>")
        data = json.loads(request.body)
        check = Menu.objects.get(id=pk)
        if data["type"] == "total_piece":
            qty = (int(data["pieces_qty"]) + check.total_pieces)/ check.pieces_qty
            check.total_pieces += int(data["pieces_qty"])
            check.total += int(data["total"])
            check.qty = qty
            real_price = check.total_pieces * check.price
            discount =  check.total / real_price
            check.discount = discount
        else:
            check.qty += int(data["pieces_qty"])
            check.total_pieces = check.qty * check.pieces_qty
            real_price = check.total_pieces * check.price
            discount =  check.total / real_price
            check.discount = discount
            check.total += int(data["total"])


        check.save()
        return JsonResponse({"msg":"Item edit successfully"})
    return render(request, 'inventory_table.html',initial_context )

@login_required(login_url="/")
def max_order(request):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    menu = Menu.objects.filter(cafe=cafe_check)
    end_date= datetime.now().date()
    start_date = end_date - timedelta(days=15)
    start_date_get = request.GET.get('start_date')
    end_date_get = request.GET.get('end_date')
    cafe_check = permission.objects.get(user=user).cafe
    order = Order_list.objects.filter(cafe=cafe_check)
    if start_date_get and end_date_get:
        order = order.filter(date__range=[start_date_get,end_date_get])
    else:
        order = order.filter(date__range=[start_date,end_date])

    dict_ = {}
    for item in order:
        for key in item.items.keys():
            if key in dict_:
                dict_[key]["item"] = key
                dict_[key]["qty"] += int(item.items[key]["qty"])
                dict_[key]["price"] = float(item.items[key]["price"])
                dict_[key]["total"] = dict_[key]["qty"] * dict_[key]["price"]
            else:
                dict_[key] = {
                    "item": key,
                    "qty" : int(item.items[key]["qty"]) ,
                    "price" : float(item.items[key]["price"]),
                    "total" : float(item.items[key]["price"]),
                }
    at_max = [dict_[item] for item in dict_]
    sorted_data_desc = sorted(at_max, key=lambda x: x['qty'], reverse=True)
    print("goo.",sorted_data_desc)
    initial_context = {"order":sorted_data_desc}
    initial_context = TemplateLayout.init(None, initial_context)
    print("dict...",dict_)

    return render(request, 'max_order.html',initial_context )

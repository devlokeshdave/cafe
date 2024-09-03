from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import json
from apps.forms.models import  Menu, tax
from apps.authentication.models import permission, cafe
from .models import Kot, Kot_Table
from datetime import datetime
from django.http import JsonResponse
"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to form_layouts/urls.py file for more pages.
"""


class FormLayoutsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

@login_required(login_url="/")
def kot_add(request, pk=None):
    # data = json.loads(request.body)
    # print("data",data)
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    menu = Menu.objects.filter(cafe=cafe_check)
    table_no = f"Table-{pk}"

    if request.method == "POST":
        if pk is None:
            print("request",request.POST)
            data = json.loads(request.POST["data"])
            sendDate = data["date"]
            sendTime = data["time"]
            # filter_check = {"cafe":cafe_check,"table":data["table"]}
            # kot = Kot.objects.filter(**filter_check).order_by('-id').first()
            is_active = True
            id = Kot(
                sendDate =sendDate,
                sendTime=sendTime,
                cafe=cafe_check,
                items=data["items"],
                active=is_active,
                table=data["table"]
            )
            id.save()
            context = {"msg":"Data saved successfully", "id":id.id}
            return JsonResponse(context, status=200)
        else:
            kot = Kot.objects.get(id=pk)
            if kot.print is not True:
                kot.print = True
                kot.save()
            return JsonResponse({"msg": "Data saved successfully"}, status=200)
    # if     pk is None:
    #     tax(
    #         cafe = cafe_,
    #         name = data["name"],
    #         tax = data["tax"]
    #     ).save()
    # else:
    #     tax_ = tax.objects.get(id=pk)
    #     tax_.name = data["name"]
    #     tax_.tax = data["tax"]
    #     tax_.save()
    initial_context = {"menu":menu,"cafe":cafe_check, "id":cafe_check.id, "table_no":table_no}
    initial_context = TemplateLayout.init(None, initial_context)
    return render(request, 'Kot_add.html',initial_context )

@login_required(login_url="/")
def kot_list(request, pk=None):
    user = request.user
    if request.method == "DELETE":
        id = Kot.objects.get(id=pk)
        id.delete()
        return JsonResponse({"msg":"Kot delete successfully"})
    cafe_check = permission.objects.get(user=user).cafe
    list_ = []
    end_date= datetime.now().date()
    start_date_get = request.GET.get('start_date')
    end_date_get = request.GET.get('end_date')
    kot = Kot.objects.filter(cafe=cafe_check)
    if start_date_get and end_date_get:
        kot = kot.filter(sendDate__range=[start_date_get,end_date_get])
    else:
        kot = kot.filter(sendDate=end_date)
    initial_context = {"order":kot, "kot_item":list_}
    initial_context = TemplateLayout.init(None, initial_context)
    return render(request, 'Kot_list.html',initial_context )

@login_required(login_url="/")
def kot_view(request, pk=None):
    list_ = []
    kot = Kot.objects.get(id=pk)
    for item in kot.items.keys():
        dict_ = {}
        dict_["name"] = item
        dict_["qty"] = kot.items[item]["qty"]
        list_.append(dict_)
    print = kot.print

    table = f"kot_Table-{kot.table.split('-')[1]}"
    initial_context = {"order":kot, "kot_item":list_,"print":print,"table":table}
    initial_context = TemplateLayout.init(None, initial_context)
    return render(request, 'Kot_View.html',initial_context )

@login_required(login_url="/")
def Kot_table(request):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    table = Kot_Table.objects.get(cafe=cafe_check)
    filter_ = {"cafe":cafe_check}
    kot_ = Kot.objects.filter(**filter_)
    tax_ = tax.objects.get(cafe=cafe_check)
    tables = []
    last_list = []
    k = 1
    for i in range(table.number):
        one_ = {}
        tables.append(f"table {k}")
        tab = kot_.filter(table=f"Table-{k}").last()
        if tab:
            if tab.print is False:
                one_["time"] = tab.sendTime.strftime("%H:%M")
                one_["item"] = tab.items
                one_["table"] = tab.table
                one_["id"] = tab.id
                last_list.append(one_)
        k += 1

    print(last_list)
    initial_context = {"tables":tables, "tax":tax_,"kot":last_list, "num": k-1}
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
    return render(request, 'KotList.html',initial_context )

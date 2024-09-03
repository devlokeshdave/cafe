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
from apps.form_layouts.models import Regular_customer, Bill_regular, Account_balance, Kot
from django.http import HttpResponse
from django.db.models import F, ExpressionWrapper, DateTimeField
# from escpos.printer import Usb
# from escpos.printer import Network

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
    arr= ["Beverages","Quick Bites","Rashoi","Starter","Main Course","Specialty Items","Salads"]
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
    table_no = f"Table-{pk}"
    filer_kot = {"cafe":cafe_name, "active":True,"table":table_no}
    all_kot = Kot.objects.filter(**filer_kot).order_by('-id').first()
    if all_kot:
        filer_kot["id__gt"] = all_kot.id
        records_after_latest_true = Kot.objects.filter(**filer_kot)
    else:
        records_after_latest_true = None
    tables = ["Table-1","Table-2","Table-3","Table-4","Table-5","Table-6","Table-7"]

    customer  = Regular_customer.objects.filter(cafe=cafe_name)
    initial_context = {"menu":menu,"tables":tables,"id":id,
                       "table_no":table_no, "tax_":tax_, "customer":customer, "kot":records_after_latest_true}
    print("request.method", request.method)
    initial_context = TemplateLayout.init(None, initial_context)

    if request.POST.get('_method') == "POST":
        data = request.POST["data"]
        data = json.loads(data)
        data["time"] = datetime.now().time()
        form = Order(data)
        str_cpy = ""
        if form.is_valid():
            form.save()
            filter_ = {"cafe": cafe_name, "table":data["table"]}
            kot_ = Kot.objects.filter(**filter_)
            last_kot = kot_.last()

            if last_kot and last_kot.active:
                last_kot.active = False
                last_kot.save()
                print("false done", last_kot.id, last_kot.active)

            for item in data["items"].keys():
                menu_get = menu.filter(name=item).first()
                menu_get.total_pieces -= int(data["items"][item]["qty"])
                menu_get.save()
                str_cpy += f'{item: <5} X  {data["items"][item]["qty"]: <7} {data["items"][item]["price"]: >5.2f}\n'
            if data["cust_type"] != "other":
                reg_id = ""
                filter_d = {"cafe":cafe_name, "mobile":data["mobile"]}
                check_r = Regular_customer.objects.filter(**filter_d)
                if not check_r.exists():
                    reg_id = Regular_customer(
                        cafe = cafe_name,
                        name = data["regular_name"],
                        mobile = data["mobile"]
                    )
                    reg_id.save()
                    print("save.....",reg_id)
                else:
                    reg_id = check_r.first()

                bill_reg = Bill_regular(
                    cafe =cafe_name,
                    customer=reg_id,
                    total=data["total"],
                    reaming=data["total"],
                    date=data["date"],
                    items=data["items"]
                ).save()

                check = Account_balance.objects.filter(customer=reg_id).filter(complete=False)
                if check.exists():
                    check.first().bills.add(bill_reg)
                else:
                    ac_add = Account_balance(
                        cafe=cafe_name,
                        customer=reg_id,
                        complete=False
                    )
                    ac_add.save()
                    ac_add.bills.add(bill_reg)
            head = f'{"item": <5} X  {"Qty": <7} {"Price": >5}\n'
            tax_value = f'{tax_.tax:<5.1f}'
            tax_S = f'Tax({tax_value.rstrip()}) {"":<7}  {data["tax"]:<7.1f}\n'
            total_S = f'{"Total": <15}   {data["total"]: <7}\n'
            bill_content = f"""
                {cafe_name.name}
                Address, City, State, Zip
                Phone:

                --------------------------------
                {head}
                --------------------------------
                {str_cpy}

                {tax_S}
                {total_S}

                Thank you for your visit!
                """
            print(bill_content)
            # try:
            #     # Send the bill content to the printer
            #     printer = Network('192.168.1.100', port=9100)
            #     printer.text(bill_content)
            #     printer.cut()
            #     printer.close()

            # except Exception as e:
            #     print("go....",str(e))

            return JsonResponse({"msg": "Data saved successfully"}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)

    if request.method == "DELETE":
        Order_list.objects.get(id=pk).delete()
        return JsonResponse({"msg":"Order delete successfully"})
    return render(request, "add_order.html",initial_context)

@login_required(login_url="/")
def entry(request):
    user = request.user
    cafe_check = permission.objects.get(user=user).cafe
    all_it = {

    "Beverages": {
        "Cappuccino (Add-Vanilla, Caramel, Hazelnut)": 129,
        "Espresso Shot": 99,
        "Americano": 99,
        "Cafe Late": 129,
        "Mochaccino": 149,
        "Affogato": 99,
        "Flat White": 109,
        "Nutella Cappuccino": 159,
        "Iced Americano": 109,
        "Redbull Espresso": 145,
        "Cranberry Bru": 149,
        "Vietnamese": 155,
        "Iced Late": 155,
        "Iced Caramel Late": 165,
        "Green Tea": 79,
        "Honey Ginger": 109,
        "Hibiscus": 125,
        "Butterfly": 125,
        "Chamomile": 119,
        "Kashmiri Kahva": 99,
        "Classic": 199,
        "Hazelnut": 185,
        "Brownie": 199,
        "Cookie & Cream": 185,
        "Choco Chips": 149,
        "Nutella": 179,
        "Caramel": 185,
        "Strawberry": 169,
        "Pineapple": 169,
        "Butter Scotch": 179,
        "Mango": 169,
        "Badam": 179,
        "Blueberry": 189,
        "Oreo": 189,
        "KitKat": 219,
        "Chocolate": 189,
        "Chocolate Peanut Butter": 199,
        "Ferrero Rocher": 210,
        "Mint Mojito": 169,
        "Keri Pudina": 159,
        "Blood Orange": 199,
        "Pomegranate": 179,
        "Blue Lagoon": 169,
        "Green Apple": 169,
        "Watermelon": 169,
        "Lemon Ice Tea": 119,
        "Peach Ice Tea": 149,
        "Blueberry Ice Tea": 159,
        "Redbull Ice Tea": 189,
        "Raspberry Ice Tea": 149,
        "Strawberry Banana": 219,
        "Basil Apple Kiwi": 229,
        "All Berry Bang": 239,
        "Fusion Bowl": 219,
        "Caribbean Citrus Pina Colada": 219,
        "Spiced Guava Martini": 185
    },

    "Quick Bites": {
        "Plain Dosa (Regular)": 99,
        "Plain Dosa (Butter)": 110,
        "Masala Dosa (Regular)": 129,
        "Masala Dosa (Butter)": 149,
        "Cheese Masala Dosa (Regular)": 139,
        "Cheese Masala Dosa (Butter)": 149,
        "Pav Bhaji Dosa (Regular)": 139,
        "Pav Bhaji Dosa (Butter)": 149,
        "Plain Utapam (Regular)": 139,
        "Plain Utapam (Butter)": 159,
        "Onion Utapam (Regular)": 139,
        "Onion Utapam (Butter)": 165,
        "Tomato Utapam (Regular)": 149,
        "Tomato Utapam (Butter)": 165,
        "Mix Veg Utapam (Regular)": 149,
        "Mix Veg Utapam (Butter)": 165,
        "Masala Utapam (Regular)": 149,
        "Masala Utapam (Butter)": 165,
        "Vadapav (Regular)": 40,
        "Vadapav (Butter)": 40,
        "Vadapav (Cheese)": 40,
        "Jain Vadapav (Regular)": 45,
        "Jain Vadapav (Butter)": 70,
        "Jain Vadapav (Cheese)": 100,
        "Swaminarayan Vadapav (Regular)": 40,
        "Swaminarayan Vadapav (Butter)": 60,
        "Swaminarayan Vadapav (Cheese)": 90,
        "Bombay Vadapav (Regular)": 35,
        "Bombay Vadapav (Butter)": 60,
        "Bombay Vadapav (Cheese)": 75,
        "Masala Pav (Regular)": 35,
        "Masala Pav (Butter)": 50,
        "Masala Pav (Cheese)": 75,
        "Tandoori Cheese Vadapav": 50,
        "Cheese Burst Vadapav": 50,
        "Peri Peri Vadapav": 50,
        "Cheesy Herbs Vadapav": 50,
        "Schezwan Vadapav": 50,
        "Makhani Vadapav": 50,
        "Spicy Tangy Vadapav": 50,
        "Exotic Vadapav": 50,
        "Dabeli (Regular)": 40,
        "Dabeli (Butter)": 59,
        "Dabeli (Cheese)": 89,
        "Jain Dabeli (Regular)": 45,
        "Jain Dabeli (Butter)": 69,
        "Jain Dabeli (Cheese)": 99,
        "Swaminarayan Dabeli (Regular)": 40,
        "Swaminarayan Dabeli (Butter)": 59,
        "Swaminarayan Dabeli (Cheese)": 89,
        "Bhel (Regular)": 90,
        "Bhel (Cheese)": 109,
        "Jain Bhel (Regular)": 90,
        "Jain Bhel (Cheese)": 109,
        "Sev Puri (Regular)": 75,
        "Sev Puri (Cheese)": 99,
        "Jain Sev Puri": 75,
        "Dahi Puri (9 Pcs.)": 99,
        "Pav Bhaji (Regular)": 129,
        "Pav Bhaji (Butter)": 159,
        "Pav Bhaji (Cheese)": 179,
        "Jain Pav Bhaji (Regular)": 129,
        "Jain Pav Bhaji (Butter)": 159,
        "Jain Pav Bhaji (Cheese)": 179,
        "Masala Pav (Regular)": 119,
        "Masala Pav (Butter)": 139,
        "Masala Pav (Cheese)": 169,
        "Extra Pav (Regular)": 25,
        "Extra Pav (Butter)": 35,
        "Pulav (Regular)": 129,
        "Pulav (Butter)": 159,
        "Pulav (Cheese)": 179,
        "Jain Pulav (Regular)": 129,
        "Jain Pulav (Butter)": 159,
        "Jain Pulav (Cheese)": 179,
        "Jam Muskabun (Regular)": 59,
        "Jam Muskabun (Cheese)": 89,
        "Butter Muskabun (Regular)": 59,
        "Butter Muskabun (Cheese)": 89,
        "Chocolate Muskabun (Regular)": 59,
        "Chocolate Muskabun (Cheese)": 89,
        "Chutney Muskabun (Regular)": 59,
        "Chutney Muskabun (Cheese)": 89,
        "Butter Slice (Regular)": 35,
        "Butter Slice (Cheese)": 49,
        "Jam Slice (Regular)": 39,
        "Jam Slice (Cheese)": 55,
        "Chatni Slice (Regular)": 35,
        "Chatni Slice (Cheese)": 49,
        "Sing Slice (Regular)": 39,
        "Sing Slice (Cheese)": 55,
        "Chola Kulcha": 99,
        "Extra Kulcha": 30,
        "French Fries (Regular)": 120,
        "French Fries (Cheese)": 135,
        "Peri Peri French Fries (Regular)": 129,
        "Peri Peri French Fries (Cheese)": 149,
        "Vegetable Maggi (Regular)": 79,
        "Vegetable Maggi (Butter)": 99,
        "Vegetable Maggi (Cheese)": 119,
        "Vegetable Puff (Regular)": 59,
        "Vegetable Puff (Cheese)": 89,
        "Madam D'Souza CTC (Grill)": 169,
        "Jain Madam D'Souza CTC (Grill)": 169,
        "Bread Butter (Regular)": 80,
        "Bread Butter (Grill)": 110,
        "Chatni Sandwich (Regular)": 80,
        "Chatni Sandwich (Regular Cheese)": 130,
        "Chatni Sandwich (Grill)": 120,
        "Chatni Sandwich (Grill Cheese)": 169,
        "Jam Sandwich (Regular)": 80,
        "Jam Sandwich (Regular Cheese)": 130,
        "Jam Sandwich (Grill)": 120,
        "Jam Sandwich (Grill Cheese)": 175,
        "Aloo Muter Sandwich (Regular)": 99,
        "Aloo Muter Sandwich (Regular Cheese)": 135,
        "Aloo Muter Sandwich (Grill)": 130,
        "Aloo Muter Sandwich (Grill Cheese)": 169,
        "Vegetable Sandwich (Regular)": 99,
        "Vegetable Sandwich (Regular Cheese)": 135,
        "Vegetable Sandwich (Grill)": 130,
        "Vegetable Sandwich (Grill Cheese)": 169,
        "Cheese Sandwich (Regular)": 140,
        "Cheese Sandwich (Grill Cheese)": 140,
        "Cheese Garlic Sandwich": 175,
        "Mexican Sandwich": 175,
        "Cheese Chilli Garlic Sandwich": 175,
        "Club Grill Sandwich (2 Slices)": 185,
        "Club Grill Sandwich (3 Slices)": 199,
        "3 In 1 Sandwich (Regular Cheese)": 175,
        "3 In 1 Sandwich (Grill Cheese)": 199,
        "Chocolate Sandwich (Regular)": 99,
        "Chocolate Sandwich (Grill)": 140,
        "Vegetable Burger (Regular)": 99,
        "Vegetable Burger (Cheese)": 119,
        "Crunchy Burger (Regular)": 99,
        "Crunchy Burger (Cheese)": 119,
        "Vegetable Hot Dog (Regular)": 99,
        "Vegetable Hot Dog (Cheese)": 119,
        "Steamed Momos (6 Pcs.)": 170,
        "Fried Momos (6 Pcs.)": 210,
        "Tandoori Momos (6 Pcs.)": 220,
        "Veg. Pizza (Small)": 230,
        "Veg. Pizza (Big)": 260,
        "Tandoori Paneer Pizza (Small)": 250,
        "Tandoori Paneer Pizza (Big)": 290,
        "Italian Pizza (Small)": 210,
        "Italian Pizza (Big)": 250,
        "Margherita Pizza (Plain) (Small)": 240,
        "Margherita Pizza (Plain) (Big)": 290,
        "Chatpata Pizza (Small)": 230,
        "Chatpata Pizza (Big)": 260,
        "Red Pasta": 199,
        "White Pasta": 199,
        "Cheese Pasta": 249,
        "Paneer Tikka Dry": 239,
        "Hariyali Paneer Tikka": 239,
        "Pineapple Paneer Tikka": 239,
        "Lahsuni Paneer Tikka": 265,
        "Malai Tikka": 279,
        "Shikari Paneer Tikka": 299,
        "Tandoori Platter": 365,
        "Hara Bhara Kebab (6 Pcs.)": 140,
        "Cheese Corn Balls": 170,
        "Veg. Seekh Kebab": 160,
        "Veg. Stu ffSizzler": 320,
        "Paneer Stick Sizzler": 349,
        "Cheese Stick Sizzler": 345,
        "Chinese Chatpata Sizzler": 399,
        "Dragon Potato": 209,
        "Spring Roll": 159,
        "Hakka Noodles": 209,
        "Veg. Chowmein": 179,
        "Chinese Bhel": 209,
        "Honey Chilli Potato": 179,
        "Gobi Manchurian": 199,
        "Veg. Cheese Spring Roll": 209,
        "Veg. Crispy": 210,
        "Schezwan Noodles": 209,
        "Manchurian Dry": 209,
        "Manchurian Gravy": 219,
        "Paneer Chilli Dry": 249,
        "Mushroom Chilli": 269,
        "Fried Rice": 209,
        "Schezwan Rice": 219,
        "Manchurian Rice": 239},
    "Rashoi":{
        "DAL": 170,
        "Dal Fry Dal Tadka": 180,
        "Dal Palak": 180,
        "Dal Makhani": 240,
        "Paneer Butter Masala": 280,
        "Matar Paneer": 290,
        "Shikari Paneer Tava": 320,
        "Paneer Lababdar": 300,
        "Palak Paneer": 280,
        "Paneer Mushroom": 320,
        "Paneer Matar Mushroom": 330,
        "Shahi Paneer": 280,
        "Paneer Toofani": 300,
        "Paneer Tikka Masala": 280,
        "Kadai Paneer": 280,
        "Paneer Bhurji": 320,
        "Handi Paneer": 310,
        "Paneer Chatpata": 320,
        "Paneer Kaju BT M/S": 360,
        "D'Souza Special 3x1": 500,
        "Sev Tamatar": 150,
        "Jeera Aloo": 180,
        "Bhindi Masala": 190,
        "Aloo Gobhi Dry": 210,
        "Govind Gata": 210,
        "Aloo Matar": 210,
        "Chana Masala": 210},
    "Starter" : {
        "Lemon Coriander Soup": 110,
        "Tomato Soup": 110,
        "Veg. Manchow Soup": 120,
        "Hot & Sour Soup": 120,
        "Sweet Corn Soup": 130,
        "Roasted Papad": 35,
        "Fry Papad": 40,
        "Masala Papad": 60,
        "Khichiya Plain": 40,
        "Masala Khichiya": 70,
        "Plain Rice": 170,
        "Jeera Rice": 190,
        "Chatpata Rice": 210,
        "Veg. Pulav": 210,
        "Veg. Biryani": 220,
        "Hyderabadi Biryani": 220,
        "Maa Ki Khichdi": 230,
        "Lahsuni Khichdi": 240,
        "Madam D'Souza Khichdi": 260,
        "Veg. Dum Biryani": 280,
        "Dal Rajma Khichdi": 280,
        "Cheese Khichdi": 299,
        "Butter Milk": 35,
        "Plain Curd": 75,
        "Makhaniya Lassi": 70,
        "Madam D'Souza Lassi": 135,
        "Boondi Raita": 120,
        "Veg. Raita": 120,
        "Curd Fry": 140,
        "Pineapple Raita": 140,
        "Green Salad": 70,
        "Mineral Water": 20
    },
    "Main Course": {
        "Mix Veg.": 170,
        "Veg. Kolhapuri": 210,
        "Veg. Handi": 210,
        "Veg. Kofta": 190,
        "Rani Kofta": 210,
        "Corn M/S": 210,
        "Corn Palak": 210,
        "Lahsuni Palak": 180,
        "Cheese Butter Masala": 270,
        "Kaju Butter Masala": 270,
        "Kaju Curry": 270,
        "Dum Aloo": 210,
        "Sabji Mili Juli": 260,
        "Malai Pyaz": 180,
        "Malai Kofta": 220,
        "Navratan Korma": 240,
        "Matar Methi Malai": 270,
        "Tandoori Roti": 20,
        "Tandoori Roti (Butter)": 25,
        "Lachcha Paratha": 50,
        "Butter Naan": 50,
        "Missi Roti": 60,
        "Butter Kulcha": 60,
        "Stuffed Naan": 70,
        "Garlic Naan": 70,
        "Churchur Naan": 110,
        "Cheese Chilli Garlic Naan": 140,
        "Basket (Roti, Naan, Lachcha, Missi Roti)": 160,
        "D'Souza Punjabi Thali": 270,
        "Rajasthani Thali": 270
       }
    }
    nd_date= datetime.now().date()
    for menus in all_it.keys():
        for item in all_it[menus].keys():
            Menu(
                cafe=cafe_check,
                name=item,
                price=all_it[menus][item],
                date = nd_date,
                qty = 1,
                pieces_qty = 20,
                total = all_it[menus][item] * 20,
                discount= 0,
                total_pieces = 20,
                category = menus,
            ).save()
    html = "<html><body>It is now %s.</body></html>"
    return HttpResponse(html)



@login_required(login_url="/")
def order_list(request, pk=None):
    user = request.user
    if pk is not None:
        order = Order_list.objects.get(id=pk)
        list_ = []
        for items in order.items.keys():
            dict_ = {}
            dict_["name"] = items
            dict_["qty"] = order.items[items]["qty"]
            dict_["price"] = int(order.items[items]["qty"]) * int(order.items[items]["price"])
            list_.append(dict_)

        initial_context = {"order" : order, "order_list":list_}
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
            order = order.filter(date__range=[start_date_get,end_date_get]).filter(unpaid=False)
        else:
            order = order.filter(date=end_date).filter(unpaid=False)

        order = order.order_by('-id')
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
    tax_ = tax.objects.get(cafe=cafe_check)
    tables = []
    k = 1
    kot_list = []
    for i in range(table.number):
        tables.append(f"table {k}")
        k += 1

    for tab in range(table.number):
        index = tab + 1
        table_ = f"Table-{index}"
        filer_kot = {"cafe":cafe_check, "active":False,"table":table_}
        all_kot = Kot.objects.filter(**filer_kot)
        gte_ = False
        if all_kot.exists():
            all_kot = all_kot.last()
        else:
            filer_kot["active"] = True
            all_kot = Kot.objects.filter(**filer_kot).first()
            gte_ = True
        if all_kot:
            if gte_:
                filer_kot["id__gte"] = all_kot.id
            else:
                del filer_kot["active"]
                filer_kot["id__gt"] = all_kot.id
            records_after_latest_true = Kot.objects.filter(**filer_kot)
            list_ = list(records_after_latest_true.values('id', 'cafe', 'items','table','active'))
            print("list__",records_after_latest_true,list_)
            for kot in list_:
                kot['active'] = f"{kot['active']}"
            kot_list.append(list_)
    initial_context = {"tables":tables, "tax":tax_,"kot_list":kot_list}
    print("go...",kot_list)
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

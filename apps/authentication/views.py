from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to auth/urls.py file for more pages.
"""


class AuthView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context
    
    
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:   
        if request.method == "POST":

            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # logging the user
                firstname = request.user.first_name
                lastname = request.user.last_name
                id = request.user.id
                roll = []  # request.user.groups.all()
                # for g in request.user.groups.all():
                #     roll.append(g.name)
                status = "Login"
                # history = UserHistory(
                #     first_name_h=firstname,
                #     last_name_h=lastname,
                #     roll_h=roll[0],
                #     login_h=login_time,
                #     status_h=status,
                #     id_h=id,
                # )
                # history.save()
                return redirect("dashboard")
            else:
                messages.info(request, "Username or Password is incorrect")

    context = {}
    return render(request, "auth_login_basic.html",context)

def logout_view(request):
    logout(request)
    # Redirect to a success page, or as desired.
    return redirect('/')

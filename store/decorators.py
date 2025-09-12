from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def is_delivery_man(user):
    return user.is_authenticated and user.groups.filter(name='DeliveryGroup').exists()

def delivery_man_required(function=None, redirect_field_name=None, login_url='account_login'):
    """
    Decorator for views that checks that the user is logged in and is a delivery man,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        is_delivery_man,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_required(function=None, redirect_field_name=None, login_url='account_login'):
    """
    Decorator for views that checks that the user is logged in and is a staff member,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core import serializers
from archive.models import Strain
from django.contrib.auth.models import User
from cart.models import Quote, Order, ConfirmedBasket, Purchase, Promotion, PromotionCode
from forms import CreateNewPromotionForm, GenerateNewCodesForm, EditOrderForm, LoginForm, NewUserForm
from django.http import HttpResponse
import json
from datetime import datetime
from django.shortcuts import redirect

from django.contrib.auth import logout





def logout_user(request):

    logout(request)

    return redirect("management:login")




def update_user_status(request, user_pk):

    try:

        user = User.objects.get(pk = user_pk)
    
    except User.DoesNotExist:

        data = {"status": "ERROR", "message": "User not found"}
    
    else:

        if user.is_active:

            user.is_active = False

        else:

            user.is_active = True
        
        user.save()
        
        data = {"status": "OK"}

    return HttpResponse(
        json.dumps(data),
        content_type = "application/json"
    )


def send_quote(request, quote_pk):

    try:

        quote = Quote.objects.get(pk = quote_pk)
    
    except Quote.DoesNotExist:

        pass
    
    else:

        newOrder = Order.objects.create(
            quote = quote
        )

        quote.status = "S"
        quote.save()

        messages.success(request, "The quote has been sent to %s successfully." % quote.customer_email)

        return HttpResponse(
            json.dumps({"status": "OK"}),
            content_type = "application/json"
        )
        


# view to get and return promotional codes for promotion with pk == promotion_pk
def get_promo_codes(request, promo_pk):

    # try to find promotion
    try:

        promo = Promotion.objects.get(pk = promo_pk)
    
    except Promotion.DoesNotExist:

        pass
    
    else:

        # generate list of dicts with data for each code
        codes = [
            {
                "pk": code.pk,
                "code": code.code,
                "number_of_uses": code.number_of_uses,
                "max_usages": code.max_usages,
                "active": code.active
            } for code in promo.promotioncode_set.all()
        ]
    
    # send data back to page
    return HttpResponse(
        json.dumps(codes),
        content_type = "application/json"
    )




# view to get order details
def get_order_details(request, order_pk):

    # check order exists
    try:
    
        order = Order.objects.get(pk = order_pk)
    
    except Order.DoesNotExist:
        
        # process case if order not existing
        messages.error(request, "Details for quote could not be located")
        order = None
    
    else:

        order_data = {
            "customer_name": order.quote.customer_name,
            "customer_email": order.quote.customer_email,
            "status": order.get_verbose_status_name(),
            "status_code": order.status,
            "payment_method": order.get_verbose_payment_method_name(),
            "payment_method_code": order.payment_method,
            "start_date": order.start_date.strftime('%d/%m/%Y'),
            "delivery_address": order.quote.delivery_address,
        }

        if order.cirms_number:
            order_data["cirms_number"] = order.cirms_number
        
        if order.finance_reference_number:
            order_data["finance_reference_number"] = order.finance_reference_number
        
        if order.payment_order:
            
            payment_order = order.payment_order

            if payment_order.pdf:
                order_data["payment_order_pdf"] = payment_order.get_pdf_filename()
            
            if payment_order.reference_number:
                order_data["payment_order_reference_number"] = payment_order.reference_number

        if order.shop_order:
            shop_order = order.shop_order
        
            if shop_order.order_number:
                order_data["shop_order_number"] = shop_order.order_number
            
            if shop_order.transaction_number:
                order_data["shop_transaction_number"] = shop_order.transaction_number

            
        if order.invoice_file:
            order_data["invoice_file"] = order.get_invoice_filename()

        if order.post_date:
            order_data["post_date"] = order.post_date.strftime('%d/%m/%Y')
        else:
            order_data["post_date"] = "N/A"

        if order.received_date:
            order_data["received_date"] = order.received_date.strftime('%d/%m/%Y')
        else:
            order_data["received_date"] = "N/A"

        
        

    return HttpResponse(
        json.dumps(order_data),
        content_type = "application/json"
    )

# view to get quote details
def get_quote_details(request, quote_pk):

    # check quote exists
    try:
    
        quote = Quote.objects.get(pk = quote_pk)
    
    except Quote.DoesNotExist:
        
        # process case if quote not existing
        messages.error(request, "Details for quote could not be located")
        quote = None
    
    else:

        # create dict representing quote
        quote_data = {
            "customer_name": quote.customer_name,
            "customer_email": quote.customer_email,
            "funding_type": quote.get_verbose_funding_type_name(),
            "billing_address": quote.billing_address,
            "delivery_address": quote.delivery_address,
            "customer_notes": quote.customer_note,
        }

        # if bbsrc code present, add to dict
        if quote.bbsrc_code:
            quote_data["bbsrc_code"] = quote.bbsrc_code
        else:
            quote_data["bbsrc_code"] = ""
        
        # check existence of basket and add to dict
        if quote.basket:
            quote_data["basket"] = quote.basket.as_dict()
        else:
            quote_data["basket"] = ""

    return HttpResponse(
        json.dumps(quote_data),
        content_type = "application/json"
    )




# management dashboard view
def management_dashboard(request):


    return render(
        request,
        "management/dashboard.html",
        {

        }
    )

# strain management view
def management_strains(request):

    return render(
        request,
        "management/strains.html",
        {
            "strains": Strain.objects.all()
        }
    )




# sales management view
def management_sales(request):

    createNewPromotionForm = CreateNewPromotionForm()
    generateCodesForm = GenerateNewCodesForm()
    editOrderForm = EditOrderForm()

    if request.method == "POST":

        if "editOrderForm" in request.POST:

            print "P:", request.POST
            print "F:", request.FILES

            editOrderForm = EditOrderForm(request.POST, request.FILES)

            if editOrderForm.is_valid():

                editOrderForm.process(request)
            
            else:

                editOrderForm.process_errors(request)


    if request.method == "POST":

        if "generateCodesForm" in request.POST:

            generateCodesForm = GenerateNewCodesForm(request.POST)

            if generateCodesForm.is_valid():

                generateCodesForm.process(request)
            
            else:

                generateCodesForm.process_errors(request)

        if "createNewPromotionForm" in request.POST:

            createNewPromotionForm = CreateNewPromotionForm(request.POST)

            if createNewPromotionForm.is_valid():

                createNewPromotionForm.process(request)
            
            else:

                createNewPromotionForm.process_errors(request)
    

    return render(
        request,
        "management/sales.html",
        {
            "editOrderForm": editOrderForm,
            "generateCodesForm": generateCodesForm,
            "createNewPromotionForm": createNewPromotionForm,
            "quotes": Quote.objects.all(),
            "promotions": Promotion.objects.all()
        }
    )



# user management view
def management_users(request):

    if request.method == "POST":

        new_user_form = NewUserForm(request.POST)

        if new_user_form.is_valid():

            new_user_form.process(request)
        
        else:

            new_user_form.process_errors(request)
    
    else:

        new_user_form = NewUserForm()

    return render(
        request,
        "management/users.html",
        {
            "users": User.objects.all(),
            "new_user_form": new_user_form
        }
    )


# view for management login
def login(request):

    if request.method == "POST":

        login_form = LoginForm(request.POST)

        if login_form.is_valid():

            if login_form.process(request):

                return redirect("management:dashboard")

        else:

            login_form.process_errors(request)

    else:

        login_form = LoginForm()

    return render(
        request,
        "management/login.html",
        {
            "login_form": login_form
        }
    )
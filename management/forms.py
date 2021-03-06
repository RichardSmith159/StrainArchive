from django import forms

from django.contrib import messages
from cart.models import Quote, Promotion, Order, PaymentOrder, ShopOrder
import json
from cart.promo_utils import generate_codes_for_promotion
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from cart.promo_utils import generate_code
from . models import ManagementUserProfile
from django.contrib.auth.models import User

def generate_password():

    return generate_code(10)


class NewUserForm(forms.Form):

    username = forms.CharField(max_length = 20, required = True)
    first_name = forms.CharField(max_length = 20, required = True)
    last_name = forms.CharField(max_length = 20, required = True)
    user_type = forms.CharField(max_length = 2, required = True)
    email = forms.EmailField(max_length = None, required = True)

    def process(self, request):

        cleaned_username = self.cleaned_data["username"]
        cleaned_first_name = self.cleaned_data["first_name"]
        cleaned_last_name = self.cleaned_data["last_name"]
        cleaned_user_type = self.cleaned_data["user_type"]
        cleaned_email = self.cleaned_data["email"]
        
        new_password = generate_password()

        new_user = User.objects.create_user(
            username = cleaned_username,
            password = new_password,
            email = cleaned_email
        )

        if cleaned_user_type == "ST":
            new_user.is_superuser = False
        elif cleaned_user_type == "SU":
            new_user.is_superuser = True
        else:
            new_user.is_superuser = True

        new_user.is_active = False

        new_user.save()

        new_management_profile = ManagementUserProfile.objects.create(
            first_name = cleaned_first_name,
            last_name = cleaned_last_name,
            user = new_user
        )

        messages.success(request, "New user '%s' was created successfully." % cleaned_username)
    

    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))



class LoginForm(forms.Form):

    username = forms.CharField(max_length = 20, required = True)
    password = forms.CharField(max_length = 10, required = True)

    def process(self, request):

        cleaned_username = self.cleaned_data["username"]
        cleaned_password = self.cleaned_data["password"]

        user = authenticate(username = cleaned_username, password = cleaned_password)

        if user:

            if user.is_active:

                print "HERE"

                return True

            else:

                messages.info(request, "Account not activated.")

        else:

            messages.error(request, "Username or password was incorrect.")
    
    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))




class EditOrderForm(forms.Form):

    selected_order_pk = forms.IntegerField(required = False)
    payment_order_reference_number = forms.CharField(required = False, max_length = 30)
    payment_order_pdf = forms.FileField(required = False)
    online_shop_order_number = forms.CharField(required = False, max_length = 30)
    online_shop_transaction_number = forms.CharField(required = False, max_length = 30)
    status = forms.CharField(required = False, max_length = 2)
    payment_method = forms.CharField(required = False, max_length = 2)
    post_date = forms.DateField(required = False)
    received_date = forms.DateField(required = False)
    cirms_number = forms.CharField(required = False, max_length = 30)
    finance_reference_number = forms.CharField(required = False, max_length = 30)
    invoice_file = forms.FileField(required = False)

    def process_online_shop_fields(self, request, order):

        cleaned_online_shop_order_number = self.cleaned_data["online_shop_order_number"]
        cleaned_online_shop_transaction_number = self.cleaned_data["online_shop_transaction_number"]

        if order.shop_order:

            shop_order = order.shop_order
        
        else:

            shop_order = ShopOrder.objects.create()
            order.shop_order = shop_order
            order.save()

        
        if cleaned_online_shop_order_number:

            shop_order.order_number = cleaned_online_shop_order_number
            
        if cleaned_online_shop_transaction_number:

            shop_order.transaction_number = cleaned_online_shop_transaction_number

        shop_order.save()



    def process_payment_order_fields(self, request, order):
        

        cleaned_payment_order_reference_number = self.cleaned_data["payment_order_reference_number"]
        cleaned_payment_order_pdf = self.cleaned_data["payment_order_pdf"]   

        if order.payment_order:

            payment_order = order.payment_order
        
        else:

            payment_order = PaymentOrder.objects.create()
            order.payment_order = payment_order
            order.save()

        
        if "paymentOrderFile" in request.FILES:

            payment_order.pdf = request.FILES["paymentOrderFile"]
            messages.success(request, "The payment order file was uploaded successfully.")
        
        if cleaned_payment_order_reference_number:

            payment_order.reference_number = cleaned_payment_order_reference_number

        payment_order.save()



    def process_order_fields(self, request, order):

        cleaned_status = self.cleaned_data["status"]
        cleaned_payment_method = self.cleaned_data["payment_method"]
        cleaned_post_date = self.cleaned_data["post_date"]
        cleaned_received_date = self.cleaned_data["received_date"]
        cleaned_cirms_number = self.cleaned_data["cirms_number"]
        cleaned_finance_reference_number = self.cleaned_data["finance_reference_number"]
        cleaned_invoice_file = self.cleaned_data["invoice_file"]

        if cleaned_finance_reference_number:
            order.finance_reference_number = cleaned_finance_reference_number
        
        if cleaned_cirms_number:
            order.cirms_number = cleaned_cirms_number
        
        if cleaned_status:
            order.status = cleaned_status
        
        if cleaned_payment_method:
            order.payment_method = cleaned_payment_method

        if cleaned_post_date:
            order.post_date = cleaned_post_date
        
        if cleaned_received_date:
            order.received_date = cleaned_received_date

        if "invoiceFile" in request.FILES:
            order.invoice_file = request.FILES["invoiceFile"]
            messages.success(request, "The invoice file was uploaded successfully.")
        
        messages.success(request, "The changes were made successfully.")
        order.save()


    def process(self, request):

        cleaned_selected_order_pk = self.cleaned_data["selected_order_pk"]

        try:

            order = Order.objects.get(pk = cleaned_selected_order_pk)

        except Order.DoesNotExist:

            messages.error(request, "The order could not be found in the database.")

        else:

            self.process_order_fields(request, order)
            self.process_payment_order_fields(request, order)
            self.process_online_shop_fields(request, order)
    
    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))




            


class GenerateNewCodesForm(forms.Form):

    number_of_codes = forms.IntegerField(required = True)
    max_number_of_uses = forms.IntegerField(required = True)
    initially_active = forms.BooleanField(required = False)
    promo_pk = forms.IntegerField(required = True)

    def process(self, request):

        cleaned_number_of_codes = self.cleaned_data["number_of_codes"]
        cleaned_max_number_of_uses = self.cleaned_data["max_number_of_uses"]
        cleaned_initially_active = self.cleaned_data["initially_active"]
        cleaned_promo_pk = self.cleaned_data["promo_pk"]

        try:

            promotion = Promotion.objects.get(pk = cleaned_promo_pk)
        
        except Promotion.DoesNotExist:

            messages.error(request, "Promotion with id %d could not be found." % cleaned_promo_pk)
        
        else:
            
            generate_codes_for_promotion(
                cleaned_promo_pk,
                cleaned_number_of_codes,
                cleaned_max_number_of_uses,
                cleaned_initially_active
            )

            messages.success(request, "The codes were generated successfully.")
    
    def process_errors(self, request):
        
        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))



class CreateNewPromotionForm(forms.Form):

    name = forms.CharField(max_length = 50, required = True)
    description = forms.CharField(max_length = 200, required = True)
    start_date = forms.DateField(required = True)
    expiry_date = forms.DateField(required = True)
    promo_type = forms.CharField(required = True, max_length = 3)
    percentage_amount = forms.FloatField(required = False)
    fixed_amount = forms.FloatField(required = False)

    def process(self, request):

        cleaned_name = self.cleaned_data["name"]
        cleaned_description = self.cleaned_data["description"]
        cleaned_start_date = self.cleaned_data["start_date"]
        cleaned_expiry_date = self.cleaned_data["expiry_date"]
        cleaned_promo_type = self.cleaned_data["promo_type"]
        cleaned_percentage_amount = self.cleaned_data["percentage_amount"]
        cleaned_fixed_amount = self.cleaned_data["fixed_amount"]

        if cleaned_start_date:

            new_promo = Promotion.objects.create(
                name = cleaned_name,
                description = cleaned_description,
                start_date = cleaned_start_date,
                expiry_date = cleaned_expiry_date,
                promotion_type = cleaned_promo_type
            )

            if new_promo.promotion_type == "FPR":

                params = {
                    "reduction_amount": cleaned_fixed_amount,
                    "percentage_reduction": "NULL",
                    "promo_pk": new_promo.pk
                }

            elif new_promo.promotion_type == "PR":
                
                params = {
                    "reduction_amount": "NULL",
                    "percentage_reduction": cleaned_percentage_amount,
                    "promo_pk": new_promo.pk
                }

            else:

                params = {
                    "reduction_amount": "NULL",
                    "percentage_reduction": "NULL",
                    "promo_pk": new_promo.pk
                }
            
            new_promo.promotion_parameters = json.dumps(params)
            new_promo.save()


            messages.success(
                request,
                "New promotion '%s' has been created successfully and will be active as of %s." % (cleaned_name, cleaned_start_date)
            )
        
        else:

            Promotion.objects.create(
                name = cleaned_name,
                description = cleaned_description,
                expiry_date = cleaned_expiry_date
            )

            messages.success(
                request,
                "New promotion '%s' has been created successfully and will be active as of today." % cleaned_name
            )
    

    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))

        


class QuoteForm(forms.Form):

    selected_quote_id = forms.IntegerField(required = True)
    cost = forms.FloatField(required = False)


    def process(self, request):

        cleaned_selected_quote_id = self.cleaned_data["selected_quote_id"]
        cleaned_cost = self.cleaned_data["cost"]

        try:

            selected_quote = Quote.objects.get(pk = cleaned_selected_quote_id)
        
        except Quote.DoesNotExist:

            messages.error(request, "Quote with id %d could not be found in the database." % cleaned_selected_quote_id)
        
        else:

            selected_quote.cost = cleaned_cost
            selected_quote.save()

            messages.success(request, "Changes to quote %d were made successfully." % cleaned_selected_quote_id)



    def process_errors(self, request):

        error_dict = json.loads(self.errors.as_json())
        for key in error_dict:
            for error in error_dict[key]:
                messages.error(request, "Error: %s - %s" % (key, error["message"]))
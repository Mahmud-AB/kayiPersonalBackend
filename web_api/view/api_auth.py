import json
import random
import re
from datetime import datetime, timedelta

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.core import mail
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import AccessToken
from oauth2_provider.views import TokenView
from oauthlib.oauth2.rfc6749.tokens import random_token_generator

from config import settings
from config.settings import EMAIL_HOST_USER
from web_api import serializable
from web_api.defs import common_defs, email_service
from web_api.models import Users, UsersForgotCode, PushNotification
from web_api.view import apiresponse


class CustomLoginView(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        try:
            users = Users.objects.filter(username=request.POST.get("username"))
            if len(users) > 0 and check_password(request.POST.get("password"), users[0].password):
                if not users[0].is_active:
                    return apiresponse.httpResponse(False, None, "Your account in not active")
                else:
                    auth = authenticate(username=request.POST['username'], password=request.POST['password'])
                    login(request, auth)
                    url, headers, body, status = self.create_token_response(request)
                    if status == 200:
                        body = json.loads(body)
                    return apiresponse.httpResponse(True, body, "Success")
            return apiresponse.httpResponse(False, None, "Email or password not match")
        except Exception as ex:
            print(str(ex))
            return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


class CustomTokenView(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        try:
            users = Users.objects.filter(username=request.POST.get("username"))
            if len(users) > 0 and check_password(request.POST.get("password"), users[0].password):
                if not users[0].is_active:
                    return apiresponse.httpResponse(False, None, "Your account in not active")
                else:
                    url, headers, body, status = self.create_token_response(request)
                    if status == 400:
                        return apiresponse.httpResponse(False, None, "Invalid parameter")
                    if status == 401:
                        return apiresponse.httpResponse(False, None, "Invalid client information")
                    elif status == 200:
                        body = json.loads(body)
                        access_token = body.get("access_token")
                        if access_token is not None:
                            adder = {}
                            if users[0].get_address_json() is not None:
                                adder['address'] = users[0].get_address_json().get('address', '')
                                adder['city'] = users[0].get_address_json().get('city', '')
                                adder['state'] = users[0].get_address_json().get('state', '')
                                adder['zip'] = users[0].get_address_json().get('zip', '')
                            else:
                                adder['address'] = ""
                                adder['city'] = ""
                                adder['state'] = ""
                                adder['zip'] = ""
                            body['member'] = {
                                'id': users[0].id,
                                'first_name': users[0].first_name,
                                'last_name': users[0].last_name,
                                'email': users[0].username,
                                'phone': users[0].phone,
                                'user_type': users[0].get_user_type(),
                                'address': adder,
                            }
                            return apiresponse.httpResponse(True, body, "Success")
            else:
                return apiresponse.httpResponse(False, None, "Email or password not match")
        except:
            return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def social_login(request):
    try:
        token = request.POST.get('token')
        current_user = {}
        if request.POST.get('social', '') == 'google':
            result = requests.get("https://www.googleapis.com/oauth2/v3/userinfo?access_token=" + token)
            if result.status_code == 200:
                text = json.loads(result.text)
                current_user['username'] = text['email']
                current_user['fullname'] = text['name']
                current_user['email'] = text['email']
                current_user['image'] = text['picture']
        elif request.POST.get('social', '') == 'facebook':
            result = requests.get("https://graph.facebook.com/me?fields=id,name,email&access_token=" + token)
            if result.status_code == 200:
                text = json.loads(result.text)
                current_user['username'] = text['email']
                current_user['fullname'] = text['name']
                current_user['email'] = text['email']
                current_user['image'] = 'https://graph.facebook.com/' + str(text['id']) + '/picture?type=large'
        if 'email' in current_user:
            user = None
            users = Users.objects.filter(email=current_user.get("email"))
            if len(users) > 0:
                user = users[0]
            else:
                user = Users()
                user.is_staff = False
                user.is_superuser = False
                user.is_active = True
                user.first_name = serializable.serializable_name(current_user['fullname'])[0]
                user.last_name = serializable.serializable_name(current_user['fullname'])[1]
                user.username = current_user['email']
                user.email = current_user['email']
                user.phone = ""
                user.password = make_password('sdsjmmfeuiwkjwe')
                user.image = current_user['image']
                user.save()

            if user is not None:
                expires = datetime.now() + timedelta(seconds=36000)
                access_token = random_token_generator(request)
                AccessToken.objects.create(user=user, scope='read write', application_id=1, token=access_token,
                                           expires=expires)
                return apiresponse.httpResponse(True, {
                    "token_type": "Bearer",
                    "refresh_token": None,
                    "expires_in": 36000,
                    "scope": "write read",
                    "access_token": access_token,
                    "member": {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'user_type': user.get_user_type(),
                    }
                }, "success")

            return apiresponse.httpResponse(False, None, "Something went wrong")
        return apiresponse.httpResponse(False, None, "Invalid Token")
    except Exception as ex:
        print(ex)
        return apiresponse.httpResponse(False, None, "Something went wrong")


class SellerReg(View):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        try:
            message = []
            is_valid_input = True
            user = Users()
            user.is_staff = True
            user.is_superuser = False
            user.is_active = False
            user.image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTmp7Zkhf_H_iJDUGaaRhchdSo0Qt6xUqQJ2HxC9kmAvpvmhxG6&usqp=CAU'
            user.first_name = request.POST.get("seller_shop_name")
            user.number = request.POST.get("seller_shop_number")
            user.username = request.POST.get("seller_email")
            user.email = request.POST.get("seller_email")
            user.phone = request.POST.get("seller_phone")
            user.address = request.POST.get("seller_shop_address")
            user.about = request.POST.get("seller_about")
            user.password = request.POST.get("seller_password1")
            password1 = request.POST.get("seller_password2")
            user.seller_tax = float(request.POST.get("seller_tax"))

            if len(user.first_name) < 1:
                is_valid_input = False
                message.append("Please enter your valid shop name")

            if len(user.number) < 3:
                is_valid_input = False
                message.append("Please enter your valid shop number")

            if len(user.phone) < 3:
                is_valid_input = False
                message.append("Please enter your valid phone number")

            if len(user.address) < 3:
                is_valid_input = False
                message.append("Please enter your valid shop address")

            if len(user.about) < 3:
                is_valid_input = False
                message.append("Please enter your valid shop descriptions")
            if user.seller_tax < .1:
                is_valid_input = False
                message.append("Please enter your valid tax amount")

            if user.password != password1:
                is_valid_input = False
                message.append("Password and confirm password not match")
            elif len(user.password) < 5:
                is_valid_input = False
                message.append("Password at least 6 char")

            if user.is_valid_email():
                users = Users.objects.filter(username=user.email)
                if len(users) > 0:
                    is_valid_input = False
                    message.append("Email already use")
                else:
                    user.email = user.email.lower()
                    user.username = user.email.lower()
            else:
                is_valid_input = False
                message.append("Invalid email")

            if is_valid_input:
                user.password = make_password(user.password)
                user.save()
                return apiresponse.httpResponse(True, None, "Success")
            else:
                return apiresponse.httpResponse(False, None, message)
        except Exception as ex:
            print(str(ex))
            return apiresponse.httpResponse(False, None, ["Something wend wrong! Try again"])


class BuyerReg(View):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        try:
            message = ""
            is_valid_input = True
            user = Users()
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.username = request.POST.get("email")
            user.email = request.POST.get("email")
            user.phone = request.POST.get("phone")
            user.image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTmp7Zkhf_H_iJDUGaaRhchdSo0Qt6xUqQJ2HxC9kmAvpvmhxG6&usqp=CAU'
            user.address = json.dumps({"address": request.POST.get("address", ""), "city": request.POST.get("city", ""),
                                       "state": request.POST.get("state", ""), "zip": request.POST.get("zip", "")})
            user.password = request.POST.get("password")
            password1 = request.POST.get("password_again")

            if not re.search("^\d{3}\d{3}\d{4}$", user.phone):
                is_valid_input = False
                message += "Invalid phone number,"

            if len(user.password) < 5:
                is_valid_input = False
                message += "Password at least 6 char,"

            if user.password != password1:
                is_valid_input = False
                message += "Password and confirm password not match,"

            if user.is_valid_email():
                users = Users.objects.filter(username=user.email)
                if len(users) > 0:
                    is_valid_input = False
                    message += "Email already use,"
            else:
                is_valid_input = False
                message += "Invalid email,"

            if is_valid_input:
                user.password = make_password(user.password)
                user.save()
                return apiresponse.httpResponse(True, None, "Success")
            else:
                return apiresponse.httpResponse(False, None, message)
        except:
            return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


class ForgotView(View):
    def post(self, request, *args, **kwargs):
        try:
            u_id = request.POST.get("user", 0)
            u_code = request.POST.get("code", 0)
            u_password1 = request.POST.get("password", "")
            u_password2 = request.POST.get("password_again", "")
            ufc = UsersForgotCode.objects.filter(user_id=u_id, code=u_code)
            if len(ufc) > 0:
                if len(u_password1) < 1:
                    return apiresponse.httpResponse(True, ufc[0].id, "Success")
                else:
                    if len(u_password1) < 6:
                        return apiresponse.httpResponse(False, None, "Invalid password")
                    elif u_password1 != u_password2:
                        return apiresponse.httpResponse(False, None, "Password not match")
                    else:
                        user_info = Users.objects.get(pk=u_id)
                        user_info.password = make_password(u_password1)
                        user_info.save()
                        ufc[0].delete()
                        return apiresponse.httpResponse(True, None, "Success")
            else:
                return apiresponse.httpResponse(False, None, "Invalid code")
        except Exception as ex:
            print(str(ex))
            return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")

    def get(self, request, *args, **kwargs):
        try:
            users = Users.objects.filter(email=request.GET.get("email"))
            if len(users) > 0:
                code_value = random.randint(101300, 999799)
                ufc = UsersForgotCode.objects.create(user_id=users[0].id, code=code_value)
                data = {
                    'id': users[0].id,
                    'first_name': users[0].first_name,
                    'last_name': users[0].last_name,
                    'email': users[0].username,
                    'user_type': users[0].get_user_type(),
                }
                email_service.email_password_change(request=request, user=users[0], code=ufc.code)
                return apiresponse.httpResponse(True, data, "Success")
            else:
                return apiresponse.httpResponse(False, None, "Your email not found")
        except Exception as ex:
            print(str(ex))
            return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


def push_notification(request):
    try:
        pn = PushNotification()
        if request.user.is_anonymous is False:
            pn.user_id = request.user.id
        pn.device_id = request.POST.get('device_id')
        pn.token = request.POST.get('token', '')
        pn.device_type = request.POST.get('device_type')
        if len(pn.token) > 5:
            tpm = PushNotification.objects.filter(device_id=pn.device_id)
            if len(tpm) > 0:
                tpm[0].token = pn.token
                tpm[0].user_id = pn.user_id
                tpm[0].save()
            else:
                pn.save()
        return apiresponse.httpResponse(True, None, "")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something went wrong")


def active_user(request):
    try:
        if request.user.is_superuser:
            userId = request.POST.get('id', '0')
            u = Users.objects.get(pk=int(userId))
            u.is_active = True
            u.save()
            common_defs.send_active_mail(u)
            return apiresponse.httpResponse(True, None, "Successfully active")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "User not found")


def deactivate_user(request):
    try:
        if request.user.is_superuser:
            userId = request.POST.get('id', '0')
            u = Users.objects.get(pk=int(userId))
            u.is_active = False
            u.save()
            common_defs.send_active_mail(u)
            return apiresponse.httpResponse(True, None, "Successfully deactivate")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "User not found")


def remove_user(request):
    try:
        if request.user.is_superuser:
            userId = request.POST.get('id', '0')
            u = Users.objects.get(pk=int(userId))
            u.delete()
            common_defs.send_account_delete_mail(u)
            return apiresponse.httpResponse(True, None, "Successfully deleted")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "User not found")


def user_info(request):
    try:
        if not request.user.is_anonymous:
            adder = {}
            if request.user.get_address_json() is not None:
                adder['address'] = request.user.get_address_json().get('address', '')
                adder['city'] = request.user.get_address_json().get('city', '')
                adder['state'] = request.user.get_address_json().get('state', '')
                adder['zip'] = request.user.get_address_json().get('zip', '')
            else:
                adder['address'] = ""
                adder['city'] = ""
                adder['state'] = ""
                adder['zip'] = ""
            body = {
                'id': request.user.id,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.username,
                'phone': request.user.phone,
                'user_type': request.user.get_user_type(),
                'address': adder,
            }
            return apiresponse.httpResponse(True, body, "Success")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "User not found")


def update_user_account(request):
    try:
        if not request.user.is_anonymous:
            user = Users.objects.get(pk=request.user.id)
            if request.POST.get('first_name'):
                user.first_name = request.POST.get('first_name')
            if request.POST.get('last_name'):
                user.last_name = request.POST.get('last_name')
            if request.POST.get('phone'):
                user.phone = request.POST.get('phone')
            if request.POST.get('address'):
                is_valid_address = True
                address = {"address": request.POST.get("address", "")}

                if request.POST.get('city'):
                    address["city"] = request.POST.get('city')
                else:
                    is_valid_address = False

                if request.POST.get('state'):
                    address["state"] = request.POST.get('state')
                else:
                    is_valid_address = False
                if request.POST.get('zip'):
                    address["zip"] = request.POST.get('zip')
                else:
                    is_valid_address = False

                if is_valid_address:
                    user.address = json.dumps(address)
                else:
                    return apiresponse.httpResponse(False, None, "Invalid address")
            user.save()
            return user_info(request=request)
        else:
            return apiresponse.httpResponse(False, None, "Please sign in your account")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something went wrong")


def update_user_account_password(request):
    try:
        if not request.user.is_anonymous:
            message = "Success"
            is_okay = False
            user = Users.objects.get(pk=request.user.id)
            if check_password(request.POST.get('current_password', ''), user.password):
                if request.POST.get('new_password', '') == request.POST.get('new_password_again', ''):
                    if len(request.POST.get('new_password', '')) < 5:
                        message = "Password at least 6 char"
                    else:
                        user.password = make_password(request.POST.get('new_password', ''))
                        user.save()
                        is_okay = True
                        email_service.email_password_change(request, user)
                else:
                    message = "Password and confirm password not match"
            else:
                message = "Current password not match"
        else:
            message = "Please sign in your account"
        return apiresponse.httpResponse(is_okay, None, message)
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something went wrong")


def update_user_account_email(request):
    try:
        if not request.user.is_anonymous:
            user = Users.objects.get(pk=request.user.id)
            user.email = request.POST.get('email', '').lower()
            user.username = request.POST.get('email', '').lower()

            if user.email == request.user.email:
                return apiresponse.httpResponse(True, None, "Updated")

            if user.is_valid_email():
                users = Users.objects.filter(username=user.email)
                if len(users) > 0:
                    return apiresponse.httpResponse(False, None, "Email already used")
                else:
                    user.save()
                    email_service.email_change_email(request, user, request.user.email)
                    return apiresponse.httpResponse(True, None, "Updated")
            else:
                return apiresponse.httpResponse(False, None, "Invalid email")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in your account")

    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something went wrong")


def support_message_any_user(request):
    try:
        payload = {
            'full_text': request.POST.get("message"),
            'user_name': str(request.POST.get("first_name", "")) + " " + str(request.POST.get("last_name")),
            'user_email': request.POST.get("email", ""),
            'user_phone': request.POST.get("mobile_no", ""),
            'request': request
        }

        html_message = render_to_string('email_template_support.html', payload)
        mail.send_mail((str(request.POST.get("subject", "")) + ""), strip_tags(html_message), ('TheKayi <' + EMAIL_HOST_USER + '>'),
                       [settings.EMAIL_HOST_USER_SUPPORT], html_message=html_message)
        return apiresponse.httpResponse(True, None, "Success")
    except Exception as ex:
        print(str(ex))
    return apiresponse.httpResponse(False, None, "Something went wrong")

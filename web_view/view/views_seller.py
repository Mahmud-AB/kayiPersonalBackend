import datetime
import json
from datetime import timedelta

import pytz
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect

from web_api.defs import common_defs
from web_api.defs.common_defs import is_valid_email, image_save_from_data, get_sequence_category, cites_zipcode, shop_current_city, get_current_user_id
from web_api.models import Users
from web_api.models_product import Products, ShopZipcodes, ShopPickUpStore
from web_api.models_product_order import OrderStatus, ProductsOrder
from web_view.view import httpresponse, views_admin


def reg(request):
    return httpresponse.template(request, 'seller/register.html', {})


def index(request):
    return views_admin.admin_seller_index(request, "seller")


def pickup(request):
    if request.method == "POST":
        address = request.POST.get('address', '') + " " + request.POST.get('city', '') + " " + request.POST.get('state', '') + " " + request.POST.get('zipcode', '')
        address = str(address).lstrip(" ")
        ShopPickUpStore.objects.create(
            shop=request.user,
            address=address,
            is_active=False
        )
    if request.GET.get('id', '') is not "":
        pick_up = ShopPickUpStore.objects.filter(id=request.GET.get('id')).first()
        if pick_up is not None:
            pick_up.delete()
    pickup_location = ShopPickUpStore.objects.filter(shop=request.user)
    return httpresponse.response_seller(request, 'ss/pickup', {"pickup_location": pickup_location, "permission": True})


def zipcode_area_shop_id(request):
    request.permission = False
    content = zipcode_area(request)
    if type(content) is str:
        return redirect(request.path)
    return httpresponse.response_seller(request, 'seller/product_zipcode', content)


def zipcode_area(request):
    if request.permission:
        if request.method == "POST":
            pzipcode = request.POST.get("pzipcode")
            ShopZipcodes.objects.filter(shop=request.user, zipcode__zipcode__in=[int(x) for x in pzipcode.split(",")]).delete()
            zips = [int(x) for x in pzipcode.split(",")]
            for z in zips:
                ShopZipcodes.objects.create(shop=request.user, zipcode_id=z)
        elif str(request.method).lower() == 'get' and request.GET.get("id") is not None:
            szp = ShopZipcodes.objects.get(pk=request.GET.get("id"))
            ShopZipcodes.objects.filter(shop=request.user, zipcode__city=szp.zipcode.city, zipcode__state=szp.zipcode.state).delete()
            return request.path
    zip_codes = shop_current_city(request.user)
    return {"zip_codes": zip_codes, "shop_zipcode": ShopZipcodes.objects.filter(shop=request.user).order_by("-id")}


def profile(request):
    message = []
    if str(request.method).upper() == "POST":
        user = Users.objects.get(pk=request.user.id)
        address = {}
        if len(request.POST.get('input--fl', '')) > 0:
            user.first_name = request.POST.get('input--fl')
        else:
            message.append("Invalid Shop Name")

        if len(request.POST.get('input--phone', '')) > 8:
            user.phone = request.POST.get('input--phone')
        else:
            message.append("Invalid Phone number")

        if len(request.POST.get('input--about', '')) > 8:
            user.about = request.POST.get('input--about')

        if len(request.POST.get('input--add', '')) > 3:
            address['address'] = request.POST.get('input--add', '')
        else:
            message.append("Invalid Address1")

        if user.seller_tax <= 0 and float(request.POST.get('input--tax', '0')) > 0:
            user.seller_tax = float(request.POST.get('input--tax', ''))

        if len(request.POST.get('input--st', '')) > 1:
            address['state'] = request.POST.get('input--st', '')
        else:
            message.append("Invalid State")

        if len(request.POST.get('input--ct', '')) > 1:
            address['city'] = request.POST.get('input--ct', '')
        else:
            message.append("Invalid City Name")

        if len(request.POST.get('input--zip', '')) > 1:
            address['zip'] = request.POST.get('input--zip', '')
        else:
            message.append("Invalid Zipcode")

        if len(request.POST.get('input--p1', '')) > 0 and len(request.POST.get('input--p1', '')) > 5:
            if len(request.POST.get('input--p1', '')) == len(request.POST.get('input--p2', '')):
                user.password = make_password(request.POST.get('input--p1', ''))
            else:
                message.append("Password not match")
        elif len(request.POST.get('input--p1', '')) > 0:
            message.append("Invalid Password")

        if request.POST.get('input--email', '') != user.email:
            if is_valid_email(request.POST.get('input--email', '')):
                users = Users.objects.filter(username=request.POST.get('input--email', ''))
                if len(users) > 0:
                    message.append("Email already use")
                else:
                    user.email = str(request.POST.get('input--email', '')).lower()
                    user.username = str(request.POST.get('input--email', '')).lower()
            else:
                message.append("Invalid email")

        if len(request.POST.get('input--image', '')) > 10:
            img = image_save_from_data(request.POST.get('input--image'), "user", (str(user.id) + ".png"))
            if img:
                user.image = img

        if len(message) == 0:
            user.address = json.dumps(address)
            user.save()
    return httpresponse.response_seller(request, 'ss/profile', {'uu': Users.objects.get(pk=request.user.id), "message": message})


def product_list(request):
    page = request.GET.get('page', 1)
    product_list = Products.objects.filter(shop=request.user.id, name__icontains=request.GET.get("q", "")).order_by('-id')
    paginator = Paginator(product_list, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return httpresponse.response_seller(request, 'ss/product_list', {'products': products})


def product_curd(request, product_id=0):
    try:
        p = None
        if request.method == 'GET':
            cz = cites_zipcode()
            if product_id != 0:
                p = Products.objects.get(pk=product_id)
                if p.shop.id != request.user.id:
                    return httpresponse.response_seller(request, '404', {})
            return httpresponse.response_seller(request, 'ss/product_add', {'product': p, 'category': get_sequence_category(), "weight_values": common_defs.get_sequence_weight()})
        elif request.method == 'POST':
            if request.POST.get('_method', 'DELETE') == 'DELETE':
                Products.objects.get(pk=product_id).delete()
                return redirect('/seller/product/add/0')
        return httpresponse.response_seller(request, '404', {})
    except:
        return httpresponse.response_seller(request, '500', {})


def report_filter(request):
    date_format = '%Y-%m-%d %H:%M'
    from django.utils import timezone
    request.filter = str(request.GET.get("i", "1"))
    request.shop = get_current_user_id(request.user)
    request.date_start = timezone.now() + timedelta(-7)
    request.date_end = timezone.now()

    if request.GET.get("start") is not None:
        request.date_start = pytz.utc.localize(datetime.datetime.strptime(request.GET.get("start"), date_format))
    if request.GET.get("end") is not None:
        request.date_end = pytz.utc.localize(datetime.datetime.strptime(request.GET.get("end"), date_format))

    total_amount = 0
    all = ProductsOrder.objects.filter(status=OrderStatus.COMPLETE.name, shop=request.shop, created__gte=request.date_start, created__lte=request.date_end)
    for o in all:
        total_amount = total_amount + o.total_amount
    return httpresponse.response_seller(request, 'ss/report', {
        'total_amount': round(total_amount, 2),
        'orders': all,
        'permission': False,
        'show_shop': True,
        'shop_user': request.user
    })

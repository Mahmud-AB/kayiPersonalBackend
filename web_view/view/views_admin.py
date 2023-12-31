import json

from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection, transaction
from django.db.models import Sum
from django.shortcuts import redirect

from web_api.defs import common_defs
from web_api.defs.common_defs import get_sequence_category, get_current_user_id, image_save_from_data, is_valid_email, cites_zipcode
from web_api.models import Users
from web_api.models_product import Products, ProductsAdvertising, ProductsWeight, ZipCodes, ShopZipcodes, ShopPickUpStore
from web_api.models_product_order import ProductsOrder, OrderStatus, ProductOrderDeliveryFee
from web_view.view import httpresponse


def admin_seller_index(request, type_is):
    cursor = connection.cursor()
    item1 = int(request.GET.get('', '0'))
    graph1 = []
    graph1_diff = []
    total_order = 0
    total_order_complete = 0
    total_visitor = 0
    total_visitor_products = 0
    total_product_count = 0
    try:
        total_order = len(ProductsOrder.objects.filter(shop=get_current_user_id(request.user)))
        total_order_complete = len(ProductsOrder.objects.filter(status=OrderStatus.COMPLETE.name, shop=get_current_user_id(request.user)))
    except Exception as ex:
        print(str(ex))

    try:
        sql = "select count(*) as 'complete_order',concat(YEAR(created), '-', MONTH(created), '-', Day(created)) as 'date' from product_order where shop=" + str(
            get_current_user_id(request.user)) + " and created> now() - INTERVAL 30 day  group by YEAR(created), MONTH(created), Day(created) order by created;"
        cursor.execute(sql)
        data1 = cursor.fetchall()
        for dd in data1:
            graph1.append([dd[0], dd[1]])

        if request.GET.get('start') == None:
            graph1_diff = graph1[:7]
        else:
            sql2 = "select count(*) as 'complete_order',concat(YEAR(created), '-', MONTH(created), '-', Day(created)) as 'date' from product_order where shop=" + str(
                get_current_user_id(request.user)) + " and (created BETWEEN  '" + request.GET.get('start') + "' and '" + request.GET.get('end') + "')  group by YEAR(created), MONTH(created), Day(created) order by created;"
            cursor.execute(sql2)
            data12 = cursor.fetchall()
            for dd in data12:
                graph1_diff.append([dd[0], dd[1]])

    except Exception as ex:
        print(str(ex))

    try:
        cursor.execute('SELECT sum(counter_visit) FROM `product_products` WHERE `shop_id` =' + str(common_defs.get_current_user_id(request.user)))
        total_visitor = int(cursor.fetchone()[0])

        cursor.execute('SELECT count(*) FROM `product_products` WHERE counter_visit>0 and `shop_id` =' + str(common_defs.get_current_user_id(request.user)))
        total_visitor_products = int(cursor.fetchone()[0])

        cursor.execute('SELECT count(*) FROM `product_products` WHERE `shop_id` =' + str(common_defs.get_current_user_id(request.user)))
        total_product_count = int(cursor.fetchone()[0])
    except Exception as ex:
        print(str(ex))

    context = {
        'g_to': total_order,
        'g_toc': total_order_complete,
        'g_graph1': json.dumps(graph1),
        'graph1_diff': json.dumps(graph1_diff),
        'total_visitor': total_visitor,
        'total_visitor_products': total_visitor_products,
        'total_product_count': total_product_count,
        'this_g_to': 0,
        'this_g_toc': 0,
    }
    if type_is == "admin":
        return httpresponse.response_admin(request, 'service/index', context)
    return httpresponse.response_seller(request, 'service/index', context)


def index(request):
    return admin_seller_index(request, "admin")


def users(request):
    page = request.GET.get('page', 1)
    user_data = Users.objects.filter(is_staff=False, is_superuser=False).order_by('-id')
    paginator = Paginator(user_data, 12)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return httpresponse.response_admin(request, 'service/users', {'users': users})


def active(request):
    if request.GET.get('email', '') != "":
        users = Users.objects.filter(is_staff=True, email=request.GET.get('email')).order_by("-id")
    else:
        users = Users.objects.filter(is_staff=True).order_by("-id")
    return httpresponse.response_admin(request, 'service/active', {'users': users})


def pickup(request):
    if request.GET.get('approved', '') is not "":
        pick_up = ShopPickUpStore.objects.filter(id=request.GET.get('approved')).first()
        if pick_up is not None:
            pick_up.is_active = True
            pick_up.save()
    if request.GET.get('deny', '') is not "":
        pick_up = ShopPickUpStore.objects.filter(id=request.GET.get('deny')).first()
        if pick_up is not None:
            pick_up.is_active = False
            pick_up.save()
    if request.GET.get('id', '') is not "":
        pick_up = ShopPickUpStore.objects.filter(id=request.GET.get('id')).first()
        if pick_up is not None:
            pick_up.delete()
    pickup_location = ShopPickUpStore.objects.all().order_by("is_active")
    return httpresponse.response_admin(request, 'ss/pickup', {"pickup_location": pickup_location, "permission": False})


def zipcode(request):
    try:
        with transaction.atomic():
            post_id = request.GET.get('id')
            post_city = request.POST.get('city')
            post_state = request.POST.get('state')
            post_zip_list = []
            if len(str(request.POST.get('zip', ''))) > 0:
                post_zip_list = list(map(int, str(request.POST.get('zip', '')).split(",")))

            if str(request.method).lower() == 'post':
                """Save new zipcodes"""
                for zc in post_zip_list:
                    if ZipCodes.objects.filter(zipcode=zc).first() is None:
                        zip_tax = ZipCodes.objects.filter(city=post_city, state=post_state).order_by("-tax").first()
                        if zip_tax is not None:
                            zip_tax = zip_tax.tax
                        else:
                            zip_tax = 0.0
                        ZipCodes.objects.create(id=zc, tax=zip_tax, zipcode=zc, city=post_city, state=post_state)

                """Find all seller user list"""
                for shop in ShopZipcodes.objects.all().order_by().values_list('shop').distinct():
                    """Find user use current city is or not"""
                    old_szc = ShopZipcodes.objects.filter(shop=shop[0], zipcode__city=post_city, zipcode__state=post_state).first()
                    "If current city use the seller then add new zipcode in her/his cit list"
                    if old_szc is not None:
                        for zc in post_zip_list:
                            ShopZipcodes.objects.create(shop_id=shop[0], zipcode_id=zc)
            elif str(request.method).lower() == 'get' and post_id is not None:
                ShopZipcodes.objects.filter(zipcode=int(post_id)).delete()
                ZipCodes.objects.filter(zipcode=int(post_id)).delete()
    except Exception as ex:
        print(str(ex))
    return httpresponse.response_admin(request, 'service/zipcode', {'zips': ZipCodes.objects.all().order_by("state")})


def zipcode_area(request):
    if request.method == "POST":
        pzipcode = request.POST.get("pzipcode")
        if 0 < float(request.POST.get("ptax")) < 100:
            for z in ZipCodes.objects.filter(zipcode__in=[int(x) for x in pzipcode.split(",")]):
                z.tax = float(request.POST.get("ptax"))
                z.save()
    return httpresponse.response_admin(request, 'service/product_zipcode', {"city_codes": cites_zipcode(), "all_zipcode": ZipCodes.objects.all()})


def zipcode_area_shop_id(request, shop_id):
    try:
        request.user = Users.objects.get(pk=shop_id)
        request.permission = True
        from web_view.view import views_seller
        content = views_seller.zipcode_area(request)
        if type(content) is str:
            return redirect(request.path)
        return httpresponse.response_admin(request, 'seller/product_zipcode', content)
    except Exception as ex:
        print(str(ex))
        return httpresponse.response_admin(request, '404', {})


def product_category(request):
    return httpresponse.response_admin(request, 'service/category', {'all_category': common_defs.get_sequence_category(), 'zip_codes': cites_zipcode()})


def product_weight(request):
    try:
        if request.GET.get('_method', '') == 'DELETE':
            ProductsWeight.objects.get(pk=int(request.GET.get('id', '0'))).delete()
        elif request.GET.get('_method', '') == 'POST':
            if len(request.GET.get('value', '')) > 0:
                if len(ProductsWeight.objects.filter(name=request.GET.get('value', ''), parent=request.GET.get('parent'))) == 0:
                    ProductsWeight.objects.create(name=request.GET.get('value', ''), parent=request.GET.get('parent'))
        elif request.GET.get('_method', '') == 'PATCH':
            if len(request.GET.get('value', '')) > 0:
                pw = ProductsWeight.objects.get(pk=int(request.GET.get('id', '0')))
                pw.name = request.GET.get('value', '')
                pw.save()
    except:
        print(123)
    return httpresponse.response_admin(request, 'service/weight', {'all_weight': common_defs.get_sequence_weight()})


def product_advertising(request):
    pa_list = ProductsAdvertising.objects.all().order_by('-updated')
    return httpresponse.response_admin(request, 'service/advertising', {'pa_list': pa_list})


def product_list(request, shop=0):
    page = request.GET.get('page', 1)
    if shop > 0:
        product_list = Products.objects.filter(shop_id=shop).order_by('-id')
    else:
        product_list = Products.objects.filter(name__icontains=request.GET.get("q", "")).order_by('-id')
    paginator = Paginator(product_list, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return httpresponse.response_admin(request, 'ss/product_list', {'products': products})


def seller_info(request):
    try:
        id = int(request.GET.get('id', '0'))
        if id > 0:
            user = Users.objects.filter(id=id, is_staff=True)[:2]
        else:
            user = Users.objects.filter(email=request.GET.get('email', ''), is_staff=True)[:2]
        if request.GET.get("seller_tax") is not None:
            uu = Users.objects.get(pk=user[0].id)
            uu.seller_tax = float(request.GET.get("seller_tax"))
            uu.save()
            user = Users.objects.filter(id=uu.id, is_staff=True)[:2]
        if request.GET.get("commission") is not None:
            uu = Users.objects.get(pk=user[0].id)
            uu.commission = float(request.GET.get("commission"))
            uu.save()
    except Exception as ex:
        print(str(ex))
        return httpresponse.response_admin(request, '404', {})

    amount = 0.0
    withdraw = 0.0
    order_list = []
    if len(user) > 0:
        user = [user[0]]
        amount = (ProductsOrder.objects.filter(shop=get_current_user_id(user[0])).aggregate(total_amount=Sum('amount'))).get('total_amount', 0.0)
        order_list = (ProductsOrder.objects.filter(shop=user[0].id))
    else:
        user = []

    if amount is None:
        amount = 0.0
    return httpresponse.response_admin(request, 'service/seller_info', {'users': user, 'amount': amount, 'withdraw': withdraw, 'order_list': order_list})


def profile(request):
    message = []
    if str(request.method).upper() == "POST":
        user = Users.objects.get(pk=request.user.id)
        address = {}
        user.last_name = request.POST.get('input--ll')

        if len(request.POST.get('input--fl', '')) > 0:
            user.first_name = request.POST.get('input--fl')
        else:
            message.append("Invalid First Name")
        if len(request.POST.get('input--phone', '')) > 8:
            user.phone = request.POST.get('input--phone')
        else:
            message.append("Invalid Phone number")

        if len(request.POST.get('input--add', '')) > 3:
            address['address'] = request.POST.get('input--add', '')
        else:
            message.append("Invalid Address1")

        if len(request.POST.get('input--st', '')) > 1:
            address['state'] = request.POST.get('input--st', '')
        else:
            message.append("Invalid State")

        if len(request.POST.get('input--ct', '')) > 1:
            address['city'] = request.POST.get('input--ct', '')
        else:
            message.append("Invalid City Name")

        if len(request.POST.get('input--zip', '')) == 5:
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
    return httpresponse.response_admin(request, 'ss/profile', {'uu': Users.objects.get(pk=request.user.id), "message": message})


def product_curd(request, product_id=0):
    try:
        p = None
        if request.method == 'GET':
            cz = cites_zipcode()
            if product_id != 0:
                p = Products.objects.get(pk=product_id)
            return httpresponse.response_admin(request, 'ss/product_add', {'product': p, 'category': get_sequence_category(), "weight_values": common_defs.get_sequence_weight()})
        elif request.method == 'POST':
            if request.POST.get('_method', 'DELETE') == 'DELETE':
                Products.objects.get(pk=product_id).delete()
                return redirect('/service/product/add/0')
        return httpresponse.response_admin(request, '404', {})
    except:
        return httpresponse.response_admin(request, '500', {})


def fees(request):
    try:
        if request.GET.get("fee_type") is not None:
            fee = ProductOrderDeliveryFee.objects.get(pk=request.GET.get("id"))
            fee.amount_type = request.GET.get("fee_type")
            fee.charge = float(request.GET.get("charge"))
            fee.amount_max = float(request.GET.get("max"))
            fee.amount_min = float(request.GET.get("min"))
            if fee.amount_max > fee.amount_min:
                fee.save()
            return redirect('/service/fees')
        return httpresponse.response_admin(request, 'service/chrage', {'fees': ProductOrderDeliveryFee.objects.all()})
    except:
        return httpresponse.response_admin(request, '500', {})


def report_filter(request):
    import pytz
    import datetime
    from datetime import timedelta
    from django.utils import timezone
    date_format = '%Y-%m-%d %H:%M'

    if request.GET.get("shop", '') == '':
        request.shop = 0
    else:
        request.shop = int(request.GET.get("shop", '0'))
    request.filter = str(request.GET.get("i", "1"))
    request.shop_user = Users.objects.filter(id=request.shop).first()
    request.date_start = timezone.now() + timedelta(-7)
    request.date_end = timezone.now()

    if request.GET.get("start") is not None:
        request.date_start = pytz.utc.localize(datetime.datetime.strptime(request.GET.get("start"), date_format))
    if request.GET.get("end") is not None:
        request.date_end = pytz.utc.localize(datetime.datetime.strptime(request.GET.get("end"), date_format))

    total_amount = 0
    show_shop = False
    if request.shop == 0:
        all = ProductsOrder.objects.filter(status=OrderStatus.COMPLETE.name, created__gte=request.date_start, created__lte=request.date_end)
    else:
        show_shop = True
        all = ProductsOrder.objects.filter(status=OrderStatus.COMPLETE.name, shop=request.shop, created__gte=request.date_start, created__lte=request.date_end)

    for o in all:
        total_amount = total_amount + o.total_amount
    return httpresponse.response_admin(request, 'ss/report', {
        'total_amount': round(total_amount, 2),
        'orders': all,
        'permission': True,
        'show_shop': show_shop,
        "all_shop": Users.objects.filter(is_active=True, is_staff=True, is_superuser=False),
        'shop_user': request.shop_user
    })

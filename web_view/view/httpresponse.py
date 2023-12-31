from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from web_api.defs.common_defs import get_current_user_id
from web_api.forms import CouponForm
from web_api.models import Users
from web_api.models_product_order import ProductsOrder, ProductsOrderItems, ProductCoupon, CouponType


def response_admin(request, path, context=None):
    if context is None:
        context = {}
    context['template'] = path + ".html"
    template = loader.get_template("service/include.html")
    return HttpResponse(template.render(context, request))


def response_seller(request, path, context=None):
    if context is None:
        context = {}
    context['template'] = path + ".html"
    template = loader.get_template("seller/include.html")
    return HttpResponse(template.render(context, request))


def template(request, path, context):
    template = loader.get_template(path)
    return HttpResponse(template.render(context, request))


def handler404(request, *args, **argv):
    response = template(request, "404.html", {})
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = template(request, "505.html", {})
    response.status_code = 500
    return response


def pki_file(request, pki_str):
    content = "3977622A0DC7CB8019A6FED78F1239EE6C3FE9AE1B3D8A807B3F0E152D30B4FC\ncomodoca.com\nf49fb4c8e9ddfe4"
    response = HttpResponse(content, content_type='text/plain')
    return response


@login_required(login_url="/login")
def index(request):
    if request.user.is_superuser:
        return redirect("/service")
    elif request.user.is_staff:
        return redirect("/seller")
    return template(request, "503.html", {})


def login(request):
    return template(request, "login.html", {})


def forgot_password(request):
    return template(request, "login_forgot.html", {})


def logout(request):
    response = redirect('/login')
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response


def coupon(request):
    message = None
    try:
        if str(request.method).lower() == 'post':
            form = CouponForm(request.POST)
            if form.is_valid:
                coupon_obj = form.save(commit=False)
                coupon_obj.code = str(coupon_obj.code).upper()
                if request.user.is_superuser:
                    coupon_obj.user_id = 0
                    if request.POST.get('any_order', '') == 'on':
                        coupon_obj.user_id = - 1
                else:
                    coupon_obj.user_id = request.user.id
                if request.POST.get('coupon_type', '') == 'DOLLAR':
                    coupon_obj.coupon_type = CouponType.DOLLAR.name
                elif request.POST.get('coupon_type', '') == 'PERCENTAGE':
                    coupon_obj.coupon_type = CouponType.PERCENTAGE.name

                if len(ProductCoupon.objects.filter(code=coupon_obj.code)) > 0:
                    message = "This code already use"
                else:
                    coupon_obj.save()
            else:
                message = "Invalid input data"
        elif str(request.method).lower() == 'get' and int(request.GET.get('id', '0')) > 0:
            ccc = ProductCoupon.objects.get(pk=request.GET.get('id', '0'))
            ccc.display = False
            ccc.save()

    except Exception as ex:
        print(str(ex))
        message = "Invalid input data"
    if request.user.is_superuser:
        return response_admin(request, 'ss/coupon', {'message': message, 'coupons': ProductCoupon.objects.filter(user_id__in=[-1, 0], display=True).order_by("-id")})
    else:
        return response_seller(request, 'ss/coupon', {'message': message, 'coupons': ProductCoupon.objects.filter(user_id__in=[-1, request.user.id], display=True).order_by("-id")})


def product_order(request):
    page = request.GET.get('page', 1)
    shop_id = get_current_user_id(request.user)
    try:
        delivery_type = str(request.POST.get('delivery_type', 'delivery,store_pickup')).split(',')
        order_status = str(request.POST.get('status_type', 'CANCEL,PAYMENT_PENDING,ORDERED,PENDING,PROCESSING,SHIPPING,TRANSIT,COMPLETE')).split(',')
        if request.POST.get('id') is not None and request.POST.get('id') != '':
            order_list = [ProductsOrder.objects.get(pk=request.POST.get('id', '0'))]
        elif request.POST.get('user_number') is not None and request.POST.get('user_number') != '':
            order_list = ProductsOrder.objects.filter(status__in=order_status, is_payment=True, delivery_method__in=delivery_type, phone_number=request.POST.get('user_number'), shop=shop_id)
        else:
            order_list = ProductsOrder.objects.filter(status__in=order_status, is_payment=True, delivery_method__in=delivery_type, shop=shop_id).order_by('-id')
    except Exception as ex:
        print(str(ex))
        order_list = ProductsOrder.objects.filter(shop=shop_id).order_by('-id')

    paginator = Paginator(order_list, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if request.user.is_superuser:
        return response_admin(request, 'ss/order', {'order_list': products})
    return response_seller(request, 'ss/order', {'order_list': products})


def product_order_find(request):
    page = request.GET.get('page', 1)
    try:
        delivery_type = str(request.POST.get('delivery_type', 'delivery,store_pickup')).split(',')
        order_status = str(request.POST.get('status_type', 'CANCEL,PAYMENT_PENDING,ORDERED,PENDING,PROCESSING,SHIPPING,TRANSIT,COMPLETE')).split(',')
        if request.POST.get('id') is not None and request.POST.get('id') != '':
            order_list = [ProductsOrder.objects.get(pk=request.POST.get('id', '0'))]
        elif request.POST.get('shop_email') is not None and request.POST.get('shop_email') != '':
            order_list = ProductsOrder.objects.filter(status__in=order_status, is_payment=True, delivery_method__in=delivery_type, shop=Users.objects.filter(email=request.POST.get('shop_email'))[0].id)
        elif request.POST.get('shop_number') is not None and request.POST.get('shop_number') != '':
            order_list = ProductsOrder.objects.filter(status__in=order_status, is_payment=True, delivery_method__in=delivery_type, shop=Users.objects.filter(number=request.POST.get('shop_number'))[0].id)
        else:
            order_list = ProductsOrder.objects.filter(status__in=order_status, is_payment=True, delivery_method__in=delivery_type).order_by('-id')
    except Exception as ex:
        print(str(ex))
        order_list = ProductsOrder.objects.all().order_by('-id')

    paginator = Paginator(order_list, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if request.user.is_superuser:
        return response_admin(request, 'ss/order_find', {'order_list': products})
    return template(request, '404.html', {})


def product_order_view(request, order_id):
    try:
        order = ProductsOrder.objects.get(pk=order_id)
        if request.GET.get('pickupTime') is not None:
            from datetime import datetime
            pickup_time = datetime.strptime(request.GET.get('pickupTime'), "%Y-%m-%d %H:%M:%S")
            if order.delivery_method == 'store_pickup':
                order.picup_datetime = pickup_time
                order.save()

        if request.user.is_superuser:
            order_list = ProductsOrderItems.objects.filter(product_order=order.id)
        else:
            order_list = ProductsOrderItems.objects.filter(product_order=order.id, shop=get_current_user_id(request.user))
        if request.user.is_superuser:
            return response_admin(request=request, path='ss/order_view', context={'order': order, 'invoice': order_list, 'address': order.get_address(False)})
        return response_seller(request, 'ss/order_view', {'order': order, 'invoice': order_list, 'address': order.get_address(False)})
    except Exception as ex:
        return template(request, '500.html', {})


def product_order_invoice(request, inv_id):
    try:
        user__id = get_current_user_id(request.user)
        if request.GET.get('all') is not None:
            user__id = int(request.GET.get('all'))
        current_user = Users.objects.get(pk=user__id)

        inv_id = int(inv_id.replace('inv-', ''))
        order = ProductsOrder.objects.get(pk=inv_id)
        if request.user.is_superuser:
            invoice_list = ProductsOrderItems.objects.filter(product_order=order.id)
        else:
            invoice_list = ProductsOrderItems.objects.filter(product_order=order.id, shop=current_user.id)
        if request.user.is_superuser:
            return response_admin(request, 'ss/invoice', {'current_user': current_user, 'order': order, 'invoice': invoice_list, 'address': order.get_address(False)})
        return response_seller(request, 'ss/invoice', {'current_user': current_user, 'order': order, 'invoice': invoice_list, 'address': order.get_address(False)})
    except:
        return template(request, '404.html', {})

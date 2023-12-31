from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.decorators import api_view

from config.decorator import zipcode_permission
from web_api import serializable
from web_api.defs.common_defs import product_current_zipcode
from web_api.models import Users
from web_api.models_product import Products, ProductsReview, Categories, ShopZipcodes, ProductsWhiteList
from web_api.view import apiresponse


@api_view(['GET'])
@zipcode_permission
def get_product_by_id(request, product_id):
    """request def"""
    try:
        p = Products.objects.get(id=product_id)
        p.counter_visit = p.counter_visit + 1
        p.save()

        data = serializable.serializable_product(p)
        data['zipcode'] = []
        data['whitelist'] = None
        for pr in ProductsReview.objects.filter(product=p.id):
            data['review'].append(serializable.serializable_product_review(pr))

        for lp in Products.objects.filter(category_id=p.category_id, shop__is_active=True).order_by("-counter_visit")[:10]:
            if lp.id != product_id:
                data['related_product'].append(serializable.serializable_product_related(lp))
        data['zipcode'] = product_current_zipcode(p.shop)
        if not request.user.is_anonymous:
            pwl = ProductsWhiteList.objects.filter(user_id=request.user, product__id=product_id).first()
            if pwl is not None:
                data['whitelist'] = {"id": pwl.id, "quantity": pwl.product_quantity}

        return apiresponse.httpResponse(True, data, "Success")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Product not found")


def product_response_paginator(request=None, query=None):
    """return def"""
    try:
        data = []
        page = request.GET.get('page', 1)
        paginator = Paginator(query, 10)
        try:
            p_list = paginator.page(page)
        except PageNotAnInteger:
            p_list = paginator.page(1)
        except EmptyPage:
            p_list = paginator.page(paginator.num_pages)

        for p in p_list:
            data.append(serializable.serializable_product_related(p))
        return apiresponse.response_paginated(p_list, data, request)
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


@zipcode_permission
def get_product_home(request):
    """request def"""
    final_data = []

    shop_list = []
    for shop_zipcode in ShopZipcodes.objects.filter(zipcode__zipcode=request.zipcode, shop__is_active=True)[:10]:
        shop_list.append(serializable.serializable_user_seller(shop_zipcode.shop))
    final_data.append({"title": "Shop by store", "id": 1, "list": shop_list})

    recommended_list = []
    for products in Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-discount")[:10]:
        recommended_list.append(serializable.serializable_product_related(products))
    final_data.append({"title": "Recommended for you", "id": 2, "list": recommended_list})

    popular_list = []
    for products in Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-counter_visit")[:10]:
        popular_list.append(serializable.serializable_product_related(products))
    final_data.append({"title": "Popular Choice", "id": 3, "list": popular_list})

    return apiresponse.httpResponse(True, final_data, "Success")


@zipcode_permission
def get_product_home_by_id(request, home_id=1):
    """request def"""
    try:
        name = str(request.GET.get("name", "")).strip()
        if home_id == 1:
            shop_list = []
            for shop_zipcode in ShopZipcodes.objects.filter(shop__first_name__icontains=name, zipcode__zipcode=request.zipcode, shop__is_active=True)[:10]:
                shop_list.append(serializable.serializable_user_seller(shop_zipcode.shop))
            return apiresponse.httpResponse(True, {'next': None, 'previous': None, 'count': len(shop_list), 'results': shop_list}, "Success")
        elif home_id == 2:
            query = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-discount")
            return product_response_paginator(request, query)
        elif home_id == 3:
            query = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-counter_visit")
            return product_response_paginator(request, query)
    except Exception as ex:
        print(str(ex))
    return get_product_all(request=request)


@zipcode_permission
def get_product_all(request):
    """request def"""
    p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-updated")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def get_product_by_category(request, id):
    """request def"""
    p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, category=id, shop__is_active=True).order_by("-updated")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def get_product_by_search(request):
    """request def"""
    p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, name__icontains=request.GET.get("q", ""), shop__is_active=True).order_by("-updated")
    return product_response_paginator(request=request, query=p_list)


def get_product_by_search_without_zipcode(request):
    """request def"""
    p_list = Products.objects.filter(display=True, name__icontains=request.GET.get("q", ""), shop__is_active=True).order_by("-updated")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def get_product_by_category_shop_items(request, shop_id):
    data = []
    for c in Categories.objects.all().order_by("parent"):
        temp = {
            "id": c.id,
            "name": c.name,
            "parent": c.parent,
            "display": c.display,
            "image": c.image,
            "delivery_flag": c.delivery_flag,
            "items": []
        }
        for p in Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, category=c, shop_id=shop_id, shop__is_active=True)[:10]:
            temp['items'].append(serializable.serializable_product_related(p))
        if len(temp['items']) > 0:
            data.append(temp)
    return apiresponse.httpResponse(True, data, "success")


@zipcode_permission
def get_shop_all(request):
    try:
        data = []
        query = Users.objects.filter(is_staff=True, is_active=True)
        page = request.GET.get('page', 1)
        paginator = Paginator(query, 10)
        try:
            shop_list = paginator.page(page)
        except PageNotAnInteger:
            shop_list = paginator.page(1)
        except EmptyPage:
            shop_list = paginator.page(paginator.num_pages)

        for shop in shop_list:
            data.append(serializable.serializable_user_seller(shop))
        return apiresponse.response_paginated(shop_list, data, request)
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


@zipcode_permission
def get_product_by_category_shop_ids(request, category_id, shop_id):
    p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, category_id=category_id, shop_id=shop_id, shop__is_active=True).order_by("-updated")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def new_sale_top_products(request, key):
    if key == "top":
        p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-counter_order")
    elif key == "sale":
        p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, discount__gt=0, shop__is_active=True).order_by("-discount_created")
    else:
        p_list = Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, shop__is_active=True).order_by("-created")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def get_product_by_category_shop_top_pick(request, shop_id):
    p_list = Products.objects.filter(shop_id=shop_id, shop__is_active=True).order_by("-counter_order")
    return product_response_paginator(request=request, query=p_list)


@zipcode_permission
def categories_id_sub_cat_products(request, category=0):
    data = []
    category = Categories.objects.get(pk=category)
    category_sub = Categories.objects.filter(parent=category.id)
    if len(category_sub) > 0:
        category_list = category_sub
    else:
        category_sub.append(category)

    for ch in category_sub:
        products = []
        for p in Products.objects.filter(shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True, category=ch, shop__is_active=True)[:10]:
            products.append(serializable.serializable_product_related(p))
        if len(products) > 0:
            data.append({"products": products, "key": {"id": ch.id, "name": ch.name, "image": ch.image}})
    return apiresponse.httpResponse(True, data, "")

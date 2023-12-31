import datetime
import json
import traceback

import paypalrestsdk
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum

from config import settings
from config.decorator import zipcode_permission
from web_api import serializable
from web_api.defs import email_service, common_defs
from web_api.defs.common_defs import get_current_user_id, OrderItemValue, search_dic
from web_api.models import Users
from web_api.models_product import Products, ProductsCard, ProductsWhiteList, ShopZipcodes, ShopPickUpStore
from web_api.models_product_order import ProductsOrder, ProductsOrderItems, ProductPayment, OrderStatus, ProductPaymentHistory, ProductCoupon, ProductPaymentInformation, ProductOrderDeliveryFee
from web_api.serializable_body import BodyOrder, BodyPayment
from web_api.view import apiresponse


############## Product Card ##############
@zipcode_permission
def order_card_add(request):
    """
    REQUEST POST
    [
        {

            "product": 1,
            "product_quantity": 1,
            "type": "add",
            "delivery_method": "store_pickup or delivery"
        }
    ]

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        if not request.user.is_anonymous:
            body_dumps = json.loads(request.body.decode("utf-8"))
            """parse all cards"""
            for ob in body_dumps:
                pc = ProductsCard()
                pc.user_id = request.user.id
                pc.product_id = int(ob['product'])
                pc.product_quality = int(ob['product_quantity'])

                delivery_method = ob.get('delivery_method')
                if delivery_method is None:
                    return apiresponse.httpResponse(False, None, "Please add delivery method")
                if delivery_method == 'store_pickup':
                    pp = Products.objects.get(pk=pc.product_id)
                    pus = ShopPickUpStore.objects.filter(shop_id=pp.shop.id, is_active=True)
                    if len(pus) == 0:
                        return apiresponse.httpResponse(False, None, "Currently unavailable for pickup. Please select the delivery option.")

                """Checking previously is add or not"""
                pc_list = ProductsCard.objects.filter(product_id=pc.product_id, user_id=pc.user_id)
                if len(pc_list) > 0:
                    if ob.get('type', '') == 'add':
                        pc.product_quality = pc.product_quality + pc_list[0].product_quality
                    """Delete previously add this product card"""
                    pc_list.delete()
                pc.save()
            return apiresponse.httpResponse(True, None, "success")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


@zipcode_permission
def order_card_delete(request):
    """
    REQUEST GET
    request.GET.ids="1,2,3"

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        if not request.user.is_anonymous:
            """Get card ins from param and then delete"""
            if request.GET.get('ids', '') == '':
                for pc in ProductsCard.objects.filter(user_id=request.user.id):
                    pc.delete()
            else:
                for pc in ProductsCard.objects.filter(id__in=list(map(int, str(request.GET.get('ids', '')).split(",")))):
                    if pc.user_id == request.user.id:
                        pc.delete()
            return apiresponse.httpResponse(True, None, "success")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def order_card_product_info(request):
    """
    REQUEST GET

    RESPONSE
    {
       "status": true,
       "message": "success",
       "data": {
          "card_items": [
             {
                "card_id": 3,
                "product": {
                   "id": 14,
                   "name": "Golden Temple Flour Blend",
                   "shop": {
                      "id": 1,
                      "shop_name": "Admin User",
                      "shop_number": null,
                      "seller_tax": "10.36",
                      "email": "admin@gmail.com",
                      "phone": "123456789",
                      "image": "https://randomuser.me/api/portraits/women/1.jpg",
                      "address": {
                         "address": "Nikunjo 2",
                         "state": "Dhaka",
                         "city": "Dhaka",
                         "zip": "12345"
                      }
                   },
                   "price": 13,
                   "price_new": 11.7,
                   "discount": 10.000000000000005,
                   "weight": {
                      "value": "20",
                      "type": "8"
                   },
                   "image": "https://thekayi.s3.us-east-2.amazonaws.com/product/p-14-1.png",
                   "display": true,
                   "kayi_shop": true,
                   "stars": null,
                   "total_review": 0
                },
                "product_quantity": 1
             }
          ],
          "total_amount": 26.7,
          "order_amount": 11.7,
          "delivery_amount": 15
       }
    }
    """
    data = []
    try:
        if not request.user.is_anonymous:
            in_total_amount = 0
            tax_amount = 0
            pc_list = ProductsCard.objects.filter(user_id=request.user.id).order_by("-id")
            for pc in pc_list:
                data.append({"card_id": pc.id, "product": serializable.serializable_product_related(pc.product), "product_quantity": pc.product_quality})
                new_amount = float(pc.product.price_new * pc.product_quality)
                tax_amount = tax_amount + ((float(pc.product.shop.seller_tax) / 100) * new_amount)
                in_total_amount = in_total_amount + new_amount
            delivery_amount = common_defs.delivery_fee(in_total_amount)

            tax_amount = round(tax_amount, 2)
            in_total_amount = round(in_total_amount, 2)
            delivery_comment = "(If the order is between $1 to $150, delivery fee is $15, if the order amount is more than $150 delivery fee is 10% of total amount.)"
            return apiresponse.httpResponse(True, {"card_items": data, "tax_amount": tax_amount, "total_amount": float(in_total_amount + tax_amount), "order_amount": float(in_total_amount), "delivery_comment": delivery_comment}, "success")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


############## Product WhiteList ##############
def order_whitelist_add(request):
    """
    REQUEST POST
    [
       {
           "product": 1,
           "product_quantity": 1
       }
    ]

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
   """
    try:
        body_dumps = json.loads(request.body.decode("utf-8"))
        for ob in body_dumps:
            pc = ProductsWhiteList()
            pc.user_id = request.user.id
            pc.product_id = int(ob['product'])
            pc.product_quantity = int(str(ob.get('product_quantity', '0')))

            pc_list = ProductsWhiteList.objects.filter(product_id=pc.product_id, user_id=pc.user_id)
            if len(pc_list) > 0:
                pc_list.delete()
            pc.save()
        return apiresponse.httpResponse(True, None, "success")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def order_whitelist_delete(request):
    """
    REQUEST GET
    request.GET.ids="1,2,3"

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """

    try:
        pc_list = ProductsWhiteList.objects.filter(id__in=list(map(int, str(request.GET.get('ids', '')).split(","))))
        for pc in pc_list:
            if pc.user_id == request.user.id:
                pc.delete()
        return apiresponse.httpResponse(True, None, "success")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def order_whitelist_product_info(request):
    """
    REQUEST GET

    RESPONSE
    {
        "status": true,
        "message": "success",
        "data":
        [
            {
                "card_id": 1,
                "product":
                {
                    "id": 14,
                    "name": "Golden Temple Flour Blend",
                    "shop":
                    {
                        "id": 1,
                        "shop_name": "Admin User",
                        "shop_number": null,
                        "seller_tax": "10.36",
                        "email": "admin@gmail.com",
                        "phone": "123456789",
                        "image": "https://randomuser.me/api/portraits/women/1.jpg",
                        "address":
                        {
                            "address": "Nikunjo 2",
                            "state": "Dhaka",
                            "city": "Dhaka",
                            "zip": "12345"
                        }
                    },
                    "price": 13,
                    "price_new": 11.7,
                    "discount": 10.000000000000005,
                    "weight":
                    {
                        "value": "20",
                        "type": "8"
                    },
                    "image": "https://thekayi.s3.us-east-2.amazonaws.com/product/p-14-1.png",
                    "display": true,
                    "kayi_shop": true,
                    "stars": null,
                    "total_review": 0
                },
                "product_quantity": 1
            }
        ]
    }
    """
    data = []
    try:
        pc_list = ProductsWhiteList.objects.filter(user_id=request.user.id)
        for pc in pc_list:
            data.append({"card_id": pc.id, "product": serializable.serializable_product_related(pc.product), "product_quantity": pc.product_quantity})
        return apiresponse.httpResponse(True, data, "success")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong")


############## Product Order Here ##############
@zipcode_permission
def tips(request, order_id):
    """
    REQUEST GET
    request.GET.tips=0

    RESPONSE
    {
        "status": true,
        "data": {},
        "message": "string"
    }
    """

    try:
        with transaction.atomic():
            products_order = ProductsOrder.objects.get(pk=order_id)
            if 'tips' in request.GET:
                products_order.tips = int(request.GET.get('tips', '0'))
                products_order.total_amount = products_order.amount + products_order.tips + products_order.tax_amount + products_order.delivery_amount
                products_order.save()
            return apiresponse.httpResponse(True, serializable.serializable_product_order(products_order), "")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
    return apiresponse.httpResponse(False, None, "Not found")


@zipcode_permission
def coupon(request, order_id, code):
    """
    REQUEST GET
    request.GET.tips=0

    RESPONSE
    {
        "status": true,
        "data": {},
        "message": "string"
    }
    """
    try:
        with transaction.atomic():
            products_order = ProductsOrder.objects.get(pk=order_id)
            coupon = ProductCoupon.objects.filter(code=code, display=True).first()
            event_full_datetime = datetime.datetime(coupon.expired.year, coupon.expired.month, coupon.expired.day, coupon.expired.hour, coupon.expired.minute, coupon.expired.second)

            if 'tips' in request.GET:
                products_order.tips = int(request.GET.get('tips', '0'))
                products_order.total_amount = products_order.amount + products_order.tips + products_order.tax_amount + products_order.delivery_amount
                products_order.save()
            if coupon is not None:
                if products_order.is_payment:
                    return apiresponse.httpResponse(False, None, "Already add payment")
                elif products_order.amount < coupon.amount_order:
                    return apiresponse.httpResponse(False, None, "Invalid order amount. Must me grater then $" + str(coupon.amount_order))
                elif event_full_datetime < datetime.datetime.now():
                    return apiresponse.httpResponse(False, None, "Already coupon date expired")
                else:
                    products_order.voucher = coupon
                    if products_order.get_new_amount() > 0:
                        products_order.save()
                        return apiresponse.httpResponse(True, serializable.serializable_product_order(products_order), "")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
    return apiresponse.httpResponse(False, None, "Invalid coupon")


@zipcode_permission
def order_add(request):
    """
    {
        "products":[
            {
                "product": 1,
                "quantity": 1,
                "other": "string",
            }
        ],
        "address": {
            "address": "string",
            "city": "string",
            "state": "string",
            "zip": "string"
        },
        "tips": 1,
        "phone_number": "string",
        "delivery_method": "store_pickup or delivery"
    }
    """
    response_data = []
    order_id_list = []
    if request.user.is_anonymous:
        return apiresponse.httpResponse(False, None, "Please sign in")
    try:
        with transaction.atomic():
            """Parsing list of product"""
            product_ids = []
            request_payload = json.loads(request.body.decode("utf-8"))
            order_body = [BodyOrder(**attrs) for attrs in request_payload['products']]
            phone_number = request_payload.get('phone_number', request.user.phone)

            """store_pickup/delivery"""
            delivery_method = request_payload.get('delivery_method', 'delivery')
            if delivery_method is None:
                return apiresponse.httpResponse(False, None, "Please add delivery method")
            for ob in order_body:
                product_ids.append(ob.product)

            if len(product_ids) > 0:
                """Create a product list from user request"""
                product_list = Products.objects.filter(id__in=product_ids, shop__shopzipcodes__zipcode_id__in=[request.zipcode], display=True).order_by("-updated")
                if len(product_list) == 0:
                    return apiresponse.httpResponse(False, None, "Invalid product list")

                """Create a shop list again their product shop_list={1:[OrderItemValue1,OrderItemValue2]}"""
                shop_list = {}
                for pl in product_list:
                    oiv = OrderItemValue(product=pl, order_body=order_body)
                    if search_dic(shop_list, pl.shop.id):
                        shop_list[pl.shop.id].append(oiv)
                    else:
                        shop_list[pl.shop.id] = [oiv]

                """Creating product order individually by shop"""
                for key, order_item_value in shop_list.items():
                    shop_zipcode = ShopZipcodes.objects.filter(shop_id=key, zipcode__zipcode=request.zipcode).first()
                    if shop_zipcode is None:
                        raise

                    """Creating order"""
                    if delivery_method is not None:
                        pus = ShopPickUpStore.objects.filter(shop_id=key, is_active=True)
                        if len(pus) >= 0:
                            products_order = ProductsOrder.objects.create(
                                user=request.user,
                                shop=key,
                                is_admin=order_item_value[0].product.shop.is_superuser,
                                status=OrderStatus.PAYMENT_PENDING.name,
                                is_payment=False,
                                payment=None,
                                commission=Users.objects.get(pk=key).commission,
                                phone_number=phone_number,
                                zipcode_tax=float(Users.objects.get(pk=key).seller_tax),
                                address=json.dumps(request_payload['address']),
                                tips=round(int(str(request_payload.get('tips', '0'))) / len(shop_list.items()), 2)
                            )

                            """Creating order items"""

                            for oiv in order_item_value:
                                ProductsOrderItems.objects.create(
                                    product=oiv.product,
                                    product_order=products_order.id,
                                    product_price=oiv.product.price_new,
                                    product_discount=oiv.product.discount,
                                    status=products_order.status,
                                    shop=key,
                                    is_admin=order_item_value[0].product.shop.is_superuser,
                                    product_quantity=oiv.quantity,
                                    product_price_final=oiv.price
                                )
                            """Update order like amount,delivery_amount,tax_amount"""
                            order_id_list.append(products_order.id)
                            total_product_price_final = ProductsOrderItems.objects.filter(product_order=products_order.id).aggregate(total_amount=Sum('product_price_final')).get('total_amount', 0.0)

                            if delivery_method == 'store_pickup':
                                products_order.delivery_amount = 0
                                products_order.delivery_method = 'store_pickup'
                            else:
                                products_order.delivery_method = 'delivery'
                                products_order.delivery_amount = common_defs.delivery_fee(total_product_price_final)
                            products_order.tax_amount = round(((products_order.zipcode_tax / 100) * total_product_price_final), 2)
                            products_order.amount = round(total_product_price_final, 2)
                            products_order.total_amount = round(total_product_price_final + products_order.delivery_amount + products_order.tax_amount + products_order.tips, 2)
                            products_order.save()
                            response_data.append({
                                "order_id": products_order.id,
                                "amount": products_order.total_amount,
                                "order_amount": products_order.amount,
                                "delivery_amount": products_order.delivery_amount,
                                "tax_amount": products_order.tax_amount
                            })

                ProductsCard.objects.filter(user=request.user).delete()
                return apiresponse.httpResponse(True, response_data, "Order added successfully")
            return apiresponse.httpResponse(False, None, "Invalid product list")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
    return apiresponse.httpResponse(False, None, "Something wend wrong")


def order_all(request):
    """
    REQUEST GET

    RESPONSE
    {
        "status": true,
        "message": "Order address updated",
        "data":
        [
            {
                "id": 8,
                "coupon": null,
                "status": "PAYMENT_PENDING",
                "is_payment": false,
                "tips": 10,
                "delivery_amount": 10,
                "tax_amount": 1.38,
                "amount": 27.57,
                "total_amount": 48.95,
                "new_total_amount": 48.95,
                "phone_number": "+13454715640",
                "address":
                {
                    "address": "1236 Long Dr St",
                    "city": "New York",
                    "state": "AK",
                    "zip": "123456"
                },
                "products":
                [
                    {
                        "id": 28391,
                        "title": "Onion Red 10 LB",
                        "product_price": 9.19,
                        "quantity": 1,
                        "image": "https://thekayi.s3.us-east-2.amazonaws.com/product/p-222-1.png",
                        "provider":
                        {
                            "id": 2,
                            "shop_name": "Showpno Departmental ",
                            "shop_number": "DK-1245632",
                            "seller_tax": "5.00",
                            "email": "showpno@gmail.com",
                            "phone": "3454715640",
                            "image": "https://thekayi.s3.us-east-2.amazonaws.com/user/2.png",
                            "address":
                            {
                                "address": "Nikunjo 2",
                                "state": "Dhaka",
                                "city": "Dhaka",
                                "zip": "123"
                            }
                        },
                        "status": "PAYMENT_PENDING",
                        "other": ""
                    },
                    {
                        "id": 28391,
                        "title": "Onion Red 10 LB",
                        "product_price": 9.19,
                        "quantity": 2,
                        "image": "https://thekayi.s3.us-east-2.amazonaws.com/product/p-222-1.png",
                        "provider":
                        {
                            "id": 2,
                            "shop_name": "Showpno Departmental ",
                            "shop_number": "DK-1245632",
                            "seller_tax": "5.00",
                            "email": "showpno@gmail.com",
                            "phone": "3454715640",
                            "image": "https://thekayi.s3.us-east-2.amazonaws.com/user/2.png",
                            "address":
                            {
                                "address": "Nikunjo 2",
                                "state": "Dhaka",
                                "city": "Dhaka",
                                "zip": "123"
                            }
                        },
                        "status": "PAYMENT_PENDING",
                        "other": ""
                    }
                ],
                "created": 1639046650000
            }
        ]
    }
    """
    try:
        data = []
        products_order = ProductsOrder.objects.filter(user_id=request.user).order_by("-id")
        for po in products_order:
            pickup_address = []
            if po.is_payment is False and po.delivery_method == 'store_pickup':
                for s in ShopPickUpStore.objects.filter(shop_id=po.shop, is_active=True):
                    pickup_address.append(s.address)

            item = serializable.serializable_product_order(po)
            item['pickup_address'] = pickup_address
            data.append(item)
        return apiresponse.httpResponse(True, data, "Order address updated")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "data")


def order_del(request, order_id):
    """
    REQUEST GET

    RESPONSE
    {
        "status": true,
        "data": {},
        "message": "string"
    }
    """
    try:
        products_order = ProductsOrder.objects.get(pk=order_id)
        if products_order.shop == request.user.id or request.user.is_superuser or request.user.id == products_order.user.id:
            ProductsOrderItems.objects.filter(product_order=order_id).delete()
            products_order.delete()
            ProductPaymentHistory.objects.filter(order_id=order_id).delete()
            ProductPayment.objects.filter(product_order=order_id).delete()
            return apiresponse.httpResponse(True, "delete", "okay")
        return apiresponse.httpResponse(False, None, "You are not valid user for delete this item")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, str(ex))


@zipcode_permission
def order_address_change(request, order_id):
    """
    REQUEST POST
    request.POST.address="string"
    request.POST.state="string"
    request.POST.city="string"
    request.POST.zip="string"

    RESPONSE
    {
        "status": true,
        "data": {},
        "message": "string"
    }
    """
    try:
        if not request.user.is_anonymous:
            products_order = ProductsOrder.objects.get(pk=order_id)
            if products_order.status == OrderStatus.CANCEL.name or products_order.status == OrderStatus.COMPLETE.name:
                return apiresponse.httpResponse(True, serializable.serializable_product_order(products_order), "You order is " + products_order.status + ". You can't change your address")

            address = {}
            if len(request.POST.get("address", "")) > 3:
                address = {
                    "address": request.POST.get("address", ""),
                    "state": request.POST.get("state", ""),
                    "city": request.POST.get("city", ""),
                    "zip": request.POST.get("zip", "")
                }
            else:
                val = json.loads(request.body.decode("utf-8"))
                address = {
                    "address": val.get("address", None),
                    "state": val.get("state", ""),
                    "city": val.get("city", ""),
                    "zip": val.get("zip", "")
                }

            if address.get("address") is None:
                raise
            products_order.address = json.dumps(address)
            products_order.save()
            return apiresponse.httpResponse(True, serializable.serializable_product_order(products_order), "Order address updated")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Invalid information")


def order_change_status(request, order_id):
    """
    REQUEST GET
    request.GET.status= PROCESSING, SHIPPING, TRANSIT, COMPLETE

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        with transaction.atomic():
            status = request.GET.get("status")
            if not request.user.is_anonymous:
                products_order = ProductsOrder.objects.get(pk=order_id)
                if request.user.is_superuser:
                    order_list = ProductsOrderItems.objects.filter(product_order=products_order.id, status__in=[OrderStatus.ORDERED.name, OrderStatus.PROCESSING.name, OrderStatus.SHIPPING.name, OrderStatus.TRANSIT.name])
                else:
                    order_list = ProductsOrderItems.objects.filter(product_order=products_order.id, status__in=[OrderStatus.ORDERED.name, OrderStatus.PROCESSING.name, OrderStatus.SHIPPING.name, OrderStatus.TRANSIT.name], shop=get_current_user_id(request.user))

                if status is None:
                    return apiresponse.httpResponse(False, None, "Invalid status")
                elif status == "PROCESSING":
                    if products_order.status == OrderStatus.ORDERED.name:
                        products_order.status = OrderStatus.PROCESSING.name
                        products_order.save()
                elif status == "SHIPPING":
                    if products_order.status == OrderStatus.PROCESSING.name or products_order.status == OrderStatus.ORDERED.name:
                        products_order.status = OrderStatus.SHIPPING.name
                        products_order.save()
                        email_service.email_order_shipped(request=request, order=products_order)
                elif status == "TRANSIT":
                    products_order.status = OrderStatus.TRANSIT.name
                    products_order.save()
                elif status == "COMPLETE" and request.user.is_superuser:
                    if products_order.status == OrderStatus.SHIPPING.name or products_order.status == OrderStatus.TRANSIT.name:
                        products_order.status = OrderStatus.COMPLETE.name
                        products_order.save()
                else:
                    return apiresponse.httpResponse(False, None, "Invalid status")
                for ol in order_list:
                    ol.status = products_order.status
                    ol.save()
                return apiresponse.httpResponse(True, None, "Success")
            else:
                return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Invalid information")


def order_cancel(request, order_id):
    """
    REQUEST GET
    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """

    try:
        with transaction.atomic():
            if not request.user.is_anonymous:
                products_order = ProductsOrder.objects.get(pk=order_id)
                if products_order.status == OrderStatus.COMPLETE.name:
                    return apiresponse.httpResponse(False, None, "You order is already delivered")
                elif products_order.status == OrderStatus.SHIPPING.name:
                    return apiresponse.httpResponse(False, None, "You order is shipping")
                elif products_order.status == OrderStatus.TRANSIT.name:
                    return apiresponse.httpResponse(False, None, "You order is transit")
                elif products_order.status == OrderStatus.CANCEL.name:
                    return apiresponse.httpResponse(False, None, "You order is already canceled")
                else:
                    if products_order.user.id == request.user.id or request.user.is_superuser:
                        products_order.status = OrderStatus.CANCEL.name
                        products_order.save()

                        order_item_list = ProductsOrderItems.objects.filter(product_order=products_order.id, shop=get_current_user_id(request.user))
                        for ol in order_item_list:
                            ol.status = products_order.status
                            ol.product_price_final = 0
                            ol.save()

                        order_total_amount = products_order.total_amount
                        products_order.amount = 0
                        products_order.tax_amount = 0
                        products_order.delivery_amount = 0
                        products_order.total_amount = 0
                        products_order.save()

                        if products_order.is_payment:
                            payment_history1 = ProductPaymentHistory()
                            payment_history1.amount = order_total_amount
                            payment_history1.order_id = products_order.id
                            payment_history1.debit_credit = "CR"
                            payment_history1.comment = "Order cancel"
                            payment_history1.user = request.user.id
                            payment_history1.save()
                        return apiresponse.httpResponse(True, None, "Order cancel")
                    return apiresponse.httpResponse(False, None, "You are not valid user")
            else:
                return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Invalid information")


def order_cancel_by_shop(request, order_id):
    """
    REQUEST GET
    request.GET.item= 1

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        with transaction.atomic():
            if not request.user.is_anonymous:
                products_order = ProductsOrder.objects.get(pk=order_id)

                # if True:
                if products_order.is_payment:
                    if request.GET.get("item", None) is not None:
                        order_list = ProductsOrderItems.objects.filter(id=request.GET.get("item", '0'))
                    else:
                        order_list = ProductsOrderItems.objects.filter(product_order=products_order.id)
                    for ol in order_list:
                        """Check who and when item can be cancelable"""
                        is_cancel = False
                        if products_order.shop == get_current_user_id(request.user) or request.user.is_superuser:
                            is_cancel = True

                        if products_order.status == OrderStatus.CANCEL.name:
                            is_cancel = False
                        elif products_order.status == OrderStatus.COMPLETE.name:
                            is_cancel = False
                        # elif products_order.status == OrderStatus.PAYMENT_PENDING.name:
                        #    is_cancel = False

                        if is_cancel:
                            ol.status = OrderStatus.CANCEL.name
                            ol.product_price_final = 0
                            ol.save()

                    new_amount = ProductsOrderItems.objects.filter(product_order=products_order.id).aggregate(total_amount=Sum('product_price_final')).get('total_amount', 0.0)
                    new_tax = round(((products_order.zipcode_tax / 100) * new_amount), 2)

                    cancel_amount = products_order.amount - new_amount
                    cancel_tax_amount = products_order.tax_amount - new_tax
                    cancel_delivery_amount = 0
                    if new_amount > 0:
                        products_order.amount = round(new_amount, 2)
                        products_order.tax_amount = round(new_tax, 2)
                    if new_amount < .005:
                        cancel_delivery_amount = products_order.delivery_amount
                        products_order.amount = 0
                        products_order.tax_amount = 0
                        products_order.total_amount = 0
                        products_order.tips = 0
                        products_order.delivery_amount = 0
                        products_order.status = OrderStatus.CANCEL.name
                    products_order.total_amount = round(new_amount + new_tax + products_order.delivery_amount + products_order.tips, 2)
                    products_order.save()

                    if cancel_amount > 0:
                        ProductPaymentHistory.objects.create(
                            amount=round(cancel_amount, 2),
                            order_id=products_order.id,
                            debit_credit="CR",
                            comment="Order canceled (Order Item #" + str(ol.id) + ")",
                            user=request.user.id
                        )
                    if cancel_tax_amount > 0.004:
                        ProductPaymentHistory.objects.create(
                            amount=round(cancel_tax_amount + cancel_delivery_amount + products_order.tips, 2),
                            order_id=products_order.id,
                            debit_credit="CR",
                            comment="Order canceled tax, delivery and tips (Order Item #" + str(ol.id) + ")",
                            user=request.user.id
                        )
                    return apiresponse.httpResponse(True, None, "Order cancel")
                else:
                    return apiresponse.httpResponse(False, None, "Order is waiting for payment")
            else:
                return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
    return apiresponse.httpResponse(False, None, "Invalid information")


############## Order Payment ##############
def order_payment_open_transaction(request, order_id):
    """
    REQUEST POST
    {
    }

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        with transaction.atomic():
            if not request.user.is_anonymous:
                ppi_old = ProductPaymentInformation.objects.filter(product_order_id=order_id).first()
                if ppi_old is None:
                    products_order = ProductsOrder.objects.get(pk=order_id)
                    ppi = ProductPaymentInformation()
                    ppi.amount = products_order.total_amount
                    ppi.product_order = products_order
                    ppi.user = request.user
                    ppi.payment_type = "paypal"
                    ppi.payment_request = json.dumps(json.loads(request.body.decode("utf-8")))
                    ppi.payment_response = json.dumps({})
                    ppi.is_payment = False
                    ppi.save()
                    return apiresponse.httpResponse(True, None, "Success")
            else:
                return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
    return apiresponse.httpResponse(False, None, "Invalid information")


def order_payment_add(request):
    """
    REQUEST POST
    {
           "order_id": 1,
           "type": "kayi or paypal",
           "pick_up_address": "string",
           "payment_info": {
                "payer_id": "string",
                "paypal_sdk_id": "string"
           }
    }

    RESPONSE
    {
        "status": true,
        "data": null,
        "message": "string"
    }
    """
    try:
        message = ""
        with transaction.atomic():
            if not request.user.is_anonymous:
                """get payment method from request body"""
                body_payment = BodyPayment(request=request)
                products_order = ProductsOrder.objects.get(pk=body_payment.order_id)
                if products_order.delivery_method == 'store_pickup':
                    if body_payment.pick_up_address is None:
                        return apiresponse.httpResponse(False, None, "Please add Pick up address")
                    products_order.picup_location = body_payment.pick_up_address
                    products_order.save()

                """Check correct user"""
                if request.user.id != products_order.user.id:
                    return apiresponse.httpResponse(False, None, "This order is not assign to you.")

                """Check payment is already paid"""
                if products_order.is_payment is False:
                    payment_comment = None
                    payment_comment_his_dr = None
                    payment_request = json.dumps({})
                    payment_response = json.dumps({})

                    if body_payment.payment_type == "kayi":
                        """
                        Pay bill from kayi balance
                        """

                        """Get current kay balance"""
                        data_total_amount = ProductPaymentHistory.objects.filter(user=request.user.id).aggregate(total_amount=Sum('amount'))
                        if data_total_amount.get('total_amount') is None and (int(data_total_amount.get('total_amount', 0)) >= products_order.total_amount):
                            products_order.is_payment = True

                            """Content ready for payment"""
                            payment_comment = "Kayi amount execute successfully"
                            payment_comment_his_dr = "Amount cut for order (Kayi)"
                            payment_request = json.dumps({})
                            payment_response = json.dumps({})
                        else:
                            message = "Inefficient balance."
                    elif body_payment.payment_type == "paypal":
                        """
                        Pay bill from paypal balance
                        """

                        from paypalrestsdk import Payment
                        paypalrestsdk.configure({"mode": settings.PAYPAL_MODE, "client_id": settings.PAYPAL_CLIENT_ID, "client_secret": settings.PAYPAL_CLIENT_SECRET})
                        payment = Payment.find(body_payment.payment_info.paypal_sdk_id)
                        if payment.id == body_payment.payment_info.paypal_sdk_id:
                            products_order.is_payment = True

                            """Content ready for payment"""
                            payment_comment = "Paypal payment execute successfully"
                            payment_comment_his_dr = "Amount cut for order (Paypal)"
                            payment_request = json.dumps(body_payment.payment_info.json)
                            payment_response = str(payment)

                            ProductPaymentHistory.objects.create(
                                amount=products_order.total_amount,
                                order_id=products_order.id,
                                debit_credit="CR",
                                comment="Amount add (Paypal)",
                                user=request.user.id,
                            )

                            ppi = ProductPaymentInformation.objects.filter(product_order_id=products_order.id).first()
                            if ppi is None:
                                ppi = ProductPaymentInformation()
                            ppi.amount = products_order.total_amount
                            ppi.product_order = products_order
                            ppi.user = request.user
                            ppi.payment_type = "paypal"
                            ppi.payment_request = json.dumps(body_payment.payment_info.json)
                            ppi.payment_response = str(payment)
                            ppi.is_payment = True
                            ppi.save()

                        else:
                            message = "Paypal payment execute failed"

                    """"""
                    if products_order.is_payment:
                        pp = ProductPayment.objects.create(
                            amount=products_order.total_amount,
                            product_order=products_order.id,
                            payment_type=body_payment.payment_type,
                            comment=payment_comment,
                            payment_request=payment_request,
                            payment_response=payment_response
                        )

                        products_order.is_payment = True
                        products_order.payment = pp
                        products_order.status = OrderStatus.ORDERED.name
                        products_order.save()

                        ProductPaymentHistory.objects.create(
                            amount=-products_order.total_amount,
                            order_id=products_order.id,
                            debit_credit="DR",
                            comment=payment_comment_his_dr,
                            user=request.user.id,
                        )
                        for ol in ProductsOrderItems.objects.filter(product_order=products_order.id):
                            ol.status = products_order.status
                            ol.save()
                        message = payment_comment
                    else:
                        return apiresponse.httpResponse(False, None, "Invalid information")
                else:
                    message = "Payment already applied"
                    if request.user.is_superuser and request.GET.get("del_token", "") == "gZXNtK49UvTG8SB2UPpS":
                        products_order.is_payment = False
                        products_order.payment = None
                        products_order.save()
                        ProductPaymentHistory.objects.filter(order_id=body_payment.order_id).delete()
                        ProductPayment.objects.filter(product_order=body_payment.order_id).delete()
                        return apiresponse.httpResponse(True, "delete", message)
                return apiresponse.httpResponse(True, serializable.serializable_payment(products_order.payment), message)
            else:
                return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Invalid information")


def order_payment_history(request):
    """
    REQUEST GET

    RESPONSE
    {
        "status": true,
        "data": {
            "next": "string",
            "previous": "string",
            "count": 10,
            "data":[
                {
                    "id": 1,
                    "amount": 10,
                    "order_id":1,
                    "order_invoice": 10,
                    "debit_credit": 10,
                    "comment": "string",
                    'created': 1639046650000"
                }
            ]
        },
        "message": "string"
    }
    """
    try:
        if not request.user.is_anonymous:
            data = []
            page = request.GET.get('page', 1)
            paginator = Paginator(ProductPaymentHistory.objects.filter(user=request.user.id).order_by("id"), 10)
            try:
                p_list = paginator.page(page)
            except PageNotAnInteger:
                p_list = paginator.page(1)
            except EmptyPage:
                p_list = paginator.page(paginator.num_pages)

            for p in p_list:
                data.append(serializable.serializable_payment_history(p))
            return apiresponse.response_paginated(p_list, data, request)
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


def order_payment_total(request):
    """
    REQUEST GET

    RESPONSE
    {
        "status": true,
        "data": {
            "total_amount": 10
        },
        "message": "string"
    }
    """
    try:
        if not request.user.is_anonymous:
            data = ProductPaymentHistory.objects.filter(user=request.user.id).aggregate(total_amount=Sum('amount'))
            if data.get('total_amount') is None:
                data['total_amount'] = 0
            return apiresponse.httpResponse(True, {"total_amount": data.get('total_amount')}, "success")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        print(traceback.format_exc())
        return apiresponse.httpResponse(False, None, "Something wend wrong! Try again")


def user_fee(request):
    data = []
    for fee in ProductOrderDeliveryFee.objects.all():
        data.append({
            "charge": float(fee.charge),
            "amount_max": float(fee.amount_max),
            "amount_min": float(fee.amount_min),
            "amount_type": fee.amount_type
        })
    return apiresponse.httpResponse(True, data, "success")

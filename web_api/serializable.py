import time

from django.db.models import Avg, Count

from web_api.models_product import ProductsReview
from web_api.models_product_order import ProductsOrderItems


def serializable_coupon(ca):
    data = {
        "id": ca.id,
        "code": ca.code,
        "amount_order": ca.amount_order,
        "amount_discount": ca.amount_discount,
        "coupon_type": ca.coupon_type,
        "expired": ca.expired,
        "shop": ca.user_id
    }
    return data


def serializable_name(full_name):
    try:
        if full_name is not None:
            first, last = full_name.split(" ", 1)
            return [first, last]
        return ["", ""]
    except:
        return [full_name, ""]


def serializable_category(ca):
    data = {
        "id": ca.id,
        "name": ca.name,
        "parent": ca.parent,
        "display": ca.display,
        "image": ca.image,
        "child": []
    }
    return data


def serializable_user_seller(user):
    if user is not None and user.id is not None:
        data = {
            "id": user.id,
            "shop_name": user.first_name,
            "shop_number": user.number,
            "seller_tax": user.seller_tax,
            "email": user.email,
            "phone": user.phone,
            "image": user.image,
            "address": user.get_address(False)
        }
        return data
    else:
        return None


def serializable_product(p):
    image = []
    if p.image1 is not None:
        image.append(p.image1)
    if p.image2 is not None:
        image.append(p.image2)
    if p.image3 is not None:
        image.append(p.image3)
    if p.image4 is not None:
        image.append(p.image4)

    data = {
        "id": p.id,
        "category": serializable_category(p.category),
        "shop": serializable_user_seller(p.shop),
        "name": p.name,
        "price": p.price,
        "price_new": p.price_new,
        "discount": p.discount,
        "weight": p.weight,
        "available": p.available,
        "image": image,
        "display": p.display,
        "kayi_shop": p.shop.is_superuser,
        "descriptions": p.descriptions_html,
        "updated": int(time.mktime(p.updated.timetuple())) * 1000,
        "created": int(time.mktime(p.created.timetuple())) * 1000,
        "related_product": [],
        "review": [],
    }
    return data


def serializable_product_related(p):
    revi = ProductsReview.objects.filter(product=p.id).aggregate(Avg('starts'), Count('id'))
    data = {
        "id": p.id,
        "name": p.name,
        "shop": serializable_user_seller(p.shop),
        "price": p.price,
        "price_new": p.price_new,
        "discount": ((p.price - p.price_new) / p.price) * 100,
        "weight": p.weight,
        "image": p.image1,
        "display": p.display,
        "kayi_shop": p.shop.is_superuser,
        "stars": revi['starts__avg'],
        "total_review": revi['id__count'],
    }
    return data


def serializable_product_review(pr):
    data = {
        'starts': pr.starts,
        'comment': pr.comment,
        'user_info': pr.user_info
    }
    return data


def serializable_product_advertising(pr):
    data = {
        'type': pr.type,
        'type_id': pr.type_id,
        'image': pr.image,
        'text': pr.text,
        'updated': int(time.mktime(pr.updated.timetuple())) * 1000,
        'created': int(time.mktime(pr.created.timetuple())) * 1000
    }
    return data


def serializable_product_order(po):
    pickup_datetime = None
    if po.picup_datetime is not None:
        pickup_location = int(time.mktime(po.picup_datetime.timetuple())) * 1000
    data = {
        'id': po.id,
        'coupon': None,
        'status': po.status,
        'is_payment': po.is_payment,
        'tips': po.tips,
        'delivery_amount': po.delivery_amount,
        'delivery_method': po.delivery_method,
        'pickup_location': po.picup_location,
        'pickup_datetime': pickup_datetime,
        'tax_amount': po.tax_amount,
        'amount': round(po.amount, 2),
        'total_amount': po.total_amount,
        'new_total_amount': po.get_new_amount(),
        'phone_number': po.get_phone_number(),
        'address': po.get_address(False),
        'products': serializable_product_order_products(ProductsOrderItems.objects.filter(product_order=po.id)),
        'created': int(time.mktime(po.created.timetuple())) * 1000
    }
    if po.voucher is not None:
        data['coupon'] = {
            'code': po.voucher.code,
            'amount_order': po.voucher.amount_order,
            'amount_discount': po.voucher.amount_discount,
            'coupon_type': po.voucher.coupon_type,
            'expired': po.voucher.expired
        }
    return data


def serializable_product_order_products(pop):
    data = []
    for p in pop:
        data.append({
            "id": p.product.id,
            "title": p.product.name,
            "product_price": p.product_price,
            "product_price": p.product_price,
            "quantity": p.product_quantity,
            "image": p.product.image1,
            "provider": serializable_user_seller(p.product.shop),
            "status": p.status,
            "other": p.other,
        })
    return data


def serializable_payment(p):
    data = {
        "id": p.id,
        "amount": p.amount,
        "order_id": p.product_order,
        "payment_type": p.payment_type,
        "payment_request": p.payment_request,
        "payment_response": p.payment_response,
        "comment": p.comment,
        'created': int(time.mktime(p.created.timetuple())) * 1000
    }
    return data


def serializable_payment_history(p):
    data = {
        "id": p.id,
        "amount": p.amount,
        "order_id": p.order_id,
        "order_invoice": p.order_invoice,
        "debit_credit": p.debit_credit,
        "comment": p.comment,
        'created': int(time.mktime(p.created.timetuple())) * 1000
    }
    return data


def serializable_support_message(sm, support_user):
    data = {
        'id': sm.id,
        'username': sm.username,
        'sender_user': sm.sender_user,
        'support_user': {"id": support_user.id, "name": support_user.get_full_name(), "image": support_user.image},
        'message': sm.message,
        'image': sm.image,
        'is_replay': sm.is_replay,
        'is_sender': sm.is_sender,
        'created': sm.created,
    }
    return data

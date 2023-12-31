import base64
import json
import os
import re

import boto3
from django.db import connection
from django.db.models import Q
from oauth2_provider.models import get_application_model

from config import settings
from web_api.models_product import Categories, ProductsWeight, ZipCodes, ShopZipcodes
from web_api.models_product_order import OrderStatus, ProductOrderDeliveryFee, DeliveryFeeType


def get_application_user_id():
    try:
        data = get_application_model().objects.filter(name='TheKayi')
        if len(data) > 0:
            return [0].user_id
    except Exception as ex:
        print(str(ex))
    return -1


def get_current_user_id(user):
    try:
        if user.is_superuser:
            data = get_application_model().objects.filter(name='TheKayi')
            if len(data) > 0:
                return data[0].user_id
        else:
            return user.id
    except:
        print("error")
    return -1


def get_sequence_category(zipcode=None, request=None):
    all_category_date = []
    try:
        if request is not None:
            if request.GET.get('type', '') == 'new':
                all_category = Categories.objects.filter().order_by('-created')[:6]
            elif request.GET.get('type', '') == 'sale':
                all_category = Categories.objects.all().order_by('-created')[:6]
            elif request.GET.get('type', '') == 'top':
                all_category = Categories.objects.all().order_by('-created')[:6]
            else:
                all_category = Categories.objects.all()
        elif zipcode is None:
            all_category = Categories.objects.all()
        elif zipcode == 0:
            all_category = Categories.objects.all()
        else:
            zipcode = "(" + str(zipcode) + ")"
            all_category = Categories.objects.filter(Q(zipcode__contains="(0)") | Q(zipcode__contains=zipcode))
        for c in all_category:
            if c.parent is None:
                data1 = []
                for c1 in all_category:
                    if c1.parent == c.id:
                        data1.append({
                            "id": c1.id,
                            "name": c1.name,
                            "parent": c1.parent,
                            "display": c1.display,
                            "image": c1.image,
                            "delivery_flag": c1.delivery_flag,
                            "zipcode": zip_string_to_array(c1.zipcode),
                            "cities": category_zip_string_to_array(c1.zipcode),
                            "child": []
                        })
                all_category_date.append({
                    "id": c.id,
                    "name": c.name,
                    "parent": c.parent,
                    "display": c.display,
                    "image": c.image,
                    "delivery_flag": c.delivery_flag,
                    "zipcode": zip_string_to_array(c.zipcode),
                    "cities": category_zip_string_to_array(c.zipcode),
                    "child": data1
                })
    except Exception as ex:
        print(str(ex))
        all_category_date = all_category_date
    return all_category_date


def cites_zipcode():
    data = {}
    ret_data = []
    for zp in ZipCodes.objects.all().order_by("state"):
        if data.get(zp.city) is None:
            data[zp.city] = [zp.id]
        else:
            data[zp.city].append(zp.id)
    for d in data.keys():
        ret_data.append({"city": d, "zipcodes": data[d], "zipcodes_str": ','.join(map(str, data[d]))})
    return ret_data


def shop_current_city(user):
    all_city = cites_zipcode()
    selected_city = []
    for c in ShopZipcodes.objects.filter(shop=user).order_by().values_list('zipcode__city').distinct():
        for city in all_city:
            if city['city'] == c[0]:
                selected_city.append(city)
    return {'zips': all_city, 'sel': selected_city}


def product_current_zipcode(shop_user):
    selected_city = []
    for c in ShopZipcodes.objects.filter(shop=shop_user):
        selected_city.append(c.zipcode.zipcode)
    return selected_city


def category_zip_string_to_array(zip):
    selected_city = []
    zip = str(zip).replace("(", "")
    zip = str(zip).replace(")", "")
    zip = zip.replace(" ", "")
    if zip == "":
        zip = "0"
    zips = [int(x) for x in zip.split(",")]
    if 0 in zips:
        with connection.cursor() as cursor:
            cursor.execute("select distinct(city) from zip_code")
            for dd in cursor.fetchall():
                selected_city.append(dd[0])
    else:
        for dd in ZipCodes.objects.filter(id__in=zips).values_list('city', flat=True).distinct():
            selected_city.append(dd)
    return selected_city


def zip_string_to_array(zip):
    zip = str(zip).replace("(", "")
    zip = str(zip).replace(")", "")
    zip = zip.replace(" ", "")
    if zip == "":
        zip = "0"
    return [int(x) for x in zip.split(",")]


def zip_object_to_string(strs):
    data = []
    zip = zip_string_to_array(strs)
    for z in zip:
        if z == 0:
            return "(0)"
        data.append("(" + str(z) + ")")
    return ",".join(data)


def get_sequence_weight():
    all_weight_date = []
    try:
        all_weight = ProductsWeight.objects.all()
        for c in all_weight:
            if c.parent is None:
                data1 = []
                for c1 in all_weight:
                    if c1.parent == c.id:
                        data1.append({
                            "id": c1.id,
                            "name": c1.name,
                            "parent": c1.parent,
                            "child": []
                        })
                all_weight_date.append({
                    "id": c.id,
                    "name": c.name,
                    "parent": c.parent,
                    "child": data1
                })
    except Exception as ex:
        print(str(ex))
        all_weight_date = all_weight_date
    return all_weight_date


def image_save_from_data(code_data, subdir, file_name):
    try:

        # Path name#
        path_temp = "/image/temp/" + file_name
        path_s3 = (subdir + "/" + file_name)

        # Create temp path#
        if not os.path.exists("/image/temp/"):
            os.makedirs("/image/temp/")
        base64_data = re.sub('^data:image/.+;base64,', '', code_data)
        byte_data = base64.b64decode(base64_data)

        # Save file as temp file#
        fh = open(path_temp, "wb")
        fh.write(byte_data)
        fh.close()

        # Save file upload to S3#
        if upload_to_aws(path_temp, path_s3):
            os.remove(path_temp)
            return "https://thekayi.s3.us-east-2.amazonaws.com/" + path_s3
        os.remove(path_temp)
        return None
    except Exception as ex:
        print(ex)
        return None


def upload_to_aws(local_file, s3_file):
    try:
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_STORAGE_KEY_ID, aws_secret_access_key=settings.AWS_STORAGE_KEY_TOKEN)
        s3.upload_file(local_file, settings.AWS_STORAGE_BUCKET_NAME, s3_file)
        return True
    except Exception as ex:
        print(str(ex))
        return False


def delete_to_aws(s3_file):
    try:
        s3_file = str(s3_file).replace("https://thekayi.s3.us-east-2.amazonaws.com/", "")
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_STORAGE_KEY_ID, aws_secret_access_key=settings.AWS_STORAGE_KEY_TOKEN)
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_file)
        return True
    except Exception as ex:
        print(str(ex))
        return False


def send_active_mail(user):
    return True


def send_account_delete_mail(user):
    return True


def search_dic(dic, key):
    val = dic.get(key, None)
    if val is None:
        return False
    return True


def is_valid_email(email):
    import re
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
    if match == None:
        return False
    return True


def serializable_address(address, is_text=True):
    try:
        if is_text:
            temp1 = json.loads(address)
            temp2 = []
            if temp1.get('address') is not None and temp1.get('address') != '':
                temp2.append(temp1.get('address'))
            if temp1.get('city') is not None and temp1.get('city') != '':
                temp2.append(temp1.get('city'))
            if temp1.get('state') is not None and temp1.get('state') != '':
                temp2.append(temp1.get('state'))
            if temp1.get('zip') is not None and temp1.get('zip') != '':
                temp2.append(str(temp1.get('zip')))
            return ', '.join(temp2)
        return json.loads(address)
    except Exception as ex:
        print(str(ex))
        if is_text:
            return ''
        return None


def get_status(status):
    if status == OrderStatus.PAYMENT_PENDING.name:
        return OrderStatus.PAYMENT_PENDING.value[1]
    elif status == OrderStatus.ORDERED.value[1]:
        return OrderStatus.ORDERED.value[1]
    elif status == OrderStatus.PENDING.name:
        return OrderStatus.PENDING.value[1]
    elif status == OrderStatus.PROCESSING.name:
        return OrderStatus.PROCESSING.value[1]
    elif status == OrderStatus.SHIPPING.name:
        return OrderStatus.SHIPPING.value[1]
    elif status == OrderStatus.TRANSIT.name:
        return OrderStatus.TRANSIT.value[1]
    elif status == OrderStatus.COMPLETE.name:
        return OrderStatus.COMPLETE.value[1]
    else:
        return status


class OrderItemValue:
    def __init__(self, product=None, order_body=[]):
        self.comment = None
        self.product = None
        self.quantity = 0
        self.price = 0
        for ob1 in order_body:
            if product.id == ob1.product:
                self.product = product
                self.comment = ob1.other
                self.quantity = ob1.product_quantity
                self.price = round(product.price_new * ob1.product_quantity, 2)
                break


def page_range(page, last, span=10):
    return range(max(min(page - (span - 1) // 2, last - span + 1), 1), min(max(page + span // 2, span), last) + 1)


def delivery_fee(amount=0):
    for i in ProductOrderDeliveryFee.objects.all().order_by("amount_min"):
        if i.amount_min <= amount <= i.amount_max:
            if i.amount_type == DeliveryFeeType.FIX_AMOUNT.name:
                return round(i.charge, 2)
            else:
                return round((i.charge / 100) * amount, 2)
    return 0

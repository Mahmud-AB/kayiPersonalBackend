import random

from web_api import serializable
from web_api.defs.common_defs import image_save_from_data, delete_to_aws, get_current_user_id
from web_api.forms import ProductForm
from web_api.models import Users
from web_api.models_product import Products, ProductsReview, ProductsAdvertising, ZipCodes, ShopPickUpStore
from web_api.view import apiresponse


def review_add(request, product_id=0):
    try:
        if not request.user.is_anonymous:
            pr = ProductsReview.objects.filter(product=product_id, user_id=request.user.id)
            if len(pr) > 0:
                pr[0].starts = int(request.POST.get('starts', '5'))
                pr[0].comment = request.POST.get('comment', '')
                pr[0].user_info = {'id': request.user.id, 'fullname': request.user.get_full_name(), 'image': request.user.image}
                pr[0].save()
            else:
                pr = ProductsReview()
                pr.product = product_id
                pr.starts = int(request.POST.get('starts', '5'))
                pr.comment = request.POST.get('comment', '')
                pr.user_id = request.user.id
                pr.user_info = {'id': request.user.id, 'fullname': request.user.get_full_name(), 'image': request.user.image}
                pr.save()
            return apiresponse.httpResponse(True, None, "Review add successfully")
        else:
            return apiresponse.httpResponse(False, None, "Please sign in")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def save_product(request, id=0):
    try:
        if request.user.is_superuser or request.user.is_staff:
            message = []
            form = ProductForm(request.POST)
            if not form.is_valid():
                for m in form.errors:
                    message.append(str(m.title()) + ": " + str(form.errors[m][0]))
                return apiresponse.httpResponse(False, None, message)
            p = form.save(commit=False)
            p.discount = ((p.price - p.price_new) / p.price) * 100
            if p.discount > 0:
                from django.utils import timezone
                p.discount_created = timezone.now()

            if p.weight is None:
                p.weight = "{}"
            if p.descriptions is None:
                p.descriptions = ""
            if p.descriptions_html is None:
                p.descriptions_html = ""

            if id == 0:
                p.shop = Users.objects.get(pk=get_current_user_id(request.user))
                p.save()
                product = p
            else:
                product = Products.objects.get(pk=id)
                product.name = p.name
                product.price = p.price
                product.category_id = p.category_id
                product.price_new = p.price_new
                product.discount = p.discount
                product.discount_created = p.discount_created
                product.available = p.available
                product.weight = p.weight
                product.descriptions = p.descriptions
                product.descriptions_html = p.descriptions_html
                product.display = p.display
                product.save()
            return apiresponse.httpResponse(True, product.id, ["success"])
        else:
            return apiresponse.httpResponse(False, None, ["You are not proper user to add category"])
    except Exception as ex:
        print(ex)
        return apiresponse.httpResponse(False, None, ["Something wend wrong"])


def save_product_advertising(request):
    try:
        if request.user.is_superuser:
            pa = ProductsAdvertising.objects.create(
                type=request.POST.get('a_type', ''),
                type_id=int(request.POST.get('a_type_id', '0')),
                image='',
                text=''
            )
            file_name = "pa-" + str(pa.id) + ".png"
            img = image_save_from_data(request.POST.get('a_image', ''), 'product_banner', file_name)
            if img is not None:
                pa.image = img
                pa.save()
                return apiresponse.httpResponse(True, pa.id, "success")
            else:
                pa.delete()
                return apiresponse.httpResponse(False, None, "Invalid image")
        else:
            return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(ex)
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def delete_product_advertising(request):
    try:
        if request.user.is_superuser:
            pa = ProductsAdvertising.objects.get(pk=int(request.POST.get('id', '0')))
            pa.delete()
            delete_to_aws(pa.image)
            return apiresponse.httpResponse(True, pa.id, "success")
        else:
            return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(ex)
        return apiresponse.httpResponse(False, None, "Something wend wrong")


def save_image(request):
    try:
        p = Products.objects.get(pk=int(request.POST['product_id']))
        if request.user.is_superuser is False:
            if p.shop.id != request.user.id:
                return apiresponse.httpResponse(False, None, ["Invalid user"])

        file_name = "p-" + str(p.id) + "-" + str(request.POST['image_index']) + "-" + str(random.randint(1, 10000)) + ".png"
        img = image_save_from_data(request.POST['image'], 'product', file_name)
        if img is not None:
            if int(request.POST['image_index']) == 1:
                p.image1 = img
            elif int(request.POST['image_index']) == 2:
                p.image2 = img
            elif int(request.POST['image_index']) == 3:
                p.image3 = img
            elif int(request.POST['image_index']) == 4:
                p.image4 = img
            p.save()
            return apiresponse.httpResponse(True, None, ["Success"])
        return apiresponse.httpResponse(False, None, ["Invalid image"])
    except Exception as ex:
        print(ex)
        return apiresponse.httpResponse(False, None, ["Product not found or Something went wrong"])


def product_image_delete(request, product_id=0, image_seq=4):
    p = Products.objects.get(pk=product_id)
    if request.user.is_superuser is False:
        if p.shop.id != request.user.id:
            return apiresponse.httpResponse(False, None, ["Invalid user"])
    if image_seq == 1:
        p.image1 = p.image2
        p.image2 = p.image3
        p.image3 = p.image4
        p.image4 = None
    if image_seq == 2:
        p.image2 = p.image3
        p.image3 = p.image4
        p.image4 = None
    if image_seq == 3:
        p.image3 = p.image4
        p.image4 = None
    if image_seq == 4:
        p.image4 = None
    p.save()
    return apiresponse.httpResponse(True, {}, 'success')


def get_product_advertising(request):
    p_list = ProductsAdvertising.objects.all().order_by("-updated")[:6]
    data = []
    for a in p_list:
        data.append(serializable.serializable_product_advertising(a))
    return apiresponse.httpResponse(True, data, 'success')


def zipcode(request):
    data = []
    for zp in ZipCodes.objects.all().order_by("state"):
        data.append({
            'state': zp.state,
            'city': zp.city,
            'zip': zp.id,
        })
    return apiresponse.httpResponse(True, data, "Success")


def zipcode1(request):
    data = {}
    for zp in ZipCodes.objects.all().order_by("state"):
        if data.get(zp.state) == None:
            data[zp.state] = {zp.city: [zp.id]}
        else:
            if data.get(zp.state).get(zp.city) == None:
                data.get(zp.state)[zp.city] = [zp.id]
            else:
                data.get(zp.state)[zp.city].append(zp.id)

    ret_data = []
    for d in data.keys():
        ret_city = []
        for dd in data[d].keys():
            ret_city.append({'city_name': dd, 'zip_codes': data[d][dd]})
        ret_data.append({"state_name": d, 'cities': ret_city})
    return apiresponse.httpResponse(True, ret_data, "Success")


def zipcode_find(request):
    data = []
    for zp in ZipCodes.objects.all().order_by("id"):
        if str(zp.zipcode).startswith(request.GET.get("q")):
            data.append(int(zp.zipcode))

    return apiresponse.httpResponse(True, data, "Success")


def pickup_location(request, shop_id):
    data = []
    for pu in ShopPickUpStore.objects.filter(shop_id=shop_id).order_by("id"):
        if pu.is_active:
            data.append(pu.address)
    return apiresponse.httpResponse(True, data, "Success")

from django.http.multipartparser import MultiPartParser
from django.views import View

from web_api.defs import common_defs
from web_api.defs.common_defs import image_save_from_data, zip_string_to_array, category_zip_string_to_array
from web_api.forms import CategoriesForm
from web_api.models_product import Categories
from web_api.view import apiresponse


class CategoryView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get("q") is None:
            if request.zipcode > 0:
                return apiresponse.httpResponse(True, common_defs.get_sequence_category(zipcode=request.zipcode, request=request), "success")
            return apiresponse.httpResponse(True, common_defs.get_sequence_category(request=request), "success")
        else:
            data = []
            for c in Categories.objects.filter(name__icontains=request.GET.get("q"))[:10]:
                data.append({
                    "id": c.id,
                    "name": c.name,
                    "parent": c.parent,
                    "display": c.display,
                    "image": c.image,
                    "zipcode": zip_string_to_array(c.zipcode),
                    "cities": category_zip_string_to_array(c.zipcode),
                    "delivery_flag": c.delivery_flag
                })
            return apiresponse.httpResponse(True, data, "success")

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                form = CategoriesForm(request.POST)
                ca = form.save(commit=False)
                ca.display = True
                # ca.save()

                data = {
                    "id": ca.id,
                    "name": ca.name,
                    "parent": ca.parent,
                    "display": ca.display,
                    "image": ca.image,
                    "child": []
                }
                return apiresponse.httpResponse(True, data, "success")
            return apiresponse.httpResponse(False, None, "You are not proper user to add category")
        except:
            return apiresponse.httpResponse(False, None, "Something wend wrong")

    def put(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                form = MultiPartParser(request.META, request, request.upload_handlers).parse()[0]
                ca2 = Categories.objects.get(id=int(form.get('id')))

                if form.get('name') != "":
                    ca2.name = form.get('name')

                if form.get('image') != "":
                    ca2.image = form.get('image')

                if form.get('display') != "" and form.get('display') == 'true':
                    ca2.display = True
                elif form.get('display') != "" and form.get('display') == 'false':
                    ca2.display = False

                # ca2.save()
                data = {
                    "id": ca2.id,
                    "name": ca2.name,
                    "parent": ca2.parent,
                    "display": ca2.display,
                    "image": ca2.image,
                    "child": []
                }
                return apiresponse.httpResponse(True, data, "success")
            return apiresponse.httpResponse(False, None, "You are not proper user to add category")
        except:
            return apiresponse.httpResponse(False, None, "Category not found")


def categories_save(request):
    try:
        message = []
        if request.user.is_superuser:
            category_id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            parent = request.POST.get('parent', '')
            image = request.POST.get('image', '')
            display = request.POST.get('display', '')
            delivery_flag = True
            zipcode = common_defs.zip_object_to_string(request.POST.get('zipcode', ''))

            if category_id is None or category_id is '':
                category_id = None
            else:
                category_id = int(category_id)
            if name is None or name is '':
                return apiresponse.httpResponse(False, None, "Please enter category name")
            else:
                name = str(name)
            if parent is None or parent is '':
                parent = None
            else:
                parent = int(parent)
            if display is not None and display is 'true':
                display = True
            else:
                display = False
            if request.POST.get('delivery_flag') != "" and request.POST.get('delivery_flag') == 'false':
                delivery_flag = False

            if category_id is None:
                cat = Categories()
                cat.name = name
                cat.parent = parent
                cat.display = True
                cat.zipcode = zipcode
                cat.delivery_flag = delivery_flag
                cat.image = 'https://static.thenounproject.com/png/194055-200.png'
                cat.save()

                img_path = image_save_from_data(image, 'category', ("c-" + str(cat.id) + ".png"))
                if img_path is None:
                    cat.delete()
                    return apiresponse.httpResponse(False, None, "Invalid Image")
                else:
                    cat.image = img_path
                    cat.save()
                if parent is not None:
                    par = Categories.objects.filter(parent=parent)[1]
                    par.updated = cat.created
                    par.save()
                return apiresponse.httpResponse(True, {"id": cat.id, "name": cat.name, "parent": cat.parent, "display": cat.display, "image": cat.image, "child": []}, "Successfully added")
            else:
                cat = Categories.objects.get(pk=category_id)
                img_path = image_save_from_data(image, 'category', ("c-" + str(cat.id) + ".png"))
                if parent is not None:
                    cat.parent = parent
                if name is not None:
                    cat.name = name
                if display is not None:
                    cat.display = True
                if img_path is not None:
                    cat.image = img_path
                cat.zipcode = zipcode
                cat.delivery_flag = delivery_flag
                cat.save()
                return apiresponse.httpResponse(True, {"id": cat.id, "name": cat.name, "parent": cat.parent, "display": cat.display, "image": cat.image, "child": []}, "Successfully added")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Something went wrong")


def categories_delete(request):
    try:
        message = []
        if request.user.is_superuser:
            category_id = request.GET.get('id', '0')
            cat = Categories.objects.get(pk=int(category_id))
            cat.delete()
            return apiresponse.httpResponse(True, None, "Successfully added")
        return apiresponse.httpResponse(False, None, "You are not proper user to add category")
    except Exception as ex:
        print(str(ex))
        return apiresponse.httpResponse(False, None, "Category not found")

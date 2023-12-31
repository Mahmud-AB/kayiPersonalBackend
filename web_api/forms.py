from django import forms

from web_api.models import Users
from web_api.models_product import Categories, Products
from web_api.models_product_order import ProductCoupon


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'parent', 'display', 'image']


class UsersForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'password']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['category', 'name', 'price', 'price_new', 'weight', 'available', 'display', 'descriptions', 'descriptions_html']


class CouponForm(forms.ModelForm):
    code = forms.CharField(required=True)
    amount_order = forms.FloatField(required=True)
    amount_discount = forms.FloatField(required=True)
    any_order = forms.CharField(required=False)
    user_id = forms.IntegerField(required=True)
    expired = forms.DateTimeField(required=True, input_formats=["%Y-%m-%d %H:%M:%S"])
    comment = forms.CharField(required=False)

    class Meta:
        model = ProductCoupon
        fields = ['code', 'amount_order', 'amount_discount', 'user_id', 'expired', 'comment']

import jsonfield
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from web_api.models import Users


class ZipCodes(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    tax = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "zip_code"


class ShopZipcodes(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    zipcode = models.ForeignKey(ZipCodes, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shop_zipcodes"


class ShopPickUpStore(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shop_pickup_store"


class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    parent = models.IntegerField(null=True, blank=True)
    display = models.BooleanField(default=True)
    image = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    zipcode = models.TextField(default="(0)")
    delivery_flag = models.BooleanField(default=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_categories"


class CategoriesMessage(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=50)

    class Meta:
        db_table = "product_categories_message"


class Products(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)
    shop = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, default="")
    price = models.FloatField(default=0)
    price_new = models.FloatField(default=0)
    discount = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], default=0)
    discount_created = models.DateTimeField(null=True, blank=True, default=None)
    weight = jsonfield.JSONField()
    available = models.IntegerField(default=1)
    image1 = models.CharField(max_length=250, null=True, blank=True)
    image2 = models.CharField(max_length=250, null=True, blank=True)
    image3 = models.CharField(max_length=250, null=True, blank=True)
    image4 = models.CharField(max_length=250, null=True, blank=True)
    tags = models.CharField(max_length=250, null=True, blank=True)
    counter_visit = models.IntegerField(default=0)
    counter_order = models.IntegerField(default=0)
    display = models.BooleanField(default=True)
    descriptions = models.TextField(null=True, blank=True, default="")
    descriptions_html = models.TextField(null=True, blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_products"


class ProductsReview(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.IntegerField(default=0)
    starts = models.IntegerField(default=0)
    comment = models.CharField(max_length=250, null=True, blank=True)
    user_id = models.IntegerField(default=0)
    user_info = jsonfield.JSONField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_review"


class ProductsAdvertising(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=250, null=True, blank=True)
    type_id = models.IntegerField(default=0)
    image = models.TextField(default='')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_advertising"


class ProductsCard(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    product_quality = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_card"


class ProductsWhiteList(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    product_quantity = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_white_list"


class ProductsWeight(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    parent = models.IntegerField(null=True, blank=True)
    value_type = models.CharField(max_length=50)

    class Meta:
        db_table = "product_weight"

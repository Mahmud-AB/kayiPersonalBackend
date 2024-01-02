from django.contrib import admin
from web_api.defs import common_defs
from .models import Users, UsersForgotCode, HomePageItems, PushNotification, AuditLog
from .models_product_order import ProductCoupon, ProductPayment, ProductPaymentHistory, ProductsOrder, ProductsOrderItems, ProductPaymentInformation, ProductOrderDeliveryFee,OrderStatus, DeliveryFeeType
from .models_product import ZipCodes, ShopZipcodes, ShopPickUpStore, Categories, CategoriesMessage, Products, ProductsReview, ProductsAdvertising, ProductsCard, ProductsWhiteList, ProductsWeight

# Register your models here.
admin.site.register(Users)
admin.site.register(UsersForgotCode)
admin.site.register(HomePageItems)
admin.site.register(PushNotification)
admin.site.register(AuditLog)
admin.site.register(ProductCoupon)
admin.site.register(ProductPayment)
admin.site.register(ProductPaymentHistory)
admin.site.register(ProductsOrder)
admin.site.register(ProductsOrderItems)
admin.site.register(ProductPaymentInformation)
admin.site.register(ProductOrderDeliveryFee)
admin.site.register(ZipCodes)
admin.site.register(ShopZipcodes)
admin.site.register(ShopPickUpStore)
admin.site.register(Categories)
admin.site.register(CategoriesMessage)
admin.site.register(Products)
admin.site.register(ProductsReview)
admin.site.register(ProductsAdvertising)
admin.site.register(ProductsCard)
admin.site.register(ProductsWhiteList)
admin.site.register(ProductsWeight)

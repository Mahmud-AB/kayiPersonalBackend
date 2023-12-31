from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _

from web_api.defs import common_defs
from web_api.models import Users
from web_api.models_product import Products


class OrderStatus(Enum):
    CANCEL = 'CANCEL', _('Cancel')
    PAYMENT_PENDING = 'PAYMENT_PENDING', _('Payment Pending')
    ORDERED = 'ORDERED', _('Ordered')
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Acknowledged')
    SHIPPING = 'SHIPPING', _('Ready to Ship')
    TRANSIT = 'TRANSIT', _('Transit')
    COMPLETE = 'COMPLETE', _('Delivered')

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class CouponType(Enum):
    DOLLAR = 'DOLLAR', _('Dollar')
    PERCENTAGE = 'PERCENTAGE', _('Percentage')

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class DeliveryFeeType(Enum):
    FIX_AMOUNT = 'FIX_AMOUNT', _('Fix Amount')
    PERCENTAGE = 'PERCENTAGE', _('Percentage')

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ProductCoupon(models.Model):
    id = models.AutoField(primary_key=True),
    code = models.CharField(max_length=100, null=True)
    amount_order = models.FloatField(default=0)
    amount_discount = models.FloatField(default=0)
    coupon_type = models.CharField(max_length=30, choices=CouponType.choices(), default=CouponType.DOLLAR.name)
    user_id = models.IntegerField(default=0, null=True)
    expired = models.DateTimeField()
    comment = models.TextField()
    display = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_coupon"


class ProductPayment(models.Model):
    id = models.AutoField(primary_key=True),
    amount = models.FloatField(default=0)
    product_order = models.IntegerField(default=0)
    payment_type = models.CharField(max_length=250, null=True, blank=True)
    payment_request = models.TextField()
    payment_response = models.TextField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_payment"


class ProductPaymentHistory(models.Model):
    id = models.AutoField(primary_key=True),
    amount = models.FloatField(default=0, null=False)
    user = models.IntegerField(default=0, null=False)
    order_id = models.IntegerField(default=0, null=True)
    order_invoice = models.IntegerField(default=0, null=True)
    debit_credit = models.CharField(max_length=250, null=False)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_payment_history"


class ProductsOrder(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.IntegerField(default=0, null=False)
    is_admin = models.BooleanField(default=False, null=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    voucher = models.ForeignKey(ProductCoupon, on_delete=models.CASCADE, null=True)
    amount = models.FloatField(default=0, null=False)
    tax_amount = models.FloatField(default=0, null=False)
    zipcode_tax = models.FloatField(default=0, null=False)
    tips = models.FloatField(default=0, null=False)
    delivery_amount = models.FloatField(default=0, null=False)
    delivery_method = models.TextField(max_length=100, null=True, default='delivery')
    total_amount = models.FloatField(default=0, null=False)
    commission = models.FloatField(default=0, null=False)
    status = models.CharField(max_length=30, choices=OrderStatus.choices(), default=OrderStatus.PAYMENT_PENDING.name)
    is_payment = models.BooleanField(default=False)
    payment = models.ForeignKey(ProductPayment, on_delete=models.CASCADE, null=True)
    address = models.TextField(max_length=100, null=True)
    phone_number = models.TextField(max_length=100, null=True)
    picup_location = models.TextField(max_length=200, null=True)
    picup_datetime = models.DateTimeField(null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_commission(self):
        return round((self.commission / 100) * self.amount, 2)

    def get_address(self, is_text=True):
        return common_defs.serializable_address(self.address, is_text)

    def get_new_amount(self):
        if self.voucher is not None:
            if self.voucher.coupon_type == CouponType.PERCENTAGE.name:
                return round((self.total_amount - (self.voucher.amount_discount / 100 * self.total_amount)), 2)
            else:
                return round((self.total_amount - self.voucher.amount_discount), 2)
        else:
            return self.total_amount

    def get_voucher_amount(self):
        if self.voucher is not None:
            if self.voucher.coupon_type == CouponType.PERCENTAGE.name:
                return round((self.voucher.amount_discount / 100 * self.total_amount), 2)
            else:
                return round(self.voucher.amount_discount, 2)
        else:
            return self.total_amount

    def get_status(self):
        return common_defs.get_status(self.status)

    def get_phone_number(self):
        if self.phone_number is None:
            self.phone_number = self.user.phone
        if self.phone_number is not None and self.phone_number.find("+1") < 0:
            self.phone_number = "+1" + self.phone_number
        return self.phone_number

    class Meta:
        db_table = "product_order"


class ProductsOrderItems(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    product_order = models.IntegerField(default=0)
    product_price = models.FloatField(default=0)
    product_price_final = models.FloatField(default=0)
    product_discount = models.FloatField(default=0)
    product_quantity = models.IntegerField(default=0)
    shop = models.IntegerField(default=0, null=False)
    is_admin = models.BooleanField(default=False, null=False)
    other = models.CharField(max_length=200, null=True, default="")
    status = models.CharField(max_length=30, choices=OrderStatus.choices(), default=OrderStatus.ORDERED.name)
    created = models.DateTimeField(auto_now_add=True)

    def get_status(self):
        return common_defs.get_status(self.status)

    class Meta:
        db_table = "product_order_items"


class ProductPaymentInformation(models.Model):
    id = models.AutoField(primary_key=True),
    amount = models.FloatField(default=0)
    product_order = models.ForeignKey(ProductsOrder, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    payment_type = models.CharField(max_length=250, null=True, blank=True)
    payment_request = models.TextField()
    payment_response = models.TextField()
    is_payment = models.BooleanField(default=False)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_payment_information"


class ProductOrderDeliveryFee(models.Model):
    id = models.AutoField(primary_key=True),
    charge = models.FloatField(default=0)
    amount_max = models.FloatField(default=0)
    amount_min = models.FloatField(default=0)
    amount_type = models.CharField(max_length=30, choices=DeliveryFeeType.choices(), default=DeliveryFeeType.FIX_AMOUNT.name)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_order_delivery_fee"

from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    phone = models.CharField(max_length=20, null=True)
    number = models.CharField(max_length=100, null=True)
    address = models.TextField(max_length=100, null=True)
    balance = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    seller_tax = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    commission = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    about = models.TextField(null=True)
    image = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)

    def get_address(self, is_text=True):
        from web_api.defs import common_defs
        return common_defs.serializable_address(address=self.address, is_text=is_text)

    def get_address_json(self, ):
        from web_api.defs import common_defs
        return common_defs.serializable_address(self.address, False)

    def is_valid_email(self):
        import re
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.username)
        if match == None:
            return False
        return True

    def get_user_type(self):
        if self.is_superuser:
            return "ADMIN"
        elif self.is_staff:
            return "SELLER"
        else:
            return "BUYER"

    class Meta:
        db_table = "users"


class UsersForgotCode(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    code = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users_forgot_code"


class HomePageItems(models.Model):
    id = models.AutoField(primary_key=True)
    fix_id = models.IntegerField()
    title = models.CharField(max_length=100, null=True)
    sql = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "home_page_items"


class PushNotification(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    device_id = models.CharField(max_length=200)
    token = models.TextField()
    device_type = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "push_notification"


class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(null=True, blank=True)
    method = models.CharField(max_length=200)
    path = models.TextField()
    request_param = models.TextField()
    request_header = models.TextField()
    request_payload = models.TextField()
    response = models.TextField()
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"

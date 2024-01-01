from django.contrib import admin
from .models import Users, UsersForgotCode, HomePageItems, PushNotification, AuditLog

# Register your models here.
admin.site.register(Users)
admin.site.register(UsersForgotCode)
admin.site.register(HomePageItems)
admin.site.register(PushNotification)
admin.site.register(AuditLog)

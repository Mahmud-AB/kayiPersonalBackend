from django.urls import path, include

from web_view.view import httpresponse, views_seller

urlpatterns = [
    path('', httpresponse.index),
    path('.well-known/pki-validation/<slug:pki_str>.txt', httpresponse.pki_file),
    path('forgot-password', httpresponse.forgot_password),
    path('register/seller/', views_seller.reg),
    path('service/', include('web_view.urls_admin')),
    path('seller/', include('web_view.urls_seller')),
    path('login/', httpresponse.login, name='login'),
    path('logout', httpresponse.logout, name='login'),
]

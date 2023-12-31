from django.urls import path

from web_view.view import views_seller, httpresponse

urlpatterns = [
    path('', views_seller.index, name='index'),
    path('coupon', httpresponse.coupon, name='coupon'),
    path('register', views_seller.index, name='index'),
    path('product/list', views_seller.product_list, name='product_list'),
    path('product/add/<int:product_id>', views_seller.product_curd, name='product_list'),
    path('profile', views_seller.profile, name='profile'),
    path('zipcode/area', views_seller.zipcode_area_shop_id, name='zipcode_area'),
    path('pickup', views_seller.pickup, name='pickup'),

    path('report/filter', views_seller.report_filter, name='report_filter'),

    path('order', httpresponse.product_order, name='product_order'),
    path('order/<int:order_id>', httpresponse.product_order_view, name='product_order_view'),
    path('order/invoice/<slug:inv_id>', httpresponse.product_order_invoice, name='product_order_invoice'),
]

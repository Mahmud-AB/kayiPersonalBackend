from django.urls import path

from web_view.view import views_admin, httpresponse

urlpatterns = [
    path('', views_admin.index, name='index'),
    path('users', views_admin.users, name='users'),
    path('coupon', httpresponse.coupon, name='coupon'),
    path('active', views_admin.active, name='active'),
    path('info', views_admin.seller_info, name='seller_info'),

    path('fees', views_admin.fees, name='fees'),
    path('pickup', views_admin.pickup, name='pickup'),
    path('zipcode', views_admin.zipcode, name='zipcode'),
    # TODO path('zipcode/area', views_admin.zipcode_area, name='zipcode_area'),
    path('zipcode/area/<int:shop_id>', views_admin.zipcode_area_shop_id, name='zipcode_area'),

    path('report/filter', views_admin.report_filter, name='report_filter'),

    path('category', views_admin.product_category, name='product_category'),
    path('weight', views_admin.product_weight, name='index'),
    path('profile', views_admin.profile, name='profile'),
    path('order', httpresponse.product_order, name='product_order'),
    path('order/find', httpresponse.product_order_find, name='product_order_find'),
    path('order/<int:order_id>', httpresponse.product_order_view, name='product_order_view'),
    path('order/invoice/<slug:inv_id>', httpresponse.product_order_invoice, name='product_order_invoice'),
    path('product/advertising', views_admin.product_advertising, name='product_advertising'),

    path('product/list', views_admin.product_list, name='product_list'),
    path('product/list/<int:shop>', views_admin.product_list, name='product_list_id'),

    path('product/add/<int:product_id>', views_admin.product_curd, name='product_list'),
    path('product/list/add/<int:product_id>', views_admin.product_curd, name='product_list_shop'),
]

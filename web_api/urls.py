from django.urls import path

from web_api.view import api_product, api_order, api_product_search
from web_api.view.api_auth import CustomTokenView, BuyerReg, SellerReg, CustomLoginView, ForgotView, active_user, remove_user, social_login, update_user_account, update_user_account_password, update_user_account_email, deactivate_user, user_info, push_notification, support_message_any_user
from web_api.view.api_category import CategoryView, categories_save, categories_delete

urlpatterns = [
    path('user/reg', BuyerReg.as_view(), name='BuyerReg'),
    path('user/token', CustomTokenView.as_view(), name='CustomTokenView'),
    path('user/token/social', social_login, name='social_login'),
    path('user/login', CustomLoginView.as_view(), name='CustomLoginView'),
    path('user/push-notification', push_notification, name='push-notification'),
    path('user/support-message-any-user', support_message_any_user, name='support-message-any-user'),
    path('user/active', active_user, name='active-user'),
    path('user/deactivate', deactivate_user, name='deactivate_user'),
    path('user/info', user_info, name='user_info'),
    path('user/remove', remove_user, name='remove-user'),
    path('user/forgot', ForgotView.as_view(), name='ForgotView'),
    path('user/update', update_user_account, name='update_user_account'),
    path('user/update/email', update_user_account_email, name='update_user_account_email'),
    path('user/update/password', update_user_account_password, name='update_user_account_password'),
    path('user/reg/seller', SellerReg.as_view(), name='SellerReg'),

    path('shop/picup-location/<int:shop_id>', api_product.pickup_location, name='pickup_location'),

    path('product/categories', CategoryView.as_view(), name='CategoryView'),
    path('product/categories-save', categories_save, name='categories-save'),
    path('product/categories-delete', categories_delete, name='categories-delete'),

    path('product/zipcode', api_product.zipcode, name='zipcode'),
    path('product/zipcode1', api_product.zipcode1, name='zipcode1'),
    path('product/zipcode/find', api_product.zipcode_find, name='zipcode_find'),

    path('product/product-advertising-get', api_product.get_product_advertising, name='get_product_home'),
    path('product/product-advertising-save', api_product.save_product_advertising, name='save_product_advertising'),
    path('product/product-advertising-delete', api_product.delete_product_advertising, name='delete_product_advertising'),

    path('product/card-save', api_order.order_card_add, name='order_card_add'),
    path('product/card-delete', api_order.order_card_delete, name='order_card_delete'),
    path('product/card-product-info', api_order.order_card_product_info, name='order_card_product_info'),

    path('product/whitelist-save', api_order.order_whitelist_add, name='order_whitelist_add'),
    path('product/whitelist-delete', api_order.order_whitelist_delete, name='order_whitelist_delete'),
    path('product/whitelist-product-info', api_order.order_whitelist_product_info, name='order_whitelist_product_info'),

    path('product/user/fee', api_order.user_fee, name='user_fee'),
    path('product/order/add', api_order.order_add, name='order_add'),
    path('product/order/<int:order_id>/tips', api_order.tips, name='tips'),
    path('product/order/<int:order_id>/coupon/<slug:code>', api_order.coupon, name='coupon'),
    path('product/order/del/<int:order_id>', api_order.order_del, name='order_del'),
    path('product/order/all', api_order.order_all, name='order_all'),
    path('product/order/address-change/<int:order_id>', api_order.order_address_change, name='order_address_change'),
    path('product/order/cancel/<int:order_id>', api_order.order_cancel, name='order_cancel'),
    path('product/order/change-status/<int:order_id>', api_order.order_change_status, name='order_change_status'),
    path('product/order/order-cancel-by-shop/<int:order_id>', api_order.order_cancel_by_shop, name='order_cancel'),
    path('product/order/order-cancel-by-shop-one/<int:order_id>', api_order.order_cancel_by_shop, name='order_cancel'),
    path('product/order/payment/open-transaction/<int:order_id>', api_order.order_payment_open_transaction, name='order_payment_open_transaction'),
    path('product/order/payment/add', api_order.order_payment_add, name='order_payment_add'),
    path('product/order/payment/total', api_order.order_payment_total, name='order_payment_total'),
    path('product/order/payment/history', api_order.order_payment_history, name='order_payment_history'),

    path('product/review-add/<int:product_id>', api_product.review_add, name='review_add'),

    path('product/save/<int:id>', api_product.save_product, name='ProductSaveView'),
    path('product/save/image', api_product.save_image, name='save_image'),
    path('product/img/delete/<int:product_id>/<int:image_seq>', api_product.product_image_delete, name='product_image_delete'),

    path('product/search', api_product_search.get_product_by_search, name='get_product_by_search'),
    path('product/search/without-zipcode', api_product_search.get_product_by_search_without_zipcode, name='get_product_by_search_without_zipcode'),
    path('product/get/<int:product_id>', api_product_search.get_product_by_id, name='get_product_by_id'),
    path('product/get/home', api_product_search.get_product_home, name='get_product_home'),
    path('product/get/home/<int:home_id>', api_product_search.get_product_home_by_id, name='get_product_home_by_id'),
    path('product/get/all', api_product_search.get_product_all, name='get_product_all'),
    path('product/get/shop/all', api_product_search.get_shop_all, name='get_shop_all'),
    path('product/get/shop/<int:shop_id>/toppick', api_product_search.get_product_by_category_shop_top_pick, name='get_product_by_category_shop_top_pick'),
    path('product/get/shop/<int:shop_id>/category/items', api_product_search.get_product_by_category_shop_items, name='get_product_by_category_shop_items'),

    path('product/get/categories', CategoryView.as_view(), name='CategoryView'),
    path('product/get/categories/<int:category>/sub-cat/products', api_product_search.categories_id_sub_cat_products, name='categories_id_sub_cat_products'),
    path('product/get/by/<slug:key>', api_product_search.new_sale_top_products, name='new_sale_top_products'),

    path('product/get/category/<int:id>', api_product_search.get_product_by_category, name='get_product_by_category'),
    path('product/get/category/<int:category_id>/shop/<int:shop_id>', api_product_search.get_product_by_category_shop_ids, name='get_product_by_category_shop_ids'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('api/register/', views.register_view),
    path('api/login/', views.login_view),

    # Users
    path('api/users/', views.get_users),
    path('api/users/<int:user_id>/', views.update_user),
    path('api/users/<int:user_id>/delete/', views.delete_user),

    # Products
    path('api/products/', views.get_all_products),
    path('api/products/<int:product_id>/', views.get_product),
    path('api/products/add/', views.add_product),
    path('api/products/<int:product_id>/update/', views.update_product),
    path('api/products/<int:product_id>/delete/', views.delete_product),

    # Reviews
    path('api/products/<int:product_id>/reviews/', views.get_reviews),
    path('api/products/<int:product_id>/reviews/add/', views.add_review),
    path('api/reviews/<int:review_id>/delete/', views.delete_review),


    # Cart
    path('api/cart/', views.cart_list_create),
    path('api/cart/<int:cart_id>/', views.cart_update_delete),

    path('api/cart/<int:user_id>/add/', views.add_to_cart),
    path('api/cart/<int:user_id>/', views.get_user_cart),
    path('api/cart/<int:user_id>/delete/<int:product_id>/', views.delete_cart_item),
    path('api/cart/<int:user_id>/update/<int:product_id>/', views.update_cart_quantity),
    path('api/cart/<int:user_id>/clear/', views.clear_user_cart),


    # Wishlist
    # path('api/wishlist/', views.wishlist_list_create),
    # path('api/wishlist/<int:wishlist_id>/', views.delete_wishlist_item),
    path('api/wishlist/<int:user_id>/', views.get_user_wishlist), 
    path('api/wishlist/<int:user_id>/add/', views.add_to_wishlist),  
    # path('api/wishlist/<int:wishlist_id>/delete/', views.delete_wishlist_item),  # DELETE
    path('api/wishlist/delete/', views.delete_wishlist_item),  # DELETE



    # Orders
    path('api/orders/', views.order_list_create),
    path('api/orders/<int:order_id>/', views.order_update_delete),


    # Order Items
    path('api/orders/<int:order_id>/items/', views.get_order_items),
    path('api/order-items/<int:item_id>/', views.update_delete_order_item),
    path('api/user/<int:user_id>/orders/', views.user_orders),



#  # Product URLs
#     path('products/', views.product_list, name='product_list'),
#     path('products/<int:product_id>/', views.product_detail, name='product_detail'),
#     path('products/<int:product_id>/update/', views.update_product, name='update_product'),
    
#     # Order URLs
#     path('orders/', views.order_list, name='order_list'),
#     path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
#     path('orders/<int:order_id>/update/', views.update_order, name='update_order'),


]

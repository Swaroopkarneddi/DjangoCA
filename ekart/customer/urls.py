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

    # Wishlist
    # path('api/wishlist/', views.wishlist_list_create),
    # path('api/wishlist/<int:wishlist_id>/', views.delete_wishlist_item),
    path('api/wishlist/<int:user_id>/', views.get_user_wishlist),  # GET wishlist of a user
    path('api/wishlist/<int:user_id>/add/', views.add_to_wishlist),  # POST add to wishlist
    # path('api/wishlist/<int:wishlist_id>/delete/', views.delete_wishlist_item),  # DELETE
    path('api/wishlist/delete/', views.delete_wishlist_item),  # DELETE



    # Orders
    path('api/orders/', views.order_list_create),
    path('api/orders/<int:order_id>/', views.order_update_delete),


    # Order Items
    path('api/orders/<int:order_id>/items/', views.get_order_items),
    path('api/order-items/<int:item_id>/', views.update_delete_order_item),

    path('api/user/<int:user_id>/orders/', views.user_orders),

]

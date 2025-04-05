from django.contrib import admin
from .models import UserCustomer, Product, Order, Cart, Review, Wishlist, OrderItem

# Registering all models
admin.site.register(UserCustomer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(OrderItem)

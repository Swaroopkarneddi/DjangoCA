from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/products/', views.get_all_products, name='get_products'),
    path('api/products/add/', views.add_product, name='add_product'),
]

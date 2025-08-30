from django.urls import path
from . import views

urlpatterns = [
    # cart paths
    path('cart/', views.cart, name='cart'),
    path('add/', views.cart_add, name='cart_add'),
    path('delete', views.cart_delete, name='cart_delete'),
    path('update', views.cart_update, name='cart_update'),


    #path('cart/update/<int:cart_item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    #path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    #path('product/<int:product_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    #path('cart/increase/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    #path('cart/decrease/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),

]
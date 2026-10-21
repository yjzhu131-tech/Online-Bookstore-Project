from django.urls import path
from . import views
urlpatterns = [path('',views.catalog,name='catalog'),path('books/<int:pk>/',views.detail,name='detail'),path('bag/',views.cart,name='cart'),path('bag/add/<int:pk>/',views.add_cart,name='add_cart'),path('bag/remove/<int:pk>/',views.remove_cart,name='remove_cart'),path('checkout/',views.checkout,name='checkout'),path('orders/<uuid:number>/',views.confirmation,name='confirmation')]

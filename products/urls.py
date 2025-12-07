from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='get-products/', permanent=True)),
    # path('home/', views.home, name='home'),
    path('get-products/', views.get_prods, name='get-products'),
    path('add-product/', views.add_product, name='add-product'),
    path('product-details/<int:product_id>/', views.product_details, name='product-details'),
]
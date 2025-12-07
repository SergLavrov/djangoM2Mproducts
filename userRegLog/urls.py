from django.urls import path
from . import views
#           или можно так:
# from userRegLog import views

# <!--Через классы представлений !!! -->
urlpatterns = [
    path('register/', views.RegisterFormView.as_view(), name='register'),
    path('login/', views.LoginFormView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('get-products/', views.MainView.as_view(), name='get-products'),
]

# <!--Через обычные функции -->
# urlpatterns = [
#     path('register/', views.register_user, name='register'),
#     path('login/', views.login_user, name='login'),
#     path('logout/', views.logout_user, name='logout'),
# ]

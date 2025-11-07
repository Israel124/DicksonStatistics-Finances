from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import include

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]
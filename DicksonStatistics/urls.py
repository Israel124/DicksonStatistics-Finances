from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import include

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('vertical/', views.analisis_vertical, name='vertical'),
    path('cargar-periodos/', views.cargar_periodos, name='cargar_periodos'),
    path('guardar-analisis/', views.guardar_analisis_vertical, name='guardar_analisis'),
    path('horizontal/', views.analisis_vertical, name='horizontal'),
    path('eoaf/', views.EOAF, name='eoaf'),
    path('razones/', views.razones_financieras, name='razones'),
    path('dupont/', views.dupont, name='dupont'),
    path('directo/', views.metodo_directo, name='directo'),
    path('indirecto/', views.metodo_indirecto, name='indirecto'),
    path('liquidity/', views.liquidez, name='liquidity'),
    path('activity/', views.actividades, name= 'activity'),
    path('debt/', views.DEBT, name= 'debt'),
    path('profitability/', views.profitability, name = 'profitability'),
    path('profile/', views.perfil, name= 'profile'),
    path('settings/', views.configuracion, name= 'settings'),
]

from django import views
from django.contrib import admin
from django.urls import include, path
from principal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.visualizar_login, name='login'),
    path('registrar/', views.registrar_cadastro, name='registrar_cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('funcionario/', include('funcionario.urls')),
    path('fornecedores/', include('fornecedores.urls')),
    path('insumos/', include('insumos.urls')),
    path('relatorios/', include('relatorios.urls')),
]

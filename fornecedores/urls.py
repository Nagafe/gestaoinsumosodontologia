from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_fornecedores, name='listar_fornecedores'),
    path('buscar_fornecedores/', views.buscar_fornecedores, name='buscar_fornecedores'),
    path('cadastrar/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('editar/<int:id_fornecedor>/', views.editar_fornecedor, name='editar_fornecedor'),
    path('excluir/<int:id_fornecedor>/', views.excluir_fornecedor, name='excluir_fornecedor'),
]
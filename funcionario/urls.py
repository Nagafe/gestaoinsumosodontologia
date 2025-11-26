from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_funcionarios, name='listar_funcionarios'),
    path('buscar_funcionario/', views.buscar_funcionario, name='buscar_funcionario'),
    path('cadastrar_funcionario/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('editar_funcionario/<int:id_funcionario>/', views.editar_funcionario, name='editar_funcionario'),
    path('excluir_funcionario/<int:id_funcionario>/', views.excluir_funcionario, name='excluir_funcionario'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_insumos, name='listar_insumos'),
    path('buscar_insumos/', views.buscar_insumos, name='buscar_insumos'),
    path('cadastrar/', views.cadastrar_insumo, name='cadastrar_insumo'),
    path('editar/<int:id_insumo>/', views.editar_insumo, name='editar_insumo'),
    path('excluir/<int:id_insumo>/', views.excluir_insumo, name='excluir_insumo'),
    
    #movimentações
    path('movimentacao/entrada/', views.registrar_entrada, name='registrar_entrada'),
    path('movimentacao/saida/', views.registrar_saida, name='registrar_saida'),
    path('ajax/carregar-lotes/', views.carregar_lotes_disponiveis, name='carregar_lotes'),
]
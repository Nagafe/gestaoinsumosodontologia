from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_relatorios, name='index_relatorios'),
    path('custo-consumido/', views.relatorio_custo_consumido, name='relatorio_custo_consumido'),
    path('historico-compras/', views.relatorio_historico_compras, name='relatorio_historico_compras'),
]
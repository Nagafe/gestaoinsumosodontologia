from django.shortcuts import render, redirect
from django.db.models import Sum, F
from datetime import date, datetime, timedelta
from insumos.models import Insumo, Movimentacao

def index_relatorios(request):
    """Menu principal de relatórios"""
    if 'funcionario_id' not in request.session:
        return redirect('login')
    return render(request, 'relatorios/index.html')

def relatorio_custo_consumido(request):
    """
    RF012: Custo Total de Materiais Consumidos por Período.
    Lógica: Soma (Quantidade * Custo no Momento da Saída) de todas as saídas no período.
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')
    
    # Datas padrão (início do mês até hoje)
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    data_inicio = request.GET.get('data_inicio', inicio_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    # Filtra Movimentações do tipo SAIDA no intervalo
    # Ajustamos data_fim para pegar até o final do dia (23:59:59)
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    
    movimentacoes = Movimentacao.objects.filter(
        tipo='SAIDA',
        data_movimentacao__gte=data_inicio,
        data_movimentacao__lt=data_fim_ajustada
    ).select_related('lote__insumo', 'funcionario').order_by('-data_movimentacao')
    
    # Cálculo do Total (Soma de Qtd * Custo Unitário salvo na movimentação)
    total_consumido = 0
    for mov in movimentacoes:
        # Multiplica e soma. Se custo_unitario for None (antigos), considera 0
        custo = mov.custo_unitario or 0
        subtotal = mov.quantidade * custo
        total_consumido += subtotal
        
        # Adiciona atributo temporário para exibir na tabela
        mov.subtotal_calculado = subtotal

    return render(request, 'relatorios/custo_consumido.html', {
        'movimentacoes': movimentacoes,
        'total_consumido': total_consumido,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

def relatorio_historico_compras(request):
    """
    RF013: Histórico de Entradas de um Insumo Específico.
    Objetivo: Analisar variação de preço de compra.
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')
    
    insumos = Insumo.objects.all().order_by('nome')
    insumo_selecionado = request.GET.get('insumo')
    
    compras = []
    if insumo_selecionado:
        compras = Movimentacao.objects.filter(
            tipo='ENTRADA',
            lote__insumo_id=insumo_selecionado
        ).annotate(
            total_nota=F('quantidade') * F('custo_unitario')
        ).select_related('fornecedor', 'lote').order_by('-data_movimentacao')

    return render(request, 'relatorios/historico_compras.html', {
        'insumos': insumos,
        'insumo_selecionado': int(insumo_selecionado) if insumo_selecionado else None,
        'compras': compras
    })
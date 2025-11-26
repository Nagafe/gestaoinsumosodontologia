from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, ProtectedError
from decimal import Decimal
from django.db import transaction
from fornecedores.models import Fornecedor
from funcionario.models import Funcionario
from .models import Insumo, Lote, Movimentacao



# --- LISTAGEM E BUSCA (HTMX) ---

def listar_insumos(request):
    if 'funcionario_id' not in request.session:
        return redirect('login')
    
    # Ordena por nome para facilitar a leitura
    insumos = Insumo.objects.all().order_by('nome')
    return render(request, 'insumos/insumos.html', {'insumos': insumos})

def buscar_insumos(request):
    """
    Retorna apenas o partial da tabela filtrado (HTMX).
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    termo = request.GET.get('q', '')
    
    if termo:
        insumos = Insumo.objects.filter(
            Q(nome__icontains=termo) |
            Q(categoria__icontains=termo)
        ).order_by('nome')
    else:
        insumos = Insumo.objects.all().order_by('nome')
        
    return render(request, 'insumos/partials/tabela_insumos.html', {'insumos': insumos})
#-------------------------------------------------
# --- CRUD (CREATE, UPDATE, DELETE) de Insumos ---
# ------------------------------------------------
def cadastrar_insumo(request):
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            categoria = request.POST.get('categoria')
            unidade_medida = request.POST.get('unidade_medida')
            estoque_minimo = request.POST.get('estoque_minimo')
            
            # Validação simples
            if Insumo.objects.filter(nome__iexact=nome).exists():
                messages.error(request, 'Já existe um insumo com este nome.')
                return render(request, 'insumos/cadastrar_insumo.html', {
                    'categorias': Insumo.CATEGORIAS, 
                    'unidades': Insumo.UNIDADES
                })

            novo = Insumo(
                nome=nome,
                categoria=categoria,
                unidade_medida=unidade_medida,
                estoque_minimo=estoque_minimo,
                # Saldo e Custo nascem zerados por padrão (definido no Model)
                ativo=True if request.POST.get('ativo') else False
            )
            novo.save()
            
            messages.success(request, 'Insumo cadastrado com sucesso!')
            return redirect('listar_insumos')
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')
            
    # Passamos as opções de Select para o template
    return render(request, 'insumos/cadastrar_insumo.html', {
        'categorias': Insumo.CATEGORIAS, 
        'unidades': Insumo.UNIDADES
    })

def editar_insumo(request, id_insumo):
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    insumo = get_object_or_404(Insumo, id=id_insumo)
    
    if request.method == 'POST':
        try:
            # Captura dados editáveis
            insumo.nome = request.POST.get('nome')
            insumo.categoria = request.POST.get('categoria')
            insumo.unidade_medida = request.POST.get('unidade_medida')
            insumo.estoque_minimo = request.POST.get('estoque_minimo')
            insumo.ativo = True if request.POST.get('ativo') else False
            
            # NOTA: Não alteramos saldo_geral nem custo_medio aqui.
            # Eles são intocáveis pelo usuário, apenas o sistema mexe neles via Movimentação.
            
            insumo.save()
            messages.success(request, 'Insumo atualizado com sucesso.')
            return redirect('listar_insumos')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
            
    return render(request, 'insumos/editar_insumo.html', {
        'insumo': insumo,
        'categorias': Insumo.CATEGORIAS, 
        'unidades': Insumo.UNIDADES
    })

def excluir_insumo(request, id_insumo):
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    insumo = get_object_or_404(Insumo, id=id_insumo)
    
    try:
        nome = insumo.nome
        insumo.delete()
        messages.success(request, f'Insumo "{nome}" excluído com sucesso.')
    except ProtectedError:
        messages.error(request, 'Não é possível excluir: Este insumo já possui movimentações (Lotes/Entradas) vinculadas. Inative-o em vez de excluir.')
    except Exception as e:
        messages.error(request, f'Erro ao excluir: {e}')
        
    return redirect('listar_insumos')
# Create your views here.


#Movimentações de Insumos (Entradas e Saídas)

#--- REGISTRAR ENTRADA DE INSUMO ---
@transaction.atomic
def registrar_entrada(request):
    # 1. Segurança
    if 'funcionario_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        try:
            # 2. Coleta dados do formulário
            insumo_id = request.POST.get('insumo')
            fornecedor_id = request.POST.get('fornecedor')
            quantidade = int(request.POST.get('quantidade'))
            
            # Tratamento do valor (converte "1.200,50" para decimal)
            custo_total_str = request.POST.get('custo_total').replace('.', '').replace(',', '.')
            custo_total_compra = Decimal(custo_total_str)
            
            numero_lote = request.POST.get('numero_lote')
            data_validade = request.POST.get('data_validade')

            # Busca objetos no banco
            insumo = Insumo.objects.get(id=insumo_id)
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            funcionario = Funcionario.objects.get(id=request.session['funcionario_id'])

            # Calcula custo unitário desta nota
            custo_unitario_compra = custo_total_compra / quantidade

            # ---------------------------------------------------------
            # 3. CÁLCULO DO CUSTO MÉDIO PONDERADO (RF005)
            # ---------------------------------------------------------
            valor_estoque_atual = insumo.saldo_geral * insumo.custo_medio
            valor_desta_compra = quantidade * custo_unitario_compra
            novo_saldo_geral = insumo.saldo_geral + quantidade
            
            if novo_saldo_geral > 0:
                novo_custo_medio = (valor_estoque_atual + valor_desta_compra) / novo_saldo_geral
            else:
                novo_custo_medio = custo_unitario_compra

            # ---------------------------------------------------------
            # 4. GESTÃO DE LOTE (RF009)
            # ---------------------------------------------------------
            # Cria ou recupera o lote
            lote, created = Lote.objects.get_or_create(
                insumo=insumo,
                numero_lote=numero_lote,
                defaults={'data_validade': data_validade}
            )
            
            # Atualiza saldo do lote específico
            lote.quantidade_lote += quantidade
            lote.save()

            # ---------------------------------------------------------
            # 5. REGISTRAR HISTÓRICO
            # ---------------------------------------------------------
            Movimentacao.objects.create(
                lote=lote,
                tipo='ENTRADA',
                quantidade=quantidade,
                custo_unitario=custo_unitario_compra,
                fornecedor=fornecedor,
                funcionario=funcionario
            )

            # ---------------------------------------------------------
            # 6. ATUALIZA INSUMO (FINAL)
            # ---------------------------------------------------------
            insumo.saldo_geral = novo_saldo_geral
            insumo.custo_medio = novo_custo_medio
            insumo.save()

            messages.success(request, f'Entrada de {quantidade}x "{insumo.nome}" registrada com sucesso!')
            return redirect('listar_insumos')

        except Exception as e:
            messages.error(request, f'Erro ao registrar entrada: {e}')
    
    # GET: Carrega opções para o formulário
    insumos = Insumo.objects.filter(ativo=True).order_by('nome')
    fornecedores = Fornecedor.objects.filter(ativo=True).order_by('nome')
    
    return render(request, 'insumos/movimentacoes/entrada.html', {
        'insumos': insumos,
        'fornecedores': fornecedores
    })




#---------------------------------
#--- REGISTRAR SAÍDA DE INSUMO ---
#---------------------------------


#--- View auxiliar para carregar lotes via HTMX ---
def carregar_lotes_disponiveis(request):
    """
    View auxiliar chamada pelo HTMX.
    Retorna as <option> com os lotes que têm saldo > 0 para o insumo selecionado.
    """
    insumo_id = request.GET.get('insumo')
    
    # Filtra apenas lotes deste insumo que ainda têm produtos (saldo > 0)
    # Ordena por validade (FIFO - First In, First Out idealmente)
    lotes = Lote.objects.filter(
        insumo_id=insumo_id, 
        quantidade_lote__gt=0
    ).order_by('data_validade')
    
    return render(request, 'insumos/partials/options_lotes.html', {'lotes': lotes})


#--- View principal para registrar saída ---
#--- O Transaction Atomic garante que tudo ou nada seja salvo ---
#--- Ele funciona como uma "transação" de banco de dados ---
#--- Ele faz com que, se algum erro ocorrer durante o processo de saída,
#--- nenhuma alteração seja feita no banco, mantendo a integridade dos dados. ---

@transaction.atomic
def registrar_saida(request):
    # 1. Segurança
    if 'funcionario_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        try:
            # 2. Coleta dados
            lote_id = request.POST.get('lote')
            quantidade = int(request.POST.get('quantidade'))
            motivo = request.POST.get('motivo')
            
            # Recupera objetos
            lote = Lote.objects.get(id=lote_id)
            insumo = lote.insumo # O insumo vem através do lote
            funcionario = Funcionario.objects.get(id=request.session['funcionario_id'])

            # 3. VALIDAÇÃO DE SALDO (RF007)
            if quantidade > lote.quantidade_lote:
                messages.error(request, f'Erro: A quantidade solicitada ({quantidade}) é maior que o saldo deste lote ({lote.quantidade_lote}).')
                # Recarrega a página para tentar de novo
                return redirect('registrar_saida')

            # 4. BAIXA NO ESTOQUE (RF007)
            
            # Baixa no Lote Específico
            lote.quantidade_lote -= quantidade
            lote.save()
            
            # Baixa no Saldo Geral do Insumo
            insumo.saldo_geral -= quantidade
            insumo.save()
            
            # 5. REGISTRO DE MOVIMENTAÇÃO (RF006)
            Movimentacao.objects.create(
                lote=lote,
                tipo='SAIDA',
                quantidade=quantidade,
                custo_unitario=insumo.custo_medio,
                motivo=motivo,
                funcionario=funcionario,
                # Fornecedor fica null na saída
                # Custo Unitário não preenchemos na saída (custo é histórico de entrada), 
                # mas se quiser saber o custo "da baixa", seria insumo.custo_medio.
            )
            
            messages.success(request, f'Saída de {quantidade}x "{insumo.nome}" registrada com sucesso!')
            return redirect('listar_insumos')

        except Exception as e:
            messages.error(request, f'Erro ao registrar saída: {e}')
            
    # GET: Carrega apenas os insumos que têm saldo geral > 0
    # Não faz sentido permitir selecionar um insumo que está zerado
    insumos = Insumo.objects.filter(ativo=True, saldo_geral__gt=0).order_by('nome')
    
    return render(request, 'insumos/movimentacoes/saida.html', {'insumos': insumos})
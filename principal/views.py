from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from funcionario.models import Funcionario
from datetime import date, timedelta
from django.db.models import Sum, F
from insumos.models import Insumo, Lote

def visualizar_login(request):
    # 1. Se já logado, manda pra home
    if 'funcionario_id' in request.session:
        return redirect('home')

    # 2. Se for POST, tenta fazer o LOGIN
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            funcionario = Funcionario.objects.get(email=email)
            
            # Verifica senha e se está ativo
            if check_password(senha, funcionario.senha):
                if funcionario.ativo:
                    # SUCESSO
                    request.session['funcionario_id'] = funcionario.id
                    request.session['funcionario_nome'] = funcionario.nome
                    request.session['tipo_usuario'] = funcionario.tipo_usuario
                    return redirect('home')
                else:
                    messages.warning(request, 'Seu cadastro ainda está pendente de aprovação pelo administrador.')
            else:
                messages.error(request, 'Senha incorreta.')
        
        except Funcionario.DoesNotExist:
            messages.error(request, 'E-mail não encontrado.')

    # 3. Se for GET (ou falha no login), renderiza a tela
    return render(request, 'login.html')

def registrar_cadastro(request):
    """
    Este método recebe apenas o POST do modal de cadastro.
    Após processar, redireciona de volta para o login com uma mensagem.
    """
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email_cadastro')
        senha = request.POST.get('senha_cadastro')
        
        # Captura os dados complementares obrigatórios
        cpf = request.POST.get('cpf')
        data_nascimento = request.POST.get('data_nascimento')
        sexo = request.POST.get('sexo')
        fone = request.POST.get('fone')

        try:
            if Funcionario.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já possui cadastro.')
            elif Funcionario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
            else:
                novo_func = Funcionario(
                    nome=nome,
                    email=email,
                    senha=make_password(senha), # Criptografa
                    ativo=False, # Nasce inativo
                    cargo='PADRAO',
                    tipo_usuario='PADRAO',
                    cpf=cpf,
                    data_nascimento=data_nascimento,
                    sexo=sexo,
                    fone=fone,
                    endereco='Não informado (Cadastro Inicial)',
                    local_nascimento='Não informado'
                )
                novo_func.save()
                messages.success(request, 'Solicitação enviada! Aguarde a liberação do administrador.')
                
        except Exception as e:
            messages.error(request, f'Erro interno ao cadastrar: {str(e)}')
            
    # Redireciona sempre para a tela de login (visualizar_login)
    return redirect('login')

# Mantenha o logout e home como estavam
def logout_view(request):
    request.session.flush()
    return redirect('login')








#--- View da Home com Indicadores Gerenciais ---
def home_view(request):
    """
    Dashboard Principal: Carrega indicadores gerenciais
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')
    

    # 1. VALOR TOTAL DO ESTOQUE (RF011)
    # Soma (Saldo * Custo Médio) de todos os insumos ativos
    total_inventario = Insumo.objects.filter(ativo=True).aggregate(
        total=Sum(F('saldo_geral') * F('custo_medio'))
    )['total']
    
    # Se for None (banco vazio), vira 0
    total_inventario = total_inventario or 0 

    # 2. ALERTAS DE ESTOQUE BAIXO (RF008)
    # Filtra insumos onde Saldo <= Mínimo
    insumos_baixo_estoque = Insumo.objects.filter(
        ativo=True,
        saldo_geral__lte=F('estoque_minimo')
    ).order_by('saldo_geral')[:5] # Pega apenas os top 5 críticos

    # 3. ALERTAS DE VENCIMENTO (RF009)
    # Filtra lotes com saldo > 0 que vencem nos próximos 30 dias
    hoje = date.today()
    limite_30_dias = hoje + timedelta(days=30)
    
    lotes_vencendo = Lote.objects.filter(
        quantidade_lote__gt=0, # Só interessa lote que ainda tem produto
        data_validade__gte=hoje,
        data_validade__lte=limite_30_dias
    ).order_by('data_validade')[:5]

    context = {
        'funcionario_nome': request.session.get('funcionario_nome').split()[0],  # Primeiro nome
        'total_inventario': total_inventario,
        'insumos_baixo_estoque': insumos_baixo_estoque,
        'lotes_vencendo': lotes_vencendo
    }
    
    return render(request, 'home.html', context)
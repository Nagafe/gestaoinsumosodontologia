from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q # Importante para a busca complexa
from .models import Funcionario

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def listar_funcionarios(request):
    """
    Lista funcionários e processa a busca via HTMX.
    """
    # Se não estiver logado, chuta para o login
    if 'funcionario_id' not in request.session:
        return redirect('login')

    termo_busca = request.GET.get('q')
    
    # Ordenação padrão alfabética
    funcionarios = Funcionario.objects.all().order_by('nome')

    if termo_busca:
        # Filtra por Nome OU CPF OU Email (Case insensitive)
        funcionarios = funcionarios.filter(
            Q(nome__icontains=termo_busca) |
            Q(cpf__icontains=termo_busca) |
            Q(email__icontains=termo_busca)
        )

    context = {'funcionarios': funcionarios}

    # SE for uma requisição HTMX (apenas a tabela)
    if request.headers.get('HX-Request'):
        return render(request, 'funcionarios/partials/tabela_funcionarios.html', context)

    # SE for requisição normal (página inteira)
    return render(request, 'funcionarios/funcionarios.html', context)



def buscar_funcionario(request):
    """
    Chamada EXCLUSIVA pelo HTMX.
    Retorna apenas o HTML da tabela (partial) com os resultados filtrados.
    """
    if 'funcionario_id' not in request.session:
        # Se a sessão expirou, o HTMX pode redirecionar via cabeçalho, 
        # mas por segurança retornamos vazio ou erro.
        return redirect('login')
        
    termo = request.GET.get('q', '')
    
    if termo:
        # Filtra por Nome, CPF ou Email
        funcionarios = Funcionario.objects.filter(
            Q(nome__icontains=termo) |
            Q(cpf__icontains=termo) |
            Q(email__icontains=termo)
        ).order_by('nome')
    else:
        # Se apagar a busca, retorna todos novamente
        funcionarios = Funcionario.objects.all().order_by('nome')
        

    return render(request, 'funcionarios/partials/tabela_funcionarios.html', {'funcionarios': funcionarios})


#Cadastrar um novo funcionário

def cadastrar_funcionario(request):
    # 1. Verifica segurança (Login)
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            # 2. Captura os dados do HTML
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            
            # Dados complementares
            data_nascimento = request.POST.get('data_nascimento')
            sexo = request.POST.get('sexo')
            fone = request.POST.get('fone')
            cargo = request.POST.get('cargo')
            tipo_usuario = request.POST.get('tipo_usuario')
            endereco = request.POST.get('endereco')
            local_nascimento = request.POST.get('local_nascimento')
            
            # 3. Validações de Duplicidade
            if Funcionario.objects.filter(email=email).exists():
                messages.error(request, 'Este E-mail já está cadastrado.')
                return render(request, 'funcionarios/cadastrar_funcionario.html')
            
            if Funcionario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
                return render(request, 'funcionarios/cadastrar_funcionario.html')

            # 4. Cria o objeto (Criptografando a senha)
            novo_func = Funcionario(
                nome=nome,
                cpf=cpf,
                email=email,
                senha=make_password(senha), # Importante: Hash
                data_nascimento=data_nascimento,
                sexo=sexo,
                fone=fone,
                cargo=cargo,
                tipo_usuario=tipo_usuario,
                endereco=endereco,
                local_nascimento=local_nascimento,
                # Checkbox retorna 'on' ou None
                ativo=True if request.POST.get('ativo') else False 
            )
            
            novo_func.save()
            
            # 5. Sucesso e Redirecionamento
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('listar_funcionarios')
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {str(e)}')
            
    # Se for GET, apenas mostra o formulário vazio
    return render(request, 'funcionarios/cadastrar_funcionario.html')







def editar_funcionario(request, id_funcionario):
    # 1. Verifica login
    if 'funcionario_id' not in request.session:
        return redirect('login')
    
    # 2. Busca o funcionário (ou erro 404 se não achar)
    func = get_object_or_404(Funcionario, id=id_funcionario)
    
    if request.method == 'POST':
        try:
            # 3. Captura dados
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            
            # Validação de Duplicidade (Excluímos o próprio ID da busca)
            if Funcionario.objects.filter(email=email).exclude(id=func.id).exists():
                messages.error(request, 'Este E-mail já pertence a outro usuário.')
                return render(request, 'funcionarios/editar_funcionario.html', {'func': func})
            
            if Funcionario.objects.filter(cpf=cpf).exclude(id=func.id).exists():
                messages.error(request, 'Este CPF já pertence a outro usuário.')
                return render(request, 'funcionarios/editar_funcionario.html', {'func': func})

            # 4. Atualiza os campos
            func.nome = nome
            func.cpf = cpf
            func.email = email
            func.data_nascimento = request.POST.get('data_nascimento')
            func.sexo = request.POST.get('sexo')
            func.fone = request.POST.get('fone')
            func.cargo = request.POST.get('cargo')
            func.tipo_usuario = request.POST.get('tipo_usuario')
            func.endereco = request.POST.get('endereco')
            func.local_nascimento = request.POST.get('local_nascimento')
            func.ativo = True if request.POST.get('ativo') else False
            
            # Senha: Só atualiza se o campo não estiver vazio
            if senha and senha.strip():
                func.senha = make_password(senha)
            
            func.save()
            
            messages.success(request, f'Dados de "{func.nome}" atualizados com sucesso.')
            return redirect('listar_funcionarios')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    # GET: Renderiza o template com os dados atuais
    return render(request, 'funcionarios/editar_funcionario.html', {'func': func})




# Certifique-se de que este import está no topo, caso contrário adicione:
from django.db.models import ProtectedError

def excluir_funcionario(request, id_funcionario):
    # 1. Verificação de Segurança (Login)
    if 'funcionario_id' not in request.session:
        return redirect('login')

    if request.session.get('tipo_usuario') != 'ADMIN':
        messages.error(request, 'Apenas administradores podem excluir funcionários.')
        return redirect('listar_funcionarios')
    
    # 2. Busca o funcionário
    func = get_object_or_404(Funcionario, id=id_funcionario)
    
    # 3. Proteção: Impedir auto-exclusão
    # Se o ID do usuário logado na sessão for igual ao ID que está tentando excluir
    if func.id == request.session['funcionario_id']:
        messages.error(request, 'Segurança: Você não pode excluir seu próprio usuário enquanto está logado.')
        return redirect('listar_funcionarios')
        
    try:
        nome_removido = func.nome
        func.delete()
        messages.success(request, f'Funcionário "{nome_removido}" excluído com sucesso.')
        
    except ProtectedError:
        # Captura o erro se o funcionário tiver vínculo com movimentações de estoque (on_delete=PROTECT)
        messages.error(request, 'Não é possível excluir: Este funcionário possui movimentações de estoque registradas. Tente apenas inativá-lo.')
        
    except Exception as e:
        # Captura qualquer outro erro de banco de dados
        messages.error(request, f'Erro ao excluir: {str(e)}')
        
    return redirect('listar_funcionarios')
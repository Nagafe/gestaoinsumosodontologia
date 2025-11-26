from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, ProtectedError
from .models import Fornecedor

def listar_fornecedores(request):
    """
    Carrega a estrutura da página de gestão de fornecedores.
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')

    fornecedores = Fornecedor.objects.all().order_by('nome')
    return render(request, 'fornecedores/fornecedores.html', {'fornecedores': fornecedores})

def buscar_fornecedores(request):
    """
    MÉTODO HTMX: Retorna apenas o partial da tabela filtrado.
    """
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    termo = request.GET.get('q', '')
    
    if termo:
        fornecedores = Fornecedor.objects.filter(
            Q(nome__icontains=termo) |
            Q(cnpj__icontains=termo) |
            Q(email__icontains=termo)
        ).order_by('nome')
    else:
        fornecedores = Fornecedor.objects.all().order_by('nome')
        
    # Atenção: Retorna para o template parcial (dentro da pasta partials)
    return render(request, 'fornecedores/partials/tabela_fornecedores.html', {'fornecedores': fornecedores})




#Cadastrar Fornecedores

def cadastrar_fornecedor(request):
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            fone = request.POST.get('fone')
            email = request.POST.get('email')
            endereco = request.POST.get('endereco')
            
            # TRATAMENTO DO CNPJ: Se vier vazio string "", vira None
            cnpj = request.POST.get('cnpj')
            if not cnpj:
                cnpj = None
            
            # Valida duplicidade apenas se CNPJ foi informado
            if cnpj and Fornecedor.objects.filter(cnpj=cnpj).exists():
                messages.error(request, 'Este CNPJ já está cadastrado.')
                return render(request, 'fornecedores/cadastrar_fornecedor.html')
            

            if email and Fornecedor.objects.filter(email=email).exists():
                messages.error(request, 'Este E-mail já está cadastrado.')
                return render(request, 'fornecedores/cadastrar_fornecedor.html')
            
            novo = Fornecedor(
                nome=nome,
                fone=fone,
                email=email,
                cnpj=cnpj,
                endereco=endereco,
                ativo=True if request.POST.get('ativo') else False
            )
            novo.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('listar_fornecedores')
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')
            
    return render(request, 'fornecedores/cadastrar_fornecedor.html')




def editar_fornecedor(request, id_fornecedor):
    if 'funcionario_id' not in request.session:
        return redirect('login')
        
    fornecedor = get_object_or_404(Fornecedor, id=id_fornecedor)
    
    if request.method == 'POST':
        try:
            # Tratamento do CNPJ
            cnpj = request.POST.get('cnpj')
            if not cnpj:
                cnpj = None

            email = request.POST.get('email')
            if not email:
                email = None
                
                    
            # Valida duplicidade excluindo o próprio fornecedor da busca
            if cnpj and Fornecedor.objects.filter(cnpj=cnpj).exclude(id=fornecedor.id).exists():
                messages.error(request, 'Este CNPJ já pertence a outro fornecedor.')
                return render(request, 'fornecedores/editar_fornecedor.html', {'fornecedor': fornecedor})

            if email and Fornecedor.objects.filter(email=email).exclude(id=fornecedor.id).exists():
                messages.error(request, 'Este E-mail já pertence a outro fornecedor.')
                return render(request, 'fornecedores/editar_fornecedor.html', {'fornecedor': fornecedor})

            fornecedor.nome = request.POST.get('nome')
            fornecedor.fone = request.POST.get('fone')
            fornecedor.email = request.POST.get('email')
            fornecedor.cnpj = cnpj
            fornecedor.endereco = request.POST.get('endereco')
            fornecedor.ativo = True if request.POST.get('ativo') else False
            
            fornecedor.save()
            messages.success(request, 'Fornecedor atualizado com sucesso.')
            return redirect('listar_fornecedores')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
            
    return render(request, 'fornecedores/editar_fornecedor.html', {'fornecedor': fornecedor})




#--- Excluir Fornecedor ---
def excluir_fornecedor(request, id_fornecedor):
    if 'funcionario_id' not in request.session:
        return redirect('login')
    if request.session.get('tipo_usuario') != 'ADMIN':
        messages.error(request, 'Apenas administradores podem excluir fornecedor.')
        return redirect('listar_fornecedores')  


    fornecedor = get_object_or_404(Fornecedor, id=id_fornecedor)
    
    try:
        nome = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome}" excluído com sucesso.')
    except ProtectedError:
        messages.error(request, 'Não é possível excluir: Este fornecedor possui insumos vinculados.')
    except Exception as e:
        messages.error(request, f'Erro ao excluir: {e}')
        
    return redirect('listar_fornecedores')
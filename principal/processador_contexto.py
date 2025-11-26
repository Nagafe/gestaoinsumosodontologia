def dados_funcionario(request):
    nome = request.session.get('funcionario_nome', '')
    primeiro_nome = ''
    if nome:
        primeiro_nome = nome.split()[0]
    return {
        'funcionario_nome': primeiro_nome
    }
from django.db import models

from django.db import models

class Funcionario(models.Model):
    # Opções de Permissão
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('PADRAO', 'Padrão'),
    ]

    # Opções de Sexo
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    # Dados Pessoais
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    local_nascimento = models.CharField(max_length=100)
    fone = models.CharField(max_length=20)
    endereco = models.TextField()

    # Dados Profissionais e de Sistema
    cargo = models.CharField(max_length=50) # Ex: "Recepcionista", "Dentista"
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='PADRAO'
    )
    
    # Login Manual (Como não estamos usando AbstractUser)
    email = models.EmailField(unique=True) 
    senha = models.CharField(max_length=128)

    # Controle
    ativo = models.BooleanField(default=True) # Começa ativo? Ou 'N' se for via cadastro externo?
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
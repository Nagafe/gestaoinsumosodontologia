from django.db import models

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    fone = models.CharField(max_length=100, help_text="Telefone ou Celular", null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    cnpj = models.CharField(max_length=20, unique=True, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
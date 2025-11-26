from django.db import models
from funcionario.models import Funcionario
from fornecedores.models import Fornecedor 

class Insumo(models.Model):
    CATEGORIAS = [
        ('CONSUMIVEL', 'Consumíveis'),
        ('EPI', 'EPI'),
        ('MEDICAMENTO', 'Medicamentos'),
        ('INSTRUMENTAL', 'Instrumental')
    ]
    UNIDADES = [
        ('CAIXA', 'Caixa'),
        ('FRASCO', 'Frasco'),
        ('KIT', 'Kit'),
        ('UNIDADE', 'Unidade'),
        ('LITRO', 'Litro'),
        ('PACOTE', 'Pacote'),
        ('PAR', 'Par'),
        ('ROLO', 'Rolo')
    ]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    unidade_medida = models.CharField(max_length=20, choices=UNIDADES)
    
    # Campo para o Alerta de Estoque Baixo (RF008)
    estoque_minimo = models.IntegerField(default=5)
    saldo_geral = models.IntegerField(default=0) 
    
    # Custo Médio = Atualizado a cada nova compra (Entrada)
    custo_medio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Lote(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50)
    data_validade = models.DateField() # Essencial para RF009
    
    # Quanto deste lote específico ainda existe?
    quantidade_lote = models.IntegerField(default=0) 
    
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.insumo.nome} - Lote {self.numero_lote}"

class Movimentacao(models.Model):
    TIPO_MOVIMENTACAO = [
        ('ENTRADA', 'Entrada (Compra)'),
        ('SAIDA', 'Saída (Uso)')
    ]
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMENTACAO)
    quantidade = models.IntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Motivo: Essencial na SAÍDA (ex: "Paciente X", "Perda", "Vencimento")
    motivo = models.CharField(max_length=200, null=True, blank=True)
    
    # Rastreabilidade
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT)  
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.lote.numero_lote} - Qtd: {self.quantidade}"
SGICO - Sistema de Gestão de Insumos e Custos Odontológicos

📋 Visão Geral do Produto

O SGICO é uma aplicação web desenvolvida para solucionar o controle de estoque e a gestão de custos de uma clínica odontológica. O sistema centraliza o cadastro de materiais, fornecedores e movimentações, permitindo um cálculo preciso do Custo Médio Ponderado e oferecendo visibilidade financeira sobre o inventário.

🎯 Objetivo Principal

Fornecer ao gestor (Dr. Luiz Eduardo) e sua equipe uma ferramenta para:

Eliminar a falta inesperada de materiais.

Controlar a validade dos lotes (evitando desperdício).

Calcular automaticamente o valor monetário do estoque.

Gerar relatórios de custos consumidos por período.

🏗️ Arquitetura do Sistema

O projeto foi desenvolvido utilizando a arquitetura MTV (Model-Template-View) do Django, com separação modular por contextos de negócio (Apps).

Diagrama de Entidade e Relacionamento (Conceitual)

![Der Conceitual - SGICO.png](<principal/static/images/principal/static/images/Der Conceitual - SGICO.png>)

A estrutura de dados foi projetada para garantir a rastreabilidade total, desde a compra (Entrada) até o uso (Saída), vinculando Lotes e Validades.

Diagrama de Classes

![Diagrama de Classe (SGICO).png](<principal/static/images/principal/static/images/Diagrama de Classe (SGICO).png>)

Detalhamento técnico das classes implementadas no Django (models.py), com seus atributos e métodos principais.

🚀 Funcionalidades Principais (Casos de Uso)

O sistema cobre os 3 processos críticos da clínica, conforme detalhado nos diagramas de sequência abaixo.

1. Registrar Entrada (Compra)

Permite lançar notas fiscais, registrando o fornecedor, a quantidade, o custo de aquisição e, crucialmente, o Lote e Validade. O sistema recalcula automaticamente o Custo Médio Ponderado do insumo.

![Diagrama de Sequencia Entrada (SGICO).png](<principal/static/images/Diagrama de Sequencia 1 - Registrar Entrada (Compra) de Insumo.png>)


2. Registrar Saída (Uso)

Baixa de estoque com seleção obrigatória do Lote (Rastreabilidade). O sistema valida se há saldo suficiente e registra o motivo da saída (ex: Paciente X).

![Diagrama de Sequencia Saida (SGICO).png](<principal/static/images/Diagrama de Sequencia 2 - Registrar Saída (Uso) de Insumo.png>)

3. Consultar Custo Consumido (Relatório)

Ferramenta gerencial que soma o valor monetário de todas as saídas em um período, permitindo análise de gastos mensais.

![Consultar Custo Consumido Relatório (SGICO.png)](<principal/static/images/Diagrama de Sequencia 3 - Consultar Custo de Materiais Consumidos.png>)

💻 Tecnologias Utilizadas

Backend: Python 3, Django Framework.

Frontend: HTML5, CSS3, Bootstrap 4 (Responsivo).

Interatividade: HTMX (para buscas dinâmicas e carregamento de lotes sem refresh), SweetAlert2 (para confirmações visuais).

Banco de Dados: SQLite (Desenvolvimento) / PostgreSQL (Produção).

Ícones: FontAwesome.

📂 Estrutura do Projeto

SGICO/
├── principal/          # Configurações globais (settings, urls)
│   └── static/images/  # Diagramas e assets
├── funcionario/        # App: Gestão de Usuários e Autenticação
├── fornecedores/       # App: CRUD de Fornecedores
├── insumos/            # App: Catálogo, Lotes e Movimentações (Core)
└── relatorios/         # App: Relatórios Gerenciais e Financeiros


🔧 Como Executar o Projeto

Pré-requisitos

Python 3.10+ instalado.

Git instalado.

Passo a Passo

Clone o repositório:

git clone [https://github.com/seu-usuario/sgico.git](https://github.com/seu-usuario/sgico.git)
cd sgico


Crie e ative um ambiente virtual:

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate


Instale as dependências:

pip install django
# (Liste outras libs se houver, como django-htmx)


Execute as migrações do banco de dados:

python manage.py makemigrations
python manage.py migrate


Crie um superusuário (opcional, pois o sistema tem cadastro próprio):

python manage.py createsuperuser


Inicie o servidor:

python manage.py runserver


Acesse http://127.0.0.1:8000 no seu navegador.

🛡️ Regras de Negócio Implementadas

Segurança: Apenas usuários com perfil ADMIN podem excluir registros ou visualizar relatórios financeiros sensíveis.

Integridade: Não é permitido excluir insumos ou fornecedores que já possuam histórico de movimentação (erro tratado com ProtectedError).

Estoque Negativo: O sistema bloqueia saídas se a quantidade solicitada for maior que o saldo do lote.

Cadastro Pendente: Novos usuários cadastrados via tela de login nascem como "Inativos" e precisam de aprovação.

📄 Documentação Adicional

Documento de Visão

[Documento de Visão](<documentos/Sistema de Gestão de Insumos e Custos Odontológicos.pdf>)

Casos de Uso Descritivos

[Caso de Uso Descritivos](<documentos/Sistema de Gestão de Insumos e Custos Odontológicos.pdf>)

Autor: Nagafe de Oliveira Martins

Desenvolvido como solução para gestão odontológica.

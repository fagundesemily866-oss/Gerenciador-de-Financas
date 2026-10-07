# 💰 Gerenciador de Finanças Pessoais

Sistema moderno de gestão financeira pessoal desenvolvido em **Python** com **CustomTkinter**, arquitetado sob os padrões **MVC (Model-View-Controller)** e **DAO (Data Access Object)** com banco de dados **SQLite**.

---

##  Funcionalidades Principais

O sistema conta com 9 módulos completos acessíveis pela barra lateral retrátil:


### 📊 Dashboard
- Visualização do saldo atual.
- Receitas e despesas.
- Valores economizados.
- Limites e valores disponíveis.
- Gráfico de **Saldo & Fluxo**.
- Visualização da evolução financeira.
- Indicadores de saúde financeira.

### 🤖 Assistente IA
- Assistente financeiro integrado ao **Gemini**.
- Análise dos dados financeiros.
- Recomendações e alertas.
- Consultas rápidas sobre gastos e finanças.

### 💰 Lançamentos
- Cadastro de receitas e despesas.
- Categorias e terceiros.
- Status do lançamento.
- Data de vencimento e pagamento.
- Comprovante.
- Filtros por tipo.
- Busca por descrição.
- Exclusão de lançamentos com confirmação.

### 🎯 Metas Financeiras
- Criação de metas de reserva.
- Valor atual e valor objetivo.
- Prazo da meta.
- Aportes.
- Acompanhamento do percentual de progresso.
- Conclusão automática da meta.
- Celebração visual ao atingir 100%.
- Opções para aumentar, reduzir ou manter a meta.

### 🔮 Simulador
- Simulação de diferentes cenários financeiros.
- Cenários **Otimista, Planejado e Pessimista**.
- Simulação de corte de despesas.
- Renda extra.
- Aportes.
- Períodos de 3 meses a 5 anos.

### 📄 Relatório
- Resumo financeiro mensal.
- Comparação de receitas e despesas.
- Evolução financeira.
- Gráficos.
- Informações sobre metas.
- Exportação do relatório.

### 🤝 Terceiros
- Cadastro de clientes, fornecedores, familiares, funcionários e estabelecimentos.
- Relação com o usuário.
- Foto ou imagem personalizada.
- Logos pré-definidos.
- Edição e exclusão de terceiros.

### 🏷️ Categorias
- Cadastro de categorias.
- Categorias de receita e despesa.
- Definição de limite de orçamento.
- Indicador de utilização do limite.
- Edição e exclusão.

### 👤 Meu Perfil
- Visualização e edição dos dados do usuário.
- E-mail e senha.
- Cadastro de renda mensal.
- Foto de perfil.
- Alteração de senha.
- Perfil **Pessoal ou PJ**.
- Tema claro e escuro.

### ❤️ Saúde Financeira
- Score financeiro.
- Plano de ação personalizado.
- Acompanhamento dos gastos.
- Indicadores de limite e orçamento.

---

## 🏗️ Arquitetura do Projeto

```
text
Gerenciador-de-Financas/
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
│
├── assets/
├── data/
│
├── controllers/
│   ├── categoria_controller.py
│   ├── inteligencia_financeira_controller.py
│   ├── lancamento_controller.py
│   ├── meta_controller.py
│   ├── saude_financeira_controller.py
│   ├── terceiro_controller.py
│   └── usuario_controller.py
│
├── dao/
│   ├── categoria_dao.py
│   ├── lancamento_dao.py
│   ├── meta_dao.py
│   ├── saude_financeira_dao.py
│   ├── simulacao_dao.py
│   ├── terceiro_dao.py
│   └── usuario_dao.py
│
├── models/
│   ├── database.py
│   ├── categoria.py
│   ├── lancamento.py
│   ├── meta.py
│   ├── saude_financeira.py
│   ├── simulacao.py
│   ├── terceiro.py
│   └── usuario.py
│
├── services/
│   ├── ai_service.py
│   └── seguranca.py
│
├── views/
│   ├── assistente_ia_view.py
│   ├── categoria_view.py
│   ├── celebracao_view.py
│   ├── grafico_evolucao.py
│   ├── lancamento_view.py
│   ├── login_view.py
│   ├── menu_view.py
│   ├── meta_view.py
│   ├── notificacao_toast.py
│   ├── relatorio_view.py
│   ├── saude_financeira_view.py
│   ├── simulador_view.py
│   ├── tema.py
│   ├── terceiro_view.py
│   └── usuario_view.py
│
└── tests/
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior instalado.

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```
### Ou manualmente:
```bash
pip install customtkinter pillow python-dotenv google-genai
```

### 2. Iniciar a Aplicação
```bash
python main.py
```

---

## 🧪 Testes Automatizados

O projeto possui suíte de testes unitários e de integração cobrindo os DAOs, regras de negócio e validações:

```bash
python -m unittest discover tests
```
---

## 🗃️ Modelo de Dados

O banco possui as seguintes entidades principais:

- Usuario — dados do usuário, perfil, renda e foto.
- Categoria — categorias de receitas e despesas e seus limites.
- Lancamento — registros financeiros.
- Terceiro — clientes, fornecedores, familiares e outros contatos.
- Meta_reserva — metas e reservas financeiras.
- Saude_financeira — score e plano de ação financeiro.

*O relacionamento entre essas entidades foi desenvolvido no BRModelo.*

O limite de orçamento é armazenado diretamente na entidade Categoria.

---

## 🛠️ Tecnologias

**Tecnologia	Utilização**
- Python	Linguagem principal
- CustomTkinter	Interface gráfica
- SQLite	Banco de dados
- Pillow	Imagens e fotos de perfil
- Google Gemini	Assistente IA
- python-dotenv	Variáveis de ambiente
- unittest	Testes automatizados

*MVC + DAO	Arquitetura do sistema*

---
### Contexto acadêmico

*O projeto nasceu no PISM (plataforma apresentada pelo professor para iniciar o projeto a partir das ideias) e evoluiu durante o desenvolvimento.*

**Problema.**
- Muita gente não sabe para onde o dinheiro vai no fim do mês: os gastos ficam espalhados, não há um limite visível e só se percebe o estouro depois que ele aconteceu.

**Objetivo.**
- Oferecer um lugar único e simples para registrar receitas e despesas, encontrar os maiores gastos e acompanhar, em tempo real, o quanto do orçamento do mês já foi consumido.

---
## 👤 Personas

**Persona**      **Perfil**                          **Oque precisa**

- Helena, 21	  Empresária	         Separar as finanças do negócio e acompanhar o caixa.

- Vanessa, 35	  Dona de casa	         Controlar as despesas da casa dentro de um limite.

- Carlos, 42	  Autônomo	            Registrar receitas irregulares e ver quanto sobra.

- Ronaldo, 27	  Jovem profissional	   Criar reserva e entender para onde vai o salário

---
## Épicos do PISM

**Gerenciamento de finanças:** cadastrar receitas e despesas.
**Filtro de gastos:** filtrar por valor mínimo e período e identificar os maiores gastos.
**Saúde financeira:** barra atualizada a cada gasto, limite mensal, mudança de cor ao atingir o limite e aviso quando não há limite definido.

---

*A coluna Status reflete o estado do código em outubro/2026. Atualize-a antes da entrega.*

**O menu lateral tem 9 módulos: Dashboard, Assistente IA, Lançamentos, Metas, Simulador, Relatório, Terceiros, Categorias e Perfil. Os demais arquivos de views/ são telas de apoio (login, menu, tema, toast, celebração e gráfico)**

## O que o sistema não faz

- Não tem servidor próprio, nuvem nem sincronização entre dispositivos. Todos os dados ficam no computador do usuário.

- Não tem contas online nem uso simultâneo por várias pessoas.

- Não faz integração bancária (importar extrato, Open Finance etc.).

- Não tem módulo fiscal (impostos, notas fiscais, declaração).

*O único recurso que usa internet é o Assistente IA, que é opcional e usa a API do Gemini (Google). Sem chave configurada, ou sem conexão, o restante do sistema funciona normalmente. Ao usar o assistente, o texto da conversa é enviado ao Google: não digite dados pessoais sensíveis.*

---
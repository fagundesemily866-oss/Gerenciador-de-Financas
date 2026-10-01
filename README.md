# 💰 Gerenciador de Finanças Pessoais

Sistema moderno de gestão financeira pessoal desenvolvido em **Python** com **CustomTkinter**, arquitetado sob os padrões **MVC (Model-View-Controller)** e **DAO (Data Access Object)** com banco de dados **SQLite**.

---

## ✨ Funcionalidades Principais

O sistema conta com 9 módulos completos acessíveis pela barra lateral retrátil:

1. **📊 Dashboard & Saúde Financeira:**
   - 6 cards de métricas (Saldo Atual, Receitas, Despesas, Economizado, Limite Mensal, Disponível para Gastar).
   - Indicador de Score de Saúde Financeira com checklist de boas práticas.
   - Gráfico donut de gastos por categoria e gráfico vetorial de fluxo de caixa semestral.
   - **Planejador Rápido de Economia:** controle interativo de economia com salto fixo de **5% em 5%**.

2. **🤖 Assistente IA de Finanças:**
   - Chat interativo com sugestões inteligentes e respostas analíticas com barras visuais.
   - Ações rápidas de consulta com navegação direta para os módulos.
   - Painel lateral com resumo do mês, alertas e recomendações preditivas.

3. **💰 Lançamentos:**
   - Registro de receitas e despesas com categorização e vínculo a terceiros.
   - Filtros por tipo (Todos, Receitas, Despesas) e busca textual.
   - **Exclusão de lançamentos:** botão interativo de lixeira `🗑️` com confirmação.

4. **🎯 Metas Financeiras:**
   - Definição de objetivos com valor alvo, valor atual, prazo e previsão.
   - Aporte direto nas metas com cálculo de evolução percentual.
   - **Celebração Animada:** ao atingir 100% da meta, dispara animação com foguetes e confetes explodindo no centro da tela.
   - **Pop-up de Decisão:** opções para *Aumentar a Meta*, *Recuar a Meta* ou *Apenas Manter*.

5. **🔮 Simulador de Cenários:**
   - Laboratório preditivo de impacto financeiro (3 meses a 5 anos).
   - Sliders com **método arrastar em tempo real** para corte de despesas (passo fixo de 5%), renda extra e aportes.
   - Comparativo dinâmico de 3 cenários: *Otimista*, *Planejado* e *Pessimista*.

6. **📄 Relatório Mensal:**
   - Resumo executivo com balanço e comparativo com o mês anterior.
   - Gráficos de barras duplas de evolução semestral de receitas e despesas.
   - **Seção de Metas no Relatório:** frases amigáveis e claras indicando quanto foi guardado para cada meta no mês.
   - Exportação do relatório consolidado em arquivo.

7. **🤝 Terceiros & Contatos:**
   - Gestão de fornecedores, clientes, familiares, **funcionários** e **lugares/estabelecimentos**.
   - Seletor de logos pré-definidos (👨‍💼 Func., 🏢 Lugar, 🏬 Loja, 🚚 Fornecedor) ou upload de imagem.
   - Exclusão e edição de contatos com confirmação.

8. **🏷️ Categorias:**
   - Limites orçamentários por categoria de receita e despesa.
   - Indicadores de uso do orçamento com barra de progresso.
   - Exclusão e cadastro de novas categorias.

9. **👤 Meu Perfil & Preferências:**
   - Gestão de dados pessoais e cadastro de **Renda Mensal (quanto ganha)**.
   - Alternador de tema (**Modo Escuro / Modo Claro**) com reconstrução dinâmica de contraste.
   - Segurança e alteração de senha.

---

## 🏗️ Arquitetura do Projeto

```text
controle_financeiro/
├── main.py                     # Ponto de entrada e gerenciador de janelas
├── requirements.txt            # Dependências do projeto
├── models/                     # Entidades e conexão SQLite
│   ├── database.py             # Schema, migrações e conexão SQLite
│   ├── lancamento.py           # Modelo de Transação/Lançamento
│   ├── meta.py                 # Modelo de Meta
│   ├── categoria.py            # Modelo de Categoria
│   ├── terceiro.py             # Modelo de Terceiro
│   └── usuario.py              # Modelo de Usuário
├── dao/                        # Data Access Objects (persistência SQLite)
│   ├── lancamento_dao.py
│   ├── meta_dao.py
│   ├── categoria_dao.py
│   ├── terceiro_dao.py
│   ├── usuario_dao.py
│   └── simulacao_dao.py
├── controllers/                # Controladores de regras de negócio
├── services/                   # Serviços auxiliares e integração de IA
│   └── ai_service.py
├── views/                      # Camada de Apresentação (CustomTkinter)
│   ├── tema.py                 # Paleta de cores (Dark/Light) e tipografia
│   ├── menu_view.py            # Navegação principal e sidebar retrátil
│   ├── login_view.py           # Tela de autenticação e boas-vindas
│   ├── saude_financeira_view.py
│   ├── assistente_ia_view.py
│   ├── lancamento_view.py
│   ├── meta_view.py
│   ├── simulador_view.py
│   ├── relatorio_view.py
│   ├── terceiro_view.py
│   ├── categoria_view.py
│   ├── usuario_view.py
│   └── celebracao_view.py      # Modal com animação de foguetes e confetes
└── tests/                      # Suíte de testes automatizados
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior instalado.

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```
*(ou manualmente: `pip install customtkinter pillow python-dotenv`)*

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

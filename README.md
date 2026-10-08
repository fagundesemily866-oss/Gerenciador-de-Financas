# 💰 Gerenciador de Finanças Pessoais

Aplicativo desktop feito em **Python + CustomTkinter**, com **MySQL**, para organizar receitas, despesas, metas e orçamentos. Possui contas individuais, relatórios e um assistente financeiro com **Google Gemini**.

## 🎯 Problema e objetivo

**Problema:** é difícil controlar o orçamento quando receitas e gastos ficam espalhados.

**Objetivo:** reunir as finanças em um só lugar, facilitar o acompanhamento do dinheiro e ajudar na tomada de decisões.

## ✨ Funcionalidades

| Módulo | O que faz |
| --- | --- |
| 📊 **Dashboard** | Mostra receitas, despesas, saldo e movimentações recentes. |
| ❤️ **Saúde Financeira** | Exibe indicadores mensais e orientações financeiras. |
| 🤖 **Assistente IA** | Responde perguntas e ajuda a analisar os gastos. |
| 💰 **Lançamentos** | Cadastra, consulta e filtra receitas e despesas. |
| 🎯 **Metas** | Acompanha objetivos, aportes e progresso. |
| 🔮 **Simulador** | Compara cenários financeiros futuros. |
| 📄 **Relatórios** | Apresenta resumos e gráficos do mês. |
| 🏷️ **Categorias e Terceiros** | Organiza gastos e pessoas ou empresas relacionadas. |
| 👤 **Meu Perfil** | Permite gerenciar a conta e os dados pessoais. |

**As contas ficam salvas no MySQL.** Usuários novos começam sem movimentações; os dados fictícios só são criados pela opção **Gerar dados aleatórios**.

## 🚀 Instalação rápida

**1. Instale os programas necessários**

- [Python 3.10+](https://www.python.org/downloads/) — marque **Add Python to PATH** na instalação.
- [MySQL Server](https://dev.mysql.com/downloads/mysql/) — instale e inicie o serviço.

**2. Abra a pasta do projeto no VS Code** e execute no terminal:

```bash
python -m pip install -r requirements.txt
```

**3. Configure o banco:** copie `.env.example` para um arquivo chamado `.env` e preencha os dados do seu MySQL:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=gerenciador_financeiro
AI_API_KEY=
```

> `AI_API_KEY` é opcional: serve para usar o Gemini. As tabelas são preparadas automaticamente a partir de `migrations/ddl/`, desde que o usuário do MySQL tenha as permissões necessárias. Não execute o SQL de dados de exemplo se quiser começar do zero.

**4. Inicie o aplicativo:**

```bash
python main.py
```

Na primeira abertura, **crie sua conta** ou faça login. Para testar sem cadastrar movimentações manualmente, use a opção **Gerar dados aleatórios**.

## 🖼️ Prints do sistema

| Dashboard | Assistente IA |
| :---: | :---: |
| ![Dashboard do sistema](docs/imagens/01_dashboard_atual.png) | ![Tela do Assistente IA](docs/imagens/02_assistente_ia.png) |
| **Lançamentos** | **Metas** |
| ![Tela de lançamentos](docs/imagens/05_lancamentos.png) | ![Tela de metas](docs/imagens/06_metas.png) |
| **Relatório mensal** | **Categorias** |
| ![Tela do relatório mensal](docs/imagens/07_relatorio.png) | ![Tela de categorias](docs/imagens/08_categorias.png) |

## 🛠️ Tecnologias e estrutura

**Python**, **CustomTkinter**, **MySQL**, **Google Gemini**, **python-dotenv** e **unittest**. A organização segue **MVC + DAO**:

- `views/`: telas; `controllers/`: controle da aplicação; `models/` e `dao/`: dados e consultas.
- `services/`: lógica auxiliar e IA; `migrations/`: estrutura do banco; `tests/`: testes.

**Diagrama do banco:** [visualizar o modelo lógico](docs/imagens/diagrama_logico_banco.png).

## 🧪 Testes

```bash
python -m unittest discover -s tests
```

**Problemas comuns:** se faltar uma biblioteca, repita a instalação do passo 2. Se houver erro de conexão, verifique o serviço MySQL e os dados do `.env`. Não publique esse arquivo com senhas ou chaves reais.

> **Limitações:** não há integração bancária automática nem sincronização própria em nuvem. O assistente IA precisa de internet e de uma chave de API válida.

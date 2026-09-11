# Gerenciador de Finanças Pessoais — Base MVC (Tkinter)

Base funcional de um gerenciador de finanças pessoais, estruturada em **MVC**
(Model-View-Controller), usando apenas a biblioteca padrão do Python
(`tkinter` + `sqlite3`). O visual é propositalmente simples (widgets padrão
do Tkinter/ttk, sem estilização customizada), com o foco em uma arquitetura
de código limpa e extensível.

## Estrutura do projeto

```
finance_manager/
├── main.py                              # Ponto de entrada da aplicação
├── models/
│   ├── database.py                      # Conexão e schema do SQLite
│   └── transaction.py                   # Entidade Transaction + repositório (CRUD)
├── views/
│   └── main_view.py                     # Interface gráfica (Tkinter)
├── controllers/
│   └── transaction_controller.py        # Regras de negócio e validações
└── data/
    └── finance.db                       # Banco de dados (criado automaticamente)
```

### Model
- `Database`: abre/gerencia a conexão SQLite e garante a criação da tabela
  `transactions` na primeira execução.
- `Transaction`: dataclass que representa uma transação (id, descrição,
  valor, tipo, categoria, data).
- `TransactionModel`: repositório com as operações de persistência
  (`add`, `update`, `delete`, `get_by_id`, `get_all`), incluindo suporte
  a filtros por tipo e categoria.

### Controller
- `TransactionController`: recebe os dados brutos vindos da View (texto),
  valida (descrição obrigatória, valor numérico positivo, tipo/categoria
  válidos, data no formato `AAAA-MM-DD`), converte e delega a persistência
  ao `TransactionModel`. Também calcula o resumo financeiro (total de
  receitas, despesas e saldo).

### View
- `MainView`: janela Tkinter com:
  - Formulário para cadastro/edição (descrição, valor, tipo, categoria, data);
  - Botões: Adicionar, Atualizar, Excluir, Limpar Campos;
  - Filtros por tipo e categoria;
  - Tabela (Treeview) listando as transações;
  - Resumo com totais de receitas, despesas e saldo.
  - Clicar em uma linha da tabela carrega os dados no formulário para edição.

A View **nunca acessa o Model diretamente** — toda operação passa pelo
Controller, o que mantém a lógica de negócio centralizada e testável.

## Como executar

Nenhuma dependência externa é necessária (apenas Python 3.8+ com Tkinter,
que já acompanha a instalação padrão na maioria dos sistemas).

```bash
cd finance_manager
python main.py
```

O banco de dados SQLite (`data/finance.db`) é criado automaticamente na
primeira execução.

## Possíveis extensões futuras

Esta é uma **base**, pensada para ser evoluída. Alguns pontos naturais de
expansão, já que a arquitetura foi organizada para isso:

- Adicionar autenticação/múltiplos usuários (uma nova tabela + FK em `transactions`);
- Categorias personalizáveis pelo usuário (hoje são uma lista fixa em `TransactionModel.CATEGORIES`);
- Gráficos de gastos por categoria/mês (ex.: usando `matplotlib` embutido no Tkinter);
- Exportação de relatórios (CSV/PDF);
- Testes automatizados unitários para `TransactionController` (a lógica de
  validação já está isolada da interface, o que facilita testá-la sem
  precisar abrir a janela gráfica);
- Paginação/scroll infinito na tabela para grandes volumes de dados;
- Edição de metas/orçamento mensal por categoria.

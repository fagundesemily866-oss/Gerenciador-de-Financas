# 💰 Gerenciador de Finanças Pessoais

**Projeto acadêmico | Python • CustomTkinter • MySQL • Google Gemini**

Aplicativo desktop para registrar receitas e despesas, controlar orçamentos, acompanhar metas e analisar a saúde financeira. Usa a arquitetura **MVC + DAO** e mantém os dados de cada conta no **MySQL**.

## 📋 Funcionalidades


| Tela | Principal função |
| --- | --- |
| **Dashboard** | Exibe receitas, despesas, saldo, movimentações recentes e metas. |
| **Saúde Financeira** | Mostra diagnóstico do mês, indicadores, pontuação e orientações. |
| **Assistente IA** | Permite fazer perguntas financeiras; integração opcional com Gemini. |
| **Lançamentos** | Cadastra e consulta receitas e despesas. |
| **Metas** | Cria objetivos, registra aportes e acompanha progresso. |
| **Simulador de Cenários** | Testa cortes de gastos, renda extra e aportes, além de mostrar o impacto nas metas. |
| **Relatório Mensal** | Resume receitas e despesas e exporta relatório em **`.txt`**. |
| **Terceiros** | Organiza pessoas, clientes, fornecedores e estabelecimentos. |
| **Categorias** | Organiza receitas/despesas e define limites mensais. |
| **Meu Perfil** | Permite consultar e editar dados da conta, senha e preferências. |

---

## 🚀 Instalação completa (Windows)

### 1. Requisitos

- **Python 3.10 ou superior** (recomendado marcar **Add Python to PATH** ao instalar).
- **MySQL Server** instalado e em execução. O **MySQL Workbench** é opcional: ele facilita a administração, mas não substitui o servidor.
- Conexão com a internet para instalar bibliotecas e para usar o Gemini. As demais funções usam o servidor MySQL configurado.

### 2. Preparar os arquivos

1. Extraia o ZIP do projeto em uma pasta do computador.
2. Abra a pasta **`Gerenciador-de-Financas`**, onde está o arquivo `main.py`.
3. Abra o terminal nessa pasta (por exemplo, digite `cmd` na barra de endereço do Explorador de Arquivos e pressione Enter).
4. **Não exclua** as pastas `migrations/`, `models/`, `dao/`, `controllers/`, `views/` nem o arquivo `models/database.py`.

### 3. Instalar as bibliotecas

No terminal, execute:

```bat
py -m pip install -r requirements.txt
```

Se o comando `py` não funcionar, tente `python` no lugar dele. Entre as dependências estão CustomTkinter, python-dotenv, Google GenAI e mysql-connector-python.

### 4. Configurar o MySQL e o arquivo `.env`

1. Confirme que o **MySQL Server está iniciado** e anote o usuário e a senha configurados na instalação.
2. Na pasta do projeto, **copie** `.env.example` e renomeie a cópia para **`.env`** (não confunda com `.env.txt`). Se o Windows não mostrar extensões, habilite **Exibir → Extensões de nomes de arquivo**.
3. Edite o `.env` com os dados do MySQL **deste computador**:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=coloque_a_senha_do_seu_mysql
MYSQL_DATABASE=gerenciador_financeiro
AI_API_KEY=
```

- **`MYSQL_HOST`**: `localhost` quando o banco está no mesmo computador; use o endereço do servidor quando ele estiver em outra máquina.
- **`MYSQL_USER` e `MYSQL_PASSWORD`**: credenciais de acesso ao MySQL (não são o login do aplicativo).
- **`MYSQL_DATABASE`**: nome do banco usado pelo aplicativo.
- **`AI_API_KEY`**: chave opcional do Gemini. Sem chave, o restante do aplicativo pode funcionar normalmente.

### 5. Criar o banco e as tabelas

**Normalmente não precisa executar SQL manualmente.** Na primeira conexão, `models/database.py`:

1. Conecta ao MySQL usando o `.env`.
2. Cria o banco `gerenciador_financeiro` caso não exista (se a conta do MySQL tiver permissão).
3. Lê `migrations/ddl/V1__criar_estrutura.sql` e cria as tabelas necessárias, sem recriar as que já existem.
4. Garante algumas tabelas e campos auxiliares utilizados pelo sistema.

**Atenção:** `migrations/dml/V1__dados_exemplo.sql` contém dados de exemplo e **não precisa ser executado**. Para começar sem registros fictícios, deixe esse arquivo sem executar.

Se o usuário do MySQL **não tiver permissão para criar bancos**, peça ao responsável pelo MySQL que crie um banco com o mesmo nome do `.env` e conceda as permissões necessárias ao usuário configurado.

### 6. Abrir o aplicativo

```bat
py main.py
```

Se necessário, use `python main.py`. A tela de **Entrar / Criar Conta** será aberta.

### 7. Criar uma conta e entrar depois

1. Na tela inicial, abra a aba **Criar Conta**.
2. Digite nome, e-mail, perfil **PF** ou **PJ** e uma senha com **pelo menos 8 caracteres**.
3. Confirme a senha e clique em **Criar Minha Conta**.
4. A conta será gravada no MySQL e começará **sem lançamentos fictícios**.
5. Depois de fechar o programa, inicie-o novamente e use **o mesmo e-mail e senha** para entrar.

**Importante:** os usuários e suas movimentações ficam no **servidor MySQL configurado**, não dentro do arquivo ZIP. O acesso posterior à mesma conta exige esse banco com os registros preservados.

### 8. Dados aleatórios (somente para demonstração)

Na tela inicial, clique em **🎲 Gerar dados aleatórios** e **confirme**. O aplicativo cria uma **nova conta de demonstração**, separada das contas reais, já preenchida com dados fictícios. Guarde as credenciais que aparecerem na tela caso queira entrar nessa conta novamente.

Sem clicar nesse botão, o aplicativo **não gera movimentações aleatórias automaticamente**.

---

## 🧭 Como usar cada módulo

**Ordem sugerida para começar com uma conta vazia:**

1. **Categorias:** cadastre, por exemplo, `Salário` (receita), `Alimentação` (despesa) e `Moradia` (despesa). Defina um limite mensal nas categorias de despesa, se desejar.
2. **Terceiros (opcional):** cadastre uma pessoa ou empresa que será associada a um lançamento.
3. **Lançamentos:** selecione **Receita** ou **Despesa**, informe valor, descrição, categoria, data e status; salve o registro. Use a listagem e os filtros para consultar as movimentações.
4. **Dashboard:** confira saldo, receitas, despesas, movimentações recentes e suas metas. Os valores são calculados a partir dos registros da conta.
5. **Saúde Financeira:** abra a opção específica no menu para ver os indicadores e orientações do mês. Sem registros suficientes, a tela mostra **Aguardando dados**, sem criar uma pontuação fictícia.
6. **Metas:** crie uma meta informando objetivo, valor-alvo e prazo. Use **+ Guardar valor** para registrar aportes e acompanhar a porcentagem atingida.
7. **Simulador de Cenários:** escolha período, redução de despesas, renda extra e aportes; clique em **Atualizar Simulação**. Consulte **Comparação**, **Consequências** e **Visão por Metas**. Você também pode salvar e carregar cenários.
8. **Relatório Mensal:** consulte os resultados do período e clique em **Exportar relatório (.txt)** para gerar um arquivo de texto.
9. **Assistente IA:** com uma chave Gemini configurada, escreva uma pergunta e clique em **Enviar**. Sem chave válida ou conexão, as demais telas continuam disponíveis.
10. **Meu Perfil:** consulte e edite os dados da conta. Use **Sair da Conta** para voltar ao login sem apagar os registros.

**Dica:** dados de meses diferentes são exibidos de acordo com o período selecionado. Se uma tela estiver vazia, confira se há lançamentos no mês mostrado.

---

## 🧪 Testes automatizados

Com o terminal aberto na pasta do projeto:

```bat
py -m unittest discover -s tests
```

Os testes verificam partes da lógica e dos componentes, mas **não substituem** uma execução completa com o servidor MySQL e a interface gráfica.

## 🛠️ Problemas frequentes

| Problema | O que verificar |
| --- | --- |
| `python` ou `py` não é reconhecido | Instalação do Python, PATH ou reinicialização do terminal. |
| `No module named ...` | Execute `py -m pip install -r requirements.txt` com o Python usado para abrir o projeto. |
| `Can't connect to MySQL server` | O MySQL Server está iniciado? Porta 3306 e `MYSQL_HOST` estão corretos? |
| `Access denied for user` | Confira `MYSQL_USER`, `MYSQL_PASSWORD` e permissões no MySQL. |
| Falha ao criar banco/tabela | Verifique permissões e se a pasta `migrations/ddl/` está presente. |
| Conta antiga não aparece | O `.env` aponta para o banco correto? O backup das contas foi restaurado? |
| Tela com saldo zerado / saúde aguardando dados | Confira a conta logada, o mês selecionado e os lançamentos. |
| Assistente IA não responde | Verifique `AI_API_KEY`, internet, disponibilidade da API e mensagens de erro. |

## 🏗️ Estrutura principal

```text
Gerenciador-de-Financas/
├── main.py                 # Entrada do programa
├── README.md               # Este tutorial
├── requirements.txt        # Bibliotecas
├── .env.example            # Modelo das configurações
├── assets/                 # Ícones e recursos
├── views/                  # Telas CustomTkinter
├── controllers/            # Regras e coordenação
├── dao/                    # Consultas e gravação no MySQL
├── models/                 # Modelos e database.py (conexão)
├── migrations/
│   ├── ddl/                # Criação de tabelas
│   └── dml/                # Dados de exemplo (opcionais)
├── services/               # IA, sessão e simulações
└── tests/                  # Testes automatizados
```

## 🔒 Limitações e privacidade

- Não possui integração automática com bancos, Open Finance ou emissão fiscal.
- Não inclui servidor próprio nem sincronização em nuvem: os dados ficam no **MySQL configurado**, que pode ser local ou remoto.
- O Gemini é opcional e requer internet e uma chave de API válida. O conteúdo das mensagens enviadas ao assistente pode ser processado pelo serviço externo; não inclua dados pessoais sensíveis nas perguntas.
- Para impedir perda de informações, faça **backups periódicos do MySQL**.

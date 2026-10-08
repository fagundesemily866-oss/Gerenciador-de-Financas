# Atualização — Assistente IA, dados e contas

## Instalação
1. Extraia este ZIP em uma nova pasta. **Não execute o script de exemplo** `migrations/dml/V1__dados_exemplo.sql` se deseja contas vazias.
2. Copie o **seu arquivo `.env` original** (não incluído no ZIP por segurança) para a raiz da nova pasta. Conserve `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` e, se usar IA, `AI_API_KEY`.
3. Mantenha o mesmo servidor MySQL e o mesmo banco `gerenciador_financeiro`. As contas são armazenadas no MySQL, **não no diretório do programa**. Não apague seu banco antigo ao atualizar o código.
4. No terminal da pasta do projeto, execute `python -m pip install -r requirements.txt` e depois `python main.py`.

## Funcionalidades
- **Entrar**: e-mail e senha de contas já gravadas. O DAO recupera a conta do MySQL após reiniciar o programa.
- **Criar Conta**: salva um usuário novo, com senha protegida por hash e sem lançamentos, categorias ou metas fictícios. Entra na conta recém-criada.
- **Gerar dados aleatórios**: botão exclusivo na aba **Entrar**, com confirmação. Cria **outra conta**, identificada como demonstração, gera nela dados fictícios e informa o e-mail e a senha aleatórios para futuras entradas. **Guarde essas credenciais** caso queira retornar à conta demo.
- **Assistente IA**: chat legível, área rolável ampla, entrada fixa, saldos do mês extraídos do MySQL e análise de despesas reais. As mensagens fictícias anteriores não aparecem.
- **Dashboard, Relatórios, Lançamentos, Metas, Categorias e Terceiros**: sem valores de exemplo embutidos; consultam os registros da conta logada. As telas antigas de Dashboard e Relatório continuam importáveis por compatibilidade e apontam às novas implementações.
- **Visão por Metas do Simulador**: conserva a correção anterior.

## Importante sobre dados anteriores
Esta atualização **não apaga nenhuma informação do MySQL**, inclusive registros fictícios que já tenham sido gravados lá anteriormente. Se entrar numa conta antiga com dados de demonstração persistidos, os registros continuarão sendo mostrados por serem linhas reais do banco. Para ter uma conta vazia, use **Criar Conta** com outro e-mail.

`models/database.py` **não deve ser apagado**: é a camada que liga o aplicativo ao MySQL e aplica os scripts de estrutura em `migrations/ddl` de maneira idempotente. Os scripts `migrations/dml` são opcionais, não são executados ao iniciar.

## Verificação
- Compilação de todos os arquivos Python: sem erros de sintaxe.
- Testes de lógica financeira e Visão por Metas: passando.
- Verificação de cadastro, hash de senha, commit e login posterior: passando com conexão de teste simulada.
- Não foi possível executar a GUI nem uma conexão real com seu MySQL neste ambiente; faça uma validação local usando o arquivo `.env` correto.

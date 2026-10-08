# Correção: Visão por Metas no Simulador

## O que foi corrigido

- O simulador lê metas diretamente de `MetaDAO.listar_todas()`, a mesma fonte da tela **Minhas Metas**.
- `MetaDAO` lê a tabela MySQL `meta_reserva`, criada em `migrations/ddl/V1__criar_estrutura.sql`.
- Metas concluídas e metas em andamento agora aparecem na aba **Visão por Metas**.
- Metas concluídas são identificadas corretamente, sem receber novos aportes fictícios na simulação.
- Se ainda não houver lançamentos, a aba continua mostrando os valores e o progresso real das metas, com aviso de que as projeções exigem receitas/despesas.
- A aba consulta os dados atuais sempre que for aberta e oferece o botão **Atualizar metas**.
- Os cartões de cenários são empilhados em espaços estreitos para evitar cortes de texto.

## Arquivos modificados

- `views/simulador_view.py`
- `services/simulador_cenarios.py`
- `tests/test_visao_metas_simulador.py` (novo)

## Sobre migrations e database.py

`migrations/ddl/V1__criar_estrutura.sql` contém a definição das tabelas; não contém os registros pessoais do seu MySQL. Eles permanecem no servidor MySQL usado pelo aplicativo.

O arquivo `models/database.py` **não foi apagado** porque fornece a conexão com MySQL usada por todos os DAOs. Removê-lo quebraria o projeto. Nenhuma tabela existente foi zerada, removida ou recriada pela correção.

## Para instalar e executar

1. Substitua os arquivos do projeto pela versão deste ZIP (ou extraia em outra pasta).
2. O arquivo `.env` original **não foi colocado no ZIP** para evitar compartilhar senhas e chaves de API. Copie o `.env` do seu projeto anterior para a pasta raiz do projeto atualizado (use `.env.example` como referência, se necessário).
3. Mantenha o servidor MySQL original e as credenciais que apontam para o banco onde você criou suas metas.
4. Instale as dependências, se necessário: `pip install -r requirements.txt`.
5. Execute `python main.py`, faça login no mesmo usuário e abra Simulador de Cenários → Visão por Metas.

## Teste automatizado

`python -m unittest discover -s tests -p test_visao_metas_simulador.py -v`

Os testes da lógica de projeção passaram neste ambiente. O aplicativo gráfico não foi executado de ponta a ponta aqui, porque não há conexão com seu MySQL local nem CustomTkinter instalado neste ambiente.

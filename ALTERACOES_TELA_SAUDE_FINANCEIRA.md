# Tela Saúde Financeira independente

- Dashboard permanece com receitas, despesas, saldo, movimentações e metas.
- Novo item **Saúde Financeira** no menu, com tela própria e rolável.
- A avaliação é feita usando somente lançamentos do usuário logado e o mês selecionado.
- A pontuação, as orientações e os valores são atualizados ao abrir a tela, trocar o mês ou clicar em ↻.
- Sem lançamentos, a tela continua aberta e exibe **Aguardando dados**; não cria score ou registros fictícios.
- O menu lateral agora rola quando não há altura suficiente para mostrar todos os itens.
- Não foi necessário modificar o banco, as migrations, as contas ou o arquivo `.env`.

Teste sem servidor MySQL: `python -m unittest discover -s tests -p 'test_saude_mensal.py' -v`.

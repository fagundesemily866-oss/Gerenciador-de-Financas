Testes históricos escritos para a antiga arquitetura SQLite.
Foram preservados como referência, mas não são compatíveis com a classe Database do MySQL.
As suítes atuais em tests/test_*.py usam dados de teste em memória ou mocks
para não tocar em contas e dados reais.
Para testes integrados com servidor MySQL, configure um banco de testes separado.

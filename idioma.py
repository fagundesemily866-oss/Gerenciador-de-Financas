"""Traduções de interface (Português do Brasil / Inglês dos EUA).

Only the presentation layer is translated: internal MySQL enums, column names,
widget callbacks and financial records remain unchanged.

`instalar_idioma_ingles` decorates CustomTkinter widgets to translate visible
text/placeholder text and dropdown choices while preserving original values in
.get() so existing business logic keeps working.
"""
from __future__ import annotations

import re
import json
from pathlib import Path
from functools import wraps

IDIOMA_PADRAO = "pt_BR"
IDIOMAS_DISPONIVEIS = {"pt_BR": "Português (Brasil)", "en_US": "English (US)"}
_CONFIG_IDIOMA = Path(__file__).resolve().parent / "data" / "interface.json"


def _ler_preferencias() -> dict:
    try:
        config = json.loads(_CONFIG_IDIOMA.read_text(encoding="utf-8"))
        return config if isinstance(config, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def carregar_idioma_preferido() -> str:
    idioma = _ler_preferencias().get("language", IDIOMA_PADRAO)
    return idioma if idioma in IDIOMAS_DISPONIVEIS else IDIOMA_PADRAO


_idioma_atual = carregar_idioma_preferido()


def obter_idioma() -> str:
    return _idioma_atual


def definir_idioma(idioma: str, salvar: bool = True) -> None:
    """Define idioma, preservando tema e outras preferências no mesmo JSON."""
    if idioma not in IDIOMAS_DISPONIVEIS:
        raise ValueError("Idioma não suportado")
    global _idioma_atual
    _idioma_atual = idioma
    if salvar:
        try:
            dados = _ler_preferencias()
            dados["language"] = idioma
            _CONFIG_IDIOMA.parent.mkdir(parents=True, exist_ok=True)
            temporario = _CONFIG_IDIOMA.with_suffix(".tmp")
            temporario.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            temporario.replace(_CONFIG_IDIOMA)
        except OSError:
            # Mesmo com pasta de dados somente leitura, a seleção vale na sessão.
            pass


# Exact phrases (including dynamic status messages) used by the application.
TRADUCOES = {
    # navigation and account
    'Gerenciador de': 'Finance', 'Finanças Pessoais': 'Personal Finance',
    'Gerenciador de Finanças Pessoais': 'Personal Finance Manager',
    'Gerenciador': 'Personal', 'de Finanças': 'Finance', 'Pessoais': 'Manager',
    'Dashboard & Saúde Financeira': 'Dashboard',
    'Dashboard': 'Dashboard', 'Saúde Financeira': 'Financial Health',
    'Assistente IA': 'AI Assistant', 'Lançamentos': 'Transactions',
    'Metas': 'Goals', 'Simulador de Cenários': 'Scenario Simulator',
    'Relatório Mensal': 'Monthly Report', 'Terceiros': 'Contacts',
    'Categorias': 'Categories', 'Meu Perfil': 'My Profile',
    'Perfil PF': 'Personal Account', 'Perfil PJ': 'Business Account',
    'Usuário': 'User', 'Usuário Demo': 'Demo User',
    'Pessoa Física': 'Individual', 'Pessoa Jurídica': 'Business',
    'PF - Pessoa Física': 'PF - Individual', 'PJ - Pessoa Jurídica': 'PJ - Business',
    '🌙  Tema': '🌙  Theme', '🚪  Sair da Conta': '🚪  Sign Out',
    '⏻  Fechar App': '⏻  Exit App',
    'Esta tela ainda está em desenvolvimento.': 'This page is under development.',
    'Em construção': 'Under construction',
    '🎲  Modo demonstração — todos os dados desta conta são FICTÍCIOS (gerados aleatoriamente).':
        '🎲  Demo mode — all financial data in this account is FICTIONAL (randomly generated).',
    '💡 Resumo dos saldos, movimentações e metas': '💡 Balances, transactions and goals at a glance',
    '💡 Diagnóstico e score financeiro atualizados pelos lançamentos': '💡 Financial score calculated from transactions',
    '💡 Assistência inteligente e recomendações personalizadas': '💡 Smart financial assistance and recommendations',
    '💡 Registro e acompanhamento de receitas, despesas e fluxo': '💡 Track income, expenses and cash flow',
    '💡 Planejamento de objetivos e progresso de economia para sonhos': '💡 Plan savings goals and track progress',
    '💡 Teste de corte de gastos e renda extra sem alterar dados reais': '💡 Try financial changes without modifying real records',
    '💡 Demonstrativos mensais consolidados, gráficos e balanços': '💡 Monthly statements, charts and balances',
    '💡 Cadastro e controle de contatos, clientes e fornecedores': '💡 Manage contacts, clients and suppliers',
    '💡 Organização de despesas e limites de orçamento por categoria': '💡 Group expenses and set category budgets',
    '💡 Dados cadastrais, segurança da conta e preferências de perfil': '💡 Account details, security and preferences',
    # login
    'Bem-vindo de volta!': 'Welcome back!',
    'Acesse sua conta ou crie uma nova': 'Sign in or create an account',
    'Entrar': 'Sign In', 'Criar Conta': 'Create Account',
    'E-mail:': 'Email:', 'E-mail': 'Email',
    'Senha:': 'Password:', 'Senha': 'Password', 'Sua senha': 'Your password',
    'Entrar no Sistema': 'Sign In', '🎲 Gerar dados aleatórios': '🎲 Generate Demo Data',
    'Opcional: cria uma nova conta com dados fictícios, somente após confirmar.':
        'Optional: creates a demo account with sample records after confirmation.',
    'Nome Completo:': 'Full Name:', 'Nome Completo': 'Full Name',
    'Ex: João da Silva': 'E.g. John Smith',
    'Tipo de Perfil:': 'Account Type:', 'Tipo de Perfil': 'Account Type',
    'Confirmar Senha:': 'Confirm Password:', 'Repita a senha': 'Repeat your password',
    'Mín. 8 caracteres': 'Minimum 8 characters',
    'Sua conta começa vazia. Seus dados ficarão salvos no MySQL.':
        'Your account starts empty. Your data is saved in MySQL.',
    'Criar Minha Conta': 'Create My Account',
    'Controle inteligente das suas finanças.': 'Smarter control of your finances.',
    'seu.email@exemplo.com': 'your.email@example.com', 'exemplo@email.com': 'example@email.com',
    'Esqueceu sua senha?': 'Forgot your password?',
    'Cancelar': 'Cancel', 'Confirmar': 'Confirm', 'Fechar': 'Close',
    'Sim': 'Yes', 'Não': 'No', 'Salvar': 'Save', 'Excluir': 'Delete', 'Editar': 'Edit',
    'Atualizar': 'Refresh', 'Remover': 'Remove', 'Limpar': 'Clear',
    'Sucesso': 'Success', 'Erro': 'Error', 'Aviso': 'Warning', 'Informação': 'Information',
    'Atenção': 'Attention', 'Deseja continuar?': 'Do you want to continue?',
    'Configuração': 'Settings', 'Opções': 'Options',
    # dashboard, reports, health
    'Receitas do mês': 'Monthly Income', 'Despesas do mês': 'Monthly Expenses',
    'Saldo do mês': 'Monthly Balance', 'Receitas − despesas': 'Income − expenses',
    'Registradas na sua conta': 'Recorded in your account',
    'Movimentações recentes': 'Recent Transactions', 'Minhas metas': 'My Goals',
    'Nenhuma meta cadastrada ainda.': 'No goals have been created yet.',
    'Criar meta': 'Create Goal', 'Cadastrar lançamento': 'Add Transaction',
    'Exportar relatório (.txt)': 'Export Report (.txt)',
    'Histórico completo': 'Full History',
    'Seu diagnóstico mensal, com base nas movimentações cadastradas.':
        'Your monthly assessment based on recorded transactions.',
    'DIAGNÓSTICO DO MÊS': 'MONTHLY ASSESSMENT',
    'Pontuação financeira': 'Financial Score',
    'Calculada com os dados do período selecionado': 'Calculated using data from the selected period',
    'Adicionar lançamento': 'Add Transaction', '+ Adicionar lançamento': '+ Add Transaction',
    'Ver categorias': 'View Categories', 'Aguardando dados': 'Waiting for Data',
    'Dados insuficientes': 'Insufficient Data', 'Em atenção': 'Needs Attention',
    'Saudável': 'Healthy', 'Excelente': 'Excellent',
    'Gastos do mês': 'Monthly Spending', 'Comprometimento da renda': 'Income Used',
    'Receitas': 'Income', 'Despesas': 'Expenses', 'Saldo': 'Balance',
    'Evolução financeira': 'Financial Trends', 'Resumo mensal': 'Monthly Summary',
    'Resumo do mês': 'Monthly Overview',
    # assistant
    'Escreva sua pergunta aqui...': 'Ask a question about your finances...',
    'Enviar  ➤': 'Send  ➤', 'Aguarde...': 'Please wait...',
    'Seu consultor financeiro pessoal, sempre ao seu lado.': 'Your financial assistant, always here to help.',
    'Analisar despesas': 'Analyze Expenses', 'Entenda seus gastos': 'Understand your spending',
    'Defina um objetivo': 'Set a financial goal', 'Veja um panorama': 'See the big picture',
    'Buscar transações, metas, categorias...': 'Search transactions, goals, categories...',
    'Como posso economizar mais?': 'How can I save more?',
    'Estou dentro do meu orçamento?': 'Am I staying within my budget?',
    'Quais foram meus maiores gastos neste mês?': 'What were my biggest expenses this month?',
    # transactions
    'Registre e acompanhe todas as suas receitas, despesas e mantenha suas finanças em dia.':
        'Track your income and expenses in one place.',
    'Novo Lançamento': 'New Transaction', 'Registre uma receita ou despesa de forma rápida e organizada.':
        'Add income or an expense quickly and easily.',
    '⛔  Despesa': '⛔  Expense', '＋  Receita': '＋  Income',
    'Valor (R$) *': 'Amount (R$) *', 'Valor (R$)': 'Amount (R$)',
    'Descrição *': 'Description *', 'Descrição': 'Description',
    'Ex: Aluguel, Supermercado, Conta de Luz...': 'E.g. Rent, Groceries, Electricity...',
    'Categoria *': 'Category *', 'Categoria': 'Category',
    'Beneficiário / Fornecedor': 'Recipient / Supplier',
    'Ex: Pão de Açúcar': 'E.g. Grocery Store',
    'Data *': 'Date *', 'Data': 'Date', 'Status do Pagamento *': 'Payment Status *',
    'ⓘ Formato da data: DD/MM/AAAA': 'ⓘ Date format: DD/MM/YYYY',
    '＋  Salvar Lançamento': '＋  Save Transaction',
    '🔄  Limpar Campos': '🔄  Clear Fields', 'Lançamentos Recentes': 'Recent Transactions',
    'Acompanhe, edite ou filtre seus lançamentos.': 'View, edit and filter transactions.',
    'Ver todos →': 'View All →', 'Buscar por descrição, categoria...': 'Search description or category...',
    'Data ↕': 'Date ↕', 'Status': 'Status', 'Ações': 'Actions',
    'Nenhum lançamento encontrado.': 'No transactions found.',
    'PAGO': 'PAID', 'PENDENTE': 'PENDING', 'RECEBIDO': 'RECEIVED',
    'RECEITA': 'INCOME', 'DESPESA': 'EXPENSE', 'PESSOAL': 'PERSONAL',
    'Nova Despesa': 'New Expense', 'Nova Receita': 'New Income',
    # goals
    'Conquiste seus planos com organização e disciplina.':
        'Reach your goals by staying organized and consistent.',
    '“ Grandes conquistas começam com pequenos\npassos, todos os dias. ”':
        '“ Big achievements begin with small\nsteps, every day. ”',
    'Minhas Metas': 'My Goals', 'Nenhuma meta cadastrada': 'No goals created',
    'Crie sua primeira meta no painel ao lado!': 'Create your first goal using the panel on the right!',
    'Novo valor alvo da meta (R$)': 'New goal target (R$)',
    'Novo valor recuado da meta (R$)': 'New reduced goal target (R$)',
    'Confirmar Recuo': 'Confirm Reduction',
    'Valor alvo': 'Target Amount', 'Já guardado': 'Saved So Far',
    'Prazo': 'Deadline', 'Mensal': 'Monthly', 'Previsão': 'Forecast',
    '+ Guardar valor': '+ Add Savings', 'Quanto deseja guardar agora? (R$)':
        'How much would you like to save now? (R$)',
    'Total poupado': 'Total Saved', 'Metas ativas': 'Active Goals',
    'Em dia': 'On Track', 'Atrasadas': 'Overdue', 'Atrasada': 'Overdue',
    '◇ Atrasada': '◇ Overdue',
    'Nova Meta': 'New Goal', 'Defina um objetivo e comece a construir seu futuro.':
        'Set a goal and start building your future.',
    'Objetivo / Descrição': 'Goal / Description',
    'Ex: Reserva de Emergência, Viagem, Carro...': 'E.g. Emergency Fund, Vacation, Car...',
    'Valor alvo (R$)': 'Target Amount (R$)', 'Valor já guardado (R$)': 'Amount Saved (R$)',
    'Prazo estimado': 'Estimated Timeframe', 'Contribuição mensal (R$)': 'Monthly Contribution (R$)',
    'Data limite (opcional)': 'Deadline (optional)', '＋  Criar meta': '＋  Create Goal',
    '📈  Progresso das suas metas': '📈  Your Goals Progress',
    'Cadastre uma meta para acompanhar o progresso aqui.': 'Create a goal to track its progress here.',
    'Alvo': 'Target', 'Guardado': 'Saved', 'Excluir meta': 'Delete Goal',
    # simulator
    'PLANEJE SEU FUTURO': 'PLAN YOUR FUTURE', 'Simulador de Cenários': 'Scenario Simulator',
    'Descubra como diferentes decisões financeiras podem impactar seus resultados ao longo do tempo.':
        'See how financial choices could change your results over time.',
    '📂  Carregar Cenário': '📂  Load Scenario', '💾  Salvar Cenário': '💾  Save Scenario',
    '⚙  Configuração do Cenário': '⚙  Scenario Settings',
    'Ajuste os parâmetros e veja o impacto no seu futuro.':
        'Adjust the inputs and see their potential future impact.',
    '📅  Horizonte de Tempo': '📅  Time Horizon', '%  Corte de Despesas': '%  Expense Reduction',
    'Redução nas despesas mensais': 'Monthly expense reduction',
    'Aplicar redução em:': 'Apply reduction to:', '↑  Aumento de Renda Extra': '↑  Extra Income',
    'Valor adicional por mês': 'Additional amount per month',
    '🎯  Aporte Mensal para Metas': '🎯  Monthly Goal Contributions',
    'Valor que será investido mensalmente': 'Amount contributed each month',
    '🔄  Limpar': '🔄  Reset', '▶  Atualizar Simulação': '▶  Update Simulation',
    'Escolha um cenário': 'Choose a scenario',
    'Ainda não há lançamentos para simular.': 'There are no transactions to simulate yet.',
    'Cadastre receitas e despesas (ou use "Criar finanças aleatórias" ao criar a conta) para ver os cenários.':
        'Add income and expenses (or generate demo data) to compare scenarios.',
    'acumulado ao final': 'total at the end', 'Economizado': 'Saved',
    'vs planejado': 'vs planned', 'Cenário base': 'Baseline Scenario',
    'referência de comparação': 'Comparison baseline',
    'Veja os três cenários na aba “Consequências”.':
        'See all three scenarios on the “Consequences” tab.',
    '↻  Atualizar metas': '↻  Refresh Goals',
    "Nenhuma meta cadastrada. Crie uma meta em 'Minhas Metas' para acompanhá-la aqui.":
        "No goals created. Create one under 'My Goals' to track it here.",
    '✔  Meta concluída — os valores acima são os reais do banco.':
        '✔  Goal reached — values above reflect actual database records.',
    'Em andamento  •  aguardando lançamentos para calcular projeções.':
        'In progress  •  add transactions to calculate projections.',
    'Comparação': 'Comparison', 'Consequências': 'Consequences',
    'Visão por Metas': 'Goals Overview',
    'Otimista': 'Optimistic', 'Planejado': 'Planned', 'Pessimista': 'Pessimistic',
    'Automático': 'Automatic', 'Todos': 'All', 'Todas': 'All',
    # contacts
    'Gerencie seus fornecedores, clientes e familiares em um só lugar.':
        'Manage suppliers, clients and family contacts in one place.',
    'Buscar no app...': 'Search the app...',
    'Buscar por nome, razão social ou observações...':
        'Search names, companies or notes...',
    'Ordenar por': 'Sort By', 'Nome / Razão Social': 'Name / Company',
    'Tipo ↕': 'Type ↕', 'Telefone': 'Phone',
    'Última atividade': 'Last Activity',
    'Nenhum contato cadastrado nesta conta.': 'No contacts saved in this account.',
    '👤  Novo contato': '👤  New Contact', 'Dados principais': 'Basic Details',
    'Observações': 'Notes', 'Clique para alterar Logo / Foto': 'Click to change logo / photo',
    'Nome ou Razão Social *': 'Name or Company *',
    'Ex.: Supermercado BH, João Silva...': 'E.g. Local Grocery, John Smith...',
    'Tipo de vínculo *': 'Contact Type *', 'Endereço': 'Address',
    'Ex.: Rua das Flores, 123 - Belo Horizonte/MG': 'E.g. 123 Main Street',
    'Informações adicionais sobre este contato...': 'Additional notes about this contact...',
    '🗑  Limpar': '🗑  Clear', '💾  Salvar contato': '💾  Save Contact',
    'Fornecedor': 'Supplier', 'Cliente': 'Client', 'Familiar': 'Family',
    'Funcionário': 'Employee', 'Estabelecimento': 'Business',
    # categories
    'Organize seus gastos e receitas com categorias personalizadas.':
        'Organize income and expenses with custom categories.',
    'Dica': 'Tip', 'Use categorias para ter relatórios mais precisos\ne acompanhar seus limites de gastos.':
        'Use categories to improve reports\nand track your budgets.',
    'Buscar categoria pelo nome...': 'Search categories...',
    'Tipo': 'Type', 'Contexto de Uso': 'Usage Context',
    'Limite / Meta Mensal': 'Monthly Budget / Goal',
    'Progresso': 'Progress', 'Nenhuma categoria cadastrada nesta conta.':
        'No categories created in this account.',
    '🏷️  Nova Categoria': '🏷️  New Category',
    'Nome da Categoria': 'Category Name',
    'Ex.: Viagem, Alimentação, Salário...': 'E.g. Travel, Food, Salary...',
    'Limite de Orçamento (R$/mês)': 'Budget Limit (R$/month)',
    'Deixe 0 para sem limite de orçamento': 'Enter 0 for no budget limit',
    '＋  Adicionar Categoria': '＋  Add Category',
    '💡  Categorias Sugeridas': '💡  Suggested Categories',
    '＋  Adicionar todas': '＋  Add All',
    # profile
    '🏠  Meu Perfil': '🏠  My Profile',
    'Gerencie seus dados, segurança e preferências da sua conta.':
        'Manage your account, security and preferences.',
    'Seus dados estão seguros': 'Your Data Is Protected',
    'Utilizamos criptografia e boas práticas\nde segurança para proteger sua conta.':
        'We use security best practices\nto protect your account.',
    'Membro desde': 'Member Since', 'Dados do Perfil': 'Profile Details',
    '💾  Salvar': '💾  Save',
    'Mantenha suas informações pessoais sempre atualizadas.':
        'Keep your account information up to date.',
    'Renda Mensal (R$)': 'Monthly Income (R$)',
    'Ex: 5.000,00': 'E.g. 5,000.00',
    'Segurança da Conta': 'Account Security',
    'Altere sua senha periodicamente para manter sua conta segura.':
        'Update your password regularly to keep your account secure.',
    '🔒  Atualizar Senha': '🔒  Update Password',
    'Preferências do Aplicativo': 'App Preferences',
    'Personalize sua experiência no sistema.': 'Customize your experience.',
    'Tema da Interface': 'Appearance', 'Escolha o tema visual do aplicativo.':
        'Choose the app appearance.',
    'Idioma': 'Language', 'Idioma do sistema.': 'App language.',
    'Gerenciador Financeiro': 'Finance Manager',
    'Metas financeiras': 'Financial Goals',
    'Relatórios mensais': 'Monthly Reports',
    'Finance Manager': 'Finance Manager',

    'Notificações': 'Notifications',
    'Receba avisos sobre metas e vencimentos.':
        'Receive goal and due-date reminders.',
    'Ativadas': 'Enabled',
    'Privacidade e Dados': 'Privacy and Data',
    'Suas informações e dados financeiros estão protegidos.':
        'Your financial information is protected.',
    'Trocar Senha': 'Change Password', 'Senha Atual': 'Current Password',
    'Nova Senha': 'New Password', 'Confirmar Nova Senha': 'Confirm New Password',
    # common option values (internal values are preserved by dropdown wrappers)
    'Receita': 'Income', 'Despesa': 'Expense', 'Pessoal': 'Personal',
    'Curto': 'Short', 'Médio': 'Medium', 'Longo': 'Long',
    'CURTO': 'SHORT', 'MEDIO': 'MEDIUM', 'LONGO': 'LONG',
    '3 Meses': '3 Months', '6 Meses': '6 Months', '12 Meses': '12 Months',
    '1 Ano': '1 Year', '2 Anos': '2 Years', '3 Anos': '3 Years', '5 Anos': '5 Years',
    'Alimentação': 'Food', 'Transporte': 'Transportation', 'Moradia': 'Housing',
    'Lazer': 'Leisure', 'Salário': 'Salary', 'Educação': 'Education',
    'Viagem': 'Travel', 'Água': 'Water', 'Energia': 'Electricity',
    'Internet': 'Internet', 'Freelance': 'Freelance',
}


# Additional dynamically composed sections, diagnostic descriptions and dialogs.
TRADUCOES.update({
    'Modo demonstração': 'Demo Mode',
    '✦  Assistente IA': '✦  AI Assistant',
    '✦  Conversa': '✦  Conversation',
    'Converse sobre suas finanças. Os valores abaixo vêm da sua conta.':
        'Ask about your finances. All figures come from your account.',
    'Respostas personalizadas': 'Personalized Answers',
    '↑ Receitas do mês': '↑ Monthly Income',
    '↓ Despesas do mês': '↓ Monthly Expenses',
    'Ainda não há lançamentos para mostrar.': 'No transactions to display yet.',
    'Comparativo com o mês anterior': 'Compared with the previous month',
    'Nenhuma transação cadastrada nesta conta. O relatório será preenchido com seus dados reais.':
        'This account has no transactions yet. Your report will use actual account records.',
    'Sem despesas no período selecionado.': 'No expenses in the selected period.',
    'Relatório salvo com sucesso.': 'Report saved successfully.',
    'Relatório': 'Report', 'Lançamento': 'Transaction',
    'Diagnóstico mensal com score e orientações baseadas só na conta logada.':
        'Monthly financial assessment based on your account data.',
    'Orientações para este mês': 'Recommendations for This Month',
    'Saídas registradas': 'Recorded Expenses',
    'Nenhuma despesa registrada neste mês.': 'No expenses recorded this month.',
    '% da renda deste mês está comprometida com despesas.':
        '% of this month\'s income goes toward expenses.',
    'Aguardando dados': 'Waiting for Data', 'Boa': 'Good',
    'Regular': 'Fair', 'Crítica': 'Critical',
    'Cadastre receitas ou despesas neste mês para receber uma avaliação.':
        'Add income or expenses this month to receive an assessment.',
    'Adicione os lançamentos do mês para acompanhar sua situação financeira.':
        'Add monthly transactions to assess your finances.',
    'As avaliações futuras serão calculadas com seus dados reais, sem exemplos automáticos.':
        'Future assessments will use real account data, not automatic examples.',
    'Há despesas registradas, mas nenhuma receita neste mês.':
        'Expenses are recorded, but there is no income this month.',
    'Registre suas receitas para avaliar quanto da renda está comprometida.':
        'Add income to see what share is used for expenses.',
    'Revise as despesas cadastradas e identifique quais são prioritárias.':
        'Review your expenses and prioritize essential payments.',
    'Suas despesas ultrapassaram as receitas do mês.':
        'Your monthly expenses exceeded your income.',
    'Revise primeiro as categorias com os maiores gastos.':
        'Start by reviewing the categories with the highest expenses.',
    'Considere reduzir despesas não essenciais para recuperar o equilíbrio.':
        'Consider cutting nonessential expenses to restore balance.',
    'Há receitas registradas, mas nenhuma despesa no período.':
        'Income is recorded, but there are no expenses in this period.',
    'Registre também suas despesas para ter uma avaliação mais completa.':
        'Record expenses as well to improve the assessment.',
    'Acompanhe seu orçamento ao longo do mês.':
        'Track your budget throughout the month.',
    'O saldo do mês é positivo ou equilibrado.':
        'Your monthly balance is positive or balanced.',
    'Grande parte da renda já está comprometida; acompanhe os próximos gastos.':
        'Much of your income is already committed; watch upcoming expenses.',
    'Revise limites de orçamento por categoria.':
        'Review spending limits for each category.',
    'Acompanhe receitas e despesas regularmente para manter o controle.':
        'Monitor income and expenses regularly to stay in control.',
    'Considere direcionar parte do saldo disponível a uma meta financeira.':
        'Consider allocating part of your available balance to a savings goal.',
    'Parabéns! Você atingiu sua meta!': 'Congratulations! You reached your goal!',
    'O que você gostaria de fazer?': 'What would you like to do next?',
    'Criar finanças aleatórias?': 'Generate Demo Finance Data?',
    'Se preferir começar do zero, cancele.': 'Select Cancel to start with an empty account.',
    '🎲  Gerar dados fictícios': '🎲  Generate Demo Data',
    'Serão gerados dados FICTÍCIOS (receitas, despesas, categorias,\nterceiros, metas e saúde financeira) apenas para demonstração.\n\nEles não representam finanças reais e a conta ficará\nidentificada como "modo demonstração".':
        'FICTIONAL income, expenses, categories, contacts, goals and\nfinancial health records will be created for demonstration only.\n\nThese are not real financial records. The account will be\nclearly marked as a demo account.',
    '⚖  Comparação de Cenários': '⚖  Scenario Comparison',
    '⚖ Comparação': '⚖ Comparison',
    '📑  Principais Consequências': '📑  Key Outcomes',
    '📑 Consequências': '📑 Consequences',
    '🎯  Visão por Metas': '🎯  Goals Overview',
    '🎯 Visão por Metas': '🎯 Goals Overview',
    'Despesas Variáveis': 'Variable Expenses',
    'O que acontece com você em cada cenário.': 'What each scenario could mean for you.',
    'Receitas e despesas do período e o que sobra em cada cenário.':
        'Period income, expenses and projected remaining balances.',
    'Você ainda não salvou nenhum cenário.': 'You have no saved scenarios yet.',
    'Carregar cenário': 'Load Scenario', 'Carregar cenário salvo': 'Load Saved Scenario',
    'Excluir cenário': 'Delete Scenario', 'Salvar cenário': 'Save Scenario',
    'Cenário': 'Scenario', 'Cenário excluído': 'Scenario Deleted',
    'Cenário não encontrado': 'Scenario Not Found',
    'Cenário excluído com sucesso.': 'Scenario deleted successfully.',
    'Cenário salvo na sua conta.': 'Scenario saved to your account.',
    'O cenário já foi excluído ou pertence a outra conta.':
        'This scenario was deleted or belongs to another account.',
    'Projeções indisponíveis': 'Projections Unavailable',
    '✔ Meta concluída': '✔ Goal Completed',
})

# Safe partial strings that occur in dynamically formatted UI labels.
# These are deliberately restricted to longer interface phrases.
SUBSTITUICOES = (
    ('  Valor alvo', '  Target'), ('  Já guardado', '  Saved'),
    ('  Alvo', '  Target'), ('  Guardado', '  Saved'),
    ('  Progresso', '  Progress'), ('  Mensal', '  Monthly'),
    ('  Previsão', '  Forecast'), ('  Prazo', '  Deadline'),
    ('  Membro desde ', '  Member since '),
    (' meta(s) cadastrada(s)', ' goal(s) registered'),
    (' cadastradas', ' registered'), ('  •  aguardando', '  •  waiting'),
    ('Mostrando ', 'Showing '), (' lançamentos.', ' transactions.'),
    ('% do valor-alvo guardado', '% of target saved'),
    ('Atinge em:', 'Target date:'), ('Aporte:', 'Contribution:'),
    ('Previsão:', 'Forecast:'), ('Faltaria no prazo:', 'Shortfall at deadline:'),
)


def traduzir(valor):
    """Translate an application UI string to English, leaving raw data intact."""
    if not isinstance(valor, str) or not valor or obter_idioma() != "en_US":
        return valor
    exato = TRADUCOES.get(valor)
    if exato is not None:
        return exato
    # Preserve padding and emoji prefix from compact buttons.
    match = re.match(r'^(\s*(?:[📊❤️🤖💰🎯🔮📄🤝🏷️👤🔍🗑️💾＋↻🎲📂↑⚙️⏻🚪🌙] ?)*\s*)(.*?)(\s*)$', valor, re.S)
    if match and match.group(2) in TRADUCOES:
        return match.group(1) + TRADUCOES[match.group(2)] + match.group(3)
    resultado = valor
    for origem, destino in SUBSTITUICOES:
        if origem in resultado:
            resultado = resultado.replace(origem, destino)
    return resultado


def _traduzir_atributos(kwargs):
    for prop in ('text', 'placeholder_text'):
        if prop in kwargs:
            kwargs[prop] = traduzir(kwargs[prop])


def instalar_idioma(ctk):
    """Aplica traduções somente à interface, nunca aos dados do banco."""
    if getattr(ctk, '_financas_english_installed', False):
        return
    ctk._financas_english_installed = True

    from views.tema import preparar_cores_widget

    nomes = ('CTk', 'CTkToplevel', 'CTkFrame', 'CTkScrollableFrame',
             'CTkLabel', 'CTkButton', 'CTkEntry', 'CTkSwitch', 'CTkCheckBox',
             'CTkRadioButton', 'CTkOptionMenu', 'CTkComboBox',
             'CTkSegmentedButton', 'CTkTabview', 'CTkProgressBar',
             'CTkSlider', 'CTkTextbox', 'CTkInputDialog', 'CTkScrollbar')
    for nome in nomes:
        cls = getattr(ctk, nome, None)
        if cls is None:
            continue
        original_init = cls.__init__

        @wraps(original_init)
        def novo_init(self, *args, __original=original_init, **kwargs):
            kwargs = dict(kwargs)
            _traduzir_atributos(kwargs)
            preparar_cores_widget(kwargs)
            return __original(self, *args, **kwargs)
        cls.__init__ = novo_init

        if hasattr(cls, 'configure'):
            original_config = cls.configure
            @wraps(original_config)
            def novo_config(self, *args, __original=original_config, **kwargs):
                kwargs = dict(kwargs)
                _traduzir_atributos(kwargs)
                preparar_cores_widget(kwargs)
                return __original(self, *args, **kwargs)
            cls.configure = novo_config

    # Dropdowns retain the original database enum values for .get()/callbacks.
    for nome in ('CTkOptionMenu', 'CTkComboBox', 'CTkSegmentedButton'):
        cls = getattr(ctk, nome, None)
        if cls is None:
            continue
        base_init = cls.__init__
        base_config = cls.configure
        base_get = cls.get
        base_set = cls.set

        @wraps(base_init)
        def dropdown_init(self, *args, __original=base_init, **kwargs):
            kwargs = dict(kwargs)
            originals = kwargs.get('values')
            self._idioma_frente = {}
            self._idioma_verso = {}
            if originals:
                for item in originals:
                    novo = traduzir(item)
                    self._idioma_frente[item] = novo
                    self._idioma_verso[novo] = item
                kwargs['values'] = [self._idioma_frente[item] for item in originals]
            cmd = kwargs.get('command')
            if cmd is not None:
                kwargs['command'] = lambda item, _cmd=cmd, _self=self: _cmd(_self._idioma_verso.get(item, item))
            __original(self, *args, **kwargs)
        cls.__init__ = dropdown_init

        @wraps(base_config)
        def dropdown_config(self, *args, __original=base_config, **kwargs):
            kwargs = dict(kwargs)
            if 'values' in kwargs:
                original_values = kwargs['values']
                self._idioma_frente = {v: traduzir(v) for v in original_values}
                self._idioma_verso = {traduzir(v): v for v in original_values}
                kwargs['values'] = list(self._idioma_frente.values())
            if 'command' in kwargs:
                cmd = kwargs['command']
                if cmd is not None:
                    kwargs['command'] = lambda item, _cmd=cmd, _self=self: _cmd(_self._idioma_verso.get(item, item))
            return __original(self, *args, **kwargs)
        cls.configure = dropdown_config

        @wraps(base_get)
        def dropdown_get(self, *args, __original=base_get, **kwargs):
            value = __original(self, *args, **kwargs)
            return self._idioma_verso.get(value, value)
        cls.get = dropdown_get

        @wraps(base_set)
        def dropdown_set(self, value, *args, __original=base_set, **kwargs):
            return __original(self, self._idioma_frente.get(value, value), *args, **kwargs)
        cls.set = dropdown_set

    # Tabs can be addressed by their original names in application logic.
    tab = getattr(ctk, 'CTkTabview', None)
    if tab is not None:
        orig_add = tab.add
        orig_tab = tab.tab
        orig_set = tab.set
        orig_get = tab.get
        @wraps(orig_add)
        def add(self, name, *args, **kw):
            if not hasattr(self, '_idioma_abas'):
                self._idioma_abas = {}
            self._idioma_abas[traduzir(name)] = name
            return orig_add(self, traduzir(name), *args, **kw)
        @wraps(orig_tab)
        def lookup(self, name, *args, **kw):
            return orig_tab(self, traduzir(name), *args, **kw)
        @wraps(orig_set)
        def set_tab(self, name, *args, **kw):
            return orig_set(self, traduzir(name), *args, **kw)
        @wraps(orig_get)
        def get_tab(self, *args, **kw):
            value = orig_get(self, *args, **kw)
            return getattr(self, '_idioma_abas', {}).get(value, value)
        tab.add, tab.tab, tab.set, tab.get = add, lookup, set_tab, get_tab

    # Canvas text is drawn by tkinter, not CustomTkinter.
    import tkinter as tk
    canvas_create_text = tk.Canvas.create_text
    @wraps(canvas_create_text)
    def localized_canvas_text(self, *args, **kwargs):
        if 'text' in kwargs:
            kwargs['text'] = traduzir(kwargs['text'])
        return canvas_create_text(self, *args, **kwargs)
    tk.Canvas.create_text = localized_canvas_text

    # Window captions are native Tk titles and need separate localization.
    for window_name in ('CTk', 'CTkToplevel'):
        cls = getattr(ctk, window_name, None)
        if cls is None or not hasattr(cls, 'title'):
            continue
        original_title = cls.title
        @wraps(original_title)
        def translated_title(self, value=None, __original=original_title):
            if value is None:
                return __original(self)
            return __original(self, traduzir(value))
        cls.title = translated_title

    from tkinter import messagebox
    for name in ('showinfo', 'showwarning', 'showerror', 'askyesno', 'askokcancel', 'askretrycancel', 'askyesnocancel'):
        base = getattr(messagebox, name)
        @wraps(base)
        def translated_messagebox(*args, __original=base, **kwargs):
            args = list(args)
            for i in range(min(2, len(args))):
                args[i] = traduzir(args[i])
            for key in ('title', 'message', 'detail'):
                if key in kwargs:
                    kwargs[key] = traduzir(kwargs[key])
            return __original(*args, **kwargs)
        setattr(messagebox, name, translated_messagebox)


# Compatibilidade com código de versões antigas.
instalar_idioma_ingles = instalar_idioma

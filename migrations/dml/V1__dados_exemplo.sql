-- ============================================================
-- DML — Dados iniciais de demonstração
-- Execute SOMENTE se quiser popular o banco com dados de exemplo.
-- O aplicativo foi projetado para iniciar VAZIO.
-- ============================================================

USE gerenciador_financeiro;


-- ============================================================
-- USUÁRIOS
-- ============================================================

INSERT INTO usuario
    (nome, email, senha_hash, tipo_perfil, renda_mensal, foto_perfil)
VALUES
    ('João Silva', 'joao@email.com', 'hash_senha_joao', 'PESSOAL', 3500.00, NULL),
    ('Maria Oliveira', 'maria@email.com', 'hash_senha_maria', 'PESSOAL', 2800.00, NULL),
    ('Empresa Silva LTDA', 'contato@empresasilva.com', 'hash_senha_empresa', 'PJ', 12700.00, NULL);


-- ============================================================
-- CATEGORIAS - JOÃO
-- ============================================================

INSERT INTO categoria
    (id_usuario, nome, tipo, escopo, limite_orcamento)
VALUES
    (1, 'Salário', 'RECEITA', 'PESSOAL', NULL),
    (1, 'Alimentação', 'DESPESA', 'PESSOAL', 800.00),
    (1, 'Transporte', 'DESPESA', 'PESSOAL', 400.00),
    (1, 'Moradia', 'DESPESA', 'PESSOAL', 1200.00),
    (1, 'Lazer', 'DESPESA', 'PESSOAL', 300.00),
    (1, 'Freelance', 'RECEITA', 'PESSOAL', NULL);


-- ============================================================
-- CATEGORIAS - MARIA
-- ============================================================

INSERT INTO categoria
    (id_usuario, nome, tipo, escopo, limite_orcamento)
VALUES
    (2, 'Salário', 'RECEITA', 'PESSOAL', NULL),
    (2, 'Alimentação', 'DESPESA', 'PESSOAL', 700.00),
    (2, 'Transporte', 'DESPESA', 'PESSOAL', 350.00),
    (2, 'Estudos', 'DESPESA', 'PESSOAL', 500.00),
    (2, 'Lazer', 'DESPESA', 'PESSOAL', 250.00);


-- ============================================================
-- CATEGORIAS - EMPRESA
-- ============================================================

INSERT INTO categoria
    (id_usuario, nome, tipo, escopo, limite_orcamento)
VALUES
    (3, 'Vendas', 'RECEITA', 'PJ', NULL),
    (3, 'Fornecedores', 'DESPESA', 'PJ', 5000.00),
    (3, 'Marketing', 'DESPESA', 'PJ', 2000.00),
    (3, 'Equipamentos', 'DESPESA', 'PJ', 3000.00);


-- ============================================================
-- TERCEIROS - JOÃO
-- ============================================================

INSERT INTO terceiro
    (id_usuario, nome, relacao, foto_perfil)
VALUES
    (1, 'Mercado Central', 'Comércio', NULL),
    (1, 'Posto Avenida', 'Transporte', NULL),
    (1, 'Imobiliária Central', 'Moradia', NULL),
    (1, 'Carlos Mendes', 'Cliente', NULL);


-- ============================================================
-- TERCEIROS - MARIA
-- ============================================================

INSERT INTO terceiro
    (id_usuario, nome, relacao, foto_perfil)
VALUES
    (2, 'Supermercado Brasil', 'Comércio', NULL),
    (2, 'Faculdade XYZ', 'Instituição de ensino', NULL),
    (2, 'João Transportes', 'Transporte', NULL);


-- ============================================================
-- TERCEIROS - EMPRESA
-- ============================================================

INSERT INTO terceiro
    (id_usuario, nome, relacao, foto_perfil)
VALUES
    (3, 'Fornecedor ABC', 'Fornecedor', NULL),
    (3, 'Agência Digital', 'Marketing', NULL),
    (3, 'Cliente Empresa A', 'Cliente', NULL);


-- ============================================================
-- LANÇAMENTOS - JOÃO
-- ============================================================

INSERT INTO lancamento
(
    id_usuario,
    id_categoria,
    id_terceiro,
    descricao,
    valor,
    tipo,
    status,
    data_vencimento,
    data_pagamento,
    comprovante_url,
    origem_registro
)
VALUES

(1, 1, NULL,
 'Salário mensal',
 3500.00,
 'RECEITA',
 'RECEBIDO',
 '2026-09-05',
 '2026-09-05',
 NULL,
 'MANUAL'),

(1, 2, 1,
 'Compras do supermercado',
 320.50,
 'DESPESA',
 'PAGO',
 '2026-09-06',
 '2026-09-06',
 NULL,
 'MANUAL'),

(1, 2, 1,
 'Compras da semana',
 180.00,
 'DESPESA',
 'PAGO',
 '2026-09-13',
 '2026-09-13',
 NULL,
 'MANUAL'),

(1, 3, 2,
 'Combustível',
 150.00,
 'DESPESA',
 'PAGO',
 '2026-09-10',
 '2026-09-10',
 NULL,
 'MANUAL'),

(1, 4, 3,
 'Aluguel',
 1000.00,
 'DESPESA',
 'PAGO',
 '2026-09-08',
 '2026-09-08',
 NULL,
 'MANUAL'),

(1, 5, NULL,
 'Cinema e alimentação',
 120.00,
 'DESPESA',
 'PENDENTE',
 '2026-09-25',
 NULL,
 NULL,
 'MANUAL'),

(1, 6, 4,
 'Desenvolvimento de site',
 800.00,
 'RECEITA',
 'PENDENTE',
 '2026-09-30',
 NULL,
 NULL,
 'MANUAL');


-- ============================================================
-- LANÇAMENTOS - MARIA
-- ============================================================

INSERT INTO lancamento
(
    id_usuario,
    id_categoria,
    id_terceiro,
    descricao,
    valor,
    tipo,
    status,
    data_vencimento,
    data_pagamento,
    comprovante_url,
    origem_registro
)
VALUES

(2, 7, NULL,
 'Salário mensal',
 2800.00,
 'RECEITA',
 'RECEBIDO',
 '2026-09-05',
 '2026-09-05',
 NULL,
 'MANUAL'),

(2, 8, 5,
 'Compras do mês',
 450.00,
 'DESPESA',
 'PAGO',
 '2026-09-07',
 '2026-09-07',
 NULL,
 'MANUAL'),

(2, 9, 7,
 'Transporte',
 180.00,
 'DESPESA',
 'PAGO',
 '2026-09-09',
 '2026-09-09',
 NULL,
 'MANUAL'),

(2, 10, 6,
 'Mensalidade da faculdade',
 400.00,
 'DESPESA',
 'PENDENTE',
 '2026-09-20',
 NULL,
 NULL,
 'MANUAL'),

(2, 11, NULL,
 'Saída com amigos',
 150.00,
 'DESPESA',
 'PENDENTE',
 '2026-09-28',
 NULL,
 NULL,
 'MANUAL');


-- ============================================================
-- LANÇAMENTOS - EMPRESA
-- ============================================================

INSERT INTO lancamento
(
    id_usuario,
    id_categoria,
    id_terceiro,
    descricao,
    valor,
    tipo,
    status,
    data_vencimento,
    data_pagamento,
    comprovante_url,
    origem_registro
)
VALUES

(3, 12, 10,
 'Venda de projeto',
 8500.00,
 'RECEITA',
 'RECEBIDO',
 '2026-09-03',
 '2026-09-03',
 NULL,
 'MANUAL'),

(3, 13, 8,
 'Compra de materiais',
 3200.00,
 'DESPESA',
 'PAGO',
 '2026-09-05',
 '2026-09-05',
 NULL,
 'MANUAL'),

(3, 14, 9,
 'Campanha de marketing',
 1200.00,
 'DESPESA',
 'PAGO',
 '2026-09-10',
 '2026-09-10',
 NULL,
 'MANUAL'),

(3, 15, NULL,
 'Compra de computador',
 2500.00,
 'DESPESA',
 'PENDENTE',
 '2026-09-25',
 NULL,
 NULL,
 'MANUAL'),

(3, 12, 10,
 'Projeto de manutenção',
 4200.00,
 'RECEITA',
 'PENDENTE',
 '2026-09-30',
 NULL,
 NULL,
 'MANUAL');


-- ============================================================
-- METAS
-- ============================================================

INSERT INTO meta_reserva
(
    id_usuario,
    descricao,
    valor_alvo,
    valor_atual,
    prazo,
    data_criacao,
    data_limite,
    concluida,
    data_conclusao,
    celebracao_exibida
)
VALUES

(
    1,
    'Reserva de emergência',
    10000.00,
    3500.00,
    'LONGO',
    '2026-09-01',
    '2027-12-31',
    FALSE,
    NULL,
    FALSE
),

(
    1,
    'Comprar notebook',
    4000.00,
    1800.00,
    'MEDIO',
    '2026-09-01',
    '2026-12-31',
    FALSE,
    NULL,
    FALSE
),

(
    2,
    'Viagem de férias',
    5000.00,
    1200.00,
    'MEDIO',
    '2026-09-01',
    '2027-01-30',
    FALSE,
    NULL,
    FALSE
),

(
    3,
    'Novo equipamento profissional',
    15000.00,
    6000.00,
    'LONGO',
    '2026-09-01',
    '2027-12-31',
    FALSE,
    NULL,
    FALSE
);


-- ============================================================
-- SAÚDE FINANCEIRA
-- ============================================================

INSERT INTO saude_financeira
(
    id_usuario,
    score,
    data_calculo,
    plano_acao_json
)
VALUES

(
    1,
    720,
    '2026-09-30',
    JSON_ARRAY(
        'Manter controle das despesas',
        'Aumentar a reserva de emergência',
        'Evitar ultrapassar os limites das categorias'
    )
),

(
    2,
    650,
    '2026-09-30',
    JSON_ARRAY(
        'Reduzir gastos com lazer',
        'Acompanhar despesas de alimentação',
        'Aumentar o valor destinado às metas'
    )
),

(
    3,
    810,
    '2026-09-30',
    JSON_ARRAY(
        'Manter controle do orçamento',
        'Acompanhar despesas operacionais',
        'Manter reserva para investimentos'
    )
);

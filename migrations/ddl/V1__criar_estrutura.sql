-- ============================================================
-- DDL — Criação do banco e tabelas
-- Script inicial de estrutura do Gerenciador de Finanças
-- ============================================================

CREATE DATABASE IF NOT EXISTS gerenciador_financeiro;

USE gerenciador_financeiro;


-- ============================================================
-- USUÁRIO
-- ============================================================

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_perfil ENUM('PESSOAL', 'PJ') NOT NULL DEFAULT 'PESSOAL',
    renda_mensal DECIMAL(10,2),
    foto_perfil VARCHAR(255),
    modo_demo BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario)
);


-- ============================================================
-- CATEGORIA
-- ============================================================

CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('RECEITA', 'DESPESA') NOT NULL,
    escopo ENUM('PESSOAL', 'PJ') NOT NULL,
    limite_orcamento DECIMAL(10,2),
    ativa BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (id_categoria),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);


-- ============================================================
-- TERCEIRO
-- ============================================================

CREATE TABLE terceiro (
    id_terceiro INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    relacao VARCHAR(50) NOT NULL,
    foto_perfil VARCHAR(255),
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_terceiro),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);


-- ============================================================
-- LANÇAMENTO
-- ============================================================

CREATE TABLE lancamento (
    id_lancamento INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_categoria INT NOT NULL,
    id_terceiro INT,
    tipo ENUM('RECEITA', 'DESPESA') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    status ENUM('PAGO', 'PENDENTE', 'RECEBIDO') NOT NULL DEFAULT 'PENDENTE',
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    comprovante_url VARCHAR(255),
    origem_registro VARCHAR(50),
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_lancamento),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria),

    FOREIGN KEY (id_terceiro)
        REFERENCES terceiro(id_terceiro)
        ON DELETE SET NULL
);


-- ============================================================
-- META / RESERVA
-- ============================================================

CREATE TABLE meta_reserva (
    id_meta INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    descricao VARCHAR(150) NOT NULL,
    valor_alvo DECIMAL(10,2) NOT NULL,
    valor_atual DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    prazo ENUM('CURTO', 'MEDIO', 'LONGO') NOT NULL,
    data_criacao DATE NOT NULL,
    data_limite DATE NOT NULL,
    concluida BOOLEAN NOT NULL DEFAULT FALSE,
    data_conclusao DATE,
    celebracao_exibida BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (id_meta),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);


-- ============================================================
-- META — HISTÓRICO DE APORTES
-- ============================================================

CREATE TABLE meta_aporte (
    id_aporte INT AUTO_INCREMENT,
    id_meta INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_aporte DATE NOT NULL,

    PRIMARY KEY (id_aporte),

    FOREIGN KEY (id_meta)
        REFERENCES meta_reserva(id_meta)
        ON DELETE CASCADE
);


-- ============================================================
-- SAÚDE FINANCEIRA
-- ============================================================

CREATE TABLE saude_financeira (
    id_saude INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    score INT NOT NULL,
    data_calculo DATE NOT NULL,
    plano_acao_json JSON NOT NULL,

    PRIMARY KEY (id_saude),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);


-- ============================================================
-- SIMULAÇÃO
-- ============================================================

CREATE TABLE simulacao (
    id_simulacao INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    parametros_json JSON,
    resultados_json JSON,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_simulacao),

    FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

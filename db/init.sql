-- =========================
-- ENUMS
-- =========================

CREATE TYPE status_consulta AS ENUM (
  'EM_ATENDIMENTO',
  'CONFIRMADA',
  'REALIZADA',
  'CANCELADA'
);

CREATE TYPE status_lote AS ENUM (
  'VENCIDO',
  'DISPONIVEL',
  'ESGOTADO'
);

CREATE TYPE tipo_usuario AS ENUM (
  'MEDICO',
  'FARMACEUTICO',
  'RECEPCIONISTA',
  'ADMINISTRADOR'
);

CREATE TYPE tipo_entrega AS ENUM (
  'PROTOCOLO',
  'RECEITA_PARTICULAR'
);

-- =========================
-- TABELAS BÁSICAS
-- =========================

CREATE TABLE pessoa (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(255),
  cpf VARCHAR(255) UNIQUE,
  email VARCHAR(255),
  telefone VARCHAR(255),
  sexo CHAR(1),
  data_nascimento TIMESTAMP,
  endereco VARCHAR(255)
);

CREATE TABLE funcionario (
  id BIGSERIAL PRIMARY KEY,
  matricula INTEGER UNIQUE NOT NULL,
  data_admissao TIMESTAMP,
  fk_pessoa BIGINT UNIQUE REFERENCES pessoa(id)
);

CREATE TABLE usuario_sistema (
  id BIGSERIAL PRIMARY KEY,
  login VARCHAR(255) UNIQUE,
  senha VARCHAR(255),
  ativo BOOLEAN NOT NULL,
  tipo_user tipo_usuario,
  fk_usuario BIGINT UNIQUE REFERENCES funcionario(id)
);

-- =========================
-- CARGOS
-- =========================

CREATE TABLE medico (
  id BIGINT PRIMARY KEY REFERENCES funcionario(id),
  crm VARCHAR(255) UNIQUE NOT NULL,
  especialidade VARCHAR(255),
  nome_fantasia VARCHAR(255)
);

CREATE TABLE farmaceutico (
  id BIGINT PRIMARY KEY REFERENCES funcionario(id),
  crf VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE administrador (
  id BIGINT PRIMARY KEY REFERENCES funcionario(id),
  setor VARCHAR(255)
);

CREATE TABLE recepcionista (
  id BIGINT PRIMARY KEY REFERENCES funcionario(id),
  setor VARCHAR(255)
);

-- =========================
-- PACIENTE
-- =========================

CREATE TABLE paciente (
  id BIGSERIAL PRIMARY KEY,
  numero_sus VARCHAR(255) UNIQUE NOT NULL,
  fk_pessoa BIGINT UNIQUE REFERENCES pessoa(id)
);

CREATE TABLE protocolo (
  id BIGSERIAL PRIMARY KEY,
  codigo VARCHAR(255),
  status BOOLEAN DEFAULT TRUE,
  data_gerada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_entrega TIMESTAMP,
  fk_farmaceutico BIGINT REFERENCES farmaceutico(id)
);

CREATE TABLE consulta (
  id BIGSERIAL PRIMARY KEY,
  data_consulta TIMESTAMP,
  descricao VARCHAR(255),
  tipo_consulta VARCHAR(255),
  status status_consulta,
  fk_medico BIGINT NOT NULL REFERENCES medico(id),
  fk_paciente BIGINT NOT NULL REFERENCES paciente(id),
  fk_protocolo BIGINT UNIQUE REFERENCES protocolo(id)
);

-- =========================
-- FARMÁCIA
-- =========================

CREATE TABLE medicamento (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(255) UNIQUE
);

CREATE TABLE tipo_medicamento (
  id BIGSERIAL PRIMARY KEY,
  descricao VARCHAR(255),
  tipo VARCHAR(255), -- comprimido, injetável, líquido etc
  unidade_medida VARCHAR(255),
  quantidade_caixa INTEGER NOT NULL,
  estoque_minimo INTEGER NOT NULL,
  fk_medicamento BIGINT NOT NULL REFERENCES medicamento(id),

  CONSTRAINT unique_tipo UNIQUE (tipo, quantidade_caixa, unidade_medida, fk_medicamento)
);

CREATE TABLE lote_medicamento (
  id BIGSERIAL PRIMARY KEY,
  quantidade_entrada INTEGER NOT NULL,
  quantidade_estoque INTEGER NOT NULL,
  data_fabricacao TIMESTAMP,
  data_validade TIMESTAMP,
  status status_lote,
  fk_tipo_medicamento BIGINT NOT NULL REFERENCES tipo_medicamento(id)
);

CREATE TABLE protocolo_medicamento (
  fk_protocolo BIGINT REFERENCES protocolo(id),
  fk_medicamento BIGINT REFERENCES medicamento(id),
  PRIMARY KEY (fk_protocolo, fk_medicamento)
);

CREATE TABLE entrega_farmacia (
  id BIGSERIAL PRIMARY KEY,
  data_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  tipo_entrega tipo_entrega NOT NULL,
  justificativa TEXT,
  fk_paciente BIGINT DEFAULT NULL REFERENCES paciente(id),
  fk_farmaceutico BIGINT NOT NULL REFERENCES farmaceutico(id),
  fk_protocolo BIGINT UNIQUE DEFAULT NULL REFERENCES protocolo(id),

  CONSTRAINT chk_entrega_protocolo CHECK (
    (tipo_entrega = 'PROTOCOLO' AND fk_protocolo IS NOT NULL)
    OR
    (tipo_entrega = 'RECEITA_PARTICULAR' AND fk_protocolo IS NULL)
  )
);

-- =========================
-- DADOS BASE
-- =========================

INSERT INTO pessoa (nome, cpf) VALUES
('Carlos Médico', '33333333333'),
('Ana Farmácia', '44444444444');

INSERT INTO funcionario (matricula, data_admissao, fk_pessoa) VALUES
(1001, NOW(), 1),
(1002, NOW(), 2);

INSERT INTO medico (id, crm) VALUES (1, 'CRM12345');
INSERT INTO farmaceutico (id, crf) VALUES (2, 'CRF54321');

INSERT INTO usuario_sistema (login, senha, ativo, tipo_user, fk_usuario) VALUES
(
    'medico',
    'scrypt_hash_aqui',
    true,
    'MEDICO',
    1
),
(
    'farmacia',
    'scrypt_hash_aqui',
    true,
    'FARMACEUTICO',
    2
);

-- =========================
-- 10 MEDICAMENTOS
-- =========================

INSERT INTO medicamento (nome) VALUES
('Amoxicilina'),
('Ibuprofeno'),
('Omeprazol'),
('Metformina'),
('Losartana'),
('Simvastatina'),
('Azitromicina'),
('Prednisona'),
('Fluoxetina'),
('Cetirizina');

-- =========================
-- 2 TIPOS POR MEDICAMENTO
-- =========================

INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento)
SELECT 
    m.nome || ' 500mg',
    'Comprimido',
    'mg',
    20,
    10,
    m.id
FROM medicamento m;

INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento)
SELECT 
    m.nome || ' 100ml',
    'Liquido',
    'ml',
    1,
    5,
    m.id
FROM medicamento m;

-- =========================
-- 2 LOTES POR TIPO
-- =========================

DO $$
DECLARE
    tipo_id BIGINT;
BEGIN
    FOR tipo_id IN SELECT id FROM tipo_medicamento LOOP
        INSERT INTO lote_medicamento 
        (quantidade_entrada, quantidade_estoque, data_fabricacao, data_validade, status, fk_tipo_medicamento)
        VALUES
        (100, 100, '2025-01-01', '2026-12-31', 'DISPONIVEL', tipo_id),
        (50, 50, '2025-06-01', '2027-01-31', 'DISPONIVEL', tipo_id);
    END LOOP;
END$$;

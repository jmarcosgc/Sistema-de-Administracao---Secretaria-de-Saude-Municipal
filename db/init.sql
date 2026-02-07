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
  login VARCHAR(255),
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
-- PACIENTE / CONSULTA
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
-- FARMÁCIA / ESTOQUE
-- =========================

CREATE TABLE medicamento (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(255) UNIQUE
);

CREATE TABLE tipo_medicamento (
  id BIGSERIAL PRIMARY KEY,
  descricao VARCHAR(255),
  tipo VARCHAR(255),
  unidade_medida VARCHAR(255),
  quantidade_caixa INTEGER NOT NULL,
  estoque_minimo INTEGER NOT NULL,
  fk_medicamento BIGINT NOT NULL REFERENCES medicamento(id)
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
-- DADOS DE TESTE
-- =========================

INSERT INTO pessoa (nome, cpf, email, telefone, sexo, data_nascimento, endereco) VALUES
('João da Silva', '11111111111', 'joao@email.com', '999999999', 'M', '1985-05-10', 'Rua A'),
('Maria Souza', '22222222222', 'maria@email.com', '988888888', 'F', '1990-08-20', 'Rua B'),
('Carlos Médico', '33333333333', 'carlos@medico.com', '977777777', 'M', '1978-03-15', 'Rua C'),
('Ana Farmácia', '44444444444', 'ana@farmacia.com', '966666666', 'F', '1982-11-02', 'Rua D');

INSERT INTO funcionario (matricula, data_admissao, fk_pessoa) VALUES
(1001, '2020-01-01', 3),
(1002, '2021-02-01', 4);

INSERT INTO medico (id, crm, especialidade, nome_fantasia)
VALUES (1, 'CRM12345', 'Clínico Geral', 'Dr. Carlos');

INSERT INTO farmaceutico (id, crf)
VALUES (2, 'CRF54321');

INSERT INTO usuario_sistema (login, senha, ativo, tipo_user, fk_usuario) VALUES
('medico', '123', true, 'MEDICO', 1),
('farmacia', '123', true, 'FARMACEUTICO', 2);

INSERT INTO paciente (numero_sus, fk_pessoa) VALUES
('SUS0001', 1),
('SUS0002', 2);

INSERT INTO protocolo (codigo, status)
VALUES ('PROTO-001', true);

INSERT INTO consulta (
  data_consulta, descricao, tipo_consulta, status,
  fk_medico, fk_paciente, fk_protocolo
) VALUES (
  '2024-06-01 10:00',
  'Consulta de rotina',
  'SUS',
  'REALIZADA',
  1,
  1,
  1
);

INSERT INTO medicamento (nome) VALUES
('Dipirona'),
('Paracetamol');

INSERT INTO tipo_medicamento (
  descricao, tipo, unidade_medida,
  quantidade_caixa, estoque_minimo, fk_medicamento
) VALUES
('Dipirona 500mg', 'Comprimido', 'mg', 20, 10, 1),
('Paracetamol 750mg', 'Comprimido', 'mg', 20, 10, 2);

INSERT INTO lote_medicamento (
  quantidade_entrada, quantidade_estoque,
  data_fabricacao, data_validade, status, fk_tipo_medicamento
) VALUES
(100, 100, '2024-01-01', '2026-01-01', 'DISPONIVEL', 1),
(100, 100, '2024-01-01', '2026-01-01', 'DISPONIVEL', 2);

INSERT INTO protocolo_medicamento (fk_protocolo, fk_medicamento) VALUES
(1, 1),
(1, 2);

INSERT INTO entrega_farmacia (
  tipo_entrega, fk_paciente, fk_farmaceutico, fk_protocolo
) VALUES (
  'PROTOCOLO', 1, 2, 1
);

INSERT INTO entrega_farmacia (
  tipo_entrega, justificativa, fk_paciente, fk_farmaceutico
) VALUES (
  'RECEITA_PARTICULAR',
  'Receita particular apresentada pelo paciente',
  2,
  2
);


-- 1️ Inserir pessoa
INSERT INTO pessoa (nome, cpf, email, telefone, sexo, data_nascimento, endereco)
VALUES ('Teste Farmaceutico', '55555555555', 'teste@farmacia.com', '955555555', 'F', '1990-01-01', 'Rua Teste');

-- 2️ Inserir funcionario
INSERT INTO funcionario (matricula, data_admissao, fk_pessoa)
VALUES (1003, '2025-01-01', (SELECT id FROM pessoa WHERE cpf = '55555555555'));

-- 3️ Inserir farmaceutico
INSERT INTO farmaceutico (id, crf)
VALUES ((SELECT id FROM funcionario WHERE matricula = 1003), 'CRF99999');

-- 4️ Opcional: criar usuário no sistema
-- INSERT INTO usuario_sistema (login, senha, ativo, tipo_user, fk_usuario)
-- VALUES ('farmacia_teste', '123456', true, 'FARMACEUTICO', (SELECT id FROM funcionario WHERE matricula = 1003));

-- 1. Limpa os usuários antigos para evitar erro de chave única
DELETE FROM usuario_sistema WHERE login IN ('medico', 'farmacia', 'farmacia_teste');

-- 2. Agora sim, rode os seus INSERTs com as senhas criptografadas:
INSERT INTO usuario_sistema (login, senha, ativo, tipo_user, fk_usuario) VALUES
(
    'medico', 
    'scrypt:32768:8:1$h3V2oIgut2O0H7Yk$7b351eba97fc0c38ba3c79c6cf12237e44d62cbc6ed7a5533cd96197bd7a0435fecc2df68a2728cd33a4fa600418cef693edfc2a29a78234b79dc92e87d50ddc', 
    true, 
    'MEDICO', 
    1
),
(
    'farmacia', 
    'scrypt:32768:8:1$iJKW304pidH62btd$d98b72a8c804044881158a5660a87f879176eb5a42eb9d0d5f8222baf0ab1a00e880b3235125b75946a4e51bda7f84e41ffbfe269eb295acff89b804f5d289de', 
    true, 
    'FARMACEUTICO', 
    2
);

INSERT INTO usuario_sistema (login, senha, ativo, tipo_user, fk_usuario)
<<<<<<< HEAD
VALUES (
    'farmacia_teste', 
    'scrypt:32768:8:1$iJKW304pidH62btd$d98b72a8c804044881158a5660a87f879176eb5a42eb9d0d5f8222baf0ab1a00e880b3235125b75946a4e51bda7f84e41ffbfe269eb295acff89b804f5d289de', 
    true, 
    'FARMACEUTICO', 
    (SELECT id FROM funcionario WHERE matricula = 1003)
);
=======
VALUES ('farmacia_teste', '123456', true, 'FARMACEUTICO', (SELECT id FROM funcionario WHERE matricula = 1003));


-- =========================
-- Inserir 10 medicamentos
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
('Cloridrato de Fluoxetina'),
('Cetirizina');

-- =========================
-- Inserir 2 tipos para cada medicamento
-- =========================

-- Amoxicilina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Amoxicilina 500mg', 'Comprimido', 'mg', 20, 10, 1),
('Amoxicilina 250mg', 'Comprimido', 'mg', 20, 10, 1);

-- Ibuprofeno
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Ibuprofeno 400mg', 'Comprimido', 'mg', 20, 10, 2),
('Ibuprofeno 600mg', 'Comprimido', 'mg', 20, 10, 2);

-- Omeprazol
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Omeprazol 20mg', 'Comprimido', 'mg', 14, 5, 3),
('Omeprazol 40mg', 'Comprimido', 'mg', 14, 5, 3);

-- Metformina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Metformina 500mg', 'Comprimido', 'mg', 30, 10, 4),
('Metformina 850mg', 'Comprimido', 'mg', 30, 10, 4);

-- Losartana
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Losartana 50mg', 'Comprimido', 'mg', 30, 10, 5),
('Losartana 100mg', 'Comprimido', 'mg', 30, 10, 5);

-- Simvastatina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Simvastatina 20mg', 'Comprimido', 'mg', 20, 5, 6),
('Simvastatina 40mg', 'Comprimido', 'mg', 20, 5, 6);

-- Azitromicina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Azitromicina 500mg', 'Comprimido', 'mg', 6, 2, 7),
('Azitromicina 250mg', 'Comprimido', 'mg', 6, 2, 7);

-- Prednisona
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Prednisona 5mg', 'Comprimido', 'mg', 20, 5, 8),
('Prednisona 20mg', 'Comprimido', 'mg', 20, 5, 8);

-- Fluoxetina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Fluoxetina 20mg', 'Comprimido', 'mg', 28, 10, 9),
('Fluoxetina 40mg', 'Comprimido', 'mg', 28, 10, 9);

-- Cetirizina
INSERT INTO tipo_medicamento (descricao, tipo, unidade_medida, quantidade_caixa, estoque_minimo, fk_medicamento) VALUES
('Cetirizina 10mg', 'Comprimido', 'mg', 10, 5, 10),
('Cetirizina 5mg', 'Comprimido', 'mg', 10, 5, 10);

-- =========================
-- Inserir 2 lotes por tipo de medicamento
-- =========================

DO $$
DECLARE
    tipo_id BIGINT;
BEGIN
    FOR tipo_id IN SELECT id FROM tipo_medicamento LOOP
        INSERT INTO lote_medicamento (quantidade_entrada, quantidade_estoque, data_fabricacao, data_validade, status, fk_tipo_medicamento) VALUES
        (100, 100, '2025-01-01', '2026-12-31', 'DISPONIVEL', tipo_id),
        (50, 50, '2025-06-01', '2027-01-31', 'DISPONIVEL', tipo_id);
    END LOOP;
END$$;
>>>>>>> 4b080b9ea6ce3f9936f8eb8947bc7ebfd63a2ee0

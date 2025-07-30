PROJETO RELACIONAL  
	Usuário(CPF, Nome, Fone, Email).
	Técnico(ID Técnico, CPF).
	Tec_Espec(ID_Técnico, Especialidade).
	Solicitante(ID_Solicitante, CPF).
	Ocorrência(ID_Ocorrência, ID_Solicitante, CEP, Número, Status).
	Local(CEP, Número, Complemento, Bairro, Logradouro).
	Analisa(ID_Técnico,ID_Ocorrência)

Criação do Banco de Dados (Query PostgreSQL)
CREATE TABLE Usuario (
  cpf    VARCHAR(11) PRIMARY KEY
           CHECK (cpf ~ '^[0-9]{11}$'),
  nome   VARCHAR(100) NOT NULL,
  fone   VARCHAR(11) NOT NULL UNIQUE
           CHECK (fone ~ '^[0-9]{10,11}$'),
  email  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Local (
  cep         VARCHAR(8)   NOT NULL
                 CHECK (cep ~ '^[0-9]{8}$'),
  numero      INTEGER      NOT NULL
                 CHECK (numero > 0),
  complemento VARCHAR(50),
  bairro      VARCHAR(100),
  logradouro  VARCHAR(200),
  PRIMARY KEY (cep, numero)
);


CREATE TABLE Tecnico (
  id_tecnico SMALLSERIAL     PRIMARY KEY,
  cpf        VARCHAR(11) NOT NULL UNIQUE
                 REFERENCES Usuario(cpf)
                   ON DELETE CASCADE
                   ON UPDATE CASCADE
);

CREATE TABLE Tec_Espec (
  id_tecnico     SMALLINT         NOT NULL
                   REFERENCES Tecnico(id_tecnico)
                     ON DELETE CASCADE
                     ON UPDATE CASCADE,
  especialidade  VARCHAR(50) NOT NULL,
  PRIMARY KEY (id_tecnico, especialidade)
);


CREATE TABLE Solicitante (
  id_solicitante SMALLSERIAL     PRIMARY KEY,
  cpf             VARCHAR(11) NOT NULL UNIQUE
                     REFERENCES Usuario(cpf)
                       ON DELETE CASCADE
                       ON UPDATE CASCADE
);


CREATE TABLE Ocorrencia (
  id_ocorrencia  SMALLSERIAL      PRIMARY KEY,
  id_solicitante SMALLINT         NOT NULL
                   REFERENCES Solicitante(id_solicitante)
                     ON DELETE RESTRICT
                     ON UPDATE CASCADE,
  cep            VARCHAR(8)   NOT NULL,
  numero         INTEGER      NOT NULL,
  status         VARCHAR(20)  NOT NULL
                   CHECK (status IN (
                     'Aberta',
                     'Em Andamento',
                     'Concluída',
                     'Cancelada'
                   )),
  CONSTRAINT fk_ocorr_local
    FOREIGN KEY (cep, numero)
      REFERENCES Local(cep, numero)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE Analisa (
  id_tecnico     SMALLINT NOT NULL
                   REFERENCES Tecnico(id_tecnico)
                     ON DELETE CASCADE
                     ON UPDATE CASCADE,
  id_ocorrencia  SMALLINT NOT NULL
                   REFERENCES Ocorrencia(id_ocorrencia)
                     ON DELETE CASCADE
                     ON UPDATE CASCADE,
  PRIMARY KEY (id_tecnico, id_ocorrencia)
);

Criando índices
B-Tree para consulta de nomes
Vamos utilizar a árvore B por ser um ótimo índice para a comparação de igualdade e como temos como referência o Portal de Iluminação de Sorocaba(https://servicos.sorocaba.sp.gov.br/iluminacao/) uma das principais consultas é com base no nome.
“”
CREATE INDEX idx_usuario_nome
  ON Usuario(nome);
“”
B-Tree para consulta de ID_Protocolo:
Assim como no índice anterior a consulta por ID_Protocolo é bastante usada por isso vamos criar um índice para ela.
“”
CREATE INDEX idx_ocorrencia_id_protocolo
  ON Ocorrencia(id_ocorrencia);
“”
Hash index para o CEP:
Como o índice hash é ótimo para valores limitados, vamos criar esse índice para CEP já que cada cidade possui um intervalo de CEP limitado para ela, assim em consultas de locais, que serão consultas frequentes vamos ter uma melhora de desempenho.
“”
CREATE INDEX idx_local_cep_hash
  ON Local USING hash (cep);
“”

B-Tree para ID_tecnico:
Para a pesquisa rápida de Técnico por ID
“”
CREATE INDEX idx_tecnico_id_tecnico
  ON Tecnico(id_tecnico);
“”


índice Parcial em status da Ocorrência:
Como possivelmente teremos muitas consultas por ocorrências abertas, vamos criar um índice parcial em todas as ocorrências com status de “Aberta”, o objetivo era fazer um índice de agrupamento para status em Ocorrência.
“”
CREATE INDEX idx_ocorr_aberta
  ON Ocorrencia (status)
 WHERE status = 'Aberta';

“”

Inserção de Dados de Teste
“””
INSERT INTO Usuario(cpf, nome, fone, email) VALUES
('00000000001','Ana Silva','11987654321','ana.silva@example.com'),
('00000000002','Bruno Souza','21991234567','bruno.souza@example.com'),
('00000000003','Carla Oliveira','31999887766','carla.oliveira@example.com'),
('00000000004','Daniel Pereira','41998776655','daniel.pereira@example.com'),
('00000000005','Eduarda Costa','51997665544','eduarda.costa@example.com'),
('00000000006','Felipe Ramos','61996554433','felipe.ramos@example.com'),
('00000000007','Gabriela Rocha','71995443322','gabriela.rocha@example.com'),
('00000000008','Henrique Dias','81994332211','henrique.dias@example.com'),
('00000000009','Isabela Martins','91993221100','isabela.martins@example.com'),
('00000000010','João Fernandes','11992110099','joao.fernandes@example.com'),
('00000000011','Karina Alves','21991009988','karina.alves@example.com'),
('00000000012','Leonardo Lima','31990098877','leonardo.lima@example.com'),
('00000000013','Mariana Gomes','41990998866','mariana.gomes@example.com'),
('00000000014','Nicolas Moraes','51989887755','nicolas.moraes@example.com'),
('00000000015','Olívia Pinto','61988776544','olivia.pinto@example.com'),
('00000000016','Pedro Azevedo','71987665433','pedro.azevedo@example.com'),
('00000000017','Queila Barros','81986554322','queila.barros@example.com'),
('00000000018','Rafael Castro','91985443211','rafael.castro@example.com'),
('00000000019','Sofia Fernandes','11984332100','sofia.fernandes@example.com'),
('00000000020','Thiago Santos','21983221099','thiago.santos@example.com');


INSERT INTO Local(cep, numero, complemento, bairro, logradouro) VALUES
('00000001', 1,  'Comp 1',  'Bairro 1',  'Logradouro 1'),
('00000002', 2,  'Comp 2',  'Bairro 2',  'Logradouro 2'),
('00000003', 3,  'Comp 3',  'Bairro 3',  'Logradouro 3'),
('00000004', 4,  'Comp 4',  'Bairro 4',  'Logradouro 4'),
('00000005', 5,  'Comp 5',  'Bairro 5',  'Logradouro 5'),
('00000006', 6,  'Comp 6',  'Bairro 6',  'Logradouro 6'),
('00000007', 7,  'Comp 7',  'Bairro 7',  'Logradouro 7'),
('00000008', 8,  'Comp 8',  'Bairro 8',  'Logradouro 8'),
('00000009', 9,  'Comp 9',  'Bairro 9',  'Logradouro 9'),
('00000010',10,  'Comp 10', 'Bairro 10', 'Logradouro 10'),
('00000011',11,  'Comp 11', 'Bairro 11', 'Logradouro 11'),
('00000012',12,  'Comp 12', 'Bairro 12', 'Logradouro 12'),
('00000013',13,  'Comp 13', 'Bairro 13', 'Logradouro 13'),
('00000014',14,  'Comp 14', 'Bairro 14', 'Logradouro 14'),
('00000015',15,  'Comp 15', 'Bairro 15', 'Logradouro 15'),
('00000016',16,  'Comp 16', 'Bairro 16', 'Logradouro 16'),
('00000017',17,  'Comp 17', 'Bairro 17', 'Logradouro 17'),
('00000018',18,  'Comp 18', 'Bairro 18', 'Logradouro 18'),
('00000019',19,  'Comp 19', 'Bairro 19', 'Logradouro 19'),
('00000020',20,  'Comp 20', 'Bairro 20', 'Logradouro 20');


INSERT INTO Tecnico(id_tecnico, cpf) VALUES
( 1,'00000000001'),
( 2,'00000000002'),
( 3,'00000000003'),
( 4,'00000000004'),
( 5,'00000000005'),
( 6,'00000000006'),
( 7,'00000000007'),
( 8,'00000000008'),
( 9,'00000000009'),
(10,'00000000010');


INSERT INTO Tec_Espec(id_tecnico, especialidade) VALUES
( 1,'Elétrica'),
( 2,'Hidráulica'),
( 3,'Redes de Computadores'),
( 4,'Segurança'),
( 5,'Automação'),
( 6,'Instalações'),
( 7,'Telecomunicações'),
( 8,'Infraestrutura'),
( 9,'Ar-condicionado'),
(10,'Energia Solar');


INSERT INTO Solicitante(id_solicitante, cpf) VALUES
( 1,'00000000011'),
( 2,'00000000012'),
( 3,'00000000013'),
( 4,'00000000014'),
( 5,'00000000015'),
( 6,'00000000016'),
( 7,'00000000017'),
( 8,'00000000018'),
( 9,'00000000019'),
(10,'00000000020');

INSERT INTO Ocorrencia(id_ocorrencia, id_solicitante, cep, numero, status) VALUES
( 1, 1,'00000011',11,'Aberta'),
( 2, 2,'00000012',12,'Em Andamento'),
( 3, 3,'00000013',13,'Concluída'),
( 4, 4,'00000014',14,'Cancelada'),
( 5, 5,'00000015',15,'Aberta'),
( 6, 6,'00000016',16,'Em Andamento'),
( 7, 7,'00000017',17,'Concluída'),
( 8, 8,'00000018',18,'Cancelada'),
( 9, 9,'00000019',19,'Aberta'),
(10,10,'00000020',20,'Em Andamento');

INSERT INTO Analisa(id_tecnico, id_ocorrencia) VALUES
( 1, 1),
( 2, 2),
( 3, 3),
( 4, 4),
( 5, 5),
( 6, 6),
( 7, 7),
( 8, 8),
( 9, 9),
(10,10);
“””
Criando Procedures
Criação de novos usuários
Vamos criar uma Procedure para a inserção de novos usuários que trata do erro de valores já cadastrados. 
“””
CREATE OR REPLACE PROCEDURE sp_criar_usuario(
  IN p_cpf    VARCHAR,
  IN p_nome   VARCHAR,
  IN p_fone   VARCHAR,
  IN p_email  VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO Usuario(cpf,nome,fone,email)
    VALUES (p_cpf,p_nome,p_fone,p_email);
EXCEPTION WHEN unique_violation THEN
  RAISE NOTICE 'Falha: CPF, telefone ou e-mail já cadastrado.';
END;
$$;
“””
Criando uma nova ocorrência
Procedure para a criação de uma ocorrência que deve ser criada como aberta com um. Retorna o ID da ocorrência gerada.
“””
CREATE OR REPLACE PROCEDURE sp_criar_ocorrencia(
  IN  p_cpf_solicitante VARCHAR,
  IN  p_cep             VARCHAR,
  IN  p_numero          VARCHAT,
  OUT p_solicitante_id  SMALLINT,
  OUT p_ocorrencia_id   SMALLINT
)
LANGUAGE plpgsql AS $$
DECLARE
  v_id_solicitante SMALLINT;
BEGIN
  SELECT id_solicitante
    INTO v_id_solicitante
  FROM Solicitante
  WHERE cpf = p_cpf_solicitante;

  IF NOT FOUND THEN
    INSERT INTO Solicitante(cpf)
      VALUES (p_cpf_solicitante)
    RETURNING id_solicitante
      INTO v_id_solicitante;
  END IF;

  INSERT INTO Ocorrencia(id_solicitante,cep,numero,status)
    VALUES (v_id_solicitante, p_cep, p_numero, 'Aberta')
  RETURNING id_ocorrencia
    INTO p_ocorrencia_id;

  
  p_solicitante_id := v_id_solicitante;
END;
$$;
“””

Criando functions
Buscando todas as ocorrências relacionadas a um técnico
“””
CREATE OR REPLACE FUNCTION fn_get_ocorrencias_por_tecnico(
  p_tecnico_id SMALLINT
)
RETURNS TABLE(
  id_ocorrencia SMALLINT,
  status       VARCHAR,
  cpf_solicitante VARCHAR
) AS $$
BEGIN
  RETURN QUERY
    SELECT o.id_ocorrencia,
           o.status,
           sol.cpf
    FROM Analisa a
    JOIN Ocorrencia o ON o.id_ocorrencia = a.id_ocorrencia
    JOIN Solicitante sol ON sol.id_solicitante = o.id_solicitante
    WHERE a.id_tecnico = p_tecnico_id;
END;
$$ LANGUAGE plpgsql;
“””
Validando a alteração de status de um ocorrência
As ocorrências devem seguir um fluxo na hora de alterar o status, só devem ir de “Aberta” para “Em andamento”, e de “Em andamento” para “Concluida” ou “Cancelada”, e depois de chegar ao status final não devem ser alteradas. 
“””
CREATE OR REPLACE FUNCTION fn_validate_status_transition() RETURNS trigger AS $$
BEGIN
  IF OLD.status = 'Aberta'
     AND NOT (NEW.status IN ('Em Andamento','Cancelada')) THEN
    RAISE EXCEPTION 'Status inválido: % → %', OLD.status, NEW.status;
  ELSIF OLD.status = 'Em Andamento'
     AND NOT (NEW.status IN ('Concluída','Cancelada')) THEN
    RAISE EXCEPTION 'Status inválido: % → %', OLD.status, NEW.status;
  ELSIF OLD.status IN ('Concluída','Cancelada') THEN
    RAISE EXCEPTION 'Não é possível alterar status já finalizado (%).', OLD.status;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
“””

Associa as ocorrências criadas ao técnico com menos ocorrências
3.1. View para técnico e número de ocorrências
“””
CREATE OR REPLACE VIEW vw_tecnico_ocorrencias AS
SELECT
  t.id_tecnico,
  COUNT(a.id_ocorrencia) AS total_ocorrencias
FROM Tecnico t
LEFT JOIN Analisa a ON a.id_tecnico = a.id_tecnico
GROUP BY t.id_tecnico
ORDER BY t.id_tecnico;
“””
3.2 Relaciona a ocorrência criada com o técnico
“””
CREATE OR REPLACE FUNCTION fn_assign_tecnico()
RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  rec   RECORD;
  cur   CURSOR FOR
    SELECT id_tecnico, total_ocorrencias
      FROM vw_tecnico_ocorrencias;
  v_min_total   BIGINT := NULL;
  v_tecnico_sel SMALLINT := NULL;
BEGIN
  OPEN cur;
  LOOP
    FETCH cur INTO rec;
    EXIT WHEN NOT FOUND;
    IF v_min_total IS NULL OR rec.total_ocorrencias < v_min_total THEN
      v_min_total   := rec.total_ocorrencias;
      v_tecnico_sel := rec.id_tecnico;
    END IF;
  END LOOP;
  CLOSE cur;

  INSERT INTO Analisa(id_tecnico, id_ocorrencia)
    VALUES (v_tecnico_sel, NEW.id_ocorrencia);

  RETURN NEW;
END;
$$;
“””
Triggers
Inserção na tabela Analisa
Quando inserimos um técnico relacionando ele a uma ocorrência,
automaticamente o status deve ser alterado para “Em andamento”,
dispara a função criada no tópico 2.
“””
CREATE TRIGGER trg_analisa_after_insert
  AFTER INSERT ON Analisa
  FOR EACH ROW
  EXECUTE FUNCTION fn_set_em_andamento();
“””
Inserção em Ocorrências
Quando uma nova ocorrência é criada automaticamente ela é associada ao técnico com menos ocorrências. Dispara a função criada no tópico 3.
“””
CREATE TRIGGER trg_assign_tecnico
  AFTER INSERT ON Ocorrencia
  FOR EACH ROW
  EXECUTE FUNCTION fn_assign_tecnico();
“””




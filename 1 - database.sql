
-- ###################################################################### CRIACAO DE TABELAS


CREATE DATABASE sistema_produtos_informatica CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE sistema_produtos_informatica;

CREATE TABLE situacaoUsuario (
    idSituacaoUsuario INT PRIMARY KEY,
    descricao VARCHAR(7) NOT NULL
);

CREATE TABLE visibilidadeProduto (
    idVisibilidadeProduto INT PRIMARY KEY,
    descricao VARCHAR(7) NOT NULL
);

CREATE TABLE tipoLogin (
    idTipoLogin INT PRIMARY KEY,
    descricao VARCHAR(13) NOT NULL
);

CREATE TABLE tipoProduto (
    idTipoProduto INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR (20) NOT NULL
);

CREATE TABLE produto (
    idProduto INT AUTO_INCREMENT PRIMARY KEY,
    idVisibilidadeProduto INT,
    nomeProduto VARCHAR(120),
    codigoProduto VARCHAR(30),
    idTipoProduto INT,
    valorProduto DOUBLE(7,2),
    descricaoProduto VARCHAR(450),
    dataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idTipoProduto) REFERENCES tipoProduto(idTipoProduto),
    FOREIGN KEY (idVisibilidadeProduto) REFERENCES visibilidadeProduto(idVisibilidadeProduto)
);

CREATE TABLE imagemProduto (
    idImagemProduto INT AUTO_INCREMENT PRIMARY KEY,
    idProduto INT,
    imagemProduto MEDIUMTEXT,
    FOREIGN KEY (idProduto) REFERENCES produto(idProduto)
);

CREATE TABLE usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR (20),
    dataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    idSituacaoUsuario INT,
    FOREIGN KEY (idSituacaoUsuario) REFERENCES situacaoUsuario(idSituacaoUsuario)
);

CREATE TABLE endereco (
    idEndereco INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT NOT NULL,
    cep VARCHAR(9) NOT NULL,
    uf VARCHAR(2) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    rua VARCHAR(150) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    complemento VARCHAR(100),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
);

CREATE TABLE login (
    idLogin INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT,
    login VARCHAR(20) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    idTipoLogin INT,
    dataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    idSituacaoUsuario INT,
    FOREIGN KEY (idTipoLogin) REFERENCES tipoLogin(idTipoLogin),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idSituacaoUsuario) REFERENCES situacaoUsuario(idSituacaoUsuario)
);

CREATE TABLE historicoAlteracoesUsuario (
    idHistorico INT AUTO_INCREMENT PRIMARY KEY,
    tabela VARCHAR(50) NOT NULL,
    operacao ENUM('INSERT', 'UPDATE') NOT NULL,
    idRegistro INT NOT NULL,
    campo VARCHAR(50) NOT NULL,
    valorAntigo TEXT,
    valorNovo TEXT,
    dataAlteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    idLogin INT,
    FOREIGN KEY (idLogin) REFERENCES login(idLogin)
);

CREATE TABLE historicoLogin (
    idHistoricoLogin INT AUTO_INCREMENT PRIMARY KEY,
    idLogin INT,
    tipoOperacao ENUM('LOGIN', 'LOGOUT') NOT NULL,
    dataOperacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    enderecoIP VARCHAR(45),
    userAgent VARCHAR(255),
    statusOperacao ENUM('SUCESSO', 'FALHA') NOT NULL,
    detalhes VARCHAR(255),
    FOREIGN KEY (idLogin) REFERENCES login(idLogin)
);

-- Tabela para armazenar o cabeçalho da compra
CREATE TABLE compra (
    idCompra INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT NOT NULL,
    dataCompra DATETIME DEFAULT CURRENT_TIMESTAMP,
    valorTotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
);

-- Tabela para armazenar os itens individuais da compra
CREATE TABLE item_compra (
    idItemCompra INT AUTO_INCREMENT PRIMARY KEY,
    idCompra INT NOT NULL,
    idProduto INT NOT NULL,
    quantidade INT NOT NULL,
    valorUnitario DECIMAL(10,2) NOT NULL,
    valorTotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idCompra) REFERENCES compra(idCompra),
    FOREIGN KEY (idProduto) REFERENCES produto(idProduto)
);

-- ###################################################################### INSERÇÃO DE DADOS

INSERT INTO situacaoUsuario (idSituacaoUsuario, descricao) VALUES
(1, 'Ativo'),
(2, 'Inativo');

INSERT INTO visibilidadeProduto (idVisibilidadeProduto, descricao) VALUES
(1, 'Visível'),
(2, 'Oculto');

-- Inserindo dados iniciais na tabela tipoLogin
INSERT INTO tipoLogin (idTipoLogin, descricao) VALUES
(1, 'Comum'),
(2, 'Administrador');

-- Inserção de um usuário administrador
INSERT INTO usuario (idUsuario, nome, documento, idSituacaoUsuario) 
VALUES (1, 'Administrador', '12345678901', 1);

-- Inserção de um login para o usuário administrador
INSERT INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario)
VALUES (1, 'admin', '$2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2', 2, 1);

-- Inserção de um usuário comum
INSERT INTO usuario (idUsuario, nome, documento, idSituacaoUsuario) 
VALUES (2, 'Usuário Comum', '12345678901', 1);

-- Inserção de um login para o usuário comum
INSERT INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario)
VALUES (2, 'user', '$2a$10$DiTEt9DPY7Hu3G3XPFW8r.LweYF.VaBEUkqscABFzEoo3Bjj54Oia', 1, 1);

INSERT INTO tipoProduto (idTipoProduto, descricao) VALUES
(1, 'Placa Mãe'),
(2, 'Memória RAM PC'),
(3, 'Memória RAM Notebook');



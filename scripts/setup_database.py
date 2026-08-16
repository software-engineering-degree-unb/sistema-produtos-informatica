"""Cria o banco de dados e as tabelas do sistema.

Substitui o script original ``1 - database.sql``.
Executar antes do ``seed_data.py``.
"""

import pymysql

from app.config.database import get_connection
from app.config.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

SCHEMA = """
CREATE TABLE IF NOT EXISTS situacaoUsuario (
    idSituacaoUsuario INT PRIMARY KEY,
    descricao VARCHAR(7) NOT NULL
);

CREATE TABLE IF NOT EXISTS visibilidadeProduto (
    idVisibilidadeProduto INT PRIMARY KEY,
    descricao VARCHAR(7) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipoLogin (
    idTipoLogin INT PRIMARY KEY,
    descricao VARCHAR(13) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipoProduto (
    idTipoProduto INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS canalVenda (
    idCanalVenda INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS produto (
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

CREATE TABLE IF NOT EXISTS imagemProduto (
    idImagemProduto INT AUTO_INCREMENT PRIMARY KEY,
    idProduto INT,
    imagemProduto MEDIUMTEXT,
    FOREIGN KEY (idProduto) REFERENCES produto(idProduto)
);

CREATE TABLE IF NOT EXISTS usuario (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(20),
    dataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    idSituacaoUsuario INT,
    FOREIGN KEY (idSituacaoUsuario) REFERENCES situacaoUsuario(idSituacaoUsuario)
);

CREATE TABLE IF NOT EXISTS endereco (
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

CREATE TABLE IF NOT EXISTS login (
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

CREATE TABLE IF NOT EXISTS historicoAlteracoesUsuario (
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

CREATE TABLE IF NOT EXISTS historicoLogin (
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

CREATE TABLE IF NOT EXISTS compra (
    idCompra INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario INT NOT NULL,
    dataCompra DATETIME DEFAULT CURRENT_TIMESTAMP,
    valorTotal DECIMAL(10,2) NOT NULL,
    idCanalVenda INT NOT NULL,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario),
    FOREIGN KEY (idCanalVenda) REFERENCES canalVenda(idCanalVenda)
);

CREATE TABLE IF NOT EXISTS item_compra (
    idItemCompra INT AUTO_INCREMENT PRIMARY KEY,
    idCompra INT NOT NULL,
    idProduto INT NOT NULL,
    quantidade INT NOT NULL,
    valorUnitario DECIMAL(10,2) NOT NULL,
    valorTotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idCompra) REFERENCES compra(idCompra),
    FOREIGN KEY (idProduto) REFERENCES produto(idProduto)
);
"""

REFERENCE_DATA = [
    "INSERT IGNORE INTO situacaoUsuario (idSituacaoUsuario, descricao) VALUES (1, 'Ativo'), (2, 'Inativo')",
    "INSERT IGNORE INTO visibilidadeProduto (idVisibilidadeProduto, descricao) VALUES (1, 'Visível'), (2, 'Oculto')",
    "INSERT IGNORE INTO tipoLogin (idTipoLogin, descricao) VALUES (1, 'Comum'), (2, 'Administrador')",
    "INSERT IGNORE INTO canalVenda (idCanalVenda, descricao) VALUES (1, 'Loja Física'), (2, 'Loja Online'), (3, 'Marketplace'), (4, 'Revendedor Autorizado')",
]

INITIAL_USERS = [
    # admin
    "INSERT IGNORE INTO usuario (idUsuario, nome, documento, idSituacaoUsuario) VALUES (1, 'Administrador', '12345678901', 1)",
    "INSERT IGNORE INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario) VALUES (1, 'admin', '$2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2', 2, 1)",
    # usuario comum
    "INSERT IGNORE INTO usuario (idUsuario, nome, documento, idSituacaoUsuario) VALUES (2, 'Usuário Comum', '12345678901', 1)",
    "INSERT IGNORE INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario) VALUES (2, 'user', '$2a$10$DiTEt9DPY7Hu3G3XPFW8r.LweYF.VaBEUkqscABFzEoo3Bjj54Oia', 1, 1)",
]


def create_database():
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, charset="utf8mb4"
    )
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
        )
    conn.commit()
    conn.close()


def main():
    print("Criando banco de dados...")
    create_database()

    print("Criando tabelas...")
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for statement in SCHEMA.split(";"):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)

            for statement in REFERENCE_DATA:
                cursor.execute(statement)

            for statement in INITIAL_USERS:
                cursor.execute(statement)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    print("Banco de dados e tabelas criados com sucesso.")


if __name__ == "__main__":
    main()

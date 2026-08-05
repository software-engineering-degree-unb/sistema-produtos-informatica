import bcrypt

BCRYPT_COST = 10


def hash_password(senha):
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_COST)).decode("utf-8")


class Admin:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id_login):
        query = """
            SELECT u.*, l.*
            FROM usuario u
            INNER JOIN login l ON u.idUsuario = l.idUsuario
            WHERE l.idTipoLogin = 2 AND l.idLogin = %s
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (id_login,))
            return cursor.fetchone()

    def get_all_usuarios(self):
        query = """
            SELECT u.idUsuario, u.nome, u.documento, u.dataCriacao, u.idSituacaoUsuario, l.idLogin,
                   l.login, l.idTipoLogin
            FROM login l
            INNER JOIN usuario u ON l.idUsuario = u.idUsuario
        """
        with self.db.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def search_usuarios(self, search_type, search_term, status):
        query = """
            SELECT u.idUsuario, u.nome, u.documento, u.dataCriacao, u.idSituacaoUsuario, l.idLogin,
                   l.login, l.idTipoLogin
            FROM usuario u
            INNER JOIN login l ON u.idUsuario = l.idUsuario
            WHERE 1=1
        """
        params = []

        if search_term:
            if search_type == "nome":
                query += " AND u.nome LIKE %s"
                params.append(f"%{search_term}%")
            elif search_type == "documento":
                query += " AND u.documento LIKE %s"
                params.append(f"%{search_term}%")

        if status != "todos":
            query += " AND u.idSituacaoUsuario = %s"
            params.append(status)

        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def create_usuario(self, data, id_login_alterador):
        self.db.begin()
        try:
            with self.db.cursor() as cursor:
                query_usuario = (
                    "INSERT INTO usuario (nome, documento, idSituacaoUsuario) VALUES (%s, %s, %s)"
                )
                cursor.execute(query_usuario, (data["nome"], data["documento"], 1))
                usuario_id = cursor.lastrowid

                query_endereco = """
                    INSERT INTO endereco (idUsuario, cep, uf, municipio, rua, numero, complemento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    query_endereco,
                    (
                        usuario_id,
                        data["cep"],
                        data["uf"],
                        data["municipio"],
                        data["rua"],
                        data["numero"],
                        data.get("complemento", ""),
                    ),
                )

                senha_hash = hash_password(data["senha"])
                query_login = """
                    INSERT INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(
                    query_login,
                    (usuario_id, data["login"], senha_hash, data["tipoLogin"], 1),
                )
                login_id = cursor.lastrowid

                self._registrar_alteracao(cursor, "usuario", "INSERT", login_id, "nome", None, data["nome"], id_login_alterador)
                self._registrar_alteracao(cursor, "usuario", "INSERT", login_id, "documento", None, data["documento"], id_login_alterador)
                self._registrar_alteracao(cursor, "login", "INSERT", login_id, "login", None, data["login"], id_login_alterador)
                self._registrar_alteracao(cursor, "endereco", "INSERT", login_id, "cep", None, data["cep"], id_login_alterador)
                self._registrar_alteracao(
                    cursor,
                    "endereco",
                    "INSERT",
                    login_id,
                    "endereco",
                    None,
                    f"{data['rua']}, {data['numero']} - {data['municipio']}/{data['uf']}",
                    id_login_alterador,
                )

                tipo_login_texto = "Usuário Comum" if data["tipoLogin"] == "1" else "Administrador"
                self._registrar_alteracao(cursor, "login", "INSERT", login_id, "tipo_login", None, tipo_login_texto, id_login_alterador)

            self.db.commit()
            return usuario_id
        except Exception:
            self.db.rollback()
            return False

    def get_usuario_by_id(self, id_usuario):
        query = """
            SELECT u.*, l.*, e.*
            FROM usuario u
            INNER JOIN login l ON u.idUsuario = l.idUsuario
            LEFT JOIN endereco e ON u.idUsuario = e.idUsuario
            WHERE u.idUsuario = %s
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (id_usuario,))
            return cursor.fetchone()

    def update_usuario(self, id_usuario, data, id_login_alterador):
        self.db.begin()
        try:
            usuario_antigo = self.get_usuario_by_id(id_usuario)

            with self.db.cursor() as cursor:
                query_update_usuario = """
                    UPDATE usuario
                    SET nome = %s, documento = %s, idSituacaoUsuario = %s
                    WHERE idUsuario = %s
                """
                cursor.execute(
                    query_update_usuario,
                    (data["nome"], data["documento"], data["status"], id_usuario),
                )

                if usuario_antigo["nome"] != data["nome"]:
                    self._registrar_alteracao(cursor, "usuario", "UPDATE", id_usuario, "nome", usuario_antigo["nome"], data["nome"], id_login_alterador)
                if usuario_antigo["documento"] != data["documento"]:
                    self._registrar_alteracao(cursor, "usuario", "UPDATE", id_usuario, "documento", usuario_antigo["documento"], data["documento"], id_login_alterador)
                if str(usuario_antigo["idSituacaoUsuario"]) != str(data["status"]):
                    status_antigo = "Ativo" if str(usuario_antigo["idSituacaoUsuario"]) == "1" else "Inativo"
                    status_novo = "Ativo" if str(data["status"]) == "1" else "Inativo"
                    self._registrar_alteracao(cursor, "usuario", "UPDATE", id_usuario, "status", status_antigo, status_novo, id_login_alterador)

                cursor.execute("SELECT COUNT(*) as total FROM endereco WHERE idUsuario = %s", (id_usuario,))
                endereco_exists = cursor.fetchone()["total"] > 0

                if endereco_exists:
                    query_endereco = """
                        UPDATE endereco
                        SET cep = %s, uf = %s, municipio = %s, rua = %s, numero = %s, complemento = %s
                        WHERE idUsuario = %s
                    """
                else:
                    query_endereco = """
                        INSERT INTO endereco (idUsuario, cep, uf, municipio, rua, numero, complemento)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                cursor.execute(
                    query_endereco,
                    (
                        data["cep"],
                        data["uf"],
                        data["municipio"],
                        data["rua"],
                        data["numero"],
                        data.get("complemento", ""),
                        id_usuario,
                    ),
                )

                if endereco_exists:
                    if usuario_antigo["cep"] != data["cep"]:
                        self._registrar_alteracao(cursor, "endereco", "UPDATE", id_usuario, "cep", usuario_antigo["cep"], data["cep"], id_login_alterador)

                    endereco_antigo = f"{usuario_antigo['rua']}, {usuario_antigo['numero']} - {usuario_antigo['municipio']}/{usuario_antigo['uf']}"
                    endereco_novo = f"{data['rua']}, {data['numero']} - {data['municipio']}/{data['uf']}"
                    if endereco_antigo != endereco_novo:
                        self._registrar_alteracao(cursor, "endereco", "UPDATE", id_usuario, "endereco", endereco_antigo, endereco_novo, id_login_alterador)
                else:
                    self._registrar_alteracao(cursor, "endereco", "INSERT", id_usuario, "cep", None, data["cep"], id_login_alterador)
                    self._registrar_alteracao(
                        cursor,
                        "endereco",
                        "INSERT",
                        id_usuario,
                        "endereco",
                        None,
                        f"{data['rua']}, {data['numero']} - {data['municipio']}/{data['uf']}",
                        id_login_alterador,
                    )

                senha_informada = data.get("senha") and str(data.get("senha", "")).strip()
                if senha_informada:
                    query_login = """
                        UPDATE login
                        SET login = %s, senha = %s, idTipoLogin = %s, idSituacaoUsuario = %s
                        WHERE idUsuario = %s
                    """
                    login_params = (data["login"], hash_password(senha_informada), data["tipoLogin"], data["status"], id_usuario)
                else:
                    query_login = """
                        UPDATE login
                        SET login = %s, idTipoLogin = %s, idSituacaoUsuario = %s
                        WHERE idUsuario = %s
                    """
                    login_params = (data["login"], data["tipoLogin"], data["status"], id_usuario)

                cursor.execute(query_login, login_params)

                if usuario_antigo["login"] != data["login"]:
                    self._registrar_alteracao(cursor, "login", "UPDATE", id_usuario, "login", usuario_antigo["login"], data["login"], id_login_alterador)
                if senha_informada:
                    self._registrar_alteracao(cursor, "login", "UPDATE", id_usuario, "senha", "********", "********", id_login_alterador)
                if str(usuario_antigo["idTipoLogin"]) != str(data["tipoLogin"]):
                    tipo_antigo = "Usuário Comum" if str(usuario_antigo["idTipoLogin"]) == "1" else "Administrador"
                    tipo_novo = "Usuário Comum" if str(data["tipoLogin"]) == "1" else "Administrador"
                    self._registrar_alteracao(cursor, "login", "UPDATE", id_usuario, "tipo_login", tipo_antigo, tipo_novo, id_login_alterador)

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def _registrar_alteracao(self, cursor, tabela, operacao, id_registro, campo, valor_antigo, valor_novo, id_login):
        query = """
            INSERT INTO historicoAlteracoesUsuario
                (tabela, operacao, idRegistro, campo, valorAntigo, valorNovo, idLogin)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (tabela, operacao, id_registro, campo, valor_antigo, valor_novo, id_login),
        )

    def get_historico_alteracoes_usuario(self, data_inicial, data_final, tipo_operacao=""):
        from datetime import datetime, timedelta

        data_final_ajustada = (datetime.strptime(data_final, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

        query = """
            SELECT
                historicoAlteracoesUsuario.dataAlteracao,
                historicoAlteracoesUsuario.operacao,
                historicoAlteracoesUsuario.campo,
                historicoAlteracoesUsuario.valorAntigo,
                historicoAlteracoesUsuario.valorNovo,
                loginAlterado.login AS login_alterado,
                usuarioAlterado.nome AS nome_completo_alterado,
                loginAlterando.login AS login_alterou,
                usuarioAlterando.nome AS nome_completo_alterou
            FROM historicoAlteracoesUsuario
            INNER JOIN login AS loginAlterado ON historicoAlteracoesUsuario.idRegistro = loginAlterado.idLogin
            LEFT JOIN usuario AS usuarioAlterado ON loginAlterado.idUsuario = usuarioAlterado.idUsuario
            INNER JOIN login AS loginAlterando ON historicoAlteracoesUsuario.idLogin = loginAlterando.idLogin
            LEFT JOIN usuario AS usuarioAlterando ON loginAlterando.idUsuario = usuarioAlterando.idUsuario
            WHERE dataAlteracao >= %s
            AND dataAlteracao <= %s
        """
        params = [data_inicial, data_final_ajustada]

        if tipo_operacao:
            query += " AND historicoAlteracoesUsuario.operacao = %s"
            params.append(tipo_operacao)

        query += " ORDER BY historicoAlteracoesUsuario.dataAlteracao DESC"

        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

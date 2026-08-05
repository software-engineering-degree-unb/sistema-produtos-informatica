class User:
    def __init__(self, db):
        self.db = db

    def authenticate(self, login):
        query = """
            SELECT l.idLogin, l.idTipoLogin, l.login, l.senha, l.dataCriacao,
                   u.nome, l.idSituacaoUsuario, u.idUsuario
            FROM login l
            INNER JOIN usuario u ON l.idUsuario = u.idUsuario
            WHERE l.login = %s
            AND l.idSituacaoUsuario = 1 AND u.idSituacaoUsuario = 1
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (login,))
            return cursor.fetchone()

    def get_by_id(self, id_login):
        query = """
            SELECT l.idLogin, l.idUsuario, l.idTipoLogin, l.login, l.dataCriacao, l.idSituacaoUsuario
            FROM login l
            WHERE l.idLogin = %s AND l.idSituacaoUsuario = 1
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (id_login,))
            return cursor.fetchone()

class Usuario:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id_login):
        query = """
            SELECT login.*, usuario.*
            FROM login
            INNER JOIN usuario ON login.idUsuario = usuario.idUsuario
            WHERE login.idLogin = %s
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (id_login,))
            return cursor.fetchone()

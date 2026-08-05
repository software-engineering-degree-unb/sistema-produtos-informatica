from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip
    return request.client.host if request.client else "0.0.0.0"


def registrar_operacao(db, id_login, tipo_operacao, status, detalhes=None, request=None):
    try:
        query = """
            INSERT INTO historicoLogin (idLogin, tipoOperacao, enderecoIP, userAgent, statusOperacao, detalhes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        ip = get_client_ip(request) if request else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "Unknown") if request else "Unknown"
        with db.cursor() as cursor:
            cursor.execute(
                query,
                (id_login, tipo_operacao, ip, user_agent, status, detalhes),
            )
        db.commit()
        return True
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Erro ao registrar operação de login/logout: {e}")
        return False

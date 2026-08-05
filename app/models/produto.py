import base64
import os

from app.functions.helpers import parse_valor_brl

DEFAULT_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "public",
    "assets",
    "img",
    "no-image.png",
)


class Produto:
    def __init__(self, db):
        self.db = db

    def search_produtos(self, search_term, search_type="geral", tipo_produto=None, visibilidade=None, page=1, items_per_page=10):
        try:
            conditions = []
            params = []

            if search_term:
                conditions.append(
                    "(p.nomeProduto LIKE %s OR p.descricaoProduto LIKE %s OR p.codigoProduto LIKE %s)"
                )
                like = f"%{search_term}%"
                params.extend([like, like, like])

            if tipo_produto:
                conditions.append("p.idTipoProduto = %s")
                params.append(tipo_produto)

            if visibilidade:
                conditions.append("p.idVisibilidadeProduto = %s")
                params.append(visibilidade)

            where = " AND ".join(conditions) if conditions else "1=1"

            query = f"SELECT p.* FROM produto p WHERE {where} ORDER BY p.idVisibilidadeProduto ASC, p.nomeProduto ASC"

            count_query = f"SELECT COUNT(*) as total FROM produto p WHERE {where}"

            offset = (page - 1) * items_per_page
            query += f" LIMIT {int(items_per_page)} OFFSET {int(offset)}"

            with self.db.cursor() as cursor:
                cursor.execute(count_query, params)
                total = cursor.fetchone()["total"]

                cursor.execute(query, params)
                produtos = cursor.fetchall()

                for produto in produtos:
                    cursor.execute(
                        "SELECT imagemProduto FROM imagemProduto WHERE idProduto = %s",
                        (produto["idProduto"],),
                    )
                    produto["imagens"] = cursor.fetchall()

            return {
                "produtos": produtos,
                "totalItems": total,
                "itemsPerPage": items_per_page,
                "currentPage": page,
            }
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error searching products: {e}")
            return {
                "produtos": [],
                "totalItems": 0,
                "itemsPerPage": items_per_page,
                "currentPage": page,
            }

    def get_tipos_produto(self):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT idTipoProduto, descricao FROM tipoProduto")
                return cursor.fetchall()
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error fetching product types: {e}")
            return []

    def get_visibilidade_produto(self):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT idVisibilidadeProduto, descricao FROM visibilidadeProduto")
                return cursor.fetchall()
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error fetching product visibility: {e}")
            return []

    def create_produto(self, data):
        try:
            self.db.begin()

            query = """
                INSERT INTO produto
                    (nomeProduto, codigoProduto, idTipoProduto, valorProduto, descricaoProduto, idVisibilidadeProduto)
                VALUES (%s, %s, %s, %s, %s, 1)
            """
            valor = parse_valor_brl(data["valor"])

            with self.db.cursor() as cursor:
                cursor.execute(
                    query,
                    (data["nome"], data["codigo"], data["tipoProduto"], valor, data["descricao"]),
                )
                produto_id = cursor.lastrowid

                imagens = data.get("imagens") or []
                if not imagens:
                    imagens = [self._default_image_base64()]

                query_imagem = "INSERT INTO imagemProduto (idProduto, imagemProduto) VALUES (%s, %s)"
                for imagem in imagens:
                    cursor.execute(query_imagem, (produto_id, imagem))

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def _default_image_base64(self):
        with open(DEFAULT_IMAGE_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def add_tipo_produto(self, descricao):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT idTipoProduto FROM tipoProduto WHERE descricao = %s", (descricao,))
                row = cursor.fetchone()
                if row:
                    return {
                        "success": False,
                        "message": "Esta categoria já existe.",
                        "id": row["idTipoProduto"],
                    }

                cursor.execute("INSERT INTO tipoProduto (descricao) VALUES (%s)", (descricao,))
                self.db.commit()
                return {
                    "success": True,
                    "message": "Categoria adicionada com sucesso!",
                    "id": cursor.lastrowid,
                }
        except Exception as e:
            self.db.rollback()
            import logging

            logging.getLogger(__name__).error(f"Erro ao adicionar tipo de produto: {e}")
            return {
                "success": False,
                "message": f"Erro ao adicionar categoria: {e}",
            }

    def get_produto_by_id(self, id_produto):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT p.* FROM produto p WHERE p.idProduto = %s", (id_produto,))
                produto = cursor.fetchone()

                if produto:
                    cursor.execute(
                        "SELECT imagemProduto FROM imagemProduto WHERE idProduto = %s",
                        (id_produto,),
                    )
                    produto["imagens"] = cursor.fetchall()

                return produto
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Error fetching product: {e}")
            return None

    def update_produto(self, data):
        try:
            self.db.begin()

            query = """
                UPDATE produto
                SET nomeProduto = %s,
                    codigoProduto = %s,
                    idTipoProduto = %s,
                    valorProduto = %s,
                    descricaoProduto = %s,
                    idVisibilidadeProduto = %s
                WHERE idProduto = %s
            """
            valor = parse_valor_brl(data["valor"])

            with self.db.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        data["nome"],
                        data["codigo"],
                        data["tipoProduto"],
                        valor,
                        data["descricao"],
                        data["visibilidadeProduto"],
                        data["idProduto"],
                    ),
                )

                imagens_removidas = data.get("imagensRemovidas") or []
                if imagens_removidas:
                    placeholders = ",".join(["%s"] * len(imagens_removidas))
                    delete_query = (
                        f"DELETE FROM imagemProduto WHERE idProduto = %s AND imagemProduto IN ({placeholders})"
                    )
                    cursor.execute(delete_query, [data["idProduto"]] + imagens_removidas)

                imagens = data.get("imagens") or []
                if imagens:
                    query_imagem = "INSERT INTO imagemProduto (idProduto, imagemProduto) VALUES (%s, %s)"
                    for imagem in imagens:
                        cursor.execute(query_imagem, (data["idProduto"], imagem))

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            import logging

            logging.getLogger(__name__).error(f"Error updating product: {e}")
            return False

import logging
import random
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


class Compra:
    def __init__(self, db):
        self.db = db

    def registrar_compra(self, id_usuario, itens):
        try:
            self.db.begin()

            valor_total = 0
            for item in itens:
                valor_total += float(item["price"]) * int(item["quantity"])

            id_canal_venda = random.randint(1, 4)

            with self.db.cursor() as cursor:
                query = (
                    "INSERT INTO compra (idUsuario, valorTotal, idCanalVenda) VALUES (%s, %s, %s)"
                )
                cursor.execute(query, (id_usuario, valor_total, id_canal_venda))
                id_compra = cursor.lastrowid

                query_item = """
                    INSERT INTO itemCompra (idCompra, idProduto, quantidade, valorUnitario, valorTotal)
                    VALUES (%s, %s, %s, %s, %s)
                """
                for item in itens:
                    id_produto = int(item["id"])
                    quantidade = int(item["quantity"])
                    valor_unitario = float(item["price"])
                    valor_item_total = valor_unitario * quantidade
                    cursor.execute(
                        query_item,
                        (id_compra, id_produto, quantidade, valor_unitario, valor_item_total),
                    )

            self.db.commit()
            return {"success": True, "idCompra": id_compra}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao registrar compra: {e}")
            return {"success": False, "message": str(e)}

    def listar_compras_usuario(self, id_usuario):
        try:
            query = """
                SELECT c.*, COUNT(ic.idItemCompra) as totalItens
                FROM compra c
                LEFT JOIN itemCompra ic ON c.idCompra = ic.idCompra
                WHERE c.idUsuario = %s
                GROUP BY c.idCompra
                ORDER BY c.dataCompra DESC
            """
            with self.db.cursor() as cursor:
                cursor.execute(query, (id_usuario,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao listar compras: {e}")
            return []

    def get_compra_detalhes(self, id_compra):
        try:
            query_compra = """
                SELECT c.*, u.nome as nomeUsuario
                FROM compra c
                JOIN usuario u ON c.idUsuario = u.idUsuario
                WHERE c.idCompra = %s
            """
            with self.db.cursor() as cursor:
                cursor.execute(query_compra, (id_compra,))
                compra = cursor.fetchone()

                if not compra:
                    return None

                query_itens = """
                    SELECT ic.*, p.nomeProduto, p.codigoProduto
                    FROM itemCompra ic
                    JOIN produto p ON ic.idProduto = p.idProduto
                    WHERE ic.idCompra = %s
                """
                cursor.execute(query_itens, (id_compra,))
                compra["itens"] = cursor.fetchall()

                return compra
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes da compra: {e}")
            return None

    def listar_todas_compras(self, filtros=None):
        filtros = filtros or {}
        try:
            query = """
                SELECT c.*, u.nome as nomeUsuario, COUNT(ic.idItemCompra) as totalItens
                FROM compra c
                JOIN usuario u ON c.idUsuario = u.idUsuario
                LEFT JOIN itemCompra ic ON c.idCompra = ic.idCompra
                WHERE 1=1
            """
            params = []

            if filtros.get("dataInicial"):
                query += " AND c.dataCompra >= %s"
                params.append(f"{filtros['dataInicial']} 00:00:00")

            if filtros.get("dataFinal"):
                query += " AND c.dataCompra <= %s"
                params.append(f"{filtros['dataFinal']} 23:59:59")

            if filtros.get("idUsuario"):
                query += " AND c.idUsuario = %s"
                params.append(filtros["idUsuario"])

            if filtros.get("valorMinimo") not in (None, ""):
                query += " AND c.valorTotal >= %s"
                params.append(str(filtros["valorMinimo"]).replace(",", "."))

            if filtros.get("valorMaximo") not in (None, ""):
                query += " AND c.valorTotal <= %s"
                params.append(str(filtros["valorMaximo"]).replace(",", "."))

            query += " GROUP BY c.idCompra ORDER BY c.dataCompra DESC"

            if filtros.get("page") and filtros.get("itemsPerPage"):
                offset = (int(filtros["page"]) - 1) * int(filtros["itemsPerPage"])
                query += f" LIMIT {int(filtros['itemsPerPage'])} OFFSET {int(offset)}"

            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                compras = cursor.fetchall()

            estatisticas = self._calcular_estatisticas_compras(filtros)

            return {"compras": compras, "estatisticas": estatisticas}
        except Exception as e:
            logger.error(f"Erro ao listar compras: {e}")
            return {
                "compras": [],
                "estatisticas": {"totalCompras": 0, "valorTotal": 0, "mediaValor": 0},
            }

    def _calcular_estatisticas_compras(self, filtros=None):
        filtros = filtros or {}
        try:
            query = """
                SELECT
                    COUNT(c.idCompra) as totalCompras,
                    SUM(c.valorTotal) as valorTotal,
                    AVG(c.valorTotal) as mediaValor
                FROM compra c
                WHERE 1=1
            """
            params = []

            if filtros.get("dataInicial"):
                query += " AND c.dataCompra >= %s"
                params.append(f"{filtros['dataInicial']} 00:00:00")

            if filtros.get("dataFinal"):
                query += " AND c.dataCompra <= %s"
                params.append(f"{filtros['dataFinal']} 23:59:59")

            if filtros.get("idUsuario"):
                query += " AND c.idUsuario = %s"
                params.append(filtros["idUsuario"])

            if filtros.get("valorMinimo") not in (None, ""):
                query += " AND c.valorTotal >= %s"
                params.append(str(filtros["valorMinimo"]).replace(",", "."))

            if filtros.get("valorMaximo") not in (None, ""):
                query += " AND c.valorTotal <= %s"
                params.append(str(filtros["valorMaximo"]).replace(",", "."))

            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone() or {"totalCompras": 0, "valorTotal": 0, "mediaValor": 0}
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {"totalCompras": 0, "valorTotal": 0, "mediaValor": 0}

    def get_usuarios_com_compras(self):
        try:
            query = """
                SELECT DISTINCT u.idUsuario, u.nome
                FROM usuario u
                JOIN compra c ON u.idUsuario = c.idUsuario
                ORDER BY u.nome ASC
            """
            with self.db.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro ao listar usuários com compras: {e}")
            return []

    def get_relatorio_mensal(self, ano=None):
        try:
            if not ano:
                ano = date.today().year
            ano = int(ano)

            query = """
                SELECT
                    MONTH(c.dataCompra) as mes,
                    COUNT(c.idCompra) as totalCompras,
                    SUM(c.valorTotal) as valorTotal,
                    AVG(c.valorTotal) as valorMedio,
                    MIN(c.valorTotal) as valorMinimo,
                    MAX(c.valorTotal) as valorMaximo
                FROM compra c
                WHERE YEAR(c.dataCompra) = %s
                GROUP BY MONTH(c.dataCompra)
                ORDER BY mes ASC
            """

            with self.db.cursor() as cursor:
                cursor.execute(query, (ano,))
                dados_mensais = cursor.fetchall()

                meses_completos = []
                for i in range(1, 13):
                    meses_completos.append({
                        "mes": i,
                        "nomeMes": MESES[i],
                        "totalCompras": 0,
                        "valorTotal": 0,
                        "valorMedio": 0,
                        "valorMinimo": 0,
                        "valorMaximo": 0,
                    })

                for dados in dados_mensais:
                    mes = int(dados["mes"])
                    meses_completos[mes - 1] = {
                        "mes": mes,
                        "nomeMes": MESES[mes],
                        "totalCompras": dados["totalCompras"],
                        "valorTotal": dados["valorTotal"],
                        "valorMedio": dados["valorMedio"],
                        "valorMinimo": dados["valorMinimo"],
                        "valorMaximo": dados["valorMaximo"],
                    }

                query_estatisticas = """
                    SELECT
                        COUNT(c.idCompra) as totalCompras,
                        SUM(c.valorTotal) as valorTotal,
                        AVG(c.valorTotal) as valorMedio,
                        MIN(c.valorTotal) as valorMinimo,
                        MAX(c.valorTotal) as valorMaximo
                    FROM compra c
                    WHERE YEAR(c.dataCompra) = %s
                """
                cursor.execute(query_estatisticas, (ano,))
                estatisticas_anuais = cursor.fetchone() or {
                    "totalCompras": 0, "valorTotal": 0, "valorMedio": 0,
                    "valorMinimo": 0, "valorMaximo": 0,
                }

                cursor.execute("SELECT DISTINCT YEAR(dataCompra) as ano FROM compra ORDER BY ano DESC")
                anos_disponiveis = [row["ano"] for row in cursor.fetchall()]

            return {
                "dadosMensais": meses_completos,
                "estatisticasAnuais": estatisticas_anuais,
                "anosDisponiveis": anos_disponiveis,
                "anoSelecionado": ano,
            }
        except Exception as e:
            logger.error(f"Erro ao gerar relatório mensal: {e}")
            return {
                "dadosMensais": [],
                "estatisticasAnuais": {
                    "totalCompras": 0, "valorTotal": 0, "valorMedio": 0,
                    "valorMinimo": 0, "valorMaximo": 0,
                },
                "anosDisponiveis": [],
                "anoSelecionado": ano,
            }

    def get_top_clientes(self, limit=10, order_by="valorTotal", periodo=None):
        try:
            query = """
                SELECT
                    u.idUsuario,
                    u.nome,
                    l.login as email,
                    COUNT(c.idCompra) as totalCompras,
                    SUM(c.valorTotal) as valorTotal,
                    AVG(c.valorTotal) as mediaCompra,
                    MIN(c.dataCompra) as primeiraCompra,
                    MAX(c.dataCompra) as ultimaCompra
                FROM usuario u
                LEFT JOIN login l ON u.idUsuario = l.idUsuario
                JOIN compra c ON u.idUsuario = c.idUsuario
            """
            params = []

            if periodo:
                query += " WHERE c.dataCompra >= %s"
                if periodo == "mes":
                    params.append((date.today() - timedelta(days=30)).strftime("%Y-%m-%d"))
                elif periodo == "trimestre":
                    params.append((date.today() - timedelta(days=90)).strftime("%Y-%m-%d"))
                elif periodo == "semestre":
                    params.append((date.today() - timedelta(days=180)).strftime("%Y-%m-%d"))
                elif periodo == "ano":
                    params.append((date.today() - timedelta(days=365)).strftime("%Y-%m-%d"))

            query += " GROUP BY u.idUsuario, u.nome, l.login"

            if order_by == "totalCompras":
                query += " ORDER BY totalCompras DESC, valorTotal DESC"
            else:
                query += " ORDER BY valorTotal DESC, totalCompras DESC"

            query += f" LIMIT {int(limit)}"

            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                clientes = cursor.fetchall()

                for cliente in clientes:
                    query_produtos = """
                        SELECT
                            p.idProduto,
                            p.nomeProduto,
                            p.codigoProduto,
                            COUNT(ic.idItemCompra) as frequencia,
                            SUM(ic.quantidade) as quantidadeTotal
                        FROM itemCompra ic
                        JOIN compra c ON ic.idCompra = c.idCompra
                        JOIN produto p ON ic.idProduto = p.idProduto
                        WHERE c.idUsuario = %s
                        GROUP BY p.idProduto, p.nomeProduto, p.codigoProduto
                        ORDER BY frequencia DESC
                        LIMIT 3
                    """
                    cursor.execute(query_produtos, (cliente["idUsuario"],))
                    cliente["produtosPreferidos"] = cursor.fetchall()

                query_estatisticas = """
                    SELECT
                        COUNT(DISTINCT c.idUsuario) as totalClientes,
                        SUM(c.valorTotal) as valorTotalGeral,
                        COUNT(c.idCompra) as totalComprasGeral,
                        AVG(subquery.totalPorCliente) as mediaComprasPorCliente,
                        AVG(subquery.valorPorCliente) as mediaGastoPorCliente
                    FROM compra c
                    JOIN (
                        SELECT
                            idUsuario,
                            COUNT(idCompra) as totalPorCliente,
                            SUM(valorTotal) as valorPorCliente
                        FROM compra
                        GROUP BY idUsuario
                    ) as subquery
                """
                estat_params = []
                if periodo:
                    query_estatisticas += " WHERE c.dataCompra >= %s"
                    estat_params = params

                cursor.execute(query_estatisticas, estat_params)
                estatisticas = cursor.fetchone() or {
                    "totalClientes": 0, "valorTotalGeral": 0, "totalComprasGeral": 0,
                    "mediaComprasPorCliente": 0, "mediaGastoPorCliente": 0,
                }

            if clientes and estatisticas["valorTotalGeral"]:
                valor_total_top = sum(float(c["valorTotal"]) for c in clientes)
                estatisticas["percentualValorTop"] = (valor_total_top / float(estatisticas["valorTotalGeral"])) * 100
                compras_top = sum(int(c["totalCompras"]) for c in clientes)
                estatisticas["percentualComprasTop"] = (compras_top / float(estatisticas["totalComprasGeral"])) * 100 if estatisticas["totalComprasGeral"] else 0
            else:
                estatisticas["percentualValorTop"] = 0
                estatisticas["percentualComprasTop"] = 0

            return {
                "clientes": clientes,
                "estatisticas": estatisticas,
                "filtros": {"limite": limit, "ordenacao": order_by, "periodo": periodo or ""},
            }
        except Exception as e:
            logger.error(f"Erro ao buscar top clientes: {e}")
            return {
                "clientes": [],
                "estatisticas": {
                    "totalClientes": 0, "valorTotalGeral": 0, "totalComprasGeral": 0,
                    "mediaComprasPorCliente": 0, "mediaGastoPorCliente": 0,
                    "percentualValorTop": 0, "percentualComprasTop": 0,
                },
                "filtros": {"limite": limit, "ordenacao": order_by, "periodo": periodo or ""},
            }

    def listar_vendas_por_canal(self, filtros=None):
        filtros = filtros or {}
        try:
            query = """
                SELECT
                    cv.descricao as canalVenda,
                    COUNT(c.idCompra) as totalCompras,
                    SUM(c.valorTotal) as valorTotal,
                    AVG(c.valorTotal) as mediaValor
                FROM compra c
                JOIN canalVenda cv ON c.idCanalVenda = cv.idCanalVenda
                WHERE 1=1
            """
            params = []

            if filtros.get("dataInicial"):
                query += " AND c.dataCompra >= %s"
                params.append(f"{filtros['dataInicial']} 00:00:00")

            if filtros.get("dataFinal"):
                query += " AND c.dataCompra <= %s"
                params.append(f"{filtros['dataFinal']} 23:59:59")

            if filtros.get("canal"):
                query += " AND cv.descricao = %s"
                params.append(filtros["canal"])

            query += " GROUP BY cv.descricao ORDER BY valorTotal DESC"

            query_totais = """
                SELECT
                    COUNT(c.idCompra) as totalCompras,
                    SUM(c.valorTotal) as valorTotal,
                    AVG(c.valorTotal) as mediaValor
                FROM compra c
                JOIN canalVenda cv ON c.idCanalVenda = cv.idCanalVenda
                WHERE 1=1
            """

            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                vendas_por_canal = cursor.fetchall()

                cursor.execute(query_totais, params)
                totais = cursor.fetchone() or {"totalCompras": 0, "valorTotal": 0, "mediaValor": 0}

                cursor.execute("SELECT descricao FROM canalVenda ORDER BY descricao")
                canais = [row["descricao"] for row in cursor.fetchall()]

            return {"vendasPorCanal": vendas_por_canal, "totais": totais, "canais": canais}
        except Exception as e:
            logger.error(f"Erro ao listar vendas por canal: {e}")
            return {
                "vendasPorCanal": [],
                "totais": {"totalCompras": 0, "valorTotal": 0, "mediaValor": 0},
                "canais": [],
            }

"""Gera compras aleatórias para popular os relatórios.

Gera compras para os usuários 3-27 (clientes comuns) distribuídas nos últimos 2 anos.
"""

import random
from datetime import datetime, timedelta

from app.config.database import get_connection


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT idUsuario FROM usuario WHERE idUsuario > 2 AND idUsuario <= 27")
            user_ids = [row["idUsuario"] for row in cursor.fetchall()]

            cursor.execute("SELECT idProduto, valorProduto FROM produto")
            products = cursor.fetchall()

            if not user_ids or not products:
                print("Sem usuários ou produtos para gerar compras. Rode setup_database.py e seed_data.py primeiro.")
                return

            start_date = datetime.now() - timedelta(days=365 * 2)
            end_date = datetime.now()

            user_activity = {uid: random.randint(1, 10) for uid in user_ids}
            top_users = sorted(user_activity, key=user_activity.get, reverse=True)[:5]

            total_purchases = 0
            current_date = start_date

            while current_date <= end_date:
                diff = end_date - current_date
                months_ago = diff.days // 30
                purchase_probability = min(1.0, 1 - (months_ago / 30))
                purchases_per_day = random.randint(0, int(8 * purchase_probability))

                purchase_rows = []
                items_by_purchase = []

                for _ in range(purchases_per_day):
                    if random.randint(1, 100) <= 40:
                        user_id = random.choice(top_users)
                    else:
                        user_id = random.choice(user_ids)

                    hour = random.randint(8, 22)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    purchase_date = current_date.replace(hour=hour, minute=minute, second=second)

                    item_count = random.randint(1, 7)
                    available = list(products)
                    random.shuffle(available)

                    total_value = 0
                    purchase_items = []

                    for _ in range(item_count):
                        if not available:
                            break
                        product = available.pop()

                        quantity = random.randint(1, 5)
                        unit_price = float(product["valorProduto"])
                        unit_price = round(unit_price * (1 + (random.randint(-5, 5) / 100)), 2)
                        item_total = round(unit_price * quantity, 2)

                        purchase_items.append((product["idProduto"], quantity, unit_price, item_total))
                        total_value = round(total_value + item_total, 2)

                    canal_venda = random.randint(1, 4)
                    purchase_rows.append((user_id, total_value, purchase_date, canal_venda))
                    items_by_purchase.append(purchase_items)

                if purchase_rows:
                    cursor.executemany(
                        "INSERT INTO compra (idUsuario, valorTotal, dataCompra, idCanalVenda) VALUES (%s, %s, %s, %s)",
                        purchase_rows,
                    )
                    first_id = cursor.lastrowid - len(purchase_rows) + 1
                    total_purchases += len(purchase_rows)

                    flat_items = []
                    for i, purchase_items in enumerate(items_by_purchase):
                        compra_id = first_id + i
                        for item in purchase_items:
                            flat_items.append((compra_id, item[0], item[1], item[2], item[3]))

                    if flat_items:
                        cursor.executemany(
                            "INSERT INTO item_compra (idCompra, idProduto, quantidade, valorUnitario, valorTotal) VALUES (%s, %s, %s, %s, %s)",
                            flat_items,
                        )

                if total_purchases > 0 and total_purchases % 50 == 0:
                    print(f"Geradas {total_purchases} compras até agora...")

                current_date += timedelta(days=1)

        conn.commit()
        print(f"Geradas com sucesso {total_purchases} compras com itens.")
    except Exception as e:
        conn.rollback()
        print(f"Falha ao gerar dados: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    main()

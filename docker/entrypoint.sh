#!/bin/sh
set -e

echo "Aguardando banco de dados..."
python - <<'EOF'
import sys
import time

import pymysql
from app.config.settings import DB_HOST, DB_PORT, DB_PASSWORD, DB_USER

for attempt in range(60):
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=3,
        )
        conn.close()
        print("Banco de dados pronto.")
        break
    except Exception:
        time.sleep(2)
else:
    print("Banco de dados não ficou pronto a tempo.", file=sys.stderr)
    sys.exit(1)
EOF

echo "Criando banco de dados e tabelas..."
python scripts/setup_database.py

echo "Semeando dados iniciais..."
python - <<'EOF'
from app.config.database import get_connection

conn = get_connection()
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM produto")
        needs_seed = cursor.fetchone()["total"] == 0
finally:
    conn.close()

if needs_seed:
    from scripts.seed_data import main as seed_main

    seed_main()
    print("Seed executado.")
else:
    print("Banco já populado, seed ignorado.")
EOF

if [ "$GENERATE_DATA" = "true" ]; then
    echo "Gerando dados fictícios de vendas..."
    python - <<'EOF'
from app.config.database import get_connection

conn = get_connection()
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM compra")
        empty = cursor.fetchone()["total"] == 0
finally:
    conn.close()

if empty:
    from scripts.generate_data import main as generate_main

    generate_main()
else:
    print("Compras já existentes, geração ignorada.")
EOF
fi

echo "Iniciando aplicação em http://0.0.0.0:8000"
exec uvicorn main:app --host 0.0.0.0 --port 8000

import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "sistema_produtos_informatica")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")

SECRET_KEY = os.getenv("SECRET_KEY", "altera-esta-chave-em-producao")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "900"))

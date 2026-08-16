import re
from datetime import date, datetime
from decimal import Decimal


def _coerce_datetime(valor):
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)
    if isinstance(valor, str) and valor:
        return datetime.fromisoformat(valor.replace(" ", "T"))
    return None


def datetime_brl(valor):
    dt = _coerce_datetime(valor)
    return dt.strftime("%d/%m/%Y %H:%M") if dt else ""


def date_brl(valor):
    dt = _coerce_datetime(valor)
    return dt.strftime("%d/%m/%Y") if dt else ""


def format_int_brl(valor):
    try:
        return f"{int(float(valor)):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def formatar_cpf(cpf):
    cpf = re.sub(r"\D", "", str(cpf))
    if len(cpf) == 11:
        return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    return cpf


def formatar_cnpj(cnpj):
    cnpj = re.sub(r"\D", "", str(cnpj))
    if len(cnpj) == 14:
        return f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return cnpj


def parse_valor_brl(valor):
    if valor is None:
        return None
    return str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip()


def format_valor_brl(valor):
    try:
        valor = float(valor)
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "0,00"

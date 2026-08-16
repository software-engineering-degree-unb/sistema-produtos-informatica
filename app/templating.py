import json
from datetime import date, datetime, time
from decimal import Decimal

from fastapi.templating import Jinja2Templates

from app.functions.helpers import (
    date_brl,
    datetime_brl,
    format_int_brl,
    format_valor_brl,
    formatar_cnpj,
    formatar_cpf,
)


def _json_default(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


def tojson_safe(obj):
    return json.dumps(obj, ensure_ascii=False, default=_json_default)


templates = Jinja2Templates(directory="app/views")
templates.env.filters["formatar_cpf"] = formatar_cpf
templates.env.filters["formatar_cnpj"] = formatar_cnpj
templates.env.filters["format_valor_brl"] = format_valor_brl
templates.env.filters["format_int_brl"] = format_int_brl
templates.env.filters["datetime_brl"] = datetime_brl
templates.env.filters["date_brl"] = date_brl
templates.env.filters["tojson_safe"] = tojson_safe

import hmac

from fastapi import FastAPI, Header
from sqlalchemy import text

from app.config import get_settings
from app.core.errors import OrvyaError, orvya_error_handler, unexpected_error_handler
from app.core.operation import OperationIdMiddleware
from app.db import engine

app = FastAPI(title="Orvya Ops", docs_url=None, redoc_url=None)
app.add_middleware(OperationIdMiddleware)
app.add_exception_handler(OrvyaError, orvya_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

_ALLOWED_COMMANDS = {"status"}


def _authorize(token: str | None) -> None:
    configured = get_settings().ops_token
    if not configured:
        raise OrvyaError(503, "ops_indisponivel", "O executor operacional não está configurado.")
    if token is None or not hmac.compare_digest(token, configured):
        raise OrvyaError(403, "acesso_negado", "Acesso operacional negado.")


@app.get("/saude")
def health() -> dict[str, str]:
    return {"estado": "vivo"}


@app.post("/execucoes/{command}")
def execute(command: str, x_orvya_ops_token: str | None = Header(default=None)) -> dict[str, str]:
    _authorize(x_orvya_ops_token)
    if command not in _ALLOWED_COMMANDS:
        raise OrvyaError(404, "operacao_nao_permitida", "Operação não disponível.")
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"estado": "ok", "operacao": command}

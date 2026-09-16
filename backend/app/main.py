from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.core.errors import (
    OrvyaError,
    http_error_handler,
    orvya_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.core.operation import OperationIdMiddleware
from app.db import engine

EXPECTED_SCHEMA_REVISION = "20260915_0001"

app = FastAPI(title="Orvya API", version="1", docs_url=None, redoc_url=None)
app.add_middleware(OperationIdMiddleware)
app.add_exception_handler(OrvyaError, orvya_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)


@app.get("/api/v1/saude")
def health() -> dict[str, str]:
    return {"estado": "vivo"}


def _database_state() -> tuple[bool, str | None]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        return revision == EXPECTED_SCHEMA_REVISION, str(revision)
    except Exception:
        return False, None


@app.get("/api/v1/saude/pronto")
def readiness() -> dict[str, str]:
    ready, revision = _database_state()
    if not ready:
        raise OrvyaError(
            status_code=503,
            code="servico_nao_pronto",
            mensagem="A aplicação ainda não está pronta para receber tráfego.",
            retryable=True,
        )
    return {"estado": "pronto", "schema_revision": revision or EXPECTED_SCHEMA_REVISION}


def _optional_dependency_state(*values: object | None) -> str:
    present = [value not in (None, "") for value in values]
    if not any(present):
        return "nao_configurada"
    if all(present):
        return "configurada_nao_verificada"
    return "configuracao_incompleta"


@app.get("/api/v1/saude/dependencias")
def dependencies(request: Request) -> dict[str, object]:
    settings = get_settings()
    database_ready, revision = _database_state()
    return {
        "operation_id": request.state.operation_id,
        "banco": {
            "estado": "disponivel" if database_ready else "indisponivel",
            "schema_revision": revision,
        },
        "email": {
            "estado": _optional_dependency_state(settings.smtp_host, settings.smtp_port, settings.smtp_from)
        },
        "armazenamento": {
            "estado": _optional_dependency_state(
                settings.s3_endpoint,
                settings.s3_region,
                settings.s3_bucket,
                settings.s3_access_key,
                settings.s3_secret_key,
            )
        },
        "comunica_cnj": {
            "estado": _optional_dependency_state(settings.cnj_base_url, settings.cnj_token)
        },
    }

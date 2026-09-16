from dataclasses import dataclass
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@dataclass(slots=True)
class OrvyaError(Exception):
    status_code: int
    code: str
    mensagem: str
    field: str | None = None
    retryable: bool = False


def _operation_id(request: Request) -> str:
    return str(getattr(request.state, "operation_id", "indisponivel"))


def _payload(
    request: Request,
    *,
    code: str,
    mensagem: str,
    field: str | None = None,
    retryable: bool = False,
) -> dict[str, Any]:
    return {
        "erro": {
            "code": code,
            "mensagem": mensagem,
            "field": field,
            "operation_id": _operation_id(request),
            "retryable": retryable,
        }
    }


async def orvya_error_handler(request: Request, exc: OrvyaError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(
            request,
            code=exc.code,
            mensagem=exc.mensagem,
            field=exc.field,
            retryable=exc.retryable,
        ),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    loc = first.get("loc", ())
    field = str(loc[-1]) if loc else None
    return JSONResponse(
        status_code=400,
        content=_payload(
            request,
            code="entrada_invalida",
            mensagem="Revise os campos informados.",
            field=field,
        ),
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_by_status = {
        401: "sessao_necessaria",
        403: "acesso_negado",
        404: "recurso_nao_encontrado",
        409: "conflito",
        422: "regra_de_dominio",
        429: "limite_tecnico",
        503: "servico_indisponivel",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(
            request,
            code=code_by_status.get(exc.status_code, "erro_http"),
            mensagem=str(exc.detail) if exc.detail else "A operação não pôde ser concluída.",
        ),
    )


async def unexpected_error_handler(request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_payload(
            request,
            code="erro_interno",
            mensagem="A operação não pôde ser concluída.",
            retryable=False,
        ),
    )

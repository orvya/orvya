# Orvya

`ORVYA.md` é a especificação única do produto e prevalece sobre qualquer outro texto do repositório.

## Desenvolvimento local

1. Copie `.env.example` para `.env` e preencha os valores necessários.
2. Execute `docker compose up --build`.

No runtime local, o serviço da API aplica `alembic upgrade head` antes de iniciar. A API canônica é servida sob `/api/v1`; App e Admin são superfícies separadas.

FROM python:3.12 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv .venv
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE.md ./
COPY src ./src
RUN .venv/bin/pip install .
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
# CMD ["/app/.venv/bin/fastapi", "run"]

CMD ["/app/.venv/bin/uvicorn", "nbsapi.api:app", "--host", "0.0.0.0", "--port", "8080"]
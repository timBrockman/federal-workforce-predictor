# Multi-stage, non-root production Dockerfile for the template
FROM python:3.11-slim AS builder

WORKDIR /app
ENV UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

FROM python:3.11-slim

WORKDIR /app
RUN useradd -m -u 1000 appuser

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

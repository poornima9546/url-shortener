# ==============================
# Stage 1: Builder
# ==============================
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY app/requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# ==============================
# Stage 2: Production
# ==============================
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=5000

# Create non-root user
RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

# Copy installed Python packages
COPY --from=builder /install /usr/local

# Copy application
COPY app/ .

# Health check
HEALTHCHECK --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"

# Run as non-root user
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 🔑 Asegura permisos de ejecución para el entrypoint
RUN chmod +x /app/entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=autorizaciones.settings

# DO detecta el Dockerfile y corre esto
CMD ["./entrypoint.sh"]

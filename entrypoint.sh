#!/bin/sh
set -e

# Esperar a que la DB resuelva y acepte conexión
echo "Esperando a la base de datos ${DB_HOST}:${DB_PORT} ..."
ATTEMPTS=30
i=1
while [ $i -le $ATTEMPTS ]; do
  python - <<'PY'
import os, socket, sys
host = os.getenv("DB_HOST","")
port = int(os.getenv("DB_PORT","25060"))
try:
    socket.getaddrinfo(host, port)
    s = socket.create_connection((host, port), timeout=5)
    s.close()
    print("DB OK")
    sys.exit(0)
except Exception as e:
    print("DB not ready:", e)
    sys.exit(1)
PY
  if [ $? -eq 0 ]; then
    break
  fi
  echo "Reintentando (${i}/${ATTEMPTS})..."
  i=$((i+1))
  sleep 2
done

if [ $i -gt $ATTEMPTS ]; then
  echo "No se pudo conectar a la DB a tiempo."
  exit 1
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec gunicorn autorizaciones.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3

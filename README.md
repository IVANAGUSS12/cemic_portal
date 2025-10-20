# CEMIC · Autorizaciones (Django + Panel + QR)

Proyecto listo para subir a GitHub y desplegar en DigitalOcean App Platform.
Incluye:
- Panel interno protegido por login (/) con filtros, calendario y adjuntos.
- Formulario público QR (/qr/) que crea pacientes y sube archivos.
- API mínima JSON usada por el front: `/v1/patients/`, `/v1/patients/<id>/`, `/v1/attachments/`.
- Admin de Django para gestión manual: `/admin/`.
- Dockerfile, docker-compose para desarrollo local y app.do.yaml para DO.

## Requisitos
- Python 3.11+
- Docker (opcional para local)
- PostgreSQL (local vía `docker-compose` o administrado en DO)

## Setup local (sin Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.sample .env
# editar .env con tus valores
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visitar:
- Panel interno: http://127.0.0.1:8000/  (requiere login)
- QR: http://127.0.0.1:8000/qr/
- Admin: http://127.0.0.1:8000/admin/

## Desarrollo local con Docker
```bash
cp .env.sample .env
docker compose up --build
# en otro terminal crear superusuario:
docker compose exec web python manage.py createsuperuser
```

## Despliegue en DigitalOcean (App Platform)
1. Subí este repo a GitHub.
2. En DO, crea una nueva App desde el repo, seleccionando este Dockerfile.
3. Agregá una base de datos PostgreSQL administrada (sección Databases).
4. En variables de entorno de la App:
   - SECRET_KEY (secret), DEBUG=0
   - ALLOWED_HOSTS=tu-dominio.com,*
   - CSRF_TRUSTED_ORIGINS=https://tu-dominio.com
   - DB_NAME, DB_USER, DB_PASSWORD (secret), DB_HOST, DB_PORT
5. Deploy.

## Notas
- Los endpoints están `@csrf_exempt` para simplificar el fetch del front. Si querés, se puede reforzar con CSRF/Session.
- Los archivos se guardan en `/media/`; DO sirve archivos estáticos desde la app. En producción grande, preferir Spaces/S3.
- Si cambiás los nombres de estados, recordá mantenerlos en el front (select de estados en el panel).

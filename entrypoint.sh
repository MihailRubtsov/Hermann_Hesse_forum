#!/bin/sh
set -e

echo "Warte auf die Datenbank ${DB_HOST}:${DB_PORT} …"

until python -c "
import sys, django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hermann_Hesse.settings')
django.setup()
from django.db import connections
try:
    connections['default'].ensure_connection()
except Exception as exc:
    print(exc, file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done

echo "Datenbank erreichbar."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear


exec "$@"
# syntax=docker/dockerfile:1

FROM python:3.13-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && pip install -r requirements.txt \
    && apt-get purge -y gcc libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*


COPY . .


RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/seitik/media /app/seitik/staticfiles \
    && chown -R appuser:appuser /app

WORKDIR /app/seitik

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "Hermann_Hesse.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--access-logfile", "-"]
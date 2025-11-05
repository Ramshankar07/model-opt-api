FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

COPY src /app/src

# Add src to Python path so federated_api can be found
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Railway injects PORT; bind to it
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn federated_api.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}"]


FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/

EXPOSE 8000

# Render sets PORT at runtime; default to 8000 for local runs and CI.
CMD ["sh", "-c", "exec python -m uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}"]

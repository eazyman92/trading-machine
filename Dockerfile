FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home app && mkdir -p /data/datasets && chown -R app:app /data
COPY src ./src
COPY migrations ./migrations
COPY vendor ./vendor
COPY scripts ./scripts
USER app
CMD ["python", "-m", "uvicorn", "tradinglab.api:app", "--host", "0.0.0.0", "--port", "8000"]

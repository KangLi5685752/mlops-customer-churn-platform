FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY README.md /app/README.md
RUN mkdir -p /app/data/raw /app/artifacts

COPY app/ /app/app/
COPY src/ /app/src/
COPY artifacts/model_pipeline.joblib /app/artifacts/model_pipeline.joblib

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

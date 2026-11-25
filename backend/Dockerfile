FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/model && useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["sh", "-c", "python -c 'from database import initialize_database; initialize_database()' && gunicorn --workers 2 --bind 0.0.0.0:5000 --access-logfile - app:app"]
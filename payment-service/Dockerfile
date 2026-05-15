FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create db directory
RUN mkdir -p /app/db

EXPOSE 8005
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8005"]
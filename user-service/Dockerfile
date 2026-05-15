FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start server
EXPOSE 8001
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8001"]
# CMD ["sh", "-c", "python manage.py migrate && echo \"from accounts.models import User; User.objects.create_superuser('admin@kitabistan.com', 'admin123', name='Admin')\" | python manage.py shell && python manage.py runserver 0.0.0.0:8001"]
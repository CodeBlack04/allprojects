# Use a minimal base image
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv gunicorn 'uvicorn[standard]'

# Copy project files
COPY . .

# Collect static files
RUN python3 manage.py collectstatic --noinput

# Change ownership of the application directory
RUN chown -R appuser:appuser /home/appuser
USER appuser

# Expose application port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-w", "3", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "allprojects.asgi:application"]
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Permisos de ejecución en el entrypoint
RUN chmod +x entrypoint.sh

EXPOSE 8000

# El entrypoint aplica las migraciones de Alembic antes de arrancar uvicorn
CMD ["./entrypoint.sh"]

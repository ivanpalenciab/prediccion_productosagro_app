# Usa una imagen oficial de Python
FROM python:3.13-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        locales \
        libgomp1 \
    && sed -i '/^# *es_ES.UTF-8 UTF-8/s/^# *//' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=es_ES.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# Variables de entorno de idioma
ENV LANG=es_ES.UTF-8 \
    LANGUAGE=es_ES:es \
    LC_ALL=es_ES.UTF-8

# Copiar requirements primero para aprovechar la cache
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para correr FastAPI
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
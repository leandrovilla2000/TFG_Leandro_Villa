# Imagen base oficial de Python
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-dev \
    tesseract-ocr-eng \
    tesseract-ocr-script-latn \
    libtesseract-dev \
    libleptonica-dev \
    python3-pil \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Workspace
WORKDIR /app

# Copiar requerimientos y código
COPY requirements.txt ./
COPY src/ ./src/
COPY app/ ./app/

# Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto de Streamlit (por defecto)
EXPOSE 8501

# Comando por defecto para lanzar la app
CMD streamlit run app/app_gui.py


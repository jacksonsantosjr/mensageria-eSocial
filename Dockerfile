# -- Stage 1: Build Frontend --
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# -- Stage 2: Runtime Backend (FastAPI + SPA) --
FROM python:3.12-slim
WORKDIR /app

# Dependências do sistema e libxml2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências REST Backend
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copiar códigos das chaves, scripts e base backend
COPY backend ./backend/
# Criar pasta para certificados (caso necessário para arquivos temporários)
RUN mkdir -p certs

# Importar frontend construido do container `frontend-builder`
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# O Hugging Face Spaces utiliza a porta 7860 padrao
EXPOSE 7860

# Command de entrada 
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

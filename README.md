# eSocial Mensageria

Sistema independente para transmissão de eventos do eSocial ao governo federal, com validação XSD, assinatura digital (XMLDSIG) e consulta assíncrona de protocolos.

## 🎯 Sobre

O eSocial Mensageria recebe XMLs de eventos gerados pelo ERP Totvs RM, valida, assina digitalmente com certificado A1 e transmite ao Web Service do eSocial via protocolo SOAP com mTLS.

## 🏗️ Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + FastAPI |
| SOAP Client | zeep |
| Assinatura XML | signxml + cryptography |
| Validação XSD | lxml |
| Jobs Assíncronos | FastAPI BackgroundTasks + APScheduler |
| Banco de Dados | PostgreSQL (Supabase em produção) |
| Frontend | React + Vite + TypeScript |
| Estilo | Tailwind CSS v4 |

## 🚀 Setup Rápido (5 passos)

### Pré-requisitos
- Docker e Docker Compose instalados
- Certificado A1 (.pfx) disponível

### 1. Clone o repositório
```bash
git clone <repository-url>
cd esocial-mensageria
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações reais
```

### 3. Coloque o certificado A1
```bash
mkdir certs
# Copie seu arquivo .pfx para a pasta /certs/
cp /caminho/do/seu/certificado.pfx ./certs/
```

### 4. Suba os serviços
```bash
docker-compose up -d
```

### 5. Verifique a instalação
```bash
# Backend
curl http://localhost:8000/api/health

# Frontend
# Abra http://localhost:3000 no navegador
```

## 📁 Estrutura do Projeto

```
/esocial-mensageria
  /backend              → API FastAPI
    /api                → Rotas REST
    /core               → Configurações e segurança
    /services           → Lógica de negócio
    /tasks              → Jobs assíncronos (APScheduler)
    /schemas            → Modelos Pydantic
    /xsd                → Schemas XSD (cache local)
    /db                 → Modelos SQLModel + migrations
    /tests              → Testes pytest
  /frontend             → Aplicação React
    /src
      /components       → Componentes reutilizáveis
      /pages            → Páginas da aplicação
      /services         → Serviços de API
      /types            → Interfaces TypeScript
  /scripts              → Scripts utilitários
```

## 🔒 Segurança

- Certificados A1 (.pfx) são mantidos fora do repositório
- Comunicação SOAP via mTLS (TLS 1.2+)
- Senhas e segredos via variáveis de ambiente
- CORS restrito ao domínio do frontend

## 📋 Ambientes

| Ambiente | Descrição |
|----------|-----------|
| `homologacao` | Ambiente de testes (padrão para desenvolvimento) |
| `production` | Ambiente de produção do eSocial |

## 📄 Licença

Projeto proprietário — uso interno.

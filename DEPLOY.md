# Guia de Deploy - eSocial Mensageria

Este documento consolida as etapas necessárias para rodar o projeto em produção, focado na arquitetura dividida (Backend no Hugging Face e Frontend via provedores estáticos ou rede corporativa).

## 1. Backend (FastAPI) em Hugging Face Spaces

O backend foi construído em Python 3.12 utilizando FastAPI, estruturado para consumir mínimo de recursos e executar rotas assíncronas juntamente com o validador `zeep` + `signxml`.


### Preparando o Space (Docker)
1. Crie uma conta no [Hugging Face](https://huggingface.co/) e vá em **Deploy > Spaces > Create New Space**.
2. **Nome do Space:** (ex: `empresa-mensageria-esocial`, `sua-empresa-esocial`)
3. **License:** MIT / Private (Recomendado Private se for lidar com certificados reais).
4. **Space SDK:** Selecione **Docker** > **Blank**.
5. **App Port:** Configurar para `8000` (mesma definida no `backend/Dockerfile`).


### Upload dos Arquivos
Suba os seguintes arquivos e pastas que estão no dir `backend/` local para a raiz do seu Repositório do Space:
- `api/`, `core/`, `schemas/`, `services/`, `tasks/`, `db/`, `xsd/`
- `main.py`
- `requirements.txt`
- `Dockerfile`

**Atenção (Variáveis de Ambiente / Secrets):**
No Hugging Face Spaces, vá em **Settings > Variables and secrets** e defina:
- `MOCK_ESOCIAL=true` (Para testes) ou `false` (Produção SERPRO)
- A chave e o certificado A1/A3 (`CERT_PASSWORD`, `CERT_PATH`), lembrando que o certificado em si não deve ir exposto. Recomenda-se Base64 Encode nos Secrets se não houver container persistente gerenciado.

O Hugging Face irá compilar ("Build") o container via Dockerfile de forma automática sempre que você comitar no Space.

---

## 2. Frontend (React + Vite)
O Frontend gera arquivos estáticos (HTML/JS/CSS), o que o torna barato e resiliente.

### Compilando para Produção
No seu ambiente/máquina sem bloqueios de rede, rode:
```bash
cd frontend
npm install
npm run build
```
Uma pasta `dist/` será gerada. 

### Publicando o Frontend
Suba apenas a pasta `dist/` gerada para serviços como:
- **AWS S3 + CloudFront**
- **Vercel**
- **Servidor Nginx interno (On-Premise)**

\*Nota sobre integração HTTP:\* No Frontend production, assim que o backend estiver online, você deverá rever a `MOCK_URL` de integração para que ele aponte url do Hugging Face em vez de `localhost {nas variáveis padrões do Vite}!
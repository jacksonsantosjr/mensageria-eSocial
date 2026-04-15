# ⚠ Pendências: Rede Corporativa e IT

Este documento lista as configurações e execuções que foram deliberadamente puladas ou que falharam durante a construção inicial na máquina corporativa devido às políticas rígidas de Rede e Proxy. 

Ao continuar o desenvolvimento a partir de uma rede doméstica ou sem restrições, foque em solucionar estes pontos:

## 1. Instalação das Dependências do Front-End (Vite/Node)
Foi impossível instalar os pacotes do NPM. O Node.js esbarrou no bloqueio `403 Forbidden` do proxy corporativo na tentativa de requisição HTTP direta ao `registry.npmjs.org`.
**Ação:** 
- Abra o terminal na pasta `frontend/`.
- Execute `npm install` novamente para gerar a pasta `node_modules`.
- Se ocorrer erro por conta de cache do NPM corporativo anterior, limpe com `npm cache clean --force` e assegure-se de retirar qualquer configuração de proxy do arquivo `.npmrc` (`npm config rm proxy` e `npm config rm https-proxy`).

## 2. Dependências Recursivas do Python (Backend)
Embora os pacotes padrão estejam definidos no `requirements.txt`, dependendo do setup de firewall SSL Deep Inspection da rede atual, algumas bibliotecas vinculadas ao C/C++ ou as dependências cryptography (`lxml`, `signxml`) podem não ter baixado todos os *wheels* corretos se você também utiliza proxy no pip.
**Ação:**
- Abra o terminal na pasta `backend/`.
- Garanta que seu virtual environment (`.venv`) esteja ativo.
- Execute `pip install -r requirements.txt` para finalizar e confirmar que todas as libs criptográficas estão prontas.

## 3. Certificado Habilitável (.pfx)
O ambiente simulou a arquitetura perfeita para recepção da sua chave digital. No entanto, por razões óbvias de restrições corporativas/dados sensíveis, a importação final da senha vinculada ao certificado Serasa/TOTVS ficou no arquivo de variaveis provisório.
**Ação:**
- Cole fisicamente o seu arquivo certificado real dentro da rede local segura dele.
- Preencha os campos de `CERT_PASSWORD` correspondentes.

## Próximo Passo para visualização de Teste
Após rodar os instaladores citados acima, basta rodar simultaneamente:
1. `uvicorn main:app --reload` (na pasta `backend/` na porta 8000)
2. `npm run dev` (na pasta `frontend/` rodará a interface na porta 3000)
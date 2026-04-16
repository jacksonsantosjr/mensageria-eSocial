# Spec-Driven Development (SDD) - eSocial Mensageria

## 1. Visão Geral
Sistema independente para recebimento, validação, assinatura e transmissão de eventos XML do eSocial gerados (por ERP como Totvs RM) ao Web Service do governo federal usando certificados A1 (arquivos `.pfx`) e A3 (Token/Cartão Smartcard).

## 2. Objetivos e Não-Objetivos

### Objetivos (Goals)
- Processar os eventos XML de modo independente.
- Assinar eventos via XMLDSIG com suporte para certificados do tipo A1 e A3 (e-CNPJ).
- Realizar validação via XSD antes de qualquer transmissão.
- Consumir o Web Service SOAP do eSocial utilizando mTLS bidirecional.
- Manter o fluxo assíncrono padrão do governo: **Envio -> Protocolo -> Consulta Assíncrona -> Resultado**.
- Prover ambiente visual e rastreável de pendências, aprovações e lotes.

### Não-Objetivos (Non-Goals)
- Não será um ERP gerador das folhas de pagamento ou cálculos.
- Não substitui o banco de dados nativo do sistema Totvs; ele atua puramente como "Mensageria e Auditoria de Envio".

## 3. Requisitos Funcionais
1. **Suporte a Múltiplos Certificados:** O sistema DEVE permitir a validação e transmissão de dados através de certificados A1 e também suportar integração/identificação futura com hardware A3.
2. **Validador:** O sistema DEVE validar o lote contra os schemas do eSocial antes do envio e barrar o processamento antecipado com erro útil (`ValidationResult`).
3. **Assinador:** O sistema DEVE aplicar a assinatura `enveloped` em cada evento e no envelope global obrigatoriamente.
4. **Mensageria Assíncrona:** O sistema DEVE implementar uma fila de repetição (`APScheduler` / `FastAPI BackgroundTasks`) efetuando `polling` até receber os códigos finais de `200` (Processado com Sucesso) ou falhas (`401`, `422`, `500`).
5. **Dashboard Operacional:** O sistema DEVE dispor de interface gráfica (React/Vite) para conferência detalhada e submissão manual do status e erros (`<ocorrencia>`) devolvidos.

## 4. Requisitos Não Funcionais
1. **Desempenho:** Parsing e assinatura XML devem ser suportados rapidamente usando `lxml` + `signxml`.
2. **Segurança:** Senhas de certificados não trafegam e devem ser inseridas sob demanda nas execuções corporativas, sem comitar credenciais no código-fonte.

## 5. Estado Atual vs Estado Alvo (Target State)
- **Estado Atual:** 
  Foram gerasadas as cascas principais via scripts de inicialização descritos no `eSocial_Mensageria_Guia_Completo.docx`. O módulo XSD e Validador, junto com testes iniciais, existem. As pendências de rede (dependências do NPM e PIP) estão sendo baixadas.
- **Estado Alvo:**
  Faltam implementar completamente o suporte aos Web Services dinâmicos SOAP (eSocial) em modo Produção vs Homologação, integrar o fluxo via Celery real, subir as rotas finais Rest do backend, configurar UI para consultar lotes e injetar a inteligência A3.

## 6. Divisão de Tarefas / Roadmap
- **[x] Fase 0:** Infraestrutura Básica (Repo Clonado).
- **[x] Fase 1:** Scaffold FastAPI Backend + ORM Models.
- **[x] Fase 2:** Módulos LXML Validador XSD e Assinador.
- **[ ] Fase 3:** SOAP Client (zeep) + Integrações Assíncronas (APScheduler).
- **[ ] Fase 4:** Estruturação das Telas do Frontend React + Vite.
- **[ ] Fase 5:** Testes ponta-a-ponta, refino do uso A1/A3 e deploys.

## 7. Questões em Aberto / Pendências
*Como o A3 exige drivers PKCS#11 no sistema hospedeiro, será necessário validar se o backend rodará em servidor / máquina local do cliente ou via cloud com redirecionamento de porta USB.*

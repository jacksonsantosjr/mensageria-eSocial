# SPEC-001: Exportação de Recibos eSocial em PDF

## Overview
Este documento especifica a implementação da funcionalidade de geração e exportação de comprovantes de entrega do eSocial em formato PDF. O objetivo é fornecer ao usuário um documento oficial, elegante e corporativo que comprove a transmissão dos eventos para o governo.

## Goals
- Gerar PDFs profissionais com layout minimalista e autoridade.
- Suportar exportação consolidada (Lote completo).
- Suportar exportação individual (Evento específico).
- Incluir metadados de auditoria (Data/Hora de geração).

## Non-Goals
- Edição do conteúdo do PDF após a geração.
- Envio automático do PDF por e-mail (fora de escopo desta task).

## User Stories
- **Como usuário**, quero baixar o comprovante de um lote inteiro para arquivamento mensal.
- **Como usuário**, quero baixar o recibo de um evento específico para enviar a um cliente ou departamento.
- **Como gestor**, quero que o PDF tenha uma identidade visual limpa e contenha o CNPJ e Protocolo visíveis.

## Functional Requirements

### 1. Geração de PDF (Backend)
- Utilização da biblioteca `fpdf2`.
- **Layout de Cabeçalho**: Título "Comprovante de Transmissão eSocial", Logotipo da Empresa (se houver) ou Iniciais Estilizadas, e Dados da Empresa (Nome, CNPJ).
- **Layout do Corpo**:
    - Tabela de dados de transmissão: Protocolo, Ambiente (Homologação/Produção), Data de Envio.
    - Tabela de Eventos: Tipo (S-1000, etc), ID do Evento, Status, Número do Recibo.
    - **Seção de Erros**: Caso o status seja `ERROR`, exibir tabela de ocorrências com código e descrição da rejeição.
- **Layout de Rodapé**: Texto "Documento gerado automaticamente pelo sistema de Mensageria eSocial em [DATA] às [HORA]".

### 2. Gestão de Identidade Visual (Logo)
- Implementação de upload de imagem (PNG/JPG/WEBP) no cadastro da empresa.
- Armazenamento seguro via `StorageService`.

### 3. API Endpoints
- `GET /api/lotes/{id}/pdf`: Gera PDF consolidado.
- `GET /api/eventos/{id}/pdf`: Gera PDF de evento único.
- `POST /api/empresas/{id}/logo`: Upload do logotipo da empresa.

### 3. Interface (Frontend)
- Botão "Baixar Comprovante" na lista de Lotes.
- Botão de ícone (PDF) na lista de Eventos de um lote.
- Feedback de processamento (Spinner) durante a geração.

## Data Model / API Contract
Não há alterações no banco de dados. Os dados serão extraídos das tabelas `Lote`, `Evento` e `Empresa` existentes.

## Edge Cases & Error Handling
- **Recibo Inexistente**: Se o evento não estiver processado, o PDF exibirá "Pendente de Processamento" no campo de recibo.
- **Falha na Geração**: O backend deve retornar 500 com mensagem clara caso a lib `fpdf2` falhe.

## Task Breakdown
1. **Configuração**: Instalar `fpdf2` e configurar fontes básicas.
2. **Serviço PDF**: Criar `backend/services/pdf_service.py` com o layout base.
3. **Endpoints**: Implementar as rotas no FastAPI.
4. **UI Lotes**: Adicionar botões de download na página `Lotes.tsx`.
5. **UI Eventos**: Implementar visualização/download na listagem de eventos.

## Changelog
- 2026-04-16: Criação inicial da SPEC.

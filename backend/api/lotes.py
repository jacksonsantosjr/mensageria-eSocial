"""
Rotas de Lotes — Persistência Real e Integração com Storage
Endpoints para upload de XML, listagem e consulta no banco de dados Supabase.
"""
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends, status, BackgroundTasks, Response
from typing import Optional
from sqlmodel import Session, select, desc

from db.session import get_session
from core.config import settings
from db.models import Lote, LoteStatus, Empresa, Ambiente, Evento
from schemas.lote import LoteResponse, LoteDetalheResponse
from services.storage_service import storage_service
from services.batch_processor import BatchProcessor
from services.pdf_service import pdf_service

logger = logging.getLogger(__name__)
router = APIRouter()
processor = BatchProcessor()

@router.post("/lotes/upload", response_model=LoteResponse, status_code=status.HTTP_201_CREATED)
async def upload_lote(
    background_tasks: BackgroundTasks,
    empresa_id: uuid.UUID = Query(..., description="ID da empresa emissora"),
    ambiente: Ambiente = Query(Ambiente.HOMOLOGATION),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload de XML de lote de eventos do eSocial.
    """
    try:
        # 1. Validações Iniciais
        if not file.filename or not file.filename.endswith(".xml"):
            raise HTTPException(status_code=400, detail="Apenas arquivos .xml são aceitos.")
        
        empresa = session.get(Empresa, empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não cadastrada.")

        # 2. Leitura e Persistência de Arquivo (Storage)
        content = await file.read()
        lote_id = uuid.uuid4()
        storage_path = f"lotes/{empresa_id}/{lote_id}_original.xml"
        
        try:
            xml_url = await storage_service.upload_file(storage_path, content)
        except Exception as e:
            logger.error("Falha ao salvar no Storage: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Erro no Storage: {str(e)}")

        # 3. Criação do Registro no Banco (Metadados)
        db_lote = Lote(
            id=lote_id,
            empresa_id=empresa_id,
            xml_original=xml_url,
            status=LoteStatus.VALIDATING,
            ambiente=ambiente,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(db_lote)
        session.commit()
        session.refresh(db_lote)

        # 4. Processamento Assíncrono
        background_tasks.add_task(
            processor.process_lote_upload, 
            content.decode('utf-8', errors='ignore'), 
            db_lote, 
            session
        )
        
        return db_lote
    except Exception as e:
        logger.error("Erro crítico no upload: %s", str(e))
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {str(e)}")

@router.get("/lotes", response_model=list[LoteResponse])
async def listar_lotes(
    empresa_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """Lista lotes sincronizados com o banco de dados real."""
    statement = select(Lote).order_by(desc(Lote.created_at))
    if empresa_id:
        statement = statement.where(Lote.empresa_id == empresa_id)
    
    results = session.exec(statement.offset(offset).limit(limit))
    return results.all()

@router.get("/lotes/{lote_id}", response_model=LoteDetalheResponse)
async def obter_lote(lote_id: uuid.UUID, session: Session = Depends(get_session)):
    """Retorna detalhes de um lote e seus eventos do banco de dados."""
    lote = session.get(Lote, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    
    # Adicionamos a URL pública de download para o frontend
    lote_dict = lote.model_dump()
    if lote.xml_original:
        lote_dict["xml_original_url"] = storage_service.get_public_url(lote.xml_original)
        
    return {**lote_dict, "eventos": lote.eventos}


@router.post("/lotes/{lote_id}/sign", response_model=LoteResponse)
async def assinar_lote(lote_id: uuid.UUID, session: Session = Depends(get_session)):
    """Dispara o processo de assinatura para um lote existente."""
    lote = session.get(Lote, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    
    if lote.status != LoteStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Lote em status {lote.status} não pode ser assinado.")

    # Busca XML original do Storage
    try:
        content = await storage_service.download_file(lote.xml_original)
        # Re-processa (Extração + Assinatura A1 se disponível)
        await processor.process_lote_upload(content.decode('utf-8', errors='ignore'), lote, session)
        session.refresh(lote)
    except Exception as e:
        logger.error("Falha ao assinar lote %s: %s", lote_id, str(e))
        raise HTTPException(status_code=500, detail=f"Erro no processamento de assinatura: {e}")

    return lote

@router.post("/lotes/{lote_id}/send", response_model=LoteResponse)
async def enviar_lote(lote_id: uuid.UUID, session: Session = Depends(get_session)):
    """Envia um lote já assinado para o Web Service do eSocial."""
    lote = session.get(Lote, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    
    if lote.status != LoteStatus.SIGNED:
        raise HTTPException(status_code=400, detail="Apenas lotes com status ASSINADO (SIGNED) podem ser enviados.")

    try:
        if settings.mock_esocial:
            # --- MODO MOCK: Simula transmissão ---
            import secrets
            lote.protocolo = f"MOCK-{secrets.token_hex(8).upper()}"
            lote.status = LoteStatus.SENT
            lote.updated_at = datetime.utcnow()
            session.add(lote)
            session.commit()
            session.refresh(lote)
            logger.info("MOCK: Lote %s transmitido com protocolo %s", lote_id, lote.protocolo)
        else:
            # --- MODO REAL: SOAP com o governo ---
            await processor.transmit_lote(lote_id, session)
            session.refresh(lote)
        
        return lote
    except Exception as e:
        logger.error("Erro ao enviar lote: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lotes/{lote_id}/pdf")
async def download_lote_pdf(lote_id: uuid.UUID, session: Session = Depends(get_session)):
    """Gera e retorna o comprovante PDF de um lote."""
    lote = session.get(Lote, lote_id)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    
    try:
        pdf_bytes = pdf_service.generate_lote_pdf(lote)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="recibo_lote_{str(lote_id)[:8]}.pdf"'
            }
        )
    except Exception as e:
        logger.error("Erro ao gerar PDF do lote %s: %s", lote_id, str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {e}")

@router.get("/eventos/{evento_id}/pdf")
async def download_evento_pdf(evento_id: uuid.UUID, session: Session = Depends(get_session)):
    """Gera e retorna o comprovante PDF de um evento individual."""
    evento = session.exec(select(Evento).where(Evento.id == evento_id)).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    
    try:
        pdf_bytes = pdf_service.generate_evento_pdf(evento)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="recibo_evento_{str(evento_id)[:8]}.pdf"'
            }
        )
    except Exception as e:
        logger.error("Erro ao gerar PDF do evento %s: %s", evento_id, str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {e}")

import sys
import os
from dotenv import load_dotenv

import traceback
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

try:
    from db.session import engine
    from sqlmodel import Session, select
    from db.models import Lote
    from services.pdf_service import pdf_service

    with Session(engine) as session:
        lotes = session.exec(select(Lote).where(Lote.status == 'SENT')).all()
        if lotes:
            print(f"Encontrado {len(lotes)} lotes SENT. Testando geração...")
            for lote in lotes:
                try:
                    pdf_service.generate_lote_pdf(lote)
                    print(f"Lote {lote.id} => SUCESSO!")
                except Exception as e:
                    print(f"Lote {lote.id} => ERRO GERANDO PDF:")
                    traceback.print_exc()
        else:
            print("Nenhum lote SENT no banco.")
except Exception as main_e:
    print("ERRO GLOBAL:")
    traceback.print_exc()

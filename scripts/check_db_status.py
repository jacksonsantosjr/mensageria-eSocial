import os
import sys
from sqlmodel import Session, select, create_engine
from dotenv import load_dotenv

# Adiciona o diretorio backend ao path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from db.models import Empresa
    from core.config import settings
except ImportError as e:
    print(f"Erro ao importar modelos: {e}")
    sys.exit(1)

def check_db():
    load_dotenv()
    cnpj = os.getenv("CNPJ_TRANSMISSOR")
    if not cnpj:
        print("Erro: CNPJ_TRANSMISSOR nao definido no .env")
        return

    engine = create_engine(settings.database_url)
    try:
        with Session(engine) as session:
            statement = select(Empresa).where(Empresa.cnpj == cnpj)
            emp = session.exec(statement).first()
            
            if emp:
                print(f"Empresa encontrada: {emp.razao_social}")
                if emp.cert_base64:
                    print(f"Status do Certificado: OK (Variavel cert_base64 preenchida)")
                else:
                    print(f"Status do Certificado: AUSENTE no Banco de Dados")
                    print(f"Nota: O BatchProcessor depende do cert_base64 no banco para o fluxo A1.")
            else:
                print(f"Empresa com CNPJ {cnpj} NAO encontrada no banco de dados.")
    except Exception as e:
        print(f"Erro de conexao com o banco: {e}")

if __name__ == "__main__":
    check_db()

"""
Serviço de Geração de PDFs — eSocial Mensageria
Utiliza fpdf2 para criar comprovantes de entrega elegantes e profissionais.
"""
import io
import logging
import httpx
from datetime import datetime, timedelta
from fpdf import FPDF
from db.models import Lote, Evento, Empresa, LoteStatus, Ambiente
from services.storage_service import storage_service

logger = logging.getLogger(__name__)

class PDFReceiptGenerator(FPDF):
    def header(self):
        # O cabeçalho será customizado no momento da geração para incluir o logo
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        
        # O Fuso do HF Spaces é UTC. Ajustando para BRT (UTC-3)
        now_brt = datetime.now() - timedelta(hours=3)
        now_str = now_brt.strftime("%d/%m/%Y às %H:%M:%S")
        self.cell(0, 10, f"Documento gerado automaticamente pelo sistema de Mensageria eSocial em {now_str}", align="C")

    def create_table_header(self, columns):
        self.set_fill_color(240, 240, 240)
        self.set_text_color(50, 50, 50)
        self.set_font("helvetica", "B", 9)
        for col_name, width in columns:
            self.cell(width, 8, col_name, border=1, align="C", fill=True)
        self.ln()

class PDFService:
    def _setup_document(self, pdf: PDFReceiptGenerator, empresa: Empresa):
        pdf.add_page()
        
        text_start_x = 10
        text_start_y = 12
        
        # Logo da Empresa
        has_logo = False
        if empresa.logo_path:
            logo_url = empresa.logo_path
            
            # Formata URL absoluta do Supabase se for caminho interno do storage
            if not logo_url.startswith("http"):
                logo_url = storage_service.get_public_url(logo_url)
                
            try:
                # Download temporário do logo via httpx
                with httpx.Client() as client:
                    resp = client.get(logo_url, timeout=5.0)
                    if resp.status_code == 200:
                        logo_data = io.BytesIO(resp.content)
                        # Insere no topo esquerdo com largura menor (22mm)
                        pdf.image(logo_data, x=10, y=10, w=22)
                        has_logo = True
                        text_start_x = 36 # Recua o texto à direita da logo ajustada
            except Exception as e:
                logger.error(f"Falha ao carregar logo no PDF: {e}")

        # Razão Social
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102) # Azul Corporativo
        pdf.set_xy(text_start_x, text_start_y)
        pdf.cell(0, 8, empresa.razao_social.upper())
        pdf.ln(8)
            
        # Formata e Imprime CNPJ
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        clean_cnpj = empresa.cnpj.replace(".", "").replace("/", "").replace("-", "")
        formatted_cnpj = f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}" if len(clean_cnpj) == 14 else empresa.cnpj
        
        pdf.set_x(text_start_x)
        pdf.cell(0, 6, f"CNPJ: {formatted_cnpj}")
        pdf.ln(6)
        
        # Posicionamento pós-cabeçalho
        if has_logo:
            # Garante que o documento desça as coordenadas Y para ultrapassar a altura da imagem caso ela seja grande
            new_y = max(pdf.get_y(), 34)
            pdf.set_y(new_y)
        else:
            pdf.ln(10)
        
        # Título do Documento
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "COMPROVANTE DE TRANSMISSÃO ESOCIAL", align="C")
        pdf.ln(10)
        pdf.ln(5)

    def generate_lote_pdf(self, lote: Lote) -> bytes:
        """Gera um PDF consolidado de um lote completo."""
        pdf = PDFReceiptGenerator()
        empresa = lote.empresa
        self._setup_document(pdf, empresa)
        
        # Dados do Lote
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "DADOS DO LOTE")
        pdf.ln(8)
        pdf.set_font("helvetica", "", 10)
        
        if lote.created_at:
            dt_brt = lote.created_at - timedelta(hours=3)
            data_transmissao = dt_brt.strftime("%d/%m/%Y %H:%M")
        else:
            data_transmissao = "---"
            
        pdf.cell(90, 7, f"Protocolo: {lote.protocolo or 'N/A'}", border="B")
        pdf.cell(0, 7, f"Data de Envio: {data_transmissao}", border="B")
        pdf.ln(7)
        
        ambiente_str = "PRODUÇÃO" if lote.ambiente == Ambiente.PRODUCTION else "HOMOLOGAÇÃO (TESTES)"
        pdf.cell(90, 7, f"Ambiente: {ambiente_str}", border="B")
        pdf.cell(0, 7, f"Status: {str(lote.status.value if hasattr(lote.status, 'value') else lote.status)}", border="B")
        pdf.ln(7)
        pdf.ln(10)
        
        # Tabela de Eventos
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "EVENTOS TRANSMITIDOS")
        pdf.ln(8)
        
        cols = [("Tipo", 25), ("ID do Evento", 85), ("Status", 30), ("Recibo", 50)]
        pdf.create_table_header(cols)
        
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        
        for evt in lote.eventos:
            tipo_val = str(evt.tipo.value if hasattr(evt.tipo, 'value') else evt.tipo)
            status_val = str(evt.status.value if hasattr(evt.status, 'value') else evt.status)
            
            pdf.cell(25, 7, tipo_val, border=1, align="C")
            pdf.cell(85, 7, str(evt.evento_id_esocial or "")[:40], border=1)
            pdf.cell(30, 7, status_val, border=1, align="C")
            pdf.cell(50, 7, str(evt.nr_recibo or "---"), border=1, align="C")
            pdf.ln()
            
            # Se houver erro, detalha abaixo do evento
            if evt.status == "ERROR" and evt.ocorrencias_json:
                pdf.set_fill_color(255, 235, 235)
                items = evt.ocorrencias_json.get("items", [])
                for oc in items:
                    msg = f"Erro [{oc.get('codigo')}]: {oc.get('descricao')}"
                    pdf.multi_cell(0, 5, msg, border=1, fill=True)
        
        return bytes(pdf.output())

    def generate_evento_pdf(self, evento: Evento) -> bytes:
        """Gera um PDF para um único evento específico."""
        pdf = PDFReceiptGenerator()
        lote = evento.lote
        empresa = lote.empresa
        self._setup_document(pdf, empresa)
        
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "DETALHES DO EVENTO")
        pdf.ln(8)
        pdf.set_font("helvetica", "", 10)
        
        tipo_val = str(evento.tipo.value if hasattr(evento.tipo, 'value') else evento.tipo)
        status_val = str(evento.status.value if hasattr(evento.status, 'value') else evento.status)

        pdf.cell(100, 7, f"Tipo de Evento: {tipo_val}", border="B")
        pdf.cell(0, 7, f"Status: {status_val}", border="B")
        pdf.ln(7)
        pdf.cell(100, 7, f"ID eSocial: {evento.evento_id_esocial or '---'}", border="B")
        pdf.cell(0, 7, f"Recibo: {evento.nr_recibo or 'PENDENTE'}", border="B")
        pdf.ln(7)
        pdf.ln(10)
        
        if evento.status == "ERROR" and evento.ocorrencias_json:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 8, "MOTIVOS DA REJEIÇÃO / OCORRÊNCIAS:", ln=True)
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            
            items = evento.ocorrencias_json.get("items", [])
            for oc in items:
                pdf.set_fill_color(250, 250, 250)
                pdf.multi_cell(0, 6, f"• {oc.get('descricao')} (Código: {oc.get('codigo')})", border=1, fill=True)
        
        return bytes(pdf.output())

pdf_service = PDFService()

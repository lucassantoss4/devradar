import pdfplumber
from core.extractors.base import BaseExtractor
from core.logger import get_logger

logger = get_logger("PDFExtractor")

class PDFExtractor(BaseExtractor):
    def __init__(self):
        self.docling_available = False
        try:
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            self.docling_available = True
        except Exception as e:
            logger.warning(f"⚠️ Docling (IA) indisponível: {e}. Usando modo offline.")

    def extract(self, file_path):
        """Extrai texto de PDF usando IA ou Fallback Offline"""
        
        # 1. Tentativa IA
        if self.docling_available:
            try:
                logger.info(f"🤖 Lendo PDF com IA: {file_path.name}")
                result = self.converter.convert(file_path)
                text = result.document.export_to_markdown()
                if text and len(text.strip()) > 50:
                    return text
            except Exception as e:
                logger.error(f"❌ Falha IA: {e}. Tentando modo offline...")

        # 2. Tentativa Offline (PDFPlumber)
        try:
            logger.info(f"📄 Lendo PDF Offline: {file_path.name}")
            texto_completo = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: texto_completo += t + "\n"
            
            if texto_completo:
                return f"# Fonte: pdfplumber\n# Arquivo: {file_path.name}\n\n{texto_completo}"
                
        except Exception as e:
            logger.error(f"❌ Erro fatal no PDF {file_path.name}: {e}")
        
        return ""
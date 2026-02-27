from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class EditalSchema(BaseModel):
    id: str
    arquivo_origem: str
    titulo: str
    resumo: str
    data_inscricao_fim: Optional[date] = None
    status: str
    custo: str
    elegibilidade: str = "Não Identificada"
    link_fonte: Optional[str] = None
    processado_em: str
    metodo_extracao: str

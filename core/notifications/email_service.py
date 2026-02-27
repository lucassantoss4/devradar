import os
import logging
from datetime import datetime, date, timedelta

# Tenta importar a biblioteca do Outlook
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger("EmailService")

class NotificadorOutlook:
    def __init__(self):
        self.destinatarios = os.getenv("EMAIL_DESTINATARIOS", "")

    def _conectar_e_enviar(self, assunto, html_body):
        """Envia e-mail usando o Outlook Desktop (Apenas Windows)."""
        if not WIN32_AVAILABLE:
            logger.warning(f"⚠️ Notificação via Outlook Desktop ignorada (Ambiente não-Windows ou pywin32 ausente).")
            logger.info(f"💡 DICA: Use o Power Automate para processar alertas em produção.")
            return

        try:
            outlook = win32com.client.Dispatch('Outlook.Application')
            mail = outlook.CreateItem(0)
            mail.To = self.destinatarios
            mail.Subject = assunto
            mail.HTMLBody = html_body
            mail.Send()
            logger.info(f"✅ E-mail '{assunto}' enviado para {self.destinatarios} via Outlook!")
        except Exception as e:
            logger.error(f"❌ Erro no Outlook: {e}")

    def _gerar_card_html(self, titulo, subtitulo, tags, link, cor_borda="#3b82f6", alerta_urgencia=None):
        tags_html = "".join([
            f'<span style="background: #f3f4f6; color: #555; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; text-transform: uppercase;">{tag}</span>' 
            for tag in tags
        ])
        
        html_urgencia = ""
        if alerta_urgencia:
            html_urgencia = f'<div style="color: #ef4444; font-weight: bold; font-size: 11px; margin-bottom: 5px;">🔥 {alerta_urgencia}</div>'

        return f"""
        <div style="border-left: 4px solid {cor_borda}; background: #ffffff; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); font-family: sans-serif;">
            {html_urgencia}
            <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">
                {subtitulo}
            </div>
            <h3 style="margin: 0 0 10px 0; color: #1e293b; font-size: 16px;">{titulo}</h3>
            <div style="margin-bottom: 15px;">
                {tags_html}
            </div>
            <a href="{link}" style="background-color: {cor_borda}; color: #ffffff; text-decoration: none; padding: 8px 15px; border-radius: 5px; font-size: 13px; display: inline-block;">
                Acessar &rarr;
            </a>
        </div>
        """

    def enviar_premios(self, lista_premios):
        hoje = date.today()
        premios_filtrados = []

        for p in lista_premios:
            if p.get('status') != 'ABERTO': continue
            dias_restantes = 999
            try:
                dt_fim = datetime.strptime(p['data_inscricao_fim'], "%d/%m/%Y").date()
                dias_restantes = (dt_fim - hoje).days
            except: pass
            p['_dias_restantes'] = dias_restantes
            premios_filtrados.append(p)

        if not premios_filtrados: return

        # Ordena por urgência
        premios_filtrados.sort(key=lambda x: x['_dias_restantes'])

        html_cards = ""
        count_urgentes = 0
        for p in premios_filtrados:
            dias = p['_dias_restantes']
            aviso = None
            if dias <= 7:
                aviso = f"URGENTE: Restam apenas {dias} dias!"
                count_urgentes += 1
            elif dias <= 15:
                aviso = "Atenção: Encerra em 2 semanas"

            html_cards += self._gerar_card_html(
                titulo=p['titulo'],
                subtitulo=f"PRAZO: {p['data_inscricao_fim']}",
                tags=[p['custo'], "Edital"],
                link=p['link_fonte'],
                cor_borda="#f97316",
                alerta_urgencia=aviso
            )
        
        titulo_mail = f"🏆 DevRadar: {len(premios_filtrados)} Prêmios Abertos"
        if count_urgentes > 0:
            titulo_mail = f"🚨 URGENTE: {count_urgentes} Prêmios acabando esta semana!"

        self._enviar_template_padrao(titulo_mail, html_cards, "Premiações")

    def enviar_eventos(self, lista_eventos):
        hoje = date.today()
        limite_dias = 60
        eventos_filtrados = []
        
        for e in lista_eventos:
            dt_str = e.get('data_inicio')
            if not dt_str: continue 
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
                dias_ate_evento = (dt - hoje).days
                if 0 <= dias_ate_evento <= limite_dias:
                    e['_dias_ate'] = dias_ate_evento
                    eventos_filtrados.append(e)
            except: continue

        if not eventos_filtrados:
            logger.info(f"ℹ️ Nenhum evento encontrado nos próximos {limite_dias} dias.")
            return

        eventos_filtrados.sort(key=lambda x: x['_dias_ate'])

        html_cards = ""
        for e in eventos_filtrados:
            dias = e['_dias_ate']
            data_vis = datetime.strptime(e['data_inicio'], "%Y-%m-%d").strftime("%d/%m/%Y")
            loc = e.get('localizacao', {})
            local_txt = f"{loc.get('cidade', 'Local')}"
            
            aviso = None
            if dias == 0: aviso = "É HOJE!"
            elif dias <= 7: aviso = f"É nesta semana (Faltam {dias} dias)"

            tags = [e.get('custo', 'info')]
            if e.get('ia_foco_principal'): tags.insert(0, "IA CORE")

            html_cards += self._gerar_card_html(
                titulo=e['nome'],
                subtitulo=f"{data_vis} • {local_txt}",
                tags=tags,
                link=e['link'],
                cor_borda="#3b82f6",
                alerta_urgencia=aviso
            )

        self._enviar_template_padrao(f"📅 Agenda Tech: {len(eventos_filtrados)} Eventos (Próx. 60 dias)", html_cards, "Agenda Tech")

    def _enviar_template_padrao(self, titulo_email, conteudo_html, nome_sessao):
        html_body = f"""
        <div style="font-family: 'Segoe UI', sans-serif; background-color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #fff; border: 1px solid #e2e8f0; border-radius: 8px;">
                <div style="background-color: #1e293b; padding: 15px; text-align: center; color: white; border-radius: 8px 8px 0 0;">
                    <h2 style="margin:0; font-size: 18px;">DevRadar Intelligence</h2>
                    <p style="margin:5px 0 0; font-size:12px; color:#cbd5e1;">Monitoramento Automático • {nome_sessao}</p>
                </div>
                <div style="padding: 20px;">
                    <p style="color: #333;">Oportunidades com <strong>atenção imediata</strong>:</p>
                    {conteudo_html}
                </div>
                <div style="background-color: #f1f5f9; padding: 10px; text-align: center; font-size: 11px; color: #888;">
                    Gerado via Outlook Automation • {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
            </div>
        </div>
        """
        self._conectar_e_enviar(titulo_email, html_body)
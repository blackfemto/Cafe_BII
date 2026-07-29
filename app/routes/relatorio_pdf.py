from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

from app.database import get_db
from app import models
from app.crud.historico import listar_historico_por_fechamento

router = APIRouter()


def ajustar_fuso(data_utc):
    return data_utc - timedelta(hours=3)


@router.get("/relatorio-pdf/{fechamento_id}")
def gerar_relatorio_pdf(
    fechamento_id: int,
    db: Session = Depends(get_db)
):
    # Buscar o fechamento
    fechamento = db.query(models.FechamentoCaixa).filter(
        models.FechamentoCaixa.id == fechamento_id
    ).first()
    
    if not fechamento:
        return {"erro": "Fechamento não encontrado"}
    
    # Buscar as comandas do histórico
    comandas = listar_historico_por_fechamento(db, fechamento_id)
    
    # =============================================
    # GERAR PDF
    # =============================================
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Title'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    elements.append(Paragraph("RELATÓRIO DE FECHAMENTO DE CAIXA", titulo_style))
    
    # Subtítulo
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    data_fechamento_br = ajustar_fuso(fechamento.data_fechamento)
    elements.append(Paragraph(f"Data do Fechamento: {data_fechamento_br.strftime('%d/%m/%Y %H:%M')}", subtitulo_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # =============================================
    # RESUMO
    # =============================================
    resumo_data = [
        ["Indicador", "Valor"],
        ["Total de Vendas", f"R$ {fechamento.total_vendas:.2f}"],
        ["Quantidade de Comandas", str(len(comandas))],
        ["Dinheiro", f"R$ {fechamento.total_dinheiro:.2f}"],
        ["PIX", f"R$ {fechamento.total_pix:.2f}"],
        ["Cartão", f"R$ {fechamento.total_cartao:.2f}"],
        ["Ticket Médio", f"R$ {fechamento.total_vendas / len(comandas):.2f}" if comandas else "R$ 0,00"]
    ]
    
    resumo_table = Table(resumo_data, colWidths=[2.5 * inch, 2.5 * inch])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(resumo_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # =============================================
    # LISTA DE COMANDAS
    # =============================================
    elements.append(Paragraph("DETALHAMENTO DAS COMANDAS", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))
    
    if comandas:
        dados_comandas = [["Comanda", "Cliente", "Valor", "Forma Pagamento", "Data/Hora"]]
        for c in comandas:
            data_br = ajustar_fuso(c.data_fechamento)
            dados_comandas.append([
                c.codigo,
                c.cliente,
                f"R$ {c.total:.2f}",
                c.forma_pagamento,
                data_br.strftime("%d/%m/%Y %H:%M")
            ])
        
        comandas_table = Table(dados_comandas, colWidths=[1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
        comandas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(comandas_table)
        elements.append(Spacer(1, 0.1 * inch))
        
        # Total
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(f"Total Geral: R$ {fechamento.total_vendas:.2f}", total_style))
    else:
        elements.append(Paragraph("Nenhuma comanda registrada no período.", styles['Normal']))
    
    # =============================================
    # RODAPÉ
    # =============================================
    elements.append(Spacer(1, 0.5 * inch))
    rodape_style = ParagraphStyle(
        'Rodape',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    elements.append(Paragraph("Documento gerado automaticamente pelo Café BII", rodape_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_caixa_{fechamento_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        }
    )

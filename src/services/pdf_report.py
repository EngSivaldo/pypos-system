from fpdf import FPDF
from datetime import datetime
import os
# CORREÇÃO 1: Importamos Sale e SaleItem do mesmo lugar
from src.models.sale import Sale, SaleItem 

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'PyPOS Enterprise - Relatório de Vendas', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_sales_report(db_session):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)

    # Título com Data
    today = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f'Gerado em: {today}', 0, 1, 'L')
    pdf.ln(5)

    # Cabeçalho da Tabela
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Data/Hora', 1)
    pdf.cell(80, 10, 'ID Venda / Info', 1)
    pdf.cell(30, 10, 'Total (R$)', 1)
    pdf.ln()

    # Dados do Banco
    pdf.set_font('Arial', '', 10)
    
    # CORREÇÃO 2: Usamos 'created_at' em vez de 'date_created'
    sales = db_session.query(Sale).order_by(Sale.created_at.desc()).limit(50).all()
    
    total_geral = 0
    
    for sale in sales:
        # CORREÇÃO 3: Aqui também usamos 'created_at'
        if sale.created_at:
            data_fmt = sale.created_at.strftime("%d/%m %H:%M")
        else:
            data_fmt = "--/--"
            
        # Tratamento seguro para ID (pega os primeiros 8 caracteres se for UUID longo)
        venda_id = str(sale.id)[:8] if sale.id else "N/A"
        
        pdf.cell(40, 10, data_fmt, 1)
        pdf.cell(80, 10, f"Venda #{venda_id}", 1)
        pdf.cell(30, 10, f"R$ {sale.total_amount:.2f}", 1)
        pdf.ln()
        total_geral += sale.total_amount

    # Totalização
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'TOTAL GERAL: R$ {total_geral:.2f}', 0, 1, 'R')

    # Salvar na Pasta Documentos do Usuário
    output_folder = os.path.join(os.path.expanduser("~"), "Documents", "Relatorios_PyPOS")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    filename = f"Relatorio_Vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_folder, filename)
    
    pdf.output(filepath)
    return filepath
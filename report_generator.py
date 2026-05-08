from fpdf import FPDF
import pandas as pd
import tempfile
import os

class LogisticsReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 18)
        self.set_text_color(30, 27, 75) # Navy blue
        self.cell(0, 10, "Reporte de Laboratorio de Costos y Produccion", border=False, ln=True, align="C")
        self.set_draw_color(99, 102, 241) # Indigo
        self.set_line_width(0.5)
        self.line(10, 22, 200, 22)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    def draw_dataframe(self, title, df, col_widths=None):
        self.set_font("Arial", "B", 13)
        self.set_text_color(30, 27, 75)
        self.cell(0, 10, title, ln=True)
        self.ln(1)
        
        # Header
        self.set_font("Arial", "B", 10)
        self.set_fill_color(230, 230, 250) # Light lavender
        self.set_text_color(0, 0, 0)
        
        cols = df.columns
        if col_widths is None:
            w = (self.w - 20) / len(cols)
            widths = [w] * len(cols)
        else:
            widths = col_widths

        for i, col in enumerate(cols):
            self.cell(widths[i], 8, str(col), border=1, align='C', fill=True)
        self.ln()
        
        # Data
        self.set_font("Arial", size=9)
        for i, row in df.iterrows():
            # Alternate row colors
            if i % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(245, 245, 250)
                
            for j, col in enumerate(cols):
                val = str(row[col]).encode('latin-1', 'replace').decode('latin-1')
                self.cell(widths[j], 7, val, border=1, align='C', fill=True)
            self.ln()
        self.ln(6)

def generate_pdf(data):
    pdf = LogisticsReport()
    pdf.add_page()
    
    # 1. Tabla: Costos Fijos (Prorrateables)
    pdf.draw_dataframe("1. Costos Fijos (Prorrateables / L)", data['df_prorr'], col_widths=[100, 90])
    
    # 2. Tabla: Costos Variables por Categoría
    # df_vars tiene Concepto, STANDART, GENERICO, PREMIUM
    pdf.draw_dataframe("2. Costos Variables por Categoria (USD / L)", data['df_vars'], col_widths=[70, 40, 40, 40])
    
    # 3. Tabla: Desglose de Costos Actual
    # df_bd tiene Tipo, Concepto, USD/Lt, MXN/Lt, Total MXN
    pdf.draw_dataframe("3. Desglose de Costos Actual", data['df_bd'], col_widths=[25, 60, 30, 30, 45])
    
    # 4. Sección: Impacto de Producción (5 Cuadros/Métricas)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 10, "Impacto de Produccion", ln=True)
    pdf.ln(2)
    
    # Dibujar "Cajas" de métricas
    metrics = [
        ("Volumen Total", f"{data['litros_totales']:,.1f} Lts"),
        ("Total Piezas", f"{data['piezas']} Pzas"),
        ("Presentacion", data['envase'].split('(')[0].strip()),
        ("Costo / Litro", f"${data['costo_litro_final']:,.3f} MXN"),
        ("Costo / Pieza", f"${data['costo_pieza_total']:,.2f} MXN")
    ]
    
    # Configuración de cajas: 5 columnas
    box_w = (pdf.w - 20) / 5
    box_h = 25
    
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    for i, (label, value) in enumerate(metrics):
        # Dibujar borde de la caja
        pdf.set_draw_color(99, 102, 241)
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(x_start + (i * box_w), y_start, box_w, box_h, style='DF')
        
        # Texto de la etiqueta
        pdf.set_xy(x_start + (i * box_w), y_start + 5)
        pdf.set_font("Arial", "B", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(box_w, 5, label.upper(), ln=False, align='C')
        
        # Texto del valor
        safe_val = value.encode('latin-1', 'replace').decode('latin-1')
        pdf.set_xy(x_start + (i * box_w), y_start + 12)
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(30, 27, 75)
        pdf.cell(box_w, 7, safe_val, ln=False, align='C')

    # Output pdf file temporarily and read bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
    
    pdf.output(temp_path)
    
    with open(temp_path, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_path)
    return pdf_bytes

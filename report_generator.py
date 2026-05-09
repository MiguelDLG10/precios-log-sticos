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
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    def draw_dataframe(self, title, df, col_widths=None):
        if df.empty:
            return
            
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
            self.cell(widths[i], 8, str(col).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C', fill=True)
        self.ln()
        
        # Data
        self.set_font("Arial", size=9)
        for i, row in df.iterrows():
            # Check for page break
            if self.get_y() > 260:
                self.add_page()
                # Redraw header if page break
                self.set_font("Arial", "B", 10)
                self.set_fill_color(230, 230, 250)
                for j, col in enumerate(cols):
                    self.cell(widths[j], 8, str(col).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C', fill=True)
                self.ln()
                self.set_font("Arial", size=9)

            if i % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(245, 245, 250)
                
            for j, col in enumerate(cols):
                val = str(row[col]).encode('latin-1', 'replace').decode('latin-1')
                self.cell(widths[j], 7, val, border=1, align='C', fill=True)
            self.ln()
        self.ln(6)

def generate_pdf(data, charts=None):
    pdf = LogisticsReport()
    pdf.add_page()
    
    # 1. Tabla: Costos Fijos (Prorrateables)
    pdf.draw_dataframe("1. Costos Fijos (Prorrateables / L)", data['df_prorr'], col_widths=[100, 90])
    
    # 2. Tabla: Costos Variables por Categoria
    pdf.draw_dataframe("2. Costos Variables por Categoria (USD / L)", data['df_vars'], col_widths=[70, 40, 40, 40])
    
    # 3. Tabla: Desglose de Costos Actual
    pdf.draw_dataframe("3. Desglose de Costos Actual", data['df_bd'], col_widths=[25, 60, 30, 30, 45])
    
    # 4. Sección: Impacto de Produccion (5 Cajas)
    if pdf.get_y() > 230:
        pdf.add_page()
        
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 10, "Impacto de Produccion", ln=True)
    pdf.ln(2)
    
    impact_metrics = [
        ("Volumen Total", f"{data['litros_totales']:,.1f} Lts"),
        ("Total Piezas", f"{data['piezas']} Pzas"),
        ("Presentacion", data['envase'].split('(')[0].strip()),
        ("Costo / Litro", f"${data['costo_litro_final']:,.3f} MXN"),
        ("Costo / Pieza", f"${data['costo_pieza_total']:,.2f} MXN")
    ]
    
    box_w = (pdf.w - 20) / 5
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(99, 102, 241)
    
    for label, _ in impact_metrics:
        pdf.cell(box_w, 8, label.upper(), border='TLR', align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 27, 75)
    for _, value in impact_metrics:
        safe_val = value.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(box_w, 12, safe_val, border='BLR', align='C', fill=True)
    pdf.ln(12)

    # 5. Cálculo de Empaque (Pesos)
    if pdf.get_y() > 240:
        pdf.add_page()
    
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 10, "Calculo de Empaque", ln=True)
    pdf.ln(2)
    
    packaging_metrics = [
        ("Peso Bruto Unitario", f"{data['peso_unitario']:,.2f} Kg"),
        ("Piezas", f"{data['piezas']} Pzas"),
        ("Peso Total Flete", f"{data['peso_total']:,.2f} Kg")
    ]
    
    p_box_w = (pdf.w - 20) / 3
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(100, 116, 139)
    for label, _ in packaging_metrics:
        pdf.cell(p_box_w, 8, label.upper(), border='TLR', align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 27, 75)
    for _, value in packaging_metrics:
        pdf.cell(p_box_w, 12, value, border='BLR', align='C', fill=True)
    pdf.ln(15)

    # 6. Cotización Logística y Utilidad Neta
    if pdf.get_y() > 200:
        pdf.add_page()
        
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 10, "Cotizacion Logistica y Utilidad Neta", ln=True)
    pdf.ln(4)
    
    for q in data['quotes']:
        # Card style
        pdf.set_fill_color(250, 250, 255)
        pdf.set_draw_color(200, 200, 230)
        
        # Determine profit and colors
        safe_cost = q['cost'] if (q['cost'] is not None and q['cost'] >= 0) else 0
        if q['cost'] == 0.0: safe_cost = 0.0
        
        if q['cost'] is None or q['cost'] == -1:
            utilidad = 0
            u_str = "N/A"
            u_color = (100, 100, 100)
        else:
            utilidad = data['precio_venta_total'] - (safe_cost + data['costo_prod_mxn'])
            u_str = f"$ {utilidad:,.2f} MXN"
            u_color = (34, 139, 34) if utilidad > 0 else (220, 20, 60)
            
        # Draw Card
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(30, 27, 75)
        pdf.cell(0, 10, f"Plataforma: {q['name']}", border='TLR', ln=True, fill=True, align='L')
        
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"   Detalle: {q['detail']}", border='LR', ln=True, fill=True)
        
        # Summary row
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 8, "   UTILIDAD NETA:", border='L', fill=True)
        pdf.set_text_color(*u_color)
        pdf.cell(0, 8, u_str, border='R', ln=True, fill=True)
        
        # Breakdown row
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(80, 80, 80)
        breakdown_str = f"   (Ingreso: ${data['precio_venta_total']:,.2f} | Produccion: ${data['costo_prod_mxn']:,.2f} | Logistica: ${safe_cost:,.2f})"
        pdf.cell(0, 8, breakdown_str, border='BLR', ln=True, fill=True)
        pdf.ln(5)

    # 7. NUEVA SECCIÓN: Análisis Visual (Gráficas)
    if charts:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(30, 27, 75)
        pdf.cell(0, 10, "Analisis Visual de Costos", ln=True)
        pdf.ln(5)
        
        for title, img_path in charts.items():
            if os.path.exists(img_path):
                # Verificar espacio disponible para la imagen
                if pdf.get_y() > 180:
                    pdf.add_page()
                
                pdf.set_font("Arial", "B", 11)
                pdf.set_text_color(50, 50, 50)
                pdf.cell(0, 8, title, ln=True)
                pdf.image(img_path, w=170)
                pdf.ln(10)

    # Output pdf file temporarily and read bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
    
    pdf.output(temp_path)
    
    with open(temp_path, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_path)
    return pdf_bytes

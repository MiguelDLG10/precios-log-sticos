from fpdf import FPDF
import tempfile
import os

class LogisticsReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(13, 17, 23)
        self.cell(0, 10, "Reporte de Costos Logisticos", border=False, ln=True, align="C")
        self.set_draw_color(100, 149, 237)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

def generate_pdf(data):
    pdf = LogisticsReport()
    pdf.add_page()
    
    # Parámetros Ingresados
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Parametros Ingresados", ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"- Envase Seleccionado: {data['envase']}", ln=True)
    pdf.cell(0, 8, f"- Densidad del Producto: {data['densidad']} Kg/L", ln=True)
    pdf.cell(0, 8, f"- Numero de Piezas: {data['piezas']}", ln=True)
    pdf.cell(0, 8, f"- Precio Unitario de Venta: ${data['precio_unitario']:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Zona de Envio: {data['zona_px']}", ln=True)
    pdf.ln(5)

    # Propiedades Físicas
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Pesos Calculados", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"- Peso Bruto Unitario: {data['peso_unitario']:,.2f} Kg", ln=True)
    pdf.cell(0, 8, f"- Peso Bruto Total: {data['peso_total']:,.2f} Kg", ln=True)
    pdf.ln(5)

    # Cotizaciones
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Cotizaciones Incurridas", ln=True)
    pdf.ln(2)
    
    platforms = [
        ("Mercado Libre", data['ml_costo_total'], data['ml_costo_pieza'], data['ml_tarifa']),
        ("Amazon", data['amz_costo_total'], data['amz_costo_pieza'], data['amz_tarifa']),
        ("PaqueteExpress", data['px_costo_total'], data['px_costo_pieza'], data['px_tarifa']),
    ]
    
    for name, c_tot, c_pz, tarif in platforms:
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(50, 50, 200)
        pdf.cell(0, 8, f"Plataforma: {name}", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 6, f"   Clasificacion: {tarif}", ln=True)
        
        if c_tot == -1:
            pdf.cell(0, 6, "   Costo Total: Peso Excedido (> Maximo Permitido)", ln=True)
            pdf.cell(0, 6, "   Costo por Pieza: Consulta Tarifas de Carga Especial", ln=True)
        elif c_tot is None:
            pdf.cell(0, 6, "   Costo Total: No aplica", ln=True)
        elif c_tot == 0.0:
            pdf.cell(0, 6, "   Costo Total: Envio Gratis (A considerar politicas de vendedor)", ln=True)
        else:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 6, f"   Costo Logistico Total: ${c_tot:,.2f}", ln=True)
            if c_pz is not None:
                pdf.cell(0, 6, f"   Costo Logistico por Pieza: ${c_pz:,.2f}", ln=True)
        pdf.ln(4)

    # Output pdf file temporarily and read bytes to avoid version string return issues with PyFPDF and FPDF2
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
    
    pdf.output(temp_path)
    
    with open(temp_path, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_path)
    return pdf_bytes

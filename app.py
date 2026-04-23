import streamlit as st
import pandas as pd
from prices_logic import load_excel_data, get_cost, determine_subtariff, TARIFFS
from report_generator import generate_pdf

# --- Configuración de Página ---
st.set_page_config(page_title="Organizador de Precios", layout="wide", page_icon="📦")

# --- CSS Moderno (Glassmorphism & Aesthetics) ---
def local_css():
    st.markdown("""
    <style>
    /* Fondo principal y tipografía */
    .stApp {
        background: linear-gradient(135deg, #0d1117, #161b22);
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Contenedor tipo Glassmorphism para las tarjetas */
    .glass-card {
        background: rgba(255, 255, 255, 0.05); /* Ligeramente translúcido */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Títulos dentro de las tarjetas */
    .card-title {
        color: #58a6ff;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
        font-size: 1.25rem;
    }

    /* Valores destacados */
    .highlight-value {
        font-size: 2rem;
        font-weight: 700;
        color: #79c0ff;
        margin: 10px 0;
    }
    
    /* Etiquetas pequeñas */
    .metric-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Logos o iconos (estilizados texto) */
    .platform-icon {
        font-size: 24px;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Carga de Datos ---
@st.cache_data
def get_data():
    return load_excel_data()

df_envases = get_data()

# --- Interfaz Principal ---
col_header, _ = st.columns([3, 1])
with col_header:
    st.title("📦 Calculadora de Costos Logísticos")
    st.markdown("Calcula pesos y cotiza los envíos en las principales plataformas para evaluar tu rentabilidad.")

if df_envases.empty:
    st.error("No se pudo cargar la tabla de especificaciones ('Tabla de especificaciones de envases en Excel.xlsx'). Revisa el archivo.")
    st.stop()

st.markdown("---")

# --- Sección de Inputs (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Parámetros del Producto")
    st.markdown("Ingresa los detalles para calcular los tabuladores.")
    
    envase_seleccionado = st.selectbox("1. Selecciona el Envase:", df_envases['Etiqueta_UI'].tolist())
    densidades_opciones = [1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08]
    densidad = st.selectbox("2. Densidad del Producto (Kg/L):", densidades_opciones)
    piezas = st.number_input("3. Número de Piezas:", min_value=1, value=1, step=1)
    precio_unitario = st.number_input("4. Precio de Venta Unitario ($):", min_value=1.0, value=350.0, step=10.0, help="Requerido para determinar tarifas de Amazon y Mercado Libre.")
    
    zonas_paquetexpress = list(TARIFFS["Paquetexpress"].keys())
    zona_px = st.selectbox("5. Zona de Envío (PaqueteExpress):", zonas_paquetexpress)

# --- Cálculos Base ---
fila_seleccionada = df_envases[df_envases['Etiqueta_UI'] == envase_seleccionado].iloc[0]
capacidad_l = fila_seleccionada['Capacidad_L']
peso_envase_kg = fila_seleccionada['Peso_Envase_Kg']

peso_neto_unidad = capacidad_l * densidad
peso_bruto_unidad = peso_neto_unidad + peso_envase_kg
peso_bruto_total = peso_bruto_unidad * piezas

# --- Mostrar Métricas Físicas ---
st.markdown("### ⚖️ Cálculo de Peso")
col_w1, col_w2, col_w3 = st.columns(3)

def card_html(title, value, unit=""):
    return f"""
    <div class="glass-card">
        <div class="metric-label">{title}</div>
        <div class="highlight-value">{value:.2f} {unit}</div>
    </div>
    """

with col_w1:
    st.markdown(card_html("Peso Bruto Unitario", peso_bruto_unidad, "Kg"), unsafe_allow_html=True)
with col_w2:
    st.markdown(card_html("Multiplicador", piezas, "piezas"), unsafe_allow_html=True)
with col_w3:
    st.markdown(card_html("Peso Total del Envío", peso_bruto_total, "Kg"), unsafe_allow_html=True)


# --- Evaluación de Tarifas ---
st.markdown("---")
st.markdown("### 💰 Cotizaciones por Plataforma")

# Cálculo Mercado Libre
tarifa_ml_str = determine_subtariff("Mercado Libre", precio_unitario)
costo_ml_total = get_cost(peso_bruto_total, "Mercado Libre", tarifa_ml_str)

# Cálculo Amazon
tarifa_amz_str = determine_subtariff("Amazon", precio_unitario)
costo_amz_total = get_cost(peso_bruto_total, "Amazon", tarifa_amz_str)

# Cálculo Paquetexpress
costo_px_total = get_cost(peso_bruto_total, "Paquetexpress", zona_px)

def create_platform_card(platform_name, icon, total_cost, piece_cost, info_subtarifa):
    if total_cost is None:
        cost_str = "No aplica"
        piece_str = "---"
    elif total_cost == -1:
        cost_str = "Peso Excedido"
        piece_str = "Consulta Carga Ruteada"
    elif total_cost == 0.0:
        cost_str = "Envío Gratis / A revisar"
        piece_str = "$ 0.00"
    else:
        cost_str = f"$ {total_cost:,.2f}"
        if piece_cost is not None:
             piece_str = f"$ {piece_cost:,.2f}"
        else:
             piece_str = "---"

    html = f"""
    <div class="glass-card">
        <div class="card-title"><span class="platform-icon">{icon}</span>{platform_name}</div>
        <div class="metric-label">Costo Total Logístico</div>
        <div class="highlight-value" style="color: #4ade80;">{cost_str}</div>
        <div class="metric-label">Costo Unitario (Por Pieza)</div>
        <div style="font-size: 1.25rem; font-weight: 500; margin-top: 5px;">{piece_str}</div>
        <div style="margin-top: 15px; font-size: 0.8rem; color: #8b949e; border-top: 1px dotted #30363d; padding-top: 10px;">
            Tarifa aplicada: {info_subtarifa}
        </div>
    </div>
    """
    return html

col_plat1, col_plat2, col_plat3 = st.columns(3)

with col_plat1:
    costo_ml_pieza = costo_ml_total / piezas if costo_ml_total and costo_ml_total > 0 else None
    st.markdown(create_platform_card("Mercado Libre", "🤝", costo_ml_total, costo_ml_pieza, f"Clasificación: {tarifa_ml_str}"), unsafe_allow_html=True)

with col_plat2:
    costo_amz_pieza = costo_amz_total / piezas if costo_amz_total and costo_amz_total > 0 else None
    st.markdown(create_platform_card("Amazon", "🛒", costo_amz_total, costo_amz_pieza, f"Clasificación: {tarifa_amz_str}"), unsafe_allow_html=True)

with col_plat3:
    costo_px_pieza = costo_px_total / piezas if costo_px_total and costo_px_total > 0 else None
    st.markdown(create_platform_card("PaqueteExpress", "🚚", costo_px_total, costo_px_pieza, f"Zona: {zona_px}"), unsafe_allow_html=True)

st.markdown("<br><center><small style='color: #8b949e;'>Las tarifas son aproximadas y basadas en tabuladores estándar logísticos. Sujetas a cambios por volumetría o recargos de los operadores.</small></center>", unsafe_allow_html=True)

# --- Generación de Reporte PDF ---
st.markdown("---")
st.markdown("### 📄 Generar Reporte de Cotización")
st.markdown("Descarga un informe detallado con todos los parámetros y costos presentados.")

report_data = {
    "envase": envase_seleccionado,
    "densidad": densidad,
    "piezas": piezas,
    "precio_unitario": precio_unitario,
    "zona_px": zona_px,
    "peso_unitario": peso_bruto_unidad,
    "peso_total": peso_bruto_total,
    "ml_costo_total": costo_ml_total,
    "ml_costo_pieza": costo_ml_pieza,
    "ml_tarifa": tarifa_ml_str,
    "amz_costo_total": costo_amz_total,
    "amz_costo_pieza": costo_amz_pieza,
    "amz_tarifa": tarifa_amz_str,
    "px_costo_total": costo_px_total,
    "px_costo_pieza": costo_px_pieza,
    "px_tarifa": zona_px
}

pdf_bytes = generate_pdf(report_data)

st.download_button(
    label="🔽 Descargar Reporte en PDF",
    data=pdf_bytes,
    file_name="reporte_costos_logisticos.pdf",
    mime="application/pdf",
    type="primary"
)


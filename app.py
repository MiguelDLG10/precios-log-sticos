import streamlit as st
import pandas as pd
from prices_logic import (
load_excel_data, get_cost, determine_subtariff, TARIFFS, 
load_production_costs, save_production_costs, get_production_costs, 
get_production_costs_detailed, load_barcode_data, load_product_materia_prima, 
save_product_materia_prima, get_current_exchange_rate, get_packaging_price,
restore_latest_backup
)
from report_generator import generate_pdf

# --- Configuración de Página ---
st.set_page_config(page_title="Organizador de Precios", layout="wide", page_icon="📦")

# --- CSS Moderno (Glassmorphism & Aesthetics) ---
def local_css():
    st.markdown("""
    <style>
    /* Importar fuente Inter de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ============================================ */
    /*  DISEÑO PREMIUM - ALTA VISIBILIDAD          */
    /* ============================================ */

    /* Fondo principal y tipografía */
    .stApp {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Mejorar legibilidad global de Streamlit */
    .stApp p, .stApp li, .stApp span, .stApp label, .stApp div {
        color: #f1f5f9 !important;
        font-size: 1.1rem !important;
    }

    /* Headers principales */
    .stApp h1 {
        color: #ffffff !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }

    .stApp h2 {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }

    .stApp h3 {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Sidebar mejorado */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #f1f5f9 !important;
        font-size: 1.05rem !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Inputs del sidebar */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stNumberInput label {
        color: #67e8f9 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ============================================ */
    /*  TARJETAS GLASSMORPHISM MEJORADAS            */
    /* ============================================ */
    .glass-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        margin-bottom: 20px;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 16px 48px 0 rgba(99, 102, 241, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
        border-color: rgba(99, 102, 241, 0.45);
    }

    /* Títulos dentro de las tarjetas */
    .card-title {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        padding-bottom: 12px;
        font-size: 1.6rem !important;
        letter-spacing: -0.01em;
    }

    /* Valores destacados — GRANDES y BRILLANTES */
    .highlight-value {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        color: #67e8f9 !important;
        -webkit-text-fill-color: #67e8f9 !important;
        text-shadow: 0 0 20px rgba(103, 232, 249, 0.25);
        margin: 12px 0;
        line-height: 1.2;
    }

    /* Etiquetas — VISIBLES con color BLANCO */
    .metric-label {
        font-size: 1.2rem !important;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600 !important;
    }

    /* Logos o iconos (estilizados texto) */
    .platform-icon {
        font-size: 28px;
        margin-right: 10px;
        vertical-align: middle;
    }

    /* ============================================ */
    /*  TABLAS / DATAFRAMES                         */
    /* ============================================ */
    .stDataFrame {
        font-size: 1.15rem !important;
    }

    .stDataFrame th {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
    }

    .stDataFrame td {
        color: #f1f5f9 !important;
        font-size: 1.1rem !important;
    }

    /* ============================================ */
    /*  TABS MEJORADOS                              */
    /* ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #f1f5f9 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        border-radius: 12px 12px 0 0 !important;
    }

    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(99, 102, 241, 0.15) !important;
        border-bottom: 3px solid #818cf8 !important;
    }

    /* ============================================ */
    /*  BOTONES                                     */
    /* ============================================ */
    .stDownloadButton > button,
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }

    .stDownloadButton > button:hover,
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    /* ============================================ */
    /*  EXPANDER                                    */
    /* ============================================ */
    .streamlit-expanderHeader {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }

    /* ============================================ */
    /*  CAPTIONS Y TEXTOS SECUNDARIOS               */
    /* ============================================ */
    .stCaption, small, .stApp small {
        color: #e2e8f0 !important;
        font-size: 1.1rem !important;
    }

    /* Separadores */
    hr {
        border-color: rgba(99, 102, 241, 0.2) !important;
    }

    /* Mejorar select boxes y number inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stDataFrame {
        color: #ffffff !important;
        background-color: rgba(30, 41, 59, 0.5) !important;
        font-size: 1.05rem !important;
    }

    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Carga de Datos ---
@st.cache_data
def get_data():
    return load_excel_data()

@st.cache_data
def get_barcode_data():
    return load_barcode_data()

@st.cache_data(ttl=3600) # Actualizar cada hora para reflejar cambios diarios sin saturar
def get_live_rate():
    return get_current_exchange_rate()

df_envases = get_data()
df_barcodes = get_barcode_data()
product_costs = load_product_materia_prima()
live_rate = get_live_rate()
if live_rate is None:
    live_rate = 17.52

# --- Interfaz Principal ---

col_header, _ = st.columns([3, 1])
with col_header:
    st.title("📦 Calculadora de Costos Logísticos y Producción")
    st.markdown("Calcula pesos, tabula costos internos y cotiza en plataformas para ver tu Utilidad Real.")

if df_envases.empty:
    st.error("No se pudo cargar la tabla de especificaciones. Revisa el archivo excel.")
    st.stop()

st.markdown("---")

# --- Sección de Inputs (Sidebar) ---
with st.sidebar:
    st.header("🌍 Factores Globales")
    paridad_usd = st.number_input("Paridad USD/MXN ($):", min_value=1.0, value=live_rate, step=0.1)
    
    st.markdown("---")
    # Obtener productos únicos por Clave/Nombre
    df_barcodes['Product_Unique_Key'] = df_barcodes['Producto'].astype(str) + " | " + df_barcodes['Producto II'].astype(str).fillna('')
    unique_products = sorted(df_barcodes['Product_Unique_Key'].unique().tolist())
    
    # Lógica de Pre-procesamiento (Necesaria para que Parámetros tenga datos)
    selected_prod_unique = st.session_state.get("product_selector", "-- Seleccionar --")
    selected_product_data = None
    available_envases_indices = []
    materia_prima_default_mxn = 0.0

    if selected_prod_unique != "-- Seleccionar --":
        df_presentaciones = df_barcodes[df_barcodes['Product_Unique_Key'] == selected_prod_unique].copy()
        prod_id_first = str(df_presentaciones['Producto'].iloc[0])
        materia_prima_usd_saved = product_costs.get(prod_id_first, 0.0)
        materia_prima_default_mxn = materia_prima_usd_saved * paridad_usd
        
        for _, row in df_presentaciones.iterrows():
            e_name = str(row['Envase']).lower()
            e_cap = str(int(row['Multiplicador']))
            for i, label in enumerate(df_envases['Etiqueta_UI']):
                if e_name in label.lower() and e_cap in label:
                    if i not in available_envases_indices:
                        available_envases_indices.append(i)
        selected_product_data = df_presentaciones.iloc[0]

    # --- ⚙️ SECCIÓN: PARÁMETROS DEL PRODUCTO (Ahora Arriba) ---
    st.header("⚙️ Parámetros del Producto")
    st.markdown("Detalles de la presentación y venta.")
    
    all_envases_labels = df_envases['Etiqueta_UI'].tolist()
    envase_options = [all_envases_labels[i] for i in available_envases_indices] if available_envases_indices else all_envases_labels

    envase_seleccionado = st.selectbox(
        "1. Selecciona el Envase:", 
        envase_options,
        key="envase_selector"
    )
    
    piezas = st.number_input("2. Número de Piezas:", min_value=1, value=1, step=1)
    precio_unitario = st.number_input("3. Precio Venta C/U ($):", min_value=1.0, value=350.0, step=10.0)

    st.markdown("---")

    # --- 🔍 SECCIÓN: BUSCADOR DE PRODUCTOS (Ahora Abajo) ---
    st.header("🔍 Buscador de Productos")
    
    selected_prod_unique = st.selectbox(
        "1. Seleccionar Producto (Clave):", 
        ["-- Seleccionar --"] + unique_products,
        key="product_selector"
    )
    
    if selected_prod_unique != "-- Seleccionar --":
        st.caption(f"✅ Clave: {str(selected_product_data['Producto'])}")

    # Lógica de Densidad
    def_densidad_idx = 0
    densidades_opciones = [1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08]
    if selected_product_data is not None:
        prod_densidad = float(selected_product_data['Densidad'])
        if prod_densidad in densidades_opciones:
            def_densidad_idx = densidades_opciones.index(prod_densidad)
        else:
            densidades_opciones.append(prod_densidad)
            densidades_opciones.sort()
            def_densidad_idx = densidades_opciones.index(prod_densidad)

    densidad = st.selectbox("2. Densidad del Producto (Kg/L):", densidades_opciones, index=def_densidad_idx)
    
    st.markdown("---")
    st.subheader("🧪 Materia Prima")
    materia_prima_mxn = st.number_input(
        "Costo Materia Prima (MXN / Litro):", 
        min_value=0.0, 
        value=float(materia_prima_default_mxn), 
        step=0.5,
        help="Costo del líquido en PESOS por cada litro. Se convertirá a USD para los cálculos internos."
    )
    
    # Convertir a USD para la lógica
    materia_prima_input_usd = materia_prima_mxn / paridad_usd if paridad_usd > 0 else 0
    
    if selected_product_data is not None:
        st.markdown(f"**Costo en USD:** `${materia_prima_input_usd:.3f}`")
        if st.button("💾 GUARDAR COSTO EN CATÁLOGO", type="primary"):
            if save_product_materia_prima(selected_product_data['Producto'], materia_prima_input_usd):
                st.success("¡Costo Guardado!")
                # Actualizar caché local
                product_costs[str(selected_product_data['Producto'])] = materia_prima_input_usd
            else:
                st.error("Error al guardar.")

    st.markdown("---")
    zonas_paquetexpress = list(TARIFFS["Paquetexpress"].keys())
    zona_px = st.selectbox("7. Zona de Envío (PaqueteExpress):", zonas_paquetexpress)


# --- Cálculos Base Iniciales ---
fila_seleccionada = df_envases[df_envases['Etiqueta_UI'] == envase_seleccionado].iloc[0]
capacidad_l = fila_seleccionada['Capacidad_L']
peso_envase_kg = fila_seleccionada['Peso_Envase_Kg']
costo_envase_unit_mxn = get_packaging_price(capacidad_l)
costo_envase_total_mxn = costo_envase_unit_mxn * piezas
peso_neto_unidad = capacidad_l * densidad
peso_bruto_unidad = peso_neto_unidad + peso_envase_kg
peso_bruto_total = peso_bruto_unidad * piezas
litros_totales = capacidad_l * piezas

# --- LÓGICA DE SIMULACIÓN (LABORATORIO) ---
st.markdown("### 🧪 Escenario de Producción")
col_sim1, col_sim2 = st.columns([1, 1])

with col_sim1:
    # Lógica de Categoría
    def_cat_idx = 0
    cats_list = ["STANDART", "GENERICO", "PREMIUM"]
    if selected_product_data is not None:
        prod_cat = str(selected_product_data['Clasificación']).upper().replace('STANDART', 'STANDART').replace('GENÉRICO', 'GENERICO')
        if prod_cat in cats_list:
            def_cat_idx = cats_list.index(prod_cat)
            
    categoria_prod = st.selectbox(
        "✨ Simular Categoría (Calidad):", 
        cats_list, 
        index=def_cat_idx,
        help="Cambia la calidad del producto para ver el impacto en los costos variables."
    )

    # Determinar rango automático inicial
    current_data = load_production_costs()
    auto_range_idx = 0
    rangos_labels = []
    for i, rango in enumerate(current_data.get("rangos_volumen", [])):
        prev_max = current_data["rangos_volumen"][i-1]["max_litros"] if i > 0 else 0
        label = f"{prev_max:,.1f} - {rango['max_litros']:,.1f} L"
        if rango['max_litros'] > 100000: label = f"Más de {prev_max:,.1f} L"
        rangos_labels.append(label)
        if litros_totales <= rango["max_litros"] and auto_range_idx == 0:
            auto_range_idx = i

    selected_range_label = st.selectbox(
        "📦 Simular Rango de Volumen (Tier):", 
        rangos_labels, 
        index=auto_range_idx,
        help="Ajusta el rango para ver cómo cambian los costos según la escala de producción."
    )
    range_idx = rangos_labels.index(selected_range_label)
    current_range = current_data["rangos_volumen"][range_idx]

with col_sim2:
    st.info(f"💡 **Escenario:** {categoria_prod} | {selected_range_label}\n\n**Volumen Pedido:** {litros_totales:,.1f} Lts")

# --- Cálculos Base (Basados en el rango seleccionado) ---
costo_produccion_usd_litro, desglose_dict = get_production_costs_detailed(
    current_range["max_litros"] - 0.1, # Forzamos el uso del rango seleccionado
    categoria_prod, 
    materia_prima_input_usd
)
costo_produccion_total_usd = costo_produccion_usd_litro * litros_totales
costo_produccion_total_mxn = (costo_produccion_total_usd * paridad_usd) + costo_envase_total_mxn
precio_venta_total = precio_unitario * piezas

# --- Mostrar Métricas ---
st.markdown("### 🏭 Impacto de Producción")
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)

def card_html(title, value, unit="", subtext=""):
    if isinstance(value, (int, float)): val_str = f"{value:.2f}"
    else: val_str = str(value)
    return f"""
    <div class="glass-card">
        <div class="metric-label">{title}</div>
        <div class="highlight-value" style="font-size: 2.1rem !important;">{val_str} {unit}</div>
        <div style="font-size: 1rem; color: #e2e8f0; margin-top: 6px; opacity: 0.8;">{subtext}</div>
    </div>
    """

with col_p1:
    st.markdown(card_html("Volumen Total", litros_totales, "Lts"), unsafe_allow_html=True)
with col_p2:
    st.markdown(card_html("Total Piezas", piezas, "Pzas"), unsafe_allow_html=True)
with col_p3:
    pres_name = envase_seleccionado.split('(')[0].strip()
    st.markdown(card_html("Presentación", pres_name, "", f"Capacidad: {capacidad_l}L"), unsafe_allow_html=True)
with col_p4:
    costo_litro_final = costo_produccion_total_mxn / litros_totales if litros_totales > 0 else 0
    st.markdown(card_html("Costo / Litro", costo_litro_final, "MXN", "Líquido + Envase"), unsafe_allow_html=True)
with col_p5:
    costo_pieza_total = costo_produccion_total_mxn / piezas if piezas > 0 else 0
    st.markdown(card_html("Costo / Pieza", costo_pieza_total, "MXN", f"Envase: ${costo_envase_unit_mxn:.2f}"), unsafe_allow_html=True)


st.markdown("---")
col_lab, col_desglose = st.columns([1, 1.5], gap="large")

with col_lab:
    st.markdown("### 🧪 Laboratorio de Costos")
    st.markdown("Edita o añade variables. **Se guardan en vivo.**")
    
    # 1. Editor Prorrateables
    st.markdown("#### 🔹 Fijos (Prorrateables / L)")
    df_prorr = pd.DataFrame(list(current_data["prorrateables"].items()), columns=["Concepto", "Costo USD"]).sort_values("Concepto").reset_index(drop=True)
    edited_prorr = st.data_editor(df_prorr, num_rows="dynamic", key="edit_prorr", use_container_width=True, hide_index=True)
    
    # 2. Editor Variables Multi-Categoría
    st.markdown(f"#### 🔸 Variables por Categoría")
    st.caption(f"Editando valores para el tier: `{selected_range_label}`")
    
    all_cats = ["STANDART", "GENERICO", "PREMIUM"]
    unique_concepts = set()
    for cat in all_cats:
        unique_concepts.update(current_range.get("categorias", {}).get(cat, {}).keys())
    
    unique_concepts = sorted(list(unique_concepts))
    
    rows = []
    for concept in unique_concepts:
        row = {"Concepto": concept}
        for cat in all_cats:
            row[cat] = current_range.get("categorias", {}).get(cat, {}).get(concept, 0.0)
        rows.append(row)
    
    df_vars = pd.DataFrame(rows)
    edited_vars = st.data_editor(df_vars, num_rows="dynamic", key="edit_vars", use_container_width=True, hide_index=True)
    
    if st.button("🚀 Aplicar y Guardar Cambios", type="primary", use_container_width=True):
        # Procesar Prorrateables
        new_prorr_dict = {str(row["Concepto"]).strip(): float(row["Costo USD"]) for _, row in edited_prorr.iterrows() if str(row["Concepto"]).strip() != "" and pd.notna(row["Costo USD"])}
        current_data["prorrateables"] = new_prorr_dict
        
        # Procesar Variables Multi-Categoría
        old_keys = set(unique_concepts)
        new_keys = set()
        new_data_by_cat = {cat: {} for cat in all_cats}
        
        for _, row in edited_vars.iterrows():
            concept = str(row["Concepto"]).strip()
            if concept == "": continue
            new_keys.add(concept)
            for cat in all_cats:
                val = row.get(cat, 0.0)
                new_data_by_cat[cat][concept] = float(val) if pd.notna(val) else 0.0

        added_keys = new_keys - old_keys
        removed_keys = old_keys - new_keys
        
        # Aplicar al rango actual para todas las categorías
        for cat in all_cats:
            if "categorias" not in current_range: current_range["categorias"] = {}
            current_range["categorias"][cat] = new_data_by_cat[cat]
            
        # Sincronizar todos los otros rangos
        for rango in current_data["rangos_volumen"]:
            if rango != current_range:
                if "categorias" not in rango: rango["categorias"] = {}
                for cat in all_cats:
                    if cat not in rango["categorias"]:
                        rango["categorias"][cat] = {}
                    
                    # Actualizar valores existentes y añadir nuevos
                    # Para llaves nuevas, usamos el valor ingresado en el editor como base
                    for ak in added_keys:
                        rango["categorias"][cat][ak] = new_data_by_cat[cat][ak]
                    
                    # Eliminar llaves quitadas
                    for rk in removed_keys:
                        rango["categorias"][cat].pop(rk, None)
                    
        if save_production_costs(current_data):
            st.success("¡Cambios aplicados globalmente!")
            st.rerun()
        else:
            st.error("Error al guardar.")

    # Opción de restauración
    with st.expander("🛡️ Seguridad y Copias"):
        st.caption("Cada vez que guardas, se crea una copia de seguridad automática.")
        if st.button("⏪ Restaurar Última Copia (Deshacer)", use_container_width=True):
            if restore_latest_backup():
                st.success("¡Backup restaurado con éxito!")
                st.rerun()
            else:
                st.warning("No se encontraron copias de seguridad para restaurar.")

with col_desglose:
    st.markdown("### 📊 Desglose de Costos (Actual)")
    if costo_produccion_usd_litro > 0:
        rows = []
        
        total_mxn_lt = 0.0
        for name, usd_cost in desglose_dict["Prorrateables"].items():
            c_usd = float(usd_cost)
            c_mxn = c_usd * paridad_usd
            total_mxn_lt += c_mxn
            rows.append({
                "Tipo": "Fijo", 
                "Concepto": name, 
                "USD/Lt": f"${c_usd:.3f}", 
                "MXN/Lt": f"${c_mxn:.3f}", 
                "Total MXN": f"${c_mxn * litros_totales:,.2f}"
            })
            
        for name, usd_cost in desglose_dict["Variables"].items():
            c_usd = float(usd_cost)
            c_mxn = c_usd * paridad_usd
            total_mxn_lt += c_mxn
            rows.append({
                "Tipo": f"Var", 
                "Concepto": name, 
                "USD/Lt": f"${c_usd:.3f}", 
                "MXN/Lt": f"${c_mxn:.3f}", 
                "Total MXN": f"${c_mxn * litros_totales:,.2f}"
            })

        if costo_envase_unit_mxn > 0:
            costo_envase_por_litro = costo_envase_unit_mxn / capacidad_l if capacidad_l > 0 else 0
            total_mxn_lt += costo_envase_por_litro
            rows.append({
                "Tipo": "Empaque",
                "Concepto": "Envase/Botella",
                "USD/Lt": "N/A",
                "MXN/Lt": f"${costo_envase_por_litro:.3f}",
                "Total MXN": f"${costo_envase_total_mxn:,.2f}"
            })
        
        rows.append({
            "Tipo": "🔥 TOTAL",
            "Concepto": "LÍQUIDO + ENVASE",
            "USD/Lt": "---",
            "MXN/Lt": f"${total_mxn_lt:.3f}",
            "Total MXN": f"${costo_produccion_total_mxn:,.2f}"
        })
            
        df_bd = pd.DataFrame(rows)
        st.dataframe(df_bd, use_container_width=True, hide_index=True)
        st.info(f"💡 El costo real de este producto es de **${total_mxn_lt:.3f} MXN por litro**.")
    else:
        st.info("No hay desglose de costos asignado.")

st.markdown("### ⚖️ Cálculo de Empaque")
col_w1, col_w2, col_w3 = st.columns(3)
with col_w1:
    st.markdown(card_html("Peso Bruto Unitario", peso_bruto_unidad, "Kg"), unsafe_allow_html=True)
with col_w2:
    st.markdown(card_html("Piezas", piezas, ""), unsafe_allow_html=True)
with col_w3:
    st.markdown(card_html("Peso Total Flete", peso_bruto_total, "Kg"), unsafe_allow_html=True)

# --- Evaluación de Tarifas ---
st.markdown("---")
st.markdown("### 💰 Cotizaciones Logísticas y Utilidad Neta")

tarifa_ml_str = determine_subtariff("Mercado Libre", precio_unitario)
costo_ml_total = get_cost(peso_bruto_total, "Mercado Libre", tarifa_ml_str)

tarifa_amz_str = determine_subtariff("Amazon", precio_unitario)
costo_amz_total = get_cost(peso_bruto_total, "Amazon", tarifa_amz_str)

costo_px_total = get_cost(peso_bruto_total, "Paquetexpress", zona_px)

def create_platform_card(platform_name, icon, total_cost, info_subtarifa, p_venta_tot, c_prod_mxn):
    # Manejo de costos inválidos para el cálculo
    safe_logistics_cost = total_cost if (total_cost and total_cost > 0) else 0
    if total_cost == 0.0: safe_logistics_cost = 0.0
    
    # Recalcular margen con seguridad
    if total_cost is None or total_cost == -1:
        margen_str = "N/A"
        margen_color = "#94a3b8"
    else:
        margen = p_venta_tot - (safe_logistics_cost + c_prod_mxn)
        margen_str = f"$ {margen:,.2f}"
        margen_color = "#4ade80" if margen > 0 else "#f85149"

    html = f"""<div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;">
<div style="color: #ffffff; font-weight: 700; font-size: 1.5rem; margin-bottom: 15px;"><span>{icon}</span> {platform_name}</div>
<div style="font-size: 0.9rem; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.05em;">Utilidad Neta Final</div>
<div style="font-size: 2.4rem; font-weight: 800; color: {margen_color}; margin: 10px 0;">{margen_str}</div>
<div style="margin-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.15); padding-top: 12px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 1.1rem; color: #e2e8f0;"><span>Ingreso (+)</span><span style="color: #4ade80; font-weight: 600;">$ {p_venta_tot:,.2f}</span></div>
<div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 1.1rem; color: #e2e8f0;"><span>Producción (-)</span><span style="color: #fca5a5; font-weight: 600;">$ {c_prod_mxn:,.2f}</span></div>
<div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 1.1rem; color: #e2e8f0;"><span>Logística (-)</span><span style="color: #fca5a5; font-weight: 600;">$ {safe_logistics_cost:,.2f}</span></div>
<div style="display: flex; justify-content: space-between; border-top: 1px dashed rgba(255,255,255,0.3); padding-top: 10px; font-size: 1.2rem;">
<span style="color: #ffffff; font-weight: 700;">TOTAL NETO</span><span style="color: {margen_color}; font-weight: 800;">{margen_str}</span></div></div>
<div style="font-size: 0.85rem; color: #94a3b8; margin-top: 12px; font-style: italic;">{info_subtarifa}</div></div>"""
    return html

col_plat1, col_plat2, col_plat3 = st.columns(3)

with col_plat1:
    st.markdown(create_platform_card("Mercado Libre", "🤝", costo_ml_total, f"Clasificación: {tarifa_ml_str}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

with col_plat2:
    st.markdown(create_platform_card("Amazon", "🛒", costo_amz_total, f"Clasificación: {tarifa_amz_str}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

with col_plat3:
    st.markdown(create_platform_card("PaqueteExpress", "🚚", costo_px_total, f"Zona: {zona_px}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

st.markdown("<br><center><p style='color: #e2e8f0 !important; font-size: 1.1rem !important; opacity: 0.85;'>Las tarifas logísticas son aproximadas. Costos de producción basados en configuración interna PIZARRON.</p></center>", unsafe_allow_html=True)

# --- Generación de Reporte PDF ---
st.markdown("---")
st.markdown("### 📄 Generar Reporte de Cotización")
st.markdown("Descarga un informe con desglose logístico (próximamente versión completa con costos de producción).")

report_data = {
    "envase": envase_seleccionado,
    "densidad": densidad,
    "piezas": piezas,
    "precio_unitario": precio_unitario,
    "zona_px": zona_px,
    "peso_unitario": peso_bruto_unidad,
    "peso_total": peso_bruto_total,
    "ml_costo_total": costo_ml_total,
    "ml_costo_pieza": costo_ml_total / piezas if costo_ml_total and costo_ml_total > 0 else None,
    "ml_tarifa": tarifa_ml_str,
    "amz_costo_total": costo_amz_total,
    "amz_costo_pieza": costo_amz_total / piezas if costo_amz_total and costo_amz_total > 0 else None,
    "amz_tarifa": tarifa_amz_str,
    "px_costo_total": costo_px_total,
    "px_costo_pieza": costo_px_total / piezas if costo_px_total and costo_px_total > 0 else None,
    "px_tarifa": zona_px,
    "costo_prod_mxn": costo_produccion_total_mxn,
    "utilidad_ml": precio_venta_total - (costo_ml_total + costo_produccion_total_mxn) if costo_ml_total and costo_ml_total >= 0 else 0,
}

pdf_bytes = generate_pdf(report_data)

st.download_button(
    label="🔽 Descargar Reporte en PDF",
    data=pdf_bytes,
    file_name="reporte_costos_logisticos.pdf",
    mime="application/pdf",
    type="primary"
)


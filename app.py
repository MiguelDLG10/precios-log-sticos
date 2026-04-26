import streamlit as st
import pandas as pd
from prices_logic import load_excel_data, get_cost, determine_subtariff, TARIFFS, load_production_costs, save_production_costs, get_production_costs, get_production_costs_detailed
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
tab_calc, tab_config = st.tabs(["🚀 Calculadora de Rentabilidad", "⚙️ Editor de PIZARRON (Costos)"])

with tab_calc:
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
        st.header("⚙️ Parámetros del Producto")
        st.markdown("Ingresa los detalles para calcular los tabuladores.")
        
        envase_seleccionado = st.selectbox("1. Selecciona el Envase:", df_envases['Etiqueta_UI'].tolist())
        densidades_opciones = [1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08]
        densidad = st.selectbox("2. Densidad del Producto (Kg/L):", densidades_opciones)
        piezas = st.number_input("3. Número de Piezas:", min_value=1, value=1, step=1)
        precio_unitario = st.number_input("4. Precio Venta C/U ($):", min_value=1.0, value=350.0, step=10.0)
        
        st.markdown("---")
        st.subheader("🌍 Factores de Producción")
        categoria_prod = st.selectbox("5. Categoría:", ["STANDART", "GENERICO", "PREMIUM"])
        paridad_usd = st.number_input("6. Paridad USD/MXN ($):", min_value=1.0, value=18.50, step=0.1)

        zonas_paquetexpress = list(TARIFFS["Paquetexpress"].keys())
        zona_px = st.selectbox("7. Zona de Envío (PaqueteExpress):", zonas_paquetexpress)

    # --- Cálculos Base ---
    fila_seleccionada = df_envases[df_envases['Etiqueta_UI'] == envase_seleccionado].iloc[0]
    capacidad_l = fila_seleccionada['Capacidad_L']
    peso_envase_kg = fila_seleccionada['Peso_Envase_Kg']

    peso_neto_unidad = capacidad_l * densidad
    peso_bruto_unidad = peso_neto_unidad + peso_envase_kg
    peso_bruto_total = peso_bruto_unidad * piezas
    
    litros_totales = capacidad_l * piezas
    costo_produccion_usd_litro, desglose_dict = get_production_costs_detailed(litros_totales, categoria_prod)
    costo_produccion_total_usd = costo_produccion_usd_litro * litros_totales
    costo_produccion_total_mxn = costo_produccion_total_usd * paridad_usd
    precio_venta_total = precio_unitario * piezas

    # --- Mostrar Métricas ---
    st.markdown("### 🏭 Impacto de Producción")
    col_prod1, col_prod2, col_prod3 = st.columns(3)

    def card_html(title, value, unit="", subtext=""):
        return f"""
        <div class="glass-card">
            <div class="metric-label">{title}</div>
            <div class="highlight-value">{value:.2f} {unit}</div>
            <div style="font-size: 0.8rem; color: #8b949e;">{subtext}</div>
        </div>
        """

    with col_prod1:
        st.markdown(card_html("Volumen Total", litros_totales, "Lts"), unsafe_allow_html=True)
    with col_prod2:
        st.markdown(card_html("Costo Producción Unit.", costo_produccion_usd_litro, "USD/Lt", f"~ ${(costo_produccion_usd_litro * paridad_usd):.2f} MXN"), unsafe_allow_html=True)
    with col_prod3:
        st.markdown(card_html("Costo Total Producción", costo_produccion_total_mxn, "MXN", f"Paridad: ${paridad_usd} / USD"), unsafe_allow_html=True)

    with st.expander("📊 Ver Desglose de Costos de PIZARRON que componen el total:", expanded=False):
        if costo_produccion_usd_litro > 0:
            rows = []
            
            # Prorrateables
            for name, usd_cost in desglose_dict["Prorrateables"].items():
                c_usd = float(usd_cost)
                c_mxn = c_usd * paridad_usd
                pct = (c_usd / costo_produccion_usd_litro) * 100
                rows.append({
                    "Tipo": "Fijo (Prorrateable)", 
                    "Concepto": name, 
                    "Costo Unitario (USD/Lt)": f"${c_usd:.3f} (~${c_mxn:.3f} MXN)", 
                    "Costo Total Pedido (MXN)": f"${c_mxn * litros_totales:,.2f}", 
                    "% del Gasto Total": f"{pct:.1f}%"
                })
                
            # Variables
            for name, usd_cost in desglose_dict["Variables"].items():
                c_usd = float(usd_cost)
                c_mxn = c_usd * paridad_usd
                pct = (c_usd / costo_produccion_usd_litro) * 100
                rows.append({
                    "Tipo": f"Variable ({categoria_prod})", 
                    "Concepto": name, 
                    "Costo Unitario (USD/Lt)": f"${c_usd:.3f} (~${c_mxn:.3f} MXN)", 
                    "Costo Total Pedido (MXN)": f"${c_mxn * litros_totales:,.2f}", 
                    "% del Gasto Total": f"{pct:.1f}%"
                })
                
            df_bd = pd.DataFrame(rows)
            st.dataframe(df_bd, use_container_width=True, hide_index=True)
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
        margen_str = "---"
        margen_color = "#c9d1d9"
        
        if total_cost is None:
            cost_str = "No aplica"
        elif total_cost == -1:
            cost_str = "Peso Excedido"
        elif total_cost == 0.0:
            cost_str = "Envío Gratis / A revisar"
            margen = p_venta_tot - c_prod_mxn
            margen_str = f"$ {margen:,.2f}"
            margen_color = "#4ade80" if margen > 0 else "#f85149"
        else:
            cost_str = f"$ {total_cost:,.2f}"
            margen = p_venta_tot - (total_cost + c_prod_mxn)
            margen_str = f"$ {margen:,.2f}"
            margen_color = "#4ade80" if margen > 0 else "#f85149"

        html = f"""
        <div class="glass-card">
            <div class="card-title"><span class="platform-icon">{icon}</span>{platform_name}</div>
            <div class="metric-label">Costo Logístico Estimado</div>
            <div class="highlight-value" style="color: #58a6ff; font-size: 1.4rem;">{cost_str}</div>
            <div class="metric-label">Utilidad Bruta (Venta vs Gastos)</div>
            <div style="font-size: 1.6rem; font-weight: 700; margin-top: 5px; color: {margen_color};">{margen_str}</div>
            <div style="margin-top: 15px; font-size: 0.8rem; color: #8b949e; border-top: 1px dotted #30363d; padding-top: 10px;">
                Tarifa logística: {info_subtarifa} <br><br>
                <i>Ingreso: ${p_venta_tot:,.2f} MXN</i><br>
                <i>C. Producción: -${c_prod_mxn:,.2f} MXN</i>
            </div>
        </div>
        """
        return html

    col_plat1, col_plat2, col_plat3 = st.columns(3)

    with col_plat1:
        st.markdown(create_platform_card("Mercado Libre", "🤝", costo_ml_total, f"Clasificación: {tarifa_ml_str}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

    with col_plat2:
        st.markdown(create_platform_card("Amazon", "🛒", costo_amz_total, f"Clasificación: {tarifa_amz_str}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

    with col_plat3:
        st.markdown(create_platform_card("PaqueteExpress", "🚚", costo_px_total, f"Zona: {zona_px}", precio_venta_total, costo_produccion_total_mxn), unsafe_allow_html=True)

    st.markdown("<br><center><small style='color: #8b949e;'>Las tarifas logísticas son aproximadas. Costos de producción basados en configuración interna PIZARRON.</small></center>", unsafe_allow_html=True)

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

with tab_config:
    st.header("⚙️ Configuración PIZARRON")
    st.markdown("Esta sección almacena las variables de producción en `costos_config.json`. Al Modificarlas aquí, afectarás en vivo y para el futuro todos los cálculos de márgenes brutos de los productos. (Valores expresados en USD, con conversión a MXN mostrada como referencia).")
    
    current_data = load_production_costs()
    
    st.markdown("---")
    st.subheader("1. Costos Fijos Mínimos (Prorrateables por Litro)")
    col_p1, col_p2 = st.columns(2)
    for i, (k, v) in enumerate(current_data["prorrateables"].items()):
        col = col_p1 if i % 2 == 0 else col_p2
        val = col.number_input(f"{k} (USD)", value=float(v), step=0.01)
        col.caption(f"~ ${(val * paridad_usd):.2f} MXN")
        current_data["prorrateables"][k] = val
        
    st.markdown("---")
    st.subheader("2. Tabuladores Variables (USD por Litro)")
    st.markdown("Los rangos escalan por cantidad total de litros producidos en el pedido. Los costos se desglosan por Calidad / Tiers.")
    
    for idx, rango in enumerate(current_data["rangos_volumen"]):
        with st.expander(f"📥 Rango Nivel {idx+1}: Capado hasta {rango['max_litros']} Litros", expanded=(idx==0)):
            rango["max_litros"] = st.number_input(f"Tope de Litros del Rango", value=float(rango["max_litros"]), key=f"max_l_{idx}")
            cats = list(rango["categorias"].keys())
            tabs_cats = st.tabs(cats)
            for cat_idx, cat in enumerate(cats):
                with tabs_cats[cat_idx]:
                    ccols = st.columns(4)
                    for c_i, (k, v) in enumerate(rango["categorias"][cat].items()):
                        val = ccols[c_i].number_input(
                            f"{k} (USD)", 
                            value=float(v), 
                            step=0.01, 
                            key=f"val_{idx}_{cat}_{k}"
                        )
                        ccols[c_i].caption(f"~ ${(val * paridad_usd):.2f} MXN")
                        rango["categorias"][cat][k] = val
                        
    st.markdown("---")
    if st.button("💾 Guardar y Aplicar Cambios Globales", type="primary"):
        if save_production_costs(current_data):
            st.success("Tus costos han sido guardados. Regresa a la pestaña de 'Calculadora de Rentabilidad' para ver el impacto.")
        else:
            st.error("Hubo un error al guardar el archivo de configuración.")



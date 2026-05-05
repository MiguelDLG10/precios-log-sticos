import pandas as pd
import re
import json
import os
import requests

CONFIG_FILE = 'costos_config.json'
PRODUCT_COSTS_FILE = 'product_costs.json'
BARCODE_FILE = 'codigo de barras.xlsx'

DEFAULT_PRODUCTION_COSTS = {
    "prorrateables": {
        "Operaciones": 0.1,
        "Mantenimiento": 0.02,
        "Equipamiento": 0.03,
        "Traslados": 0.1,
        "Administrativos": 0.15,
        "Operativos": 0.15
    },
    "rangos_volumen": [
        {
            "max_litros": 59.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.125, "IVISA": 0.35, "Asociado": 0.55, "Supervicion": 0.1},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.25, "Asociado": 0.35, "Supervicion": 0.065},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.45, "Asociado": 0.65, "Supervicion": 0.1}
            }
        },
        {
            "max_litros": 239.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.125, "IVISA": 0.345, "Asociado": 0.55, "Supervicion": 0.1},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.245, "Asociado": 0.35, "Supervicion": 0.065},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.40, "Asociado": 0.65, "Supervicion": 0.1}
            }
        },
        {
            "max_litros": 499.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.125, "IVISA": 0.34, "Asociado": 0.55, "Supervicion": 0.09},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.24, "Asociado": 0.35, "Supervicion": 0.055},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.35, "Asociado": 0.65, "Supervicion": 0.1}
            }
        },
        {
            "max_litros": 749.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.125, "IVISA": 0.335, "Asociado": 0.55, "Supervicion": 0.08},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.235, "Asociado": 0.35, "Supervicion": 0.045},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.30, "Asociado": 0.65, "Supervicion": 0.1}
            }
        },
        {
            "max_litros": 999.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.125, "IVISA": 0.33, "Asociado": 0.55, "Supervicion": 0.07},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.23, "Asociado": 0.35, "Supervicion": 0.035},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.25, "Asociado": 0.65, "Supervicion": 0.1}
            }
        },
        {
            "max_litros": 999999.9,
            "categorias": {
                "STANDART": {"Publicidad": 0.10, "IVISA": 0.325, "Asociado": 0.55, "Supervicion": 0.07},
                "GENERICO": {"Publicidad": 0.12, "IVISA": 0.225, "Asociado": 0.35, "Supervicion": 0.035},
                "PREMIUM": {"Publicidad": 0.125, "IVISA": 0.20, "Asociado": 0.65, "Supervicion": 0.1}
            }
        }
    ]
}

def load_production_costs():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_PRODUCTION_COSTS
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_PRODUCTION_COSTS

def save_production_costs(data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error guardando costos: {e}")
        return False

def get_production_costs_detailed(volumen_lts, categoria, materia_prima_cost_usd=None):
    """
    Retorna el costo de producción total por litro (en USD) 
    y el desglose detallado de qué prorrateables y variables aplican.
    Si materia_prima_cost_usd es proporcionado, se suma al total.
    """
    data = load_production_costs()
    
    prorrateables = data.get("prorrateables", {})
    costo_fijo = sum(prorrateables.values())
    
    categoria = categoria.upper()
    cat_costs = {}
    
    for rango in data.get("rangos_volumen", []):
        if volumen_lts <= rango["max_litros"]:
            cat_costs = rango.get("categorias", {}).get(categoria, {})
            break
            
    if not cat_costs and len(data.get("rangos_volumen", [])) > 0:
        cat_costs = data["rangos_volumen"][-1].get("categorias", {}).get(categoria, {})
        
    costo_variable = sum(cat_costs.values())
    
    # Agregar materia prima si existe
    variables_final = cat_costs.copy()
    if materia_prima_cost_usd is not None and materia_prima_cost_usd > 0:
        variables_final["Materia Prima Específica"] = materia_prima_cost_usd
        costo_variable += materia_prima_cost_usd
    
    total_costo = costo_fijo + costo_variable
    
    desglose = {
        "Prorrateables": prorrateables,
        "Variables": variables_final,
        "Total_USD": total_costo
    }
    
    return total_costo, desglose

def get_production_costs(volumen_lts, categoria):
    """Retorna solo el numero por compatibilidad anterior"""
    val, _ = get_production_costs_detailed(volumen_lts, categoria)
    return val

def clean_capacity(capacity_str):
    if pd.isna(capacity_str):
        return 0.0
    cap = str(capacity_str).lower().strip()
    match = re.search(r'([\d\.]+)', cap)
    if not match:
        return 0.0
    val = float(match.group(1))
    if 'ml' in cap:
        return val / 1000.0
    return val

def clean_weight(weight_str):
    if pd.isna(weight_str):
        return 0.0
    wt = str(weight_str).lower().strip()
    match = re.search(r'([\d\.]+)', wt)
    if not match:
        return 0.0
    val = float(match.group(1))
    if 'grs' in wt or 'gr' in wt or 'gramos' in wt:
        return val / 1000.0
    return val

def load_excel_data(filepath='Tabla de especificaciones de envases en Excel.xlsx'):
    try:
        df = pd.read_excel(filepath)
        df['Capacidad_L'] = df['Llenados a'].apply(clean_capacity)
        df['Peso_Envase_Kg'] = df['Peso'].apply(clean_weight)
        df['Etiqueta_UI'] = df['Modelo'] + ' (' + df['Capacidad del envases'].astype(str) + ')'
        return df
    except Exception as e:
        print(f"Error cargando excel: {e}")
        return pd.DataFrame()

def load_barcode_data(filepath=BARCODE_FILE):
    try:
        if not os.path.exists(filepath):
            return pd.DataFrame()
        df = pd.read_excel(filepath)
        # Crear una etiqueta legible para el buscador
        df['Search_Label'] = df['Producto'].astype(str) + ' - ' + df['Producto II'].astype(str).fillna('')
        return df
    except Exception as e:
        print(f"Error cargando excel de códigos: {e}")
        return pd.DataFrame()

def load_product_materia_prima():
    if not os.path.exists(PRODUCT_COSTS_FILE):
        return {}
    try:
        with open(PRODUCT_COSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_product_materia_prima(product_id, cost_usd):
    data = load_product_materia_prima()
    data[str(product_id)] = float(cost_usd)
    try:
        with open(PRODUCT_COSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error guardando costo de producto: {e}")
        return False

def get_current_exchange_rate():
    """
    Obtiene el tipo de cambio USD a MXN desde una API pública (Frankfurter).
    """
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=MXN", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['rates']['MXN'])
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
def get_packaging_price(capacidad_l):
    """
    Retorna el precio del envase en MXN basado en su capacidad (datos de COT0000514 y usuario).
    Ajustado para coincidir con las capacidades reales de la tabla de envases.
    """
    cap = float(capacidad_l)
    
    # 500ml (en la tabla aparece como 0.48)
    if 0.45 <= cap <= 0.55:
        return 2.0
    # 960ml / 1Lt (en la tabla aparece como 0.96)
    elif 0.9 <= cap <= 1.1:
        return 3.0
    # 4 Lts (en la tabla aparece como 3.8)
    elif 3.5 <= cap <= 4.5:
        return 20.46
    # 5 Lts
    elif cap == 5.0:
        return 22.0 # Estimado o podrías pedir confirmación
    # 10 Lts
    elif cap == 10.0:
        return 39.66
    # 20 Lts
    elif cap == 20.0:
        return 72.19
    # 25 Lts
    elif cap == 25.0:
        return 94.66
    # Para otros tamaños (30, 50, 60), default 0 o lógica adicional
    return 0.0

# Tarifas extraídas del PDF
TARIFFS = {
    "Amazon": {
        ">= $ 299.00 / < $ 499.00": [
            (0.0, 1.0, 61.00), (1.0, 2.0, 67.00), (2.0, 3.0, 80.00),
            (3.0, 5.0, 84.00), (5.0, 7.0, 96.00), (7.0, 9.0, 113.00), (9.0, 12.0, 130.00),
            (12.0, 15.0, 150.00), (15.0, 20.0, 176.00), (20.0, 30.0, 227.00), 
            (30.0, 31.0, 245.00)
        ],
        ">= $ 499.00": [
            (0.0, 1.0, 74.00), (1.0, 2.0, 80.00), (2.0, 3.0, 95.00),
            (3.0, 5.0, 101.00), (5.0, 7.0, 114.00), (7.0, 9.0, 134.00), (9.0, 12.0, 155.00),
            (12.0, 15.0, 179.00), (15.0, 20.0, 209.00), (20.0, 30.0, 270.00),
            (30.0, 31.0, 295.00), (33.0, 34.0, 325.00), (34.0, 35.0, 335.00),
            (37.0, 38.0, 365.00), (38.0, 39.0, 375.00), (39.0, 40.0, 385.00),
            (41.0, 42.0, 405.00), (42.0, 43.0, 415.00), (43.0, 44.0, 425.00),
            (45.0, 46.0, 445.00), (46.0, 47.0, 455.00), (47.0, 48.0, 465.00),
            (48.0, 49.0, 475.00), (49.0, 50.0, 485.00), (50.0, 51.0, 495.00),
            (51.0, 52.0, 505.00), (52.0, 53.0, 515.00), (53.0, 54.0, 525.00),
            (54.0, 55.0, 535.00), (55.0, 56.0, 545.00), (56.0, 57.0, 555.00),
            (57.0, 58.0, 565.00), (59.0, 60.0, 585.00)
        ]
    },
    "Mercado Libre": {
        "< $ 299.00": [
            (0.0, 1.0, 104.30), (1.0, 2.0, 118.30), (2.0, 3.0, 133.00),
            (3.0, 4.0, 144.20), (4.0, 5.0, 154.00), (5.0, 7.0, 171.50),
            (7.0, 9.0, 195.30), (9.0, 12.0, 226.10), (12.0, 15.0, 266.00),
            (15.0, 20.0, 311.50), (20.0, 30.0, 394.10), (30.0, 40.0, 488.60)
        ],
        ">= $ 299.00 / < $ 499.00": [
            (0.0, 1.0, 59.60), (1.0, 2.0, 67.60), (2.0, 3.0, 76.00),
            (3.0, 4.0, 82.40), (4.0, 5.0, 88.00), (5.0, 7.0, 98.00),
            (7.0, 9.0, 111.60), (9.0, 12.0, 129.20), (12.0, 15.0, 152.00),
            (15.0, 20.0, 178.00), (20.0, 30.0, 225.20), (30.0, 40.0, 279.20)
        ],
        ">= $ 499.00": [
            (0.0, 1.0, 0.0), (1.0, 200.0, 0.0) # Según mercado libre los envíos gratis > $299 se aplican, pero la tabla solo manda hasta <$499. Si es mayor asume la tarifa o es gratis.
            # Para este prototipo, indicaremos que no hay costo o depende de la reputación.
        ]
    },
    "Paquetexpress": {
        "0 a 400 km": [(0.0, 5.9, 109.20), (6.0, 10.9, 123.55), (11.0, 20.9, 222.60), (21.0, 30.9, 252.00), (31.0, 40.9, 281.40), (41.0, 50.9, 326.90), (51.0, 59.9, 359.10)], 
        "401 a 800 km": [(0.0, 5.9, 130.20), (6.0, 10.9, 166.25), (11.0, 20.9, 280.00), (21.0, 30.9, 312.20), (31.0, 40.9, 369.60), (41.0, 50.9, 436.80), (51.0, 59.9, 479.50)],
        "801 a 1,200 km": [(0.0, 5.9, 166.95), (6.0, 10.9, 211.40), (11.0, 20.9, 334.60), (21.0, 30.9, 387.10), (31.0, 40.9, 469.00), (41.0, 50.9, 542.50), (51.0, 59.9, 595.70)],
        "1,201 a 1,600 km": [(0.0, 5.9, 232.40), (6.0, 10.9, 285.25), (11.0, 20.9, 422.80), (21.0, 30.9, 487.20), (31.0, 40.9, 555.80), (41.0, 50.9, 634.20), (51.0, 59.9, 702.10)],
        "1,601 a 2,000 km": [(0.0, 5.9, 275.45), (6.0, 10.9, 319.90), (11.0, 20.9, 467.60), (21.0, 30.9, 513.10), (31.0, 40.9, 665.70), (41.0, 50.9, 762.30), (51.0, 59.9, 821.80)],
        "2,001 a 2,400 km": [(0.0, 5.9, 350.70), (6.0, 10.9, 403.90), (11.0, 20.9, 649.60), (21.0, 30.9, 749.00), (31.0, 40.9, 882.70), (41.0, 50.9, 971.60), (51.0, 59.9, 1068.90)],
        "Mayor a 2,400 km": [(0.0, 5.9, 398.30), (6.0, 10.9, 462.00), (11.0, 20.9, 697.90), (21.0, 30.9, 785.40), (31.0, 40.9, 961.10), (41.0, 50.9, 1135.40), (51.0, 59.9, 1225.70)],
    }
}

def get_cost(weight_kg, platform, sub_tariff=None):
    """
    Retorna el costo de envío dependiendo del peso y la plataforma.
    """
    if platform not in TARIFFS:
        return None
    
    opts = TARIFFS[platform]
    
    # Manejar las plataformas que tienen sub-tarifas (precio de venta o distancia)
    if sub_tariff and sub_tariff in opts:
        ranges = opts[sub_tariff]
    else:
        # Si no encaja, retornar None o el default
        return None

    # En Paquetexpress si el peso excede el límite superior de la tabla (59.9), usa tarifa de carga
    if platform == "Paquetexpress":
        max_limit = ranges[-1][1]
        # Redondeamos el peso a 1 decimal para evitar gaps minúsculos como 59.95
        w_rounded = round(weight_kg, 1)
        if w_rounded > max_limit:
            carga_rates = {
                "0 a 400 km": 5.99,
                "401 a 800 km": 7.95,
                "801 a 1,200 km": 12.88,
                "1,201 a 1,600 km": 16.10,
                "1,601 a 2,000 km": 18.20,
                "2,001 a 2,400 km": 20.34,
                "Mayor a 2,400 km": 22.44,
            }
            if sub_tariff in carga_rates:
                return weight_kg * carga_rates[sub_tariff]
            return -1

    # Redondear el peso a 1 decimal soluciona los problemas de huecos "gaps" que hay entre rangos de la tabla.
    # Ejemplo: en paquetexpress hay 5.9 -> 6.0 . Un peso de 5.95 tiraba error. Ahora será 6.0.
    weight_kg_rounded = round(weight_kg, 1)
    
    for i, (min_w, max_w, cost) in enumerate(ranges):
        if min_w <= weight_kg_rounded <= max_w:
            return cost
            
        # Parche de seguridad para gaps intermedios por si la lista no es perfectamente contigua y el redondedo no basta
        elif weight_kg_rounded < min_w and i > 0 and weight_kg_rounded > ranges[i-1][1]:
            # Cayó justo en medio del rango anterior y este. Le cobramos la del rango actual superior
            return cost
            
    return -1 # Indica fuera de rango (ej. excede el máximo)

def determine_subtariff(platform, unit_price):
    """
    Determina qué tabla debe aplicarse basada en el precio de venta (para Amazon/MercadoLibre)
    """
    if platform == "Amazon":
        if unit_price < 499:
            return ">= $ 299.00 / < $ 499.00"
        else:
            return ">= $ 499.00"
    elif platform == "Mercado Libre":
        if unit_price < 299:
            return "< $ 299.00"
        elif 299 <= unit_price < 499:
            return ">= $ 299.00 / < $ 499.00"
        else:
            # Para > 499, por ahora lo forzamos a la anterior o devolvemos nulo
            return ">= $ 299.00 / < $ 499.00"
    return None

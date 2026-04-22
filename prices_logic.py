import pandas as pd
import re

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
    if platform == "Paquetexpress" and weight_kg >= 60.0:
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
        return -1 # Indica fuera de rango / no encontrado

    if platform not in TARIFFS:
        return None
    
    opts = TARIFFS[platform]
    
    # Manejar las plataformas que tienen sub-tarifas (precio de venta o distancia)
    if sub_tariff and sub_tariff in opts:
        ranges = opts[sub_tariff]
    else:
        # Si no encaja, retornar None o el default
        return None
        
    for min_w, max_w, cost in ranges:
        if min_w <= weight_kg <= max_w:
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

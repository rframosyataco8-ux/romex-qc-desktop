# ============================================================
# Romex QC Desktop — Configuración
# Exportadora Romex S.A. · Planta Chincha
# ============================================================

# --- Conexión a SQL Server ---
DB_SERVER = r"localhost"
DB_NAME = "RomexQC"
DB_USER = "rodrigo"
DB_PASSWORD = "rodrigo123"
DB_TRUSTED = False
DB_DRIVER = "ODBC Driver 17 for SQL Server"

def get_connection_string():
    if DB_TRUSTED or (not DB_USER and not DB_PASSWORD):
        return (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
    return (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )


# --- Datos de la empresa ---
COMPANY_NAME = "EXPORTADORA ROMEX S.A."
PLANT_NAME = "Planta de Cacao Chincha"
DOC_CODE = "I-EVUP-R-309"
APP_VERSION = "2.6.0"
APP_TITLE = "Romex QC · Estudio de Vida Útil"

# --- Nombres de meses ---
MONTH_NAMES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}

MONTH_NAMES_SHORT = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# --- Parámetros microbiológicos ---
MICRO_KEYS = ["rtamv", "mohos", "coliformes", "ecoli", "enterobacterias", "levaduras", "saureus"]
MICRO_LABELS = {
    "rtamv": "RTAMV",
    "mohos": "Mohos",
    "coliformes": "Coliformes",
    "ecoli": "E.Coli",
    "enterobacterias": "Enterobacterias",
    "levaduras": "Levaduras",
    "saureus": "S.Aureus"
}
MICRO_DB_COLS = {
    "rtamv": "RTAMV",
    "mohos": "Mohos",
    "coliformes": "Coliformes",
    "ecoli": "EColi",
    "enterobacterias": "Enterobacterias",
    "levaduras": "Levaduras",
    "saureus": "SAureus"
}

# --- Parámetros físicoquímicos ---
FISICO_KEYS = ["humedad", "ph", "ceniza", "grasa", "fineza", "acidez"]
FISICO_LABELS = {
    "humedad": "% Humedad",
    "ph": "pH",
    "ceniza": "% Ceniza",
    "grasa": "% Grasa",
    "fineza": "% Fineza",
    "acidez": "% Acidez"
}
FISICO_DB_COLS = {
    "humedad": "Humedad",
    "ph": "PH",
    "ceniza": "Ceniza",
    "grasa": "Grasa",
    "fineza": "Fineza",
    "acidez": "Acidez"
}

# --- Colores de gráficos ---
COLORS = {
    "rtamv": "#1565c0",
    "mohos": "#ef6c00",
    "coliformes": "#2e7d32",
    "ecoli": "#43a047",
    "enterobacterias": "#7b1fa2",
    "levaduras": "#c2185b",
    "saureus": "#c62828",
    "humedad": "#0288d1",
    "ph": "#7b1fa2",
    "ceniza": "#5d4037",
    "grasa": "#f9a825",
    "fineza": "#00897b",
    "acidez": "#c62828",
    "baseline": "#90a4ae"
}

# ============================================================
# SIEMBRA = punto de partida (análisis inicial del sistema web)
# Estos valores NO se editan en la app de escritorio.
# Fuente: data/baselines.json del repositorio estudio-vida-util-romex
# ============================================================
BASELINES = {
    "torta_natural": {
        "lote": "44260304",
        "anio_inicio": 2026,
        "mes_inicio": 3,
        "fecha_siembra": "2026-03-06",
        "micro": {"rtamv": 863, "mohos": 11, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 2.22, "ph": 5.40, "ceniza": 8.30, "grasa": 12.11}
    },
    "torta_alcalina": {
        "lote": "13260318",
        "anio_inicio": 2026,
        "mes_inicio": 3,
        "fecha_siembra": "2026-03-28",
        "micro": {"rtamv": 40, "mohos": 0, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 3.54, "ph": 6.81, "ceniza": 11.60, "grasa": 11.68}
    },
    "cocoa_natural": {
        "lote": "11260513",
        "anio_inicio": 2026,
        "mes_inicio": 5,
        "fecha_siembra": "2026-05-22",
        "micro": {"rtamv": 1238, "mohos": 15, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 2.49, "ph": 5.39, "ceniza": 8.20, "grasa": 11.80, "fineza": 99.49}
    },
    "cocoa_alcalina": {
        "lote": "07260324",
        "anio_inicio": 2026,
        "mes_inicio": 3,
        "fecha_siembra": "2026-04-02",
        "micro": {"rtamv": 1250, "mohos": 0, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 2.76, "ph": 6.87, "ceniza": 10.30, "grasa": 11.62, "fineza": 98.51}
    },
    "licor": {
        "lote": "260516",
        "anio_inicio": 2026,
        "mes_inicio": 5,
        "fecha_siembra": "2026-05-18",
        "micro": {"rtamv": 300, "mohos": 0, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 0.55, "ph": 5.42, "ceniza": 3.90, "grasa": 48.65, "fineza": 99.74, "acidez": 2.10}
    },
    "manteca": {
        "lote": "19260321",
        "anio_inicio": 2026,
        "mes_inicio": 3,
        "fecha_siembra": "2026-03-21",
        "micro": {"rtamv": 50, "mohos": 0, "coliformes": 0, "ecoli": 0, "enterobacterias": 0, "levaduras": 0, "saureus": 0},
        "fisico": {"humedad": 0.02, "acidez": 1.64}
    }
}

# Romex QC Desktop v2.0

**Exportadora Romex S.A. · Planta de Cacao Chincha**  
Sistema profesional de **Estudio de Vida Útil** (Microbiología + Físicoquímico)

Aplicación de **escritorio** nativa para Windows, conectada directamente a **SQL Server**.

---

## ¿Qué incluye?

- Login con roles **ADMIN** y **LECTOR**
- 6 productos de cacao (Torta Natural/Alcalina, Cocoa Natural/Alcalina, Licor, Manteca)
- Resultados por mes/año: Microbiología y Físicoquímico
- Punto de partida (siembra) según lote
- Gráficos de comparación (siembra vs mes) y tendencias
- Auto-guardado al editar (solo ADMIN)
- Agregar mes / nuevo producto
- Auditoría de cambios
- Diseño moderno y profesional

---

## Requisitos

| Componente | Versión recomendada |
|------------|---------------------|
| Windows | 10 / 11 |
| SQL Server | Express 2019 o superior |
| SSMS | Cualquier versión reciente |
| Python | **3.10, 3.11 o 3.12** (64-bit) |
| ODBC Driver | **ODBC Driver 17** o **18** for SQL Server |

---

## PASO A PASO

### 1. Crear la base de datos

1. Abre **SQL Server Management Studio**
2. Conéctate (`localhost` o `.\\SQLEXPRESS`)
3. Abre `sql/01_create_romexqc.sql`
4. Presiona **F5**

### 2. Configurar conexión

Edita `config.py`:

```python
DB_SERVER = r"localhost"          # o r".\\SQLEXPRESS"
DB_NAME = "RomexQC"
DB_TRUSTED = True
DB_DRIVER = "ODBC Driver 17 for SQL Server"
```

### 3. Instalar dependencias

```bat
cd romex-qc-desktop
python -m pip install -r requirements.txt
```

### 4. Ejecutar

```bat
python main.py
```

**Usuarios:**
| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | ADMIN |
| nereyda | romex2026 | ADMIN |
| lector | lector123 | LECTOR |

---

## Estructura

```
romex-qc-desktop/
├── main.py
├── config.py
├── requirements.txt
├── sql/01_create_romexqc.sql
├── db/
│   ├── connection.py
│   └── queries.py
├── ui/
│   ├── login_window.py
│   └── main_app.py
└── utils/
    └── charts.py
```

**Versión:** 2.0.0 · Octubre 2026  
**Analista:** Nereyda Huachua Flores · I-EVUP-R-309

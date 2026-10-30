# ============================================================
# Romex QC Desktop — Conexión a SQL Server
# ============================================================

import pyodbc
from config import get_connection_string, DB_DRIVER, DB_SERVER, DB_NAME


class DatabaseError(Exception):
    """Error de base de datos con mensaje amigable."""
    pass


def get_connection():
    """Abre y devuelve una conexión a SQL Server."""
    try:
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str, timeout=8)
        conn.autocommit = False
        return conn
    except pyodbc.Error as e:
        msg = str(e)
        if "IM002" in msg or "Data source name not found" in msg:
            raise DatabaseError(
                f"No se encontró el driver ODBC '{DB_DRIVER}'.\n\n"
                "Instala 'ODBC Driver 17 for SQL Server' o 'ODBC Driver 18 for SQL Server'\n"
                "desde el sitio de Microsoft e inténtalo de nuevo."
            )
        if "Login failed" in msg or "18456" in msg:
            raise DatabaseError(
                "Error de autenticación en SQL Server.\n\n"
                "Revisa config.py:\n"
                "  - Si usas Windows Authentication: DB_TRUSTED = True\n"
                "  - Si usas usuario/contraseña: DB_TRUSTED = False y completa DB_USER / DB_PASSWORD"
            )
        if "Cannot open database" in msg or "4060" in msg:
            raise DatabaseError(
                f"No se pudo abrir la base de datos '{DB_NAME}'.\n\n"
                "Asegúrate de haber ejecutado el script sql/01_create_romexqc.sql en SSMS."
            )
        if "server was not found" in msg.lower() or "08001" in msg or "Named Pipes" in msg:
            raise DatabaseError(
                f"No se pudo conectar al servidor '{DB_SERVER}'.\n\n"
                "Verifica que SQL Server esté en ejecución y que el nombre\n"
                "del servidor en config.py sea correcto (localhost o .\\SQLEXPRESS)."
            )
        raise DatabaseError(f"Error de conexión:\n{msg}")


def test_connection():
    """Prueba la conexión y devuelve (ok: bool, mensaje: str)."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM dbo.Productos")
        n = cur.fetchone()[0]
        conn.close()
        return True, f"Conectado a {DB_NAME} · {n} productos"
    except DatabaseError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error inesperado: {e}"


def execute_query(sql, params=None, fetch=True):
    """
    Ejecuta una consulta.
    - fetch=True  → devuelve lista de diccionarios
    - fetch=False → hace commit y devuelve rowcount
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        if fetch:
            columns = [col[0] for col in cur.description] if cur.description else []
            rows = cur.fetchall()
            result = []
            for row in rows:
                d = {}
                for i, col in enumerate(columns):
                    val = row[i]
                    if hasattr(val, "isoformat"):
                        val = val.isoformat()[:10] if hasattr(val, "year") else str(val)
                    d[col] = val
                result.append(d)
            conn.commit()
            return result
        else:
            conn.commit()
            return cur.rowcount
    except DatabaseError:
        raise
    except pyodbc.Error as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise DatabaseError(f"Error SQL:\n{e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def execute_non_query(sql, params=None):
    """Ejecuta INSERT/UPDATE/DELETE y devuelve filas afectadas."""
    return execute_query(sql, params, fetch=False)

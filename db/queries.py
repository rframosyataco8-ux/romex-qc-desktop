# ============================================================
# Romex QC Desktop — Consultas a la base de datos
# ============================================================

from db.connection import execute_query, execute_non_query, DatabaseError
from config import MICRO_DB_COLS, FISICO_DB_COLS


# ---------- USUARIOS ----------

def login_user(usuario, password):
    """Valida usuario y contraseña. Devuelve dict del usuario o None."""
    rows = execute_query(
        "SELECT Id, Usuario, PasswordHash, Nombre, Rol, Activo "
        "FROM dbo.Usuarios WHERE LOWER(Usuario) = LOWER(?)",
        (usuario.strip(),)
    )
    if not rows:
        return None
    u = rows[0]
    if not u["Activo"]:
        return None
    if str(u["PasswordHash"]) != str(password):
        return None
    return {
        "id": u["Id"],
        "usuario": u["Usuario"],
        "nombre": u["Nombre"],
        "rol": u["Rol"]
    }


def get_all_users():
    return execute_query(
        "SELECT Id, Usuario, Nombre, Rol, Activo, CreadoEn "
        "FROM dbo.Usuarios ORDER BY Id"
    )


def create_user(usuario, password, nombre, rol):
    execute_non_query(
        "INSERT INTO dbo.Usuarios (Usuario, PasswordHash, Nombre, Rol) "
        "VALUES (?, ?, ?, ?)",
        (usuario.strip().lower(), password, nombre.strip(), rol.upper())
    )


def update_user(user_id, nombre=None, rol=None, activo=None, password=None):
    if nombre is not None:
        execute_non_query("UPDATE dbo.Usuarios SET Nombre = ? WHERE Id = ?", (nombre, user_id))
    if rol is not None:
        execute_non_query("UPDATE dbo.Usuarios SET Rol = ? WHERE Id = ?", (rol.upper(), user_id))
    if activo is not None:
        execute_non_query("UPDATE dbo.Usuarios SET Activo = ? WHERE Id = ?", (1 if activo else 0, user_id))
    if password:
        execute_non_query("UPDATE dbo.Usuarios SET PasswordHash = ? WHERE Id = ?", (password, user_id))


# ---------- PRODUCTOS ----------

def get_productos(solo_activos=True):
    sql = "SELECT Id, Codigo, Nombre, Lote, Activo FROM dbo.Productos"
    if solo_activos:
        sql += " WHERE Activo = 1"
    sql += " ORDER BY Id"
    return execute_query(sql)


def get_producto_by_codigo(codigo):
    rows = execute_query(
        "SELECT Id, Codigo, Nombre, Lote, Activo FROM dbo.Productos WHERE Codigo = ?",
        (codigo,)
    )
    return rows[0] if rows else None


def create_producto(codigo, nombre, lote):
    execute_non_query(
        "INSERT INTO dbo.Productos (Codigo, Nombre, Lote) VALUES (?, ?, ?)",
        (codigo.strip().lower(), nombre.strip(), lote.strip())
    )


# ---------- MICROBIOLOGÍA ----------

def get_micro(producto_id, anio):
    return execute_query(
        "SELECT Id, ProductoId, Anio, Mes, FechaAnalisis, "
        "RTAMV, Mohos, Coliformes, EColi, Enterobacterias, Levaduras, SAureus, "
        "Estado, Analista, LiberadoPor, Notas "
        "FROM dbo.ResultadosMicro "
        "WHERE ProductoId = ? AND Anio = ? "
        "ORDER BY Mes",
        (producto_id, anio)
    )


def get_micro_mes(producto_id, anio, mes):
    rows = execute_query(
        "SELECT Id, ProductoId, Anio, Mes, FechaAnalisis, "
        "RTAMV, Mohos, Coliformes, EColi, Enterobacterias, Levaduras, SAureus, "
        "Estado, Analista, LiberadoPor, Notas "
        "FROM dbo.ResultadosMicro "
        "WHERE ProductoId = ? AND Anio = ? AND Mes = ?",
        (producto_id, anio, mes)
    )
    return rows[0] if rows else None


def upsert_micro(producto_id, anio, mes, data, analista=None):
    """Inserta o actualiza un registro de microbiología."""
    existing = get_micro_mes(producto_id, anio, mes)
    if existing:
        sets = []
        params = []
        for key, col in MICRO_DB_COLS.items():
            if key in data:
                sets.append(f"{col} = ?")
                params.append(int(data[key]) if data[key] is not None else 0)
        if "fecha_analisis" in data and data["fecha_analisis"]:
            sets.append("FechaAnalisis = ?")
            params.append(data["fecha_analisis"])
        if "estado" in data:
            sets.append("Estado = ?")
            params.append(data["estado"])
        if analista:
            sets.append("Analista = ?")
            params.append(analista)
        sets.append("ActualizadoEn = SYSUTCDATETIME()")
        params.extend([producto_id, anio, mes])
        sql = f"UPDATE dbo.ResultadosMicro SET {', '.join(sets)} WHERE ProductoId = ? AND Anio = ? AND Mes = ?"
        execute_non_query(sql, tuple(params))
    else:
        cols = ["ProductoId", "Anio", "Mes"]
        vals = [producto_id, anio, mes]
        placeholders = ["?", "?", "?"]
        for key, col in MICRO_DB_COLS.items():
            cols.append(col)
            vals.append(int(data.get(key, 0) or 0))
            placeholders.append("?")
        if data.get("fecha_analisis"):
            cols.append("FechaAnalisis")
            vals.append(data["fecha_analisis"])
            placeholders.append("?")
        if analista:
            cols.append("Analista")
            vals.append(analista)
            placeholders.append("?")
        sql = f"INSERT INTO dbo.ResultadosMicro ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        execute_non_query(sql, tuple(vals))


# ---------- FÍSICOQUÍMICO ----------

def get_fisico(producto_id, anio):
    return execute_query(
        "SELECT Id, ProductoId, Anio, Mes, FechaAnalisis, "
        "Humedad, PH, Ceniza, Grasa, Fineza, Acidez, "
        "Estado, Analista, Notas "
        "FROM dbo.ResultadosFisico "
        "WHERE ProductoId = ? AND Anio = ? "
        "ORDER BY Mes",
        (producto_id, anio)
    )


def get_fisico_mes(producto_id, anio, mes):
    rows = execute_query(
        "SELECT Id, ProductoId, Anio, Mes, FechaAnalisis, "
        "Humedad, PH, Ceniza, Grasa, Fineza, Acidez, "
        "Estado, Analista, Notas "
        "FROM dbo.ResultadosFisico "
        "WHERE ProductoId = ? AND Anio = ? AND Mes = ?",
        (producto_id, anio, mes)
    )
    return rows[0] if rows else None


def upsert_fisico(producto_id, anio, mes, data, analista=None):
    """Inserta o actualiza un registro físicoquímico."""
    existing = get_fisico_mes(producto_id, anio, mes)
    if existing:
        sets = []
        params = []
        for key, col in FISICO_DB_COLS.items():
            if key in data:
                sets.append(f"{col} = ?")
                val = data[key]
                params.append(float(val) if val is not None and val != "" else None)
        if "fecha_analisis" in data and data["fecha_analisis"]:
            sets.append("FechaAnalisis = ?")
            params.append(data["fecha_analisis"])
        if "estado" in data:
            sets.append("Estado = ?")
            params.append(data["estado"])
        if analista:
            sets.append("Analista = ?")
            params.append(analista)
        sets.append("ActualizadoEn = SYSUTCDATETIME()")
        params.extend([producto_id, anio, mes])
        sql = f"UPDATE dbo.ResultadosFisico SET {', '.join(sets)} WHERE ProductoId = ? AND Anio = ? AND Mes = ?"
        execute_non_query(sql, tuple(params))
    else:
        cols = ["ProductoId", "Anio", "Mes"]
        vals = [producto_id, anio, mes]
        placeholders = ["?", "?", "?"]
        for key, col in FISICO_DB_COLS.items():
            cols.append(col)
            val = data.get(key)
            vals.append(float(val) if val is not None and val != "" else None)
            placeholders.append("?")
        if data.get("fecha_analisis"):
            cols.append("FechaAnalisis")
            vals.append(data["fecha_analisis"])
            placeholders.append("?")
        if analista:
            cols.append("Analista")
            vals.append(analista)
            placeholders.append("?")
        sql = f"INSERT INTO dbo.ResultadosFisico ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        execute_non_query(sql, tuple(vals))


# ---------- AUDITORÍA ----------

def log_audit(usuario_nombre, accion, entidad, codigo=None, anio=None, mes=None, detalle=None):
    execute_non_query(
        "INSERT INTO dbo.Auditoria (UsuarioNombre, Accion, Entidad, Codigo, Anio, Mes, Detalle) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (usuario_nombre, accion, entidad, codigo, anio, mes, detalle)
    )


def get_auditoria(limit=100):
    return execute_query(
        "SELECT TOP (?) Id, UsuarioNombre, Accion, Entidad, Codigo, Anio, Mes, Detalle, CreadoEn "
        "FROM dbo.Auditoria ORDER BY CreadoEn DESC",
        (limit,)
    )

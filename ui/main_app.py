# ============================================================
# Romex QC Desktop — Ventana principal (diseño limpio v2.1)
# Exportadora Romex S.A. · Planta Chincha
# ============================================================
import base64, zlib, os

_dir = os.path.dirname(__file__)
with open(os.path.join(_dir, "main_app_data_1.b64"), "r", encoding="ascii") as _f:
    _p1 = _f.read().strip()
with open(os.path.join(_dir, "main_app_data_2.b64"), "r", encoding="ascii") as _f:
    _p2 = _f.read().strip()

_code = zlib.decompress(base64.b64decode(_p1 + _p2)).decode("utf-8")
exec(compile(_code, __file__, "exec"), globals())

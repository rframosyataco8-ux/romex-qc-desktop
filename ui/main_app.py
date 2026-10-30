# ============================================================
# Romex QC Desktop — Ventana principal
# Exportadora Romex S.A. · Planta Chincha
# ============================================================
import base64, zlib, os

_data_path = os.path.join(os.path.dirname(__file__), "main_app_data.b64")
with open(_data_path, "r", encoding="ascii") as _f:
    _PAYLOAD = _f.read().strip()

_code = zlib.decompress(base64.b64decode(_PAYLOAD)).decode("utf-8")
exec(compile(_code, __file__, "exec"), globals())

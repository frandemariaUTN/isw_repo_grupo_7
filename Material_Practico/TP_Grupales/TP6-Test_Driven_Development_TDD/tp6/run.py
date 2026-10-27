"""Levanta la app en http://127.0.0.1:5000 (base en data/ecoharmony.db).

Si existe el archivo .env con la cuenta de mail (ver .env.ejemplo), los
mails de confirmacion se envian de verdad; si no, se simulan.
"""
import sys
from pathlib import Path

CARPETA = Path(__file__).parent
sys.path.insert(0, str(CARPETA / "src"))

from ecoharmony.configuracion import cargar_env  # noqa: E402
from ecoharmony.web.app import crear_app  # noqa: E402

if __name__ == "__main__":
    cargar_env(CARPETA / ".env")
    crear_app().run(debug=True)

"""Levanta la app en http://127.0.0.1:5000 (base en data/ecoharmony.db)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ecoharmony.web.app import crear_app  # noqa: E402

if __name__ == "__main__":
    crear_app().run(debug=True)

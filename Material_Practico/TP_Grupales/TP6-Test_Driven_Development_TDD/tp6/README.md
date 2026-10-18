# TP6 - TDD: Comprar entradas (EcoHarmony Park)

Implementación de la user story **"Comprar entradas"** aplicando Desarrollo Conducido por Pruebas (ciclo Red-Green-Refactor). Grupo 7, Ingeniería y Calidad de Software 2026, UTN FRC.

> Este README es el del TP6. El README de la raíz del repositorio documenta la gestión de configuración (SCM).

---

## 1. Qué se construye

Una aplicación web responsive (backend en Python, persistencia en SQLite) donde un visitante compra entradas al parque indicando fecha, cantidad, edad de cada visitante, tipo de pase y forma de pago (efectivo, o tarjeta mediante una **pasarela de pago simulada** con el aspecto de Mercado Pago). Al confirmar, recibe un mail de confirmación (simulado con un aviso en pantalla, como permite la FAQ 5).

Las reglas de negocio salen de tres fuentes, que deben tener a mano:

- La user story "Comprar entradas" y sus criterios de aceptación.
- La descripción del dominio de EcoHarmony Park.
- Las FAQs respondidas por los PO (docentes).

---

## 2. Puesta en marcha

Requisitos: **Python 3.11 o superior** (probado con 3.14) y Git.

Todos los comandos se ejecutan **desde esta carpeta** (`tp6/`), porque acá están `pytest.ini`, `.flake8` y `requirements.txt`.

```bash
# 1. Crear el entorno virtual (una sola vez)
python -m venv .venv

# 2. Activarlo (cada vez que abras una terminal nueva)
source .venv/Scripts/activate      # Git Bash en Windows
# .venv\Scripts\Activate.ps1        # PowerShell
# .venv\Scripts\activate.bat        # CMD
# source .venv/bin/activate         # Linux o macOS

# 3. Instalar dependencias (una sola vez)
pip install -r requirements.txt
```

Si el entorno está activo, el prompt muestra `(.venv)` al principio de la línea.

**Comandos habituales**

```bash
pytest                 # correr todos los tests
pytest -v              # ver cada test con su resultado
pytest -k PRE-05       # correr un caso por su ID
pytest tests/system    # solo las pruebas en el navegador (usan el Edge instalado)
flake8 src tests       # verificar PEP8 (no debe imprimir nada)
python run.py          # levantar la app en http://127.0.0.1:5000
```

---

## 3. Estructura

```text
tp6/
├── src/ecoharmony/
│   └── dominio/        # reglas de negocio puras (sin Flask ni base de datos)
├── tests/
│   └── unit/           # pruebas unitarias
├── docs/
│   ├── Casos_de_Prueba.md          # lista de casos y supuestos
│   └── Decisiones_de_Diseno.md     # justificación del diseño (entregable)
├── data/               # base de datos SQLite (no se versiona)
├── pytest.ini          # configuración de pytest
├── .flake8             # reglas de estilo (79 columnas)
└── requirements.txt
```

A medida que avance el trabajo se suman las carpetas de integración, sistema, adaptadores (SQLite, pasarela simulada, mail), la capa web y el frontend.

---

## 4. Cómo trabajamos (reglas del equipo)

### Ciclo TDD

1. **RED:** escribir un test que falle, y verificar que falla **por el motivo esperado**.
2. **GREEN:** escribir el código **mínimo** para que pase. Se acepta código casi trivial (por ejemplo devolver un valor fijo) si el siguiente test obliga a generalizarlo.
3. **REFACTOR:** mejorar el diseño sin cambiar el comportamiento, con todos los tests en verde.

Cada fase va en **su propio commit**. Los casos demasiado triviales se pueden agrupar en un solo commit.

### Commits

Se respeta el nombrado del README de la raíz del repo:

| Fase | Mensaje |
| --- | --- |
| Test que falla | `feat: [RED] test PRE-05 menores de 15 años pagan mitad` |
| Código mínimo | `feat: [GREEN] PRE-05 menores de 15 años pagan mitad` |
| Mejora de diseño | `refactor: constantes con nombre para edades limite` |
| Documentación | `docs: decisiones D10 y D11` |
| Configuración | `chore: agregada dependencia flask` |

Un test que pasa de entrada (porque el código ya generaliza) se commitea como `feat: test ...` sin la marca de fase.

### Antes de cada commit

- `pytest` en verde (salvo en un RED, donde debe fallar solo el test nuevo).
- `flake8 src tests` sin errores.
- No subir `.venv/`, `.env` ni la base de datos `data/*.db` (ya está en el `.gitignore`).

### Estilo y diseño

- **PEP8**, líneas de hasta 79 caracteres.
- Nombres de dominio en español (`Visitante`, `Entrada`, `calcular_precio`).
- Tests con nombres descriptivos y, cuando se pueda, parametrizados con `pytest.param(..., id="PRE-05")` para que el ID del caso figure en el reporte.
- El **dominio es puro**: sin Flask, sin base de datos, sin llamadas a internet. Las dependencias externas (repositorio SQLite, pasarela de pago, mail, reloj) se acceden a través de interfaces, con un adaptador real o simulado y uno falso para los tests.
- La hora actual se inyecta, no se lee dentro de las reglas.
- Los montos son enteros en pesos.

---

## 5. Documentos de referencia

| Documento | Para qué sirve |
| --- | --- |
| `docs/Casos_de_Prueba.md` | Lista de casos de prueba (unitarias, integración, sistema), su origen y los supuestos pendientes. **Respalda los tests: si un test cambia, se actualiza este archivo.** |
| `docs/Decisiones_de_Diseno.md` | Decisiones de diseño y su motivo. Se completa con cada ciclo relevante. |
| `docs/Pasarela_Simulada.md` | Diseño del flujo y de las pantallas de la pasarela de pago simulada. |
| Consigna, FAQs, US y descripción del dominio | Fuente de las reglas de negocio. |

---

## 6. Supuestos pendientes de confirmar con el PO

Mientras los docentes no respondan, se trabaja con los supuestos S1 a S10 de `docs/Casos_de_Prueba.md` (los casos afectados están marcados con ⚠️). En resumen:

- S1: el pase se elige por visitante.
- S2: las entradas gratuitas cuentan para el límite de 10.
- S3: en efectivo la compra queda pendiente de pago en boletería.
- S4: un pago con tarjeta fallido libera el cupo.
- S5: el mail de esta US no lleva QR.
- S6: edad máxima válida de 120 años.
- S7: se puede comprar para hoy antes de la apertura, hasta las 17:30.
- S8: una compra de $0 no pasa por la pasarela de pago.
- S9: el mail se envía al confirmar la compra.
- S10: ya no aplica, porque el mail se simula (FAQ 5).

Cuando llegue una respuesta, se actualizan `Casos_de_Prueba.md` y los tests afectados, y se avisa al resto del equipo.

---

## 7. Trabajo en equipo

- **Repartir por grupos de casos** (por ejemplo `DIA`/`FEC`, `CAN`/`PAG`, `BD`) para tocar archivos distintos y evitar conflictos.
- Hacer `git pull --rebase` antes de cada `git push`, así el historial queda lineal.
- Los archivos que todos editan son `Casos_de_Prueba.md` y `Decisiones_de_Diseno.md`: agregar las filas **al final** y commitear seguido.
- Avisar al resto antes de cambiar una interfaz del dominio (nombre de función, parámetros), porque rompe los tests de los demás.

---

## 8. Estado del avance

| Grupo | Casos | Estado |
| --- | --- | --- |
| `PRE` Precios y descuentos | PRE-01 a PRE-13 | Hecho |
| `PRE` Total de compra y configuración | PRE-14 a PRE-16 | Hecho |
| `EDA`, `PAS` | Validaciones de edad y pase | Hecho |
| `DIA`, `FEC` | Calendario y reloj | Hecho |
| `CAN` | Cantidad y límite de 10 | Hecho |
| `PAG`, `ORD`, `USR`, `MAI` | Estados, orden, sesión y mail | Hecho |
| `TAR` | Validación de tarjeta | Hecho |
| `BD` | Base de datos SQLite | Hecho |
| `PSM`, `MAIL` | Pasarela de pago y mail simulados | Hecho |
| `SRV` | Servicio de compra | Hecho |
| `API` | Capa web Flask | Hecho |
| Frontend | Pantallas responsive: compra, pasarela, resultado y modal del mail | Hecho |
| `SIS` | Pruebas de sistema en el navegador (Edge con Playwright) | Hecho |

Actualizar esta tabla al cerrar cada grupo.

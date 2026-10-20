# Estructura del proyecto: cómo está armada la app

TP6 - TDD | Grupo 7. Resumen corto para entender qué hay en cada carpeta y por qué.

## Qué es

Una web para **comprar entradas** a EcoHarmony Park. Es **responsive y pensada primero para celular**, porque el PO pide una app mobile y acepta una web responsive (FAQ 24). El backend está en Python con Flask y se desarrolló con **TDD** (Red-Green-Refactor).

Para levantarla, con el `.venv` activado: `python run.py`. Después se abre http://127.0.0.1:5000.

## Carpetas

```text
tp6/
├── src/ecoharmony/
│   ├── dominio/         reglas de negocio
│   ├── aplicacion/      el flujo completo de una compra
│   ├── persistencia/    base de datos SQLite
│   ├── notificaciones/  mail simulado
│   └── web/             Flask, pantallas, CSS y JS
├── tests/
│   ├── unit/
│   ├── integration/
│   └── system/
├── docs/
├── data/
└── run.py
```

- **`src/ecoharmony/dominio/`**: las reglas de negocio puras: precios y descuentos, días de apertura, límite de 10 entradas, validación de edad y de tarjeta, y la pasarela de pago simulada. No depende de Flask ni de la base de datos, así que se prueba rápido y sin servidor.
- **`src/ecoharmony/aplicacion/`**: `ServicioDeCompra`, que une las piezas: valida la compra, la guarda, la manda a la pasarela si es con tarjeta y envía el mail.
- **`src/ecoharmony/persistencia/`**: guarda las compras en una base **SQLite** (`data/ecoharmony.db`). Viene incluida en Python y no hay que instalar nada.
- **`src/ecoharmony/notificaciones/`**: el mail de confirmación **simulado**: en vez de enviarlo, la app muestra un aviso "Mail enviado a …" (lo permite la FAQ 5).
- **`src/ecoharmony/web/`**: la capa web con Flask.
  - `app.py` tiene las rutas.
  - `templates/` tiene las pantallas HTML.
  - `static/` tiene los estilos (CSS) y la interactividad (JavaScript).
  - La paleta de colores y la fuente Lato son las de la FAQ 3.
- **`tests/`**: todos los tests que se usaron para desarrollar con TDD, separados en 3 carpetas: unitarios, de integración y de sistema. Los de sistema usan el navegador Edge con Playwright.
- **`docs/`**: la documentación del TP.
  - `Casos_de_Prueba.md`: la lista de casos con su ID, que coincide con los tests.
  - `Decisiones_de_Diseno.md`: el entregable con el porqué de cada decisión (D1, D2, …).
  - `Pasarela_Simulada.md`: cómo funciona el pago con tarjeta.
- **`data/`**: acá se crea la base de datos al usar la app. No se sube a git.
- **`run.py`**: levanta la app.

## Por qué está separado así

El **dominio** no conoce ni la web ni la base de datos. Las piezas externas (base de datos, pasarela de pago, mail y reloj) se le "enchufan" desde afuera. Eso permite:

- **Probar las reglas con TDD** sin servidor ni base real. Los tests usan datos en memoria y un reloj fijo.
- **Cambiar una pieza sin tocar las reglas.** Por ejemplo, pasamos de CSV a SQLite sin modificar el dominio.

## Decisiones que conviene conocer

- **Mercado Pago es simulado** (FAQ 4): una página propia con su aspecto. Para probar, usá la tarjeta `4509 9535 6623 3704`, vencimiento `11/30`, código `123` y cualquier DNI de 7 u 8 dígitos. Con un titular cualquiera el pago se aprueba, y con `OTHE` se rechaza.
- **Se valida todo antes de pagar.** A la pasarela solo se llega con la compra correcta.
- **Usuario de sesión fijo**, sin login (FAQ 19).
- **Las respuestas del PO** a nuestras dudas están en la sección 2 de `Casos_de_Prueba.md` (supuestos S1 a S10).

## Comandos

```bash
pytest -q             # todos los tests
pytest tests/system   # solo los del navegador
flake8 src tests      # estilo PEP8 (no debe imprimir nada)
python run.py         # levantar la app
```

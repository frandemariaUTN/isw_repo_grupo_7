# Estructura del proyecto

TP6 - TDD | Grupo 7. Qué hace cada carpeta y cada archivo, pensado para alguien que llega sin conocer el proyecto.

## Qué es

Una web para **comprar entradas** a EcoHarmony Park, desarrollada con **TDD** (Red-Green-Refactor). Se eligen fecha, visitantes (edad y tipo de pase) y forma de pago:

- **Efectivo:** la compra queda pendiente de pago en boletería.
- **Tarjeta:** se pasa por una **pasarela de pago simulada** con el aspecto de Mercado Pago.

Al confirmar, se envía un **mail con un código QR** de las entradas. La web es **responsive y pensada primero para celular**, porque el PO pide una app mobile y acepta una web responsive (FAQ 24).

**Tecnologías:** Python 3.11+, Flask (web), SQLite (base de datos), HTML, CSS y JavaScript sin frameworks, pytest y Playwright (tests).

## Cómo viaja una compra

```text
Pantalla de compra (web) ──► API Flask ──► ServicioDeCompra ──► reglas del dominio
                                                │
                     ┌──────────────────────────┼───────────────────────┐
                     ▼                          ▼                       ▼
            Base SQLite (guarda)     Pasarela simulada (tarjeta)   Mail con QR (SMTP)
```

El **dominio** (las reglas) no conoce la web, la base ni el mail. Esas piezas se le conectan desde afuera. Así las reglas se prueban sin servidor ni internet, y una pieza se puede cambiar sin tocar el resto (por ejemplo, pasamos de CSV a SQLite sin modificar el dominio).

## Carpetas y archivos

### Raíz (`tp6/`)

| Archivo | Qué hace |
| --- | --- |
| `run.py` | Levanta la app en http://127.0.0.1:5000. Lee el `.env` si existe |
| `requirements.txt` | Librerías a instalar: pytest, flake8, flask, segno (QR) y playwright |
| `pytest.ini` | Configuración de los tests (dónde está el código y qué pruebas se excluyen por defecto) |
| `.flake8` | Reglas de estilo PEP8 (líneas de hasta 79 caracteres) |
| `.env.ejemplo` | Modelo del `.env` con la cuenta de Gmail que envía los mails. El `.env` real nunca se sube a git |
| `.gitignore` | Archivos que git ignora: `.venv`, `.env` y la base de datos |
| `README.md` | Guía del equipo: instalación, reglas de trabajo y estado del avance |
| `CLAUDE.md` | Instrucciones del proyecto para el asistente de IA (Claude Code) que usamos |
| `data/` | Acá se crea la base `ecoharmony.db` al usar la app. No se sube a git |

### `src/ecoharmony/dominio/`: reglas de negocio

Código "puro": no usa Flask, base de datos ni internet.

| Archivo | Qué hace |
| --- | --- |
| `precios.py` | Precios (común $10.000, VIP $20.000) y descuentos por edad: hasta 3 años gratis, hasta 15 y desde 60 la mitad (FAQ 6 y 7) |
| `pases.py` | Tipos de pase (Común y VIP) y su validación |
| `edades.py` | Valida la edad de cada visitante (entero de 0 a 120) |
| `cantidades.py` | Valida la cantidad de entradas (de 1 a 10) |
| `conversiones.py` | Convierte lo que llega del formulario a número entero, con un mensaje de error claro |
| `visitantes.py` | `Visitante` (edad y pase) y la carga de la lista de visitantes |
| `calendario.py` | Días de apertura: cerrado los lunes, el 25/12 y el 1/1. Compra hasta un mes adelante, y para hoy hasta las 17:30 |
| `fechas.py` | Valida la fecha de visita elegida usando el calendario |
| `reloj.py` | Hora local del parque (UTC-3). La hora se recibe desde afuera, así los tests usan un reloj fijo |
| `pagos.py` | Formas de pago (efectivo o tarjeta), estados de la compra y cómo cambian según el resultado del pago |
| `compras.py` | `Compra` y `crear_compra`: valida todo junto, controla el límite de 10 entradas por fecha (FAQ 27) y arma el mensaje final |
| `tarjetas.py` | Valida la tarjeta: 16 dígitos con control de Luhn, vencimiento, código, titular y DNI. Solo conserva marca y últimos 4 dígitos |
| `pasarela.py` | Pasarela simulada: sesión de pago con un código único (token) y resultado según el titular (`APRO` aprueba, `OTHE` rechaza) |
| `mails.py` | Arma el mail de confirmación (asunto, cuerpo y texto del QR con las entradas por pase y edad) |
| `repositorio.py` | Repositorio en memoria: define qué operaciones debe tener cualquier forma de guardar compras |
| `usuarios.py` | Usuario de sesión fijo (Salva), porque el login no es parte de esta US (FAQ 19) |
| `formatos.py` | Formato de montos (`$10.000`) y de fechas (`dd/mm/aaaa`) |
| `errores.py` | Tipos de error: de validación (con el campo afectado) y de envío de mail |

### `src/ecoharmony/aplicacion/`: el caso de uso

| Archivo | Qué hace |
| --- | --- |
| `servicio_de_compra.py` | `ServicioDeCompra` coordina todo. `comprar` valida y guarda la compra, y con tarjeta abre la pasarela; `pagar` y `cancelar` aplican el resultado. Al confirmar envía el mail; si el mail falla, la compra se mantiene y se avisa |

### `src/ecoharmony/persistencia/`: base de datos

| Archivo | Qué hace |
| --- | --- |
| `repositorio_sqlite.py` | Guarda y busca compras en SQLite. Usa transacciones, así una compra nunca queda a medias y dos compras simultáneas no reciben el mismo número |

### `src/ecoharmony/notificaciones/`: envío del mail

| Archivo | Qué hace |
| --- | --- |
| `notificador_smtp.py` | Envía el mail de verdad por Gmail: versión de texto, versión HTML con la imagen del QR y el QR adjunto |
| `notificador_simulado.py` | Guarda el mail sin enviarlo. Lo usan los tests y la app cuando no hay `.env` |
| `destinatarios.py` | Valida que la dirección de mail tenga un formato correcto |
| `__init__.py` | `elegir_notificador`: si el `.env` tiene la cuenta, usa el envío real; si no, el simulado |

`src/ecoharmony/configuracion.py` lee el archivo `.env`.

### `src/ecoharmony/web/`: la aplicación web

| Archivo | Qué hace |
| --- | --- |
| `app.py` | Rutas de Flask: la pantalla de compra, los datos del calendario y los precios, la creación de la compra, la pasarela y la pantalla de resultado |
| `templates/base.html` | Estructura común: cabecera con el logo, saludo al usuario y colinas de fondo |
| `templates/compra.html` | Pantalla de compra en 3 pasos: fecha, visitantes y forma de pago, con el total siempre visible abajo |
| `templates/pasarela.html` | Pantalla de pago con el aspecto de Mercado Pago (amarillo y azul) |
| `templates/resultado.html` | Resultado: compra confirmada con aviso del mail, rechazo o pago pendiente |
| `templates/error.html` | Página no encontrada |
| `templates/_rana.html` | La mascota (rana de ojos rojos) dibujada en SVG con la paleta del PO |
| `templates/_modal_pago.html` | Pop-up que avisa que el pago se rechazó o se canceló (pedido del PO) |
| `static/css/app.css` | Estilos de la app: paleta y fuente Lato de la FAQ 3, diseño para celular y animaciones |
| `static/css/pasarela.css` | Estilos de la pasarela, distintos a los de la app para que se sienta como una página externa |
| `static/js/compra.js` | Calendario con días cerrados, carga de visitantes, total en vivo, errores junto a cada campo y envío de la compra |
| `static/js/pasarela.js` | Formato del número de tarjeta, detección de la marca y bloqueo del doble clic |
| `static/js/comun.js` | Hojas que caen al confirmar y apertura de pop-ups |

### `tests/`: pruebas de TDD

Separadas en 3 carpetas. Cada test lleva el ID de su caso (por ejemplo `PRE-05`), que coincide con `docs/Casos_de_Prueba.md`.

- **`unit/`**: reglas del dominio, una por archivo (`test_precios.py`, `test_tarjetas.py`, etc.). Son las más rápidas.
- **`integration/`**: piezas conectadas: la base SQLite, la pasarela, el envío de mails (con un servidor falso), el servicio y la API Flask.
- **`system/`**: recorren la app en el navegador Edge con Playwright, como lo haría una persona. Incluyen las 4 pruebas de usuario de la US.

### `docs/`: documentación

| Archivo | Qué hace |
| --- | --- |
| `Casos_de_Prueba.md` | Lista de todos los casos de prueba con su origen (criterio de aceptación o FAQ) y las respuestas del PO a nuestras dudas |
| `Decisiones_de_Diseno.md` | Entregable de la cátedra: cada decisión de diseño (D1, D2, …) con su motivo |
| `Pasarela_Simulada.md` | Flujo, rutas y diseño de la pasarela de pago |
| `Estructura_del_Proyecto.md` | Este documento |
| `logo/` | Logo aprobado por el PO (FAQ 17), en versión clara, oscura y SVG |

## Para probar

```bash
pytest -q               # todos los tests
pytest tests/system     # solo los del navegador
pytest -m smtp_real     # envía un mail real de prueba (necesita el .env)
flake8 src tests        # estilo PEP8 (no debe imprimir nada)
python run.py           # levantar la app
```

- **Tarjeta de prueba:** `4509 9535 6623 3704`, vencimiento `11/30`, código `123` y cualquier DNI de 7 u 8 dígitos. Con cualquier titular el pago se aprueba; con `OTHE` se rechaza.
- **Mail real:** copiar `.env.ejemplo` como `.env` y completar una cuenta de Gmail con *contraseña de aplicación*. Sin `.env`, el mail se simula.

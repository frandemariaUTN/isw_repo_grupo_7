# CLAUDE.md

Instrucciones del proyecto para Claude Code. Leelas antes de tocar nada.

## 1. Qué es este proyecto

TP6 de Ingeniería y Calidad de Software (UTN FRC, Grupo 7): implementar la user story **"Comprar entradas"** del dominio **EcoHarmony Park** con **TDD** (Red-Green-Refactor).

- Web responsive. Backend en Python 3.11+, tests con pytest, estilo PEP8 con flake8 (79 columnas).
- Persistencia en SQLite (D35). Capa web con Flask en `src/ecoharmony/web/` (`python run.py` la levanta en http://127.0.0.1:5000).
- Mail de confirmación **simulado** con un modal "Mail enviado a …" (FAQ 5, D36).
- Pago con tarjeta mediante una **pasarela de pago simulada** con el aspecto de Mercado Pago (no hay integración real).
- Idioma: código de dominio, tests, commits y respuestas **en español**.

Todos los comandos se ejecutan desde esta carpeta (donde están `pytest.ini` y `requirements.txt`) con el entorno virtual `.venv` activado:

```bash
pytest -q              # todos los tests
pytest -k PRE-05       # un caso por su ID
flake8 src tests       # no debe imprimir nada
```

## 2. Documentos que hay que mantener al día

| Archivo | Regla |
| --- | --- |
| `docs/Casos_de_Prueba.md` | Respalda los tests. **Si se agrega, quita o cambia un test, se actualiza en el mismo paso** (fila del caso, tabla "Dónde están los tests", conteos del resumen). Los IDs de los tests (`PRE-05`, `TAR-12`) deben coincidir con los del documento |
| `docs/Decisiones_de_Diseno.md` | Entregable de la cátedra. Cuando se toma una decisión de diseño relevante, se agrega una fila al final con el siguiente número (D#) |
| `docs/Pasarela_Simulada.md` | Flujo, rutas y pantalla de la pasarela simulada |
| `README.md` | Guía del equipo y tabla de estado del avance (actualizarla al cerrar cada grupo) |

Las reglas de negocio salen de la user story, la descripción del dominio y las FAQs de los PO (docentes). Los supuestos **S1 a S10** ya los respondió el PO (20/10/2026, sección 2 de `Casos_de_Prueba.md`); la única duda abierta es el límite de 10 (se mantiene la FAQ 27). **No inventes reglas de negocio nuevas:** si algo no está definido, se pregunta.

## 3. Cómo se trabaja el ciclo TDD

1. **RED:** escribir los tests y **verificar que fallan por el motivo esperado** (no por un error de tipeo).
2. **GREEN:** código mínimo para que pasen, con toda la suite en verde y `flake8` limpio.
3. **REFACTOR:** mejorar el diseño sin cambiar comportamiento, con todo en verde.

Para avanzar más rápido se trabaja **por grupos de casos** (decisión D20): un commit RED con todos los tests del grupo y un commit GREEN con el código. Los casos que pasan de entrada se commitean como `feat: test ...` sin fase.

**Commits** (prefijos del README de la raíz del repo):

- `feat: [RED] ...` / `feat: [GREEN] ...` para tests y código.
- `refactor: ...`, `docs: ...`, `chore: ...`, `fix: ...` según corresponda.
- Mensajes en español.

**Reglas de seguridad de git:**

- Agregá archivos **por nombre** (`git add src/...`), nunca `git add .`.
- No commitees `.venv/`, `.env`, `data/*.db`, zips ni archivos temporales.
- **No hagas `git push` ni `git pull` sin que se pida.**
- Mostrá qué vas a commitear antes de hacerlo.

## 4. Arquitectura

Dominio puro en `src/ecoharmony/dominio/` (sin Flask, sin base de datos, sin internet). Adaptadores en `src/ecoharmony/persistencia/` (`RepositorioSQLite`) y `src/ecoharmony/notificaciones/` (`NotificadorSimulado`). El caso de uso está en `src/ecoharmony/aplicacion/` (`ServicioDeCompra`: `comprar`, `pagar`, `cancelar`). Tests en `tests/unit/`, `tests/integration/` y `tests/system/`.

| Módulo | Contenido |
| --- | --- |
| `pases.py`, `precios.py` | Tipos de pase, precios y descuentos por edad |
| `edades.py`, `cantidades.py`, `conversiones.py` | Validación de edad y cantidad |
| `visitantes.py` | `Visitante` y `construir_visitantes` |
| `calendario.py`, `fechas.py`, `reloj.py` | Días de apertura, fechas disponibles y hora local |
| `pagos.py` | Formas de pago, estados de la compra y transiciones |
| `compras.py` | `Compra`, `crear_compra`, límite de 10, mensaje final |
| `tarjetas.py` | Validación de tarjeta y `TarjetaValidada` (solo marca, últimos 4 y titular) |
| `pasarela.py` | `PasarelaSimulada`: sesiones de pago con token y resultado según el titular |
| `repositorio.py` | `RepositorioEnMemoria` (define el contrato del repositorio SQLite) |
| `usuarios.py`, `mails.py`, `formatos.py`, `errores.py` | Usuario mock, armado del mail, formatos, errores |

Convenciones de diseño:

- **El reloj se inyecta** como `ahora`: un `datetime` **con zona horaria** (UTC-3 fijo). Los tests nunca usan la hora real. "Hoy" de referencia en los tests: miércoles 14/10/2026 10:00.
- **Montos como enteros en pesos.** Los precios llegan por parámetro con la tabla oficial como valor por defecto.
- **Errores:** `ErrorDeValidacion(campo, mensaje)`; `crear_compra` junta todos y lanza `ErroresDeValidacion`.
- **Dependencias externas detrás de interfaces** con una implementación real o simulada y una falsa (repositorio SQLite y en memoria, notificador simulado).
- **Los datos de tarjeta nunca se guardan** (ni en la base de datos ni en logs).

## 5. Reglas de negocio clave (resumen)

- Precios: común $10.000, VIP $20.000. Descuentos: ≤ 3 años gratis; ≤ 15 años y ≥ 60 años, 50%.
- El parque cierra los lunes, el 25/12 y el 1/1. Se compra desde hoy hasta un mes adelante; para hoy, hasta las 17:30.
- Máximo **10 entradas por usuario y por fecha**, sumando compras (las `FALLIDA` no cuentan).
- Formas de pago: efectivo (boletería) o tarjeta. Se **valida todo antes** de ir a la pasarela.
- Estados: `PENDIENTE_BOLETERIA`, `PENDIENTE_PAGO_ONLINE`, `PAGADA`, `FALLIDA`.
- Usuario de sesión mockeado (FAQ 19). Solo DNI (FAQ 32).

## 6. Estado y próximos pasos

**Hecho** (260 tests en verde): todos los grupos, de `PRE` a `SIS`. El frontend está en `web/templates/` y `web/static/`; las pruebas de sistema (`tests/system/`) usan Playwright 1.50 con el Edge instalado.

**Pendiente:** aplicar las respuestas del PO del 20/10/2026 (S8: $0 con tarjeta pasa por la pasarela; S4: rechazo con pop-up; S5: QR en el mail) y sumar CAN-19 (cantidad vacía).

## 7. Cómo colaborar con el equipo

- Explicá brevemente cada decisión de diseño; el equipo la justifica en un documento.
- Ante una duda de negocio, frená y preguntá: se eleva a los PO y se resuelve de forma asíncrona.
- Al terminar un paso, resumí en una o dos frases qué quedó hecho, cuántos tests pasan y qué sigue.

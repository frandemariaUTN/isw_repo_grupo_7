# Casos de prueba: US "Comprar entradas" (EcoHarmony Park)

TP6 - Test Driven Development (TDD) | Grupo 7 | Ingeniería y Calidad de Software 2026

Documento vivo: se actualiza a medida que avanzan los ciclos Red-Green-Refactor y llegan las respuestas del PO.

---

## 1. Convenciones

**Niveles de prueba**

| Nivel | Prefijos | Qué prueba | Dependencias |
| --- | --- | --- | --- |
| Unitaria | `PRE`, `EDA`, `PAS`, `DIA`, `FEC`, `CAN`, `PAG`, `ORD`, `USR`, `MAI`, `TAR` | Reglas de dominio puras | Ninguna (reloj inyectado) |
| Integración | `BD`, `PSM`, `MAIL`, `SRV`, `API` | Componentes conectados entre sí | Base SQLite temporal, pasarela simulada y mail simulado, Flask test client |
| Sistema | `SIS` | Flujo completo desde el navegador | App levantada con fakes, base SQLite temporal, reloj fijo |

**Reloj de referencia para los tests:** "hoy" = **miércoles 14/10/2026, 10:00** (hora de Argentina), salvo que el caso indique otra cosa.

**Fechas útiles (calendario 2026-2027):**

| Fecha | Día | Estado |
| --- | --- | --- |
| 19/10/2026 y 26/10/2026 | Lunes | Cerrado |
| 20/10/2026 a 25/10/2026 | Martes a domingo | Abierto |
| 14/11/2026 | Sábado | Último día permitido (hoy + 1 mes) |
| 15/11/2026 | Domingo | Abierto, pero fuera de rango |
| 25/12/2026 y 01/01/2027 | Viernes | Cerrado (feriado) |

**Columna Origen**

- `CA1` a `CA9`: criterios de aceptación de la US, en el orden en que figuran.
- `FAQ n`: pregunta n del documento de FAQs.
- `DOM`: descripción del dominio.
- `S1` a `S10`: **supuesto pendiente de confirmar con el PO** (ver sección 2). Se marcan con ⚠️.
- `S11` a `S15`: **decisión del grupo** sobre la pasarela de pago simulada (ver sección 2).

**Estados de una compra:** `PENDIENTE_BOLETERIA`, `PENDIENTE_PAGO_ONLINE`, `PAGADA`, `FALLIDA`.

**Dónde están los tests** (`tests/unit/` y `tests/integration/`):

| Archivo | Casos |
| --- | --- |
| `test_precios.py` | PRE-01 a PRE-13 |
| `test_total_compra.py` | PRE-14 a PRE-16 |
| `test_edades.py` | EDA-01 a EDA-08 |
| `test_pases.py` | PAS-01 a PAS-05 |
| `test_visitantes.py` | EDA-09, PAS-06, CAN-09 |
| `test_calendario.py` | DIA-01 a DIA-09 y DIA-11 |
| `test_fechas.py` | FEC-01 a FEC-17 y DIA-10 |
| `test_cantidades.py` | CAN-01 a CAN-07 |
| `test_pagos.py` | PAG-01 a PAG-05 y PAG-08 a PAG-12 |
| `test_usuarios.py` | USR-01 |
| `test_compras.py` | ORD-01 a ORD-09, USR-02, USR-03, PAG-06, PAG-07, PAG-13, CAN-08 y CAN-10 a CAN-18 |
| `test_mails.py` | MAI-01 a MAI-10 |
| `test_tarjetas.py` | TAR-01 a TAR-25 |
| `integration/test_repositorio_sqlite.py` | BD-01 a BD-14 (los casos de contrato, BD-12, se corren contra memoria y SQLite) |
| `integration/test_pasarela.py` | PSM-01 a PSM-19 |
| `integration/test_notificador.py` | MAIL-01 a MAIL-03 |
| `integration/test_servicio_de_compra.py` | SRV-01 a SRV-14 |
| `integration/test_api.py` | API-01 a API-22 |

**Estilo:** PEP8, tests con nombres descriptivos en español (`test_<regla>_<condicion>_<resultado>`), un `assert` conceptual por test, parametrización con `pytest.mark.parametrize` para casos similares.

**Pruebas manuales / opcionales:** marcadas con `@pytest.mark.manual`. Quedan excluidas de la corrida por defecto.

---

## 2. Supuestos pendientes de confirmar con el PO

| ID | Supuesto adoptado mientras tanto | Pregunta al PO |
| --- | --- | --- |
| S1 | El tipo de pase se elige **por visitante** | ¿Pase por visitante o uno por compra? |
| S2 | Las entradas gratuitas (≤ 3 años) **cuentan** para el límite de 10 | ¿Cuentan para el límite? |
| S3 | Efectivo: la compra queda `PENDIENTE_BOLETERIA` y **se envía el mail** al crearla | ¿Se envía mail con pago en efectivo? ¿Qué estado tiene? |
| S4 | Pago con tarjeta fallido: la orden pasa a `FALLIDA`, libera el cupo y **no se reintenta** sobre la misma orden | ¿Qué pasa si el pago falla o se cancela? |
| S5 | El mail de esta US **no lleva QR** (FAQ 18 lo pide solo para actividades) | ¿Lleva QR? |
| S6 | Edad máxima válida: **120 años** | ¿Cuál es la edad máxima razonable? |
| S7 | Se puede comprar para hoy **antes de la apertura** (8:30), siempre que sea hasta las 17:30 | ¿Hay un horario mínimo de compra? |
| S8 | Compra con tarjeta de **total $0** (todos ≤ 3 años): no pasa por la pasarela de pago, queda `PAGADA` | ¿Cómo se trata una compra sin costo? |
| S9 | El mail se envía al **confirmar** la compra: en efectivo al crearla, con tarjeta al aprobarse el pago | ¿Cuándo debe llegar el mail? |
| S10 | **Ya no aplica:** el mail se simula con un modal (FAQ 5), así que el envío no puede fallar | Resuelto por la FAQ 5 |
| S11 | La pasarela simulada se abre en **la misma pestaña** (redirección) y vuelve a la app al terminar | Decisión del grupo |
| S12 | El resultado del pago se elige con el **nombre del titular**, como en las tarjetas de prueba de Mercado Pago: `APRO` aprueba, `OTHE`, `FUND`, `SECU` y `EXPI` rechazan, `CONT` queda pendiente. Cualquier otro titular con tarjeta válida **se aprueba** | Decisión del grupo |
| S13 | En la pasarela **no se reintenta** tras un rechazo ni tras cancelar: la compra pasa a `FALLIDA` y se vuelve a la app (extiende S4) | Decisión del grupo |
| S14 | La sesión de pago **no vence por tiempo** | Decisión del grupo |
| S15 | Los datos de la tarjeta **nunca se guardan** (ni en la base de datos ni en logs): tras validar solo se conservan marca y últimos 4 dígitos | Decisión del grupo (seguridad) |

---

## 3. Pruebas unitarias (137)

### 3.1 Precios y descuentos (`PRE`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| PRE-01 | Pase común, 30 años | $10.000 | FAQ 6 |
| PRE-02 | Pase VIP, 30 años | $20.000 | FAQ 6 |
| PRE-03 | Común, 0 años | $0 | FAQ 7 |
| PRE-04 | Común, 3 años (límite superior gratis) | $0 | FAQ 7 |
| PRE-05 | Común, 4 años (primer valor con descuento) | $5.000 | FAQ 7 |
| PRE-06 | Común, 15 años (límite superior del 50%) | $5.000 | FAQ 7 |
| PRE-07 | Común, 16 años (sin descuento) | $10.000 | FAQ 7 |
| PRE-08 | Común, 59 años (sin descuento) | $10.000 | FAQ 7 |
| PRE-09 | Común, 60 años (límite inferior del 50%) | $5.000 | FAQ 7 |
| PRE-10 | Común, 85 años | $5.000 | FAQ 7 |
| PRE-11 | VIP, 3 años | $0 | FAQ 6, 7 |
| PRE-12 | VIP, 10 años | $10.000 | FAQ 6, 7 |
| PRE-13 | VIP, 70 años | $10.000 | FAQ 6, 7 |
| PRE-14 | Compra mixta: VIP 30, común 10, común 2, VIP 65 | Total $35.000 | FAQ 6, 7 |
| PRE-15 | Compra donde todos tienen ≤ 3 años | Total $0 | FAQ 7 |
| PRE-16 | Se pasa una tabla de precios con VIP a $25.000 (dos tests: precio individual y total de compra) | El cálculo usa la tabla recibida: VIP 30 años $25.000; VIP 30 + VIP 10 años $37.500 (precios no hardcodeados) | Diseño |

### 3.2 Edad del visitante (`EDA`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| EDA-01 | Edad -1 | Rechazada con error | CA1 |
| EDA-02 | Edad "abc" | Rechazada con error | CA1 |
| EDA-03 | Edad vacía o `None` | Rechazada: la edad es obligatoria | CA1 |
| EDA-04 | Edad decimal 3.5 | Rechazada: debe ser entera | CA1 |
| EDA-05 | Edad 0 | Aceptada | CA1, FAQ 7 |
| EDA-06 | Edad "25" (texto numérico, como llega del formulario) | Se normaliza a 25 y se acepta | CA1 |
| EDA-07 | Edad 121 | Rechazada ⚠️ | S6 |
| EDA-08 | Edad 120 | Aceptada ⚠️ | S6 |
| EDA-09 | Tres visitantes y el segundo sin edad | Error que identifica al visitante 2 | CA1 |

### 3.3 Tipo de pase (`PAS`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| PAS-01 | Pase "VIP" | Aceptado | CA1 |
| PAS-02 | Pase "COMUN" | Aceptado | CA1 |
| PAS-03 | Pase vacío | Rechazado: es obligatorio | CA1 |
| PAS-04 | Pase "PLATINO" | Rechazado: pase inexistente | CA1 |
| PAS-05 | Pase " vip " (espacios y minúsculas) | Se normaliza a `VIP` | Diseño |
| PAS-06 | Una compra con un visitante VIP y otro común | Aceptada, cada uno con su pase ⚠️ | S1 |

### 3.4 Días de apertura (`DIA`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| DIA-01 | Martes a domingo (parametrizado, 6 casos) | Parque abierto | FAQ 1 |
| DIA-02 | Lunes 19/10/2026 | Cerrado | FAQ 1, CA5 |
| DIA-03 | 25/12/2026 (viernes) | Cerrado por feriado | FAQ 1 |
| DIA-04 | 01/01/2027 (viernes) | Cerrado por feriado | FAQ 1 |
| DIA-05 | 24/12/2026 | Abierto | FAQ 1 |
| DIA-06 | 31/12/2026 | Abierto | FAQ 1 |
| DIA-07 | 02/01/2027 | Abierto | FAQ 1 |
| DIA-08 | Con hoy = 14/10/2026, lista de días no disponibles del rango | Exactamente los lunes 19/10, 26/10, 02/11 y 09/11 | FAQ 2 |
| DIA-09 | Con hoy = 20/12/2026, lista de días no disponibles | Los lunes 21/12, 28/12, 04/01, 11/01, 18/01 más el 25/12 y el 01/01 | FAQ 1, 2 |
| DIA-10 | Fecha cerrada | El error indica el motivo: "el parque está cerrado ese día" | CA5 |
| DIA-11 | Con hoy = 14/10/2026 a las 17:45, lista de días no disponibles | Incluye el 14/10 además de los lunes (hoy ya no se puede comprar) | FAQ 26, FAQ 2 |

### 3.5 Fecha de visita (`FEC`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| FEC-01 | Ayer (13/10/2026) | Rechazada: fecha pasada | CA2 |
| FEC-02 | Hoy (14/10/2026) a las 10:00 | Aceptada | CA2 |
| FEC-03 | Hoy a las 17:30 exactas | Aceptada (límite inclusivo) | FAQ 26 |
| FEC-04 | Hoy a las 17:31 | Rechazada | FAQ 26 |
| FEC-05 | Hoy a las 19:00 | Rechazada | FAQ 26 |
| FEC-06 | Hoy a las 08:00 (antes de abrir) | Aceptada ⚠️ | S7 |
| FEC-07 | Mañana (15/10/2026) con reloj en las 18:00 de hoy | Aceptada (el límite de las 17:30 aplica solo al mismo día) | FAQ 26 |
| FEC-08 | 14/11/2026 (hoy + 1 mes exacto) | Aceptada | FAQ 25 |
| FEC-09 | 15/11/2026 (domingo, hoy + 1 mes + 1 día) | Rechazada por exceder el horizonte | FAQ 25 |
| FEC-10 | Hoy es lunes (19/10/2026) | Rechazada: parque cerrado | CA5 |
| FEC-11 | Fecha vacía o `None` | Rechazada: es obligatoria | CA1 |
| FEC-12 | Formato inválido ("31/02/2026", "mañana") | Rechazada | CA1 |
| FEC-13 | Hoy = 31/01/2027, fecha 28/02/2027 | Aceptada (cálculo del fin de mes) | FAQ 25 |
| FEC-14 | Hoy = 20/12/2026, fecha 02/01/2027 | Aceptada (cruce de año) | FAQ 25 |
| FEC-15 | Hoy = 20/12/2026, fecha 01/01/2027 | Rechazada: feriado | FAQ 1 |
| FEC-16 | Reloj en 23:30 hora Argentina (02:30 UTC del día siguiente) | "Hoy" sigue siendo el 14/10 (zona horaria correcta) | Diseño |
| FEC-17 | Instante sin zona horaria | `ValueError`: el reloj siempre debe incluir zona horaria | Diseño |

### 3.6 Cantidad y límite de 10 entradas (`CAN`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| CAN-01 | Cantidad 0 | Rechazada | CA7 |
| CAN-02 | Cantidad -3 | Rechazada | CA7 |
| CAN-03 | Cantidad 1 | Aceptada | CA7 |
| CAN-04 | Cantidad 10 | Aceptada | CA7 |
| CAN-05 | Cantidad 11 | Rechazada | CA7 |
| CAN-06 | Cantidad "dos" | Rechazada: no numérica | CA7 |
| CAN-07 | Cantidad 2.5 | Rechazada: debe ser entera | CA7 |
| CAN-08 | Cantidad 3 con 2 visitantes cargados | Rechazada: no coincide | CA1 |
| CAN-09 | Lista de visitantes vacía | Rechazada | CA1 |
| CAN-10 | Usuario con 6 entradas previas para esa fecha, compra 4 | Aceptada (total 10) | FAQ 27 |
| CAN-11 | Usuario con 6 previas, compra 5 | Rechazada (total 11) | FAQ 27 |
| CAN-12 | Usuario con 10 previas, compra 1 | Rechazada | FAQ 27 |
| CAN-13 | Usuario con 10 previas **en otra fecha**, compra 5 | Aceptada | FAQ 27 |
| CAN-14 | **Otro usuario** con 10 previas en esa fecha | No afecta al usuario actual | FAQ 27 |
| CAN-15 | Las entradas gratuitas (≤ 3 años) cuentan para el límite | Cuentan ⚠️ | S2 |
| CAN-16 | Compras previas `FALLIDA` | No cuentan para el límite ⚠️ | S4 |
| CAN-17 | Compras previas `PENDIENTE_*` (efectivo o tarjeta sin resolver) | Cuentan para el límite ⚠️ | S3 |
| CAN-18 | Usuario con 7 previas, compra 5 | El error informa que puede comprar 3 más | CA7 |

### 3.7 Forma de pago y estados (`PAG`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| PAG-01 | Sin forma de pago | Rechazada: es obligatoria | CA6 |
| PAG-02 | Forma de pago "efectivo" | Aceptada | CA6 |
| PAG-03 | Forma de pago "tarjeta" | Aceptada | CA6 |
| PAG-04 | Forma de pago "cheque" | Rechazada | CA6 |
| PAG-05 | Forma de pago " Tarjeta " | Se normaliza | Diseño |
| PAG-06 | Compra en efectivo creada | Estado `PENDIENTE_BOLETERIA` ⚠️ | S3 |
| PAG-07 | Compra con tarjeta creada | Estado `PENDIENTE_PAGO_ONLINE` | CA4 |
| PAG-08 | `PENDIENTE_PAGO_ONLINE` y pago aprobado | Pasa a `PAGADA` | CA4 |
| PAG-09 | `PENDIENTE_PAGO_ONLINE` y pago rechazado | Pasa a `FALLIDA` ⚠️ | S4 |
| PAG-10 | `PENDIENTE_PAGO_ONLINE` y pago pendiente | Sigue `PENDIENTE_PAGO_ONLINE` | CA4 |
| PAG-11 | `PAGADA` recibe un rechazo | Transición inválida: se mantiene `PAGADA` | Diseño |
| PAG-12 | `FALLIDA` recibe una aprobación | Transición inválida ⚠️ | S4 |
| PAG-13 | Tarjeta con total $0 | Pasa directo a `PAGADA` ⚠️ | S8 |

### 3.8 Orden de compra (`ORD`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| ORD-01 | Dos compras consecutivas | Números de orden distintos | FAQ 18 |
| ORD-02 | Orden creada | Contiene usuario, fecha, forma de pago, visitantes y total | CA1 |
| ORD-03 | Orden con varios visitantes | Total = suma de subtotales | PRE |
| ORD-04 | Orden creada | Fecha y hora de creación tomadas del reloj inyectado | Diseño |
| ORD-05 | Compra de 3 entradas para el 20/10/2026 | Mensaje "Compraste 3 entradas para el 20/10/2026" | CA8 |
| ORD-06 | Compra de 1 entrada | Mensaje en singular: "Compraste 1 entrada..." | CA8 |
| ORD-07 | Fecha en el mensaje final | Formato dd/mm/aaaa | CA8 |
| ORD-08 | Falla una validación | No se crea orden ni se consume número | CA1 |
| ORD-09 | Fecha cerrada y cantidad 11 a la vez | Se informan **ambos** errores juntos | CA5, CA7 |

### 3.9 Usuario de sesión (`USR`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| USR-01 | Usuario mock | Tiene email válido y un identificador | FAQ 19 |
| USR-02 | Compra creada | Queda asociada al usuario de la sesión | CA9 |
| USR-03 | Compra sin sesión | Rechazada | CA9 |

### 3.10 Contenido del mail (`MAI`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| MAI-01 | Asunto | Incluye el número de orden | CA3 |
| MAI-02 | Destinatario | Es el email del usuario | CA3 |
| MAI-03 | Cuerpo | Incluye el número de orden | CA3, FAQ 18 |
| MAI-04 | Cuerpo | Incluye la fecha de visita | CA3 |
| MAI-05 | Cuerpo | Detalle por visitante: edad, pase y subtotal | FAQ 18 |
| MAI-06 | Cuerpo | Incluye el total | FAQ 18 |
| MAI-07 | Cuerpo | Incluye la forma de pago | CA3 |
| MAI-08 | Compra en efectivo | Indica que se abona en boletería ⚠️ | S3 |
| MAI-09 | Montos | Formato "$10.000" | Diseño |
| MAI-10 | Visitante gratuito | Figura con subtotal $0 | FAQ 7 |

### 3.11 Tarjeta de crédito o débito (`TAR`)

Datos de prueba: Mastercard `5031 7557 3453 0604`, Visa `4509 9535 6623 3704`, código de seguridad `123`, vencimiento `11/30`, DNI `12345678` (tarjetas de prueba de Mercado Pago). Con el reloj de referencia ("hoy" = 14/10/2026) para los vencimientos.

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| TAR-01 | Número Mastercard de prueba `5031 7557 3453 0604` | Válido | CA4 |
| TAR-02 | Número Visa de prueba `4509 9535 6623 3704` | Válido | CA4 |
| TAR-03 | Número con espacios y guiones (`5031-7557-3453-0604`) | Se normaliza a 16 dígitos | CA4 |
| TAR-04 | Número vacío o `None` | Rechazado: es obligatorio | CA4 |
| TAR-05 | Número con letras | Rechazado | CA4 |
| TAR-06 | Número que no cumple el algoritmo de Luhn (`...0605`) | Rechazado | CA4 |
| TAR-07 | Número de 12 dígitos | Rechazado: demasiado corto | CA4 |
| TAR-08 | Número de 20 dígitos | Rechazado: demasiado largo | CA4 |
| TAR-09 | Marca de un número que empieza con 4 | `Visa` | CA4 |
| TAR-10 | Marca de un número que empieza con 5 | `Mastercard` | CA4 |
| TAR-11 | Marca de un número con otro inicio | `Tarjeta` (genérica) | CA4 |
| TAR-12 | Vencimiento `11/30` | Válido | CA4 |
| TAR-13 | Vencimiento `10/26` (mes actual) | Válido: vence a fin de mes | CA4 |
| TAR-14 | Vencimiento `09/26` | Rechazado: tarjeta vencida | CA4 |
| TAR-15 | Vencimiento `13/30` o `00/30` | Rechazado: mes inválido | CA4 |
| TAR-16 | Vencimiento con formato inválido (`1130`, `11/2030`, `ab/cd`, vacío) | Rechazado | CA4 |
| TAR-17 | Código de seguridad `123` | Válido | CA4 |
| TAR-18 | Código de seguridad inválido (`12`, `1234`, `abc`, vacío) | Rechazado | CA4 |
| TAR-19 | Titular `APRO` y `Facundo Pérez` | Válidos | CA4 |
| TAR-20 | Titular vacío | Rechazado | CA4 |
| TAR-21 | Titular con números (`Juan 3`) | Rechazado | CA4 |
| TAR-22 | DNI del titular `12345678` y `1234567` | Válidos | FAQ 32 |
| TAR-23 | DNI inválido (`123`, `abc`, `123456789`, vacío) | Rechazado: solo DNI de 7 u 8 dígitos | FAQ 32 |
| TAR-24 | Tarjeta con varios datos inválidos a la vez | Se informan **todos** los errores juntos | CA4 |
| TAR-25 | Tarjeta válida | Conserva solo marca, últimos 4 dígitos y titular (nunca el número completo ni el código de seguridad) ⚠️ | S15 |

---

## 4. Pruebas de integración (72)

### 4.1 Base de datos SQLite (`BD`)

Repositorio de compras sobre SQLite (`sqlite3` de la biblioteca estándar). Los tests usan una base temporal por test (`tmp_path`).

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| BD-01 | Primer uso con una base inexistente | Crea el archivo y las tablas | Diseño |
| BD-02 | Guardar y recuperar por número de orden | La compra recuperada es igual a la guardada | Diseño |
| BD-03 | Guardar dos compras | Ninguna pisa a la otra | Diseño |
| BD-04 | Guardar compra con 4 visitantes | Se recuperan los 4, en orden | Diseño |
| BD-05 | Listar compras por usuario y fecha | Devuelve solo las que coinciden | FAQ 27 |
| BD-06 | Buscar orden inexistente | Devuelve `None` | Diseño |
| BD-07 | Actualizar estado de una compra | El cambio persiste al reabrir la base | CA4 |
| BD-08 | Datos con acentos, ñ y comillas | Se guardan y leen sin alterarse | Diseño |
| BD-09 | Base recién creada | Lista de compras vacía | Diseño |
| BD-10 | Reabrir el repositorio | El próximo número de orden continúa la secuencia | Diseño |
| BD-11 | Sumar entradas por usuario y fecha | Excluye las `FALLIDA` | FAQ 27, S4 |
| BD-12 | Contrato: repositorio SQLite y repositorio en memoria | Ambos pasan la misma suite | Diseño |
| BD-13 | Falla el guardado a mitad de camino | No queda una compra incompleta (transacción) | Diseño |
| BD-14 | Dos conexiones abiertas sobre la misma base piden número de orden | Obtienen números distintos | Diseño |

### 4.2 Pasarela de pago simulada (`PSM`)

Reemplaza a la integración real con Mercado Pago (la FAQ 4 autoriza simularla). La pasarela es una página propia, con el aspecto de la de Mercado Pago, a la que se llega **después de validar toda la compra**. El resultado se elige con el nombre del titular (S12). Diseño completo en `docs/Pasarela_Simulada.md`.

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| PSM-01 | Crear sesión de pago para una compra con tarjeta | Sesión `ABIERTA` con un token | CA4, FAQ 4 |
| PSM-02 | Sesión creada | Guarda el número de orden y el monto de la compra | CA4 |
| PSM-03 | Dos sesiones distintas | Tokens distintos e impredecibles (al menos 32 caracteres) | Seguridad |
| PSM-04 | Buscar un token inexistente | Devuelve `None` | CA4 |
| PSM-05 | Pagar con titular `APRO` y tarjeta válida | `APROBADO`, sesión `CERRADA` y número de operación | CA4, S12 ⚠️ |
| PSM-06 | Pagar con otro titular válido (`Facundo Pérez`) | `APROBADO` | S12 ⚠️ |
| PSM-07 | Titular `OTHE` | `RECHAZADO` por error general | S12 ⚠️ |
| PSM-08 | Titular `FUND` | `RECHAZADO` por fondos insuficientes | S12 ⚠️ |
| PSM-09 | Titular `SECU` | `RECHAZADO` por código de seguridad inválido | S12 ⚠️ |
| PSM-10 | Titular `EXPI` | `RECHAZADO` por problema con la fecha de vencimiento | S12 ⚠️ |
| PSM-11 | Titular `CONT` | `PENDIENTE` | S12 ⚠️ |
| PSM-12 | Datos de tarjeta inválidos | Errores de validación y la sesión sigue `ABIERTA` (se puede corregir) | CA4 |
| PSM-13 | Pagar una sesión ya cerrada | Error y no cambia el resultado anterior | Diseño |
| PSM-14 | Cancelar una sesión abierta | Sesión `CANCELADA` | S13 ⚠️ |
| PSM-15 | Pagar una sesión cancelada | Error | S13 ⚠️ |
| PSM-16 | Cancelar una sesión ya cerrada | Error y no cambia el resultado | Diseño |
| PSM-17 | Dos pagos aprobados | Números de operación distintos | Diseño |
| PSM-18 | Crear sesión con monto $0 | Error: no hay nada que cobrar | S8 ⚠️ |
| PSM-19 | Después de pagar | La sesión no conserva número de tarjeta ni código de seguridad | S15 ⚠️ |

### 4.3 Notificador de mail simulado (`MAIL`)

La FAQ 5 permite simular el envío del mail mostrando un modal ("Mail enviado a tu@email.com"). El notificador simulado no se conecta a ningún servidor: registra el mail y la app muestra el modal. Queda detrás de la interfaz `Notificador`, así que se podría sumar un envío real sin tocar el resto.

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| MAIL-01 | Notificador simulado | Registra el mail enviado y se puede inspeccionar | CA3, FAQ 5 |
| MAIL-02 | Destinatario con formato inválido | Error sin registrar el envío | CA3 |
| MAIL-03 | Resultado del envío | Informa la dirección a la que se envió (la usa el modal) | FAQ 5 |

### 4.4 Servicio de compra (`SRV`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| SRV-01 | Compra en efectivo válida | Guarda `PENDIENTE_BOLETERIA` y envía mail, sin pasar por la pasarela ⚠️ | S3, S9 |
| SRV-02 | Compra con tarjeta válida | Guarda `PENDIENTE_PAGO_ONLINE`, crea la sesión de pago y devuelve la URL de la pasarela; aún sin mail ⚠️ | CA4, S9 |
| SRV-03 | Compra con tarjeta y datos inválidos (sin fecha, 11 entradas, etc.) | No crea compra ni sesión: todo se valida **antes** de ir a la pasarela | CA1, CA4 |
| SRV-04 | Pago aprobado en la pasarela | Compra `PAGADA` y mail enviado | CA3, CA4 |
| SRV-05 | Pago rechazado | Compra `FALLIDA`, sin mail ⚠️ | S4, S13 |
| SRV-06 | Pago pendiente | Sin cambios y sin mail | CA4 |
| SRV-07 | Se procesa dos veces el mismo pago (doble clic o recarga) | Idempotente: un solo mail y un solo cambio de estado | Diseño |
| SRV-08 | Cancelar el pago desde la pasarela | Compra `FALLIDA` y cupo liberado ⚠️ | S13 |
| SRV-09 | Con base SQLite real: dos compras de 5 y una de 1 | Las dos primeras pasan, la tercera se rechaza | FAQ 27 |
| SRV-10 | Validación fallida | La base queda sin cambios | CA1 |
| SRV-11 | Compra `FALLIDA` previa de 10 entradas | Se puede volver a comprar 10 ⚠️ | S4 |
| SRV-12 | Compra confirmada (efectivo o pago aprobado) | El resultado incluye el email al que se envió el mail, para mostrar el modal | FAQ 5 |
| SRV-13 | Tarjeta con total $0 | `PAGADA`, mail enviado, sin crear sesión de pago ⚠️ | S8 |
| SRV-14 | Pago aprobado | El resultado incluye el mensaje final con cantidad y fecha | CA8 |

### 4.5 API web con Flask (`API`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| API-01 | `GET /` | 200 con el formulario de compra | CA1 |
| API-02 | `GET /api/dias-no-disponibles` | JSON con lunes y feriados del rango | FAQ 2 |
| API-03 | `GET /api/precios` | JSON con precios y reglas de descuento | FAQ 6, 7 |
| API-04 | `POST /api/compras` en efectivo | 201 con número de orden, cantidad y fecha | CA8 |
| API-05 | `POST /api/compras` con tarjeta | 201 con `url_pago` hacia `/pasarela/<token>` | CA4 |
| API-06 | `POST` sin forma de pago | 400 con mensaje | CA6 |
| API-07 | `POST` con fecha de un lunes | 400 con mensaje | CA5 |
| API-08 | `POST` con 11 entradas | 400 con mensaje | CA7 |
| API-09 | `POST` con un visitante sin edad | 400 que identifica al visitante | CA1 |
| API-10 | `POST` con JSON inválido | 400 | Diseño |
| API-11 | Cualquier error de validación | Formato consistente `{"errores": [{"campo", "mensaje"}]}` | Diseño |
| API-12 | `GET /pasarela/<token>` | 200 con el resumen (cantidad de entradas y total) y el formulario de tarjeta | CA4 |
| API-13 | `GET /pasarela/<token>` inexistente | 404 con página de error | CA4 |
| API-14 | `POST /pasarela/<token>/pagar` con titular `APRO` | Redirige a `/compras/<n>/resultado` y la compra queda `PAGADA` | CA4 |
| API-15 | `POST /pasarela/<token>/pagar` con tarjeta inválida | 400 con errores por campo y la sesión sigue abierta | CA4 |
| API-16 | `POST /pasarela/<token>/pagar` con titular `OTHE` | Redirige al resultado con rechazo y la compra queda `FALLIDA` | S12, S13 |
| API-17 | `POST /pasarela/<token>/cancelar` | Redirige a la app y la compra queda `FALLIDA` | S13 |
| API-18 | `POST /pasarela/<token>/pagar` sobre una sesión ya cerrada | Redirige al resultado sin reprocesar | Diseño |
| API-19 | `GET /compras/<n>/resultado` de una compra aprobada | Mensaje de éxito con cantidad de entradas y fecha | CA8 |
| API-20 | `GET /compras/<n>/resultado` de una compra rechazada o pendiente | Mensaje de rechazo con el motivo, o de pago pendiente | CA4 |
| API-21 | `GET /compras/<n>/resultado` de una compra de otro usuario o inexistente | 404 | CA9 |
| API-22 | Cualquier petición | Usa el usuario de la sesión mockeada | FAQ 19 |

---

## 5. Pruebas de sistema (35)

Se ejecutan con un navegador automatizado (Playwright), la app levantada con la pasarela simulada y el mail simulado, base SQLite temporal y reloj fijo.

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| SIS-01 | **Prueba de usuario 1 de la US:** fecha válida, menos de 10 entradas, edades, pase y tarjeta. Se confirma, se pasa a la pasarela simulada, se ingresa la tarjeta de prueba (titular `APRO`) y se pulsa "Pagar y finalizar" | Pasa: vuelve a la app con mensaje de éxito (cantidad y fecha) y mail enviado | US, CA3, CA4 |
| SIS-02 | **Prueba de usuario 2:** confirmar sin forma de pago | Falla: error visible junto al campo y no se redirige a la pasarela | US, CA6 |
| SIS-03 | **Prueba de usuario 3:** intentar elegir un lunes | No se puede seleccionar (día deshabilitado) | US, CA5, FAQ 2 |
| SIS-04 | **Prueba de usuario 4:** intentar cargar 11 entradas | Se bloquea el undécimo visitante o se muestra error | US, CA7 |
| SIS-05 | Compra completa en efectivo | No pasa por la pasarela: pantalla final con instrucciones de boletería y mail enviado | CA6 |
| SIS-06 | Pago rechazado en la pasarela (titular `OTHE`) | Vuelve a la app con mensaje de rechazo, compra `FALLIDA` y sin mail | S12, S13 |
| SIS-07 | Dos compras de 5 entradas para el mismo día, luego una tercera | La tercera se rechaza con mensaje | FAQ 27 |
| SIS-08 | Calendario | Los lunes aparecen deshabilitados | FAQ 2 |
| SIS-09 | Calendario cerca de fin de año | 25/12 y 01/01 deshabilitados | FAQ 1 |
| SIS-10 | Calendario | Fechas pasadas y posteriores a hoy + 1 mes deshabilitadas | CA2, FAQ 25 |
| SIS-11 | Reloj fijo en 17:45 | El día de hoy aparece deshabilitado | FAQ 26 |
| SIS-12 | Agregar y quitar visitantes | El total se recalcula en vivo | CA1 |
| SIS-13 | Cambiar el pase de un visitante | El subtotal y el total se actualizan | CA1, FAQ 6 |
| SIS-14 | Ingresar edades 2, 10 y 65 | Se ve el descuento aplicado en cada subtotal | FAQ 7 |
| SIS-15 | Confirmar con datos inválidos (sin forma de pago, fecha cerrada, 11 entradas) | **No se redirige** a la pasarela y se muestran los errores | CA1, CA4 |
| SIS-16 | Pantalla final de una compra aprobada | Muestra cantidad de entradas y fecha de visita | CA8 |
| SIS-17 | Compra confirmada | Se muestra el modal "Mail enviado a …" con el email del usuario, y se cierra con "Aceptar" | CA3, FAQ 5 |
| SIS-18 | Viewport 375×667 (celular) en el formulario | Sin scroll horizontal y controles táctiles de al menos 44 px | FAQ 24 |
| SIS-19 | Viewport 768×1024 (tablet) | Layout correcto sin elementos cortados | FAQ 24 |
| SIS-20 | Viewport 1280×800 (escritorio) | Layout correcto | FAQ 24 |
| SIS-21 | Estilos de la app | Fuente Lato y paleta del PO aplicadas | FAQ 3 |
| SIS-22 | Doble clic en "Confirmar" | Se crea una sola compra | Diseño |
| SIS-23 | Reiniciar el servidor tras una compra | La compra sigue en la base y cuenta para el límite | Diseño |
| SIS-24 | Errores de validación del formulario | Se muestran junto al campo correspondiente | Usabilidad |
| SIS-25 | Formulario | Campos con etiquetas y navegación completa por teclado | Usabilidad |
| SIS-26 | `manual`: comparar la pasarela simulada con la de Mercado Pago real | Encabezado amarillo, botón azul "Pagar y finalizar", resumen de compra y disposición similares | Diseño |
| SIS-27 | Pantalla de la pasarela | Muestra cantidad de entradas y total iguales a los de la app, sin cupones, envío ni descuentos | CA4 |
| SIS-28 | Formulario de tarjeta de la pasarela con número inválido, tarjeta vencida, código o DNI inválidos | Mensajes junto al campo y no se envía el pago | CA4 |
| SIS-29 | Flecha "volver" de la pasarela | Vuelve a la app, compra `FALLIDA` y cupo liberado ⚠️ | S13 |
| SIS-30 | Pasarela en 375×667 | Sin scroll horizontal y botón "Pagar y finalizar" siempre visible | FAQ 24 |
| SIS-31 | Doble clic en "Pagar y finalizar" | Se procesa un solo pago | Diseño |
| SIS-32 | Titular `CONT` | Vuelve a la app con mensaje de pago pendiente | S12 |
| SIS-33 | Enlace de pasarela inexistente | Página de error | CA4 |
| SIS-34 | Pagar y luego usar "atrás" del navegador | No se puede pagar de nuevo la sesión cerrada | Diseño |
| SIS-35 | Pasarela frente a la app | Identidad visual propia (amarillo y azul, tipografía del sistema), distinta de la app (Lato y paleta del PO): se percibe como página externa | Diseño |

---

## 6. Trazabilidad con los criterios de aceptación

| Criterio de aceptación | Casos que lo cubren |
| --- | --- |
| CA1 Fecha, cantidad, edad y pase | EDA, PAS, CAN-08/09, ORD-02, SIS-12/13 |
| CA2 Fecha actual o futura | FEC-01 a FEC-07, SIS-10 |
| CA3 Mail de confirmación | MAI, MAIL, SRV-01/04/12, SIS-01/05/17 |
| CA4 Pago con tarjeta (pasarela simulada) | PAG-07 a PAG-10, TAR, PSM, SRV-02 a SRV-08, API-05 y API-12 a API-20, SIS-01, SIS-15 y SIS-27 a SIS-34 |
| CA5 Parque abierto | DIA, FEC-10/15, API-07, SIS-03/08/09 |
| CA6 Forma de pago | PAG-01 a PAG-05, API-06, SIS-02/05/15 |
| CA7 Máximo 10 entradas | CAN, API-08, SIS-04/07 |
| CA8 Informar cantidad y fecha | ORD-05 a ORD-07, API-04, SIS-16 |
| CA9 Solo usuarios registrados | USR-01 a USR-03 |

---

## 7. Orden sugerido de ciclos Red-Green-Refactor

De menor a mayor complejidad, empezando por el dominio puro:

1. `PRE`, `EDA`, `PAS`: precios, descuentos y validaciones simples.
2. `DIA`, `FEC`: calendario y reloj inyectable.
3. `CAN`: cantidad y límite acumulado (con repositorio en memoria).
4. `PAG`, `ORD`, `USR`: estados, orden y mensaje final.
5. `MAI`: armado del contenido del mail.
6. `TAR`: validación de la tarjeta (unitarias).
7. `BD`: persistencia real en SQLite.
8. `PSM` y `MAIL`: pasarela simulada y notificador de mail simulado.
9. `SRV`: orquestación de todo el flujo.
10. `API`: capa Flask, incluidas las rutas de la pasarela.
11. `SIS`: frontend responsive, pasarela simulada y pruebas end-to-end.

Los casos demasiado triviales se agrupan en un solo commit, y los parametrizados cuentan como un caso con varias entradas.

---

## 8. Resumen

| Nivel | Casos |
| --- | --- |
| Unitarias | 137 |
| Integración | 72 |
| Sistema | 35 |
| **Total** | **244** |

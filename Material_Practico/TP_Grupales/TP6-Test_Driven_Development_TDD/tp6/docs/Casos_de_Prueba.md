# Casos de prueba: US "Comprar entradas" (EcoHarmony Park)

TP6 - Test Driven Development (TDD) | Grupo 7 | Ingeniería y Calidad de Software 2026

Documento vivo: se actualiza a medida que avanzan los ciclos Red-Green-Refactor y llegan las respuestas del PO.

---

## 1. Convenciones

**Niveles de prueba**

| Nivel | Prefijos | Qué prueba | Dependencias |
| --- | --- | --- | --- |
| Unitaria | `PRE`, `EDA`, `PAS`, `DIA`, `FEC`, `CAN`, `PAG`, `ORD`, `USR`, `MAI` | Reglas de dominio puras | Ninguna (reloj inyectado) |
| Integración | `CSV`, `MP`, `MAIL`, `SRV`, `API` | Componentes conectados entre sí | CSV temporal, pasarela y mail falsos, Flask test client |
| Sistema | `SIS` | Flujo completo desde el navegador | App levantada con fakes, CSV temporal, reloj fijo |

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

**Estados de una compra:** `PENDIENTE_BOLETERIA`, `PENDIENTE_PAGO_ONLINE`, `PAGADA`, `FALLIDA`.

**Dónde están los tests** (`tests/unit/`):

| Archivo | Casos |
| --- | --- |
| `test_precios.py` | PRE-01 a PRE-13 |
| `test_total_compra.py` | PRE-14 a PRE-16 |
| `test_edades.py` | EDA-01 a EDA-08 |
| `test_pases.py` | PAS-01 a PAS-05 |
| `test_visitantes.py` | EDA-09, PAS-06, CAN-09 |
| `test_calendario.py` | DIA-01 a DIA-09 y DIA-11 |
| `test_fechas.py` | FEC-01 a FEC-17 y DIA-10 |

**Estilo:** PEP8, tests con nombres descriptivos en español (`test_<regla>_<condicion>_<resultado>`), un `assert` conceptual por test, parametrización con `pytest.mark.parametrize` para casos similares.

**Pruebas manuales / opcionales:** marcadas con `@pytest.mark.mp_sandbox`, `@pytest.mark.smtp_real` o `manual`. Quedan excluidas de la corrida por defecto.

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
| S8 | Compra con tarjeta de **total $0** (todos ≤ 3 años): no pasa por Mercado Pago, queda `PAGADA` | ¿Cómo se trata una compra sin costo? |
| S9 | El mail se envía al **confirmar** la compra: en efectivo al crearla, con tarjeta al aprobarse el pago | ¿Cuándo debe llegar el mail? |
| S10 | Si el envío del mail falla, **la compra se mantiene** y se informa un aviso | ¿Qué hacer si falla el mail? |

---

## 3. Pruebas unitarias (112)

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

---

## 4. Pruebas de integración (64)

### 4.1 Repositorio CSV (`CSV`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| CSV-01 | Primer guardado con archivo inexistente | Crea el archivo con encabezado | Diseño |
| CSV-02 | Guardar y recuperar por número de orden | La orden recuperada es igual a la guardada | Diseño |
| CSV-03 | Guardar dos compras | Ninguna pisa a la otra | Diseño |
| CSV-04 | Guardar compra con 4 visitantes | Se recuperan los 4, en orden | Diseño |
| CSV-05 | Listar compras por usuario y fecha | Devuelve solo las que coinciden | FAQ 27 |
| CSV-06 | Buscar orden inexistente | Devuelve `None` | Diseño |
| CSV-07 | Actualizar estado de una compra | El cambio persiste al releer | CA4 |
| CSV-08 | Campos con acentos, ñ y comas | Se guardan y leen sin alterarse | Diseño |
| CSV-09 | Archivo con solo encabezado | Lista vacía | Diseño |
| CSV-10 | Reabrir el repositorio | El próximo número de orden continúa la secuencia | Diseño |
| CSV-11 | Sumar entradas por usuario y fecha | Excluye las `FALLIDA` | FAQ 27, S4 |
| CSV-12 | Archivo con columnas faltantes | Error claro, sin datos corruptos | Diseño |
| CSV-13 | Contrato: repositorio CSV y repositorio en memoria | Ambos pasan la misma suite | Diseño |
| CSV-14 | Leer con archivo inexistente | Lista vacía, sin error | Diseño |

### 4.2 Pasarela Mercado Pago (`MP`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| MP-01 | Pasarela falsa: crear preferencia | Devuelve un `init_point` | CA4, FAQ 4 |
| MP-02 | Armado de ítems | Un ítem por visitante con precio ya descontado; los gratuitos se omiten | FAQ 7 |
| MP-03 | Preferencia | `external_reference` igual al número de orden | CA4 |
| MP-04 | Preferencia | `back_urls` de success, failure y pending configuradas | CA4 |
| MP-05 | Adaptador real con SDK simulado | Arma el payload correcto | CA4 |
| MP-06 | Adaptador real: error HTTP de la API | Lanza `PasarelaError` | CA4 |
| MP-07 | Adaptador real sin credenciales | Lanza `ConfiguracionError` con mensaje claro | Diseño |
| MP-08 | Consultar pago con estado `approved` | Resultado `APROBADO` | CA4 |
| MP-09 | Consultar pago con estado `rejected` | Resultado `RECHAZADO` | CA4 |
| MP-10 | Consultar pago con estado `pending` o `in_process` | Resultado `PENDIENTE` | CA4 |
| MP-11 | Consultar `payment_id` inexistente | Error controlado | CA4 |
| MP-12 | El `external_reference` del pago no coincide con la orden | Se rechaza la confirmación | Seguridad |
| MP-13 | Preferencia | Moneda ARS | FAQ 6 |
| MP-14 | `@pytest.mark.mp_sandbox`: crear preferencia real con cuenta de prueba | `init_point` HTTPS válido | CA4 |

### 4.3 Notificador de mail (`MAIL`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| MAIL-01 | Notificador falso | Registra el mail enviado y se puede inspeccionar | CA3 |
| MAIL-02 | SMTP con `smtplib` simulado | Mensaje con From, To y Subject correctos | CA3 |
| MAIL-03 | Mensaje con acentos y ñ | Codificado en UTF-8 sin errores | CA3 |
| MAIL-04 | Falla la conexión SMTP | Lanza `NotificadorError` | S10 |
| MAIL-05 | Credenciales SMTP inválidas | Lanza `NotificadorError` | S10 |
| MAIL-06 | Destinatario con formato inválido | Error sin intentar el envío | CA3 |
| MAIL-07 | Mensaje | Incluye parte de texto plano y parte HTML | CA3 |
| MAIL-08 | `@pytest.mark.smtp_real`: envío a una casilla de pruebas | Mail recibido | CA3 |

### 4.4 Servicio de compra (`SRV`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| SRV-01 | Compra en efectivo válida | Guarda `PENDIENTE_BOLETERIA` y envía mail ⚠️ | S3, S9 |
| SRV-02 | Compra con tarjeta válida | Guarda `PENDIENTE_PAGO_ONLINE`, devuelve URL de pago, aún sin mail ⚠️ | CA4, S9 |
| SRV-03 | Retorno de pago aprobado | Orden `PAGADA` y mail enviado | CA3, CA4 |
| SRV-04 | Retorno de pago rechazado | Orden `FALLIDA`, sin mail ⚠️ | S4 |
| SRV-05 | Retorno de pago pendiente | Sin cambios y sin mail | CA4 |
| SRV-06 | Retorno aprobado repetido (doble callback) | Idempotente: un solo mail | Diseño |
| SRV-07 | Con CSV real: dos compras de 5 y una de 1 | Las dos primeras pasan, la tercera se rechaza | FAQ 27 |
| SRV-08 | Validación fallida | El CSV queda sin cambios | CA1 |
| SRV-09 | Compra `FALLIDA` previa de 10 entradas | Se puede volver a comprar 10 ⚠️ | S4 |
| SRV-10 | Falla el envío del mail | La compra se mantiene y se informa aviso ⚠️ | S10 |
| SRV-11 | Falla la pasarela al crear la preferencia | No queda orden pendiente y se devuelve error claro | CA4 |
| SRV-12 | Tarjeta con total $0 | `PAGADA`, mail enviado, sin llamar a la pasarela ⚠️ | S8 |

### 4.5 API web con Flask (`API`)

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| API-01 | `GET /` | 200 con el formulario de compra | CA1 |
| API-02 | `GET /api/dias-no-disponibles` | JSON con lunes y feriados del rango | FAQ 2 |
| API-03 | `GET /api/precios` | JSON con precios y reglas de descuento | FAQ 6, 7 |
| API-04 | `POST /api/compras` en efectivo | 201 con número de orden, cantidad y fecha | CA8 |
| API-05 | `POST /api/compras` con tarjeta | 201 con `url_pago` | CA4 |
| API-06 | `POST` sin forma de pago | 400 con mensaje | CA6 |
| API-07 | `POST` con fecha de un lunes | 400 con mensaje | CA5 |
| API-08 | `POST` con 11 entradas | 400 con mensaje | CA7 |
| API-09 | `POST` con un visitante sin edad | 400 que identifica al visitante | CA1 |
| API-10 | `POST` con JSON inválido | 400 | Diseño |
| API-11 | Cualquier error de validación | Formato consistente `{"errores": [{"campo", "mensaje"}]}` | Diseño |
| API-12 | `GET /pago/retorno?status=approved&payment_id=...` | Pantalla de resultado y orden `PAGADA` | CA4 |
| API-13 | Retorno con `payment_id` inexistente | Pantalla de error controlada | CA4 |
| API-14 | `GET /api/compras/<id>/estado` | Devuelve el estado actual | CA4 |
| API-15 | Estado de una orden inexistente | 404 | Diseño |
| API-16 | Cualquier petición | Usa el usuario de la sesión mockeada | FAQ 19 |

---

## 5. Pruebas de sistema (26)

Se ejecutan con un navegador automatizado (Playwright), la app levantada con pasarela y mail falsos, CSV temporal y reloj fijo.

| ID | Caso | Resultado esperado | Origen |
| --- | --- | --- | --- |
| SIS-01 | **Prueba de usuario 1 de la US:** fecha válida, menos de 10 entradas, edades, pase, tarjeta por Mercado Pago | Pasa: pago simulado, mail enviado y pantalla final | US, CA3, CA4 |
| SIS-02 | **Prueba de usuario 2:** confirmar sin forma de pago | Falla: error visible junto al campo | US, CA6 |
| SIS-03 | **Prueba de usuario 3:** intentar elegir un lunes | No se puede seleccionar (día deshabilitado) | US, CA5, FAQ 2 |
| SIS-04 | **Prueba de usuario 4:** intentar cargar 11 entradas | Se bloquea el undécimo visitante o se muestra error | US, CA7 |
| SIS-05 | Compra completa en efectivo | Pantalla final con instrucciones de boletería y mail enviado | CA6 |
| SIS-06 | Pago rechazado en Mercado Pago | Mensaje claro, orden `FALLIDA`, sin mail | S4 |
| SIS-07 | Dos compras de 5 entradas para el mismo día, luego una tercera | La tercera se rechaza con mensaje | FAQ 27 |
| SIS-08 | Calendario | Los lunes aparecen deshabilitados | FAQ 2 |
| SIS-09 | Calendario cerca de fin de año | 25/12 y 01/01 deshabilitados | FAQ 1 |
| SIS-10 | Calendario | Fechas pasadas y posteriores a hoy + 1 mes deshabilitadas | CA2, FAQ 25 |
| SIS-11 | Reloj fijo en 17:45 | El día de hoy aparece deshabilitado | FAQ 26 |
| SIS-12 | Agregar y quitar visitantes | El total se recalcula en vivo | CA1 |
| SIS-13 | Cambiar el pase de un visitante | El subtotal y el total se actualizan | CA1, FAQ 6 |
| SIS-14 | Ingresar edades 2, 10 y 65 | Se ve el descuento aplicado en cada subtotal | FAQ 7 |
| SIS-15 | Pago con tarjeta | Mercado Pago abre en pestaña nueva y la pestaña original se actualiza al resultado | CA4 |
| SIS-16 | Pantalla final | Muestra cantidad de entradas y fecha de visita | CA8 |
| SIS-17 | Falla el mail | La compra se completa y se muestra un aviso ⚠️ | S10 |
| SIS-18 | Viewport 375×667 (celular) | Sin scroll horizontal y controles táctiles de al menos 44 px | FAQ 24 |
| SIS-19 | Viewport 768×1024 (tablet) | Layout correcto sin elementos cortados | FAQ 24 |
| SIS-20 | Viewport 1280×800 (escritorio) | Layout correcto | FAQ 24 |
| SIS-21 | Estilos | Fuente Lato y paleta del PO aplicadas | FAQ 3 |
| SIS-22 | Doble clic en "Confirmar" | Se crea una sola compra | Diseño |
| SIS-23 | Reiniciar el servidor tras una compra | La compra sigue en el CSV y cuenta para el límite | Diseño |
| SIS-24 | Errores de validación | Se muestran junto al campo correspondiente | Usabilidad |
| SIS-25 | Formulario | Campos con etiquetas y navegación completa por teclado | Usabilidad |
| SIS-26 | `manual`: flujo completo con Mercado Pago sandbox y mail reales | Pago de prueba aprobado y mail recibido | CA3, CA4 |

---

## 6. Trazabilidad con los criterios de aceptación

| Criterio de aceptación | Casos que lo cubren |
| --- | --- |
| CA1 Fecha, cantidad, edad y pase | EDA, PAS, CAN-08/09, ORD-02, SIS-12/13 |
| CA2 Fecha actual o futura | FEC-01 a FEC-07, SIS-10 |
| CA3 Mail de confirmación | MAI, MAIL, SRV-01/03, SIS-01/05/26 |
| CA4 Redirección a Mercado Pago | PAG-07 a PAG-10, MP, SRV-02 a SRV-06, API-05/12, SIS-01/15 |
| CA5 Parque abierto | DIA, FEC-10/15, API-07, SIS-03/08/09 |
| CA6 Forma de pago | PAG-01 a PAG-05, API-06, SIS-02/05 |
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
6. `CSV`: persistencia real.
7. `MP` y `MAIL`: adaptadores falsos primero, reales después.
8. `SRV`: orquestación de todo el flujo.
9. `API`: capa Flask.
10. `SIS`: frontend responsive y pruebas end-to-end.

Los casos demasiado triviales se agrupan en un solo commit, y los parametrizados cuentan como un caso con varias entradas.

---

## 8. Resumen

| Nivel | Casos |
| --- | --- |
| Unitarias | 112 |
| Integración | 64 |
| Sistema | 26 |
| **Total** | **202** |

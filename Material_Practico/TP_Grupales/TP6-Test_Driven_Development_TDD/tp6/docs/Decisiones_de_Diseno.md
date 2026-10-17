# Decisiones de diseño: US "Comprar entradas"

TP6 - TDD | Grupo 7. Documento vivo: se completa a medida que avanzan los ciclos.

| ID | Decisión | Motivo |
| --- | --- | --- |
| D1 | Backend en Python 3.11+ con Flask | Simple y suficiente para una US con persistencia en SQLite |
| D2 | Tests con pytest | Parametrización y fixtures, menos código repetitivo |
| D3 | Dominio puro separado de Flask y de la base de datos (`src/ecoharmony/dominio`) | El TDD se concentra en reglas de negocio sin I/O |
| D4 | Persistencia detrás de una interfaz de repositorio | Se puede probar con repositorio en memoria y cambiar la base de datos sin tocar el dominio |
| D5 | Reloj inyectable | Las reglas dependen de "ahora" (17:30, un mes): los tests no deben depender de la fecha real |
| D6 | Pasarela de pago y mail detrás de interfaces; hoy ambos son simulados (D28 y D36) y se podría sumar un adaptador real sin tocar el dominio | Los tests no llaman a internet ni dependen de servicios externos |
| D7 | Nombres de dominio en español, PEP8 verificado con flake8 (79 columnas) | Coherencia con el dominio explicado por el PO |
| D8 | Montos como enteros en pesos | Los precios del parque son enteros; evita errores de redondeo de `float` |
| D9 | Commits: `feat:` para Red y Green (con la fase en el mensaje) y `refactor:` para Refactor | Respeta el nombrado de commits del README del repositorio |
| D10 | Las edades límite de los descuentos son constantes con nombre y no números sueltos | El código explica la regla del PO y un cambio de edad se hace en un solo lugar |
| D11 | El descuento se calcula con `precio // 2` | Los precios son enteros y pares, así que la división entera es exacta; si cambiaran a un valor impar habría que revisarlo |
| D12 | `Visitante` es un `dataclass` inmutable (`frozen=True`) con edad y pase | Un visitante es un valor: no cambia después de creado, y se compara por contenido |
| D13 | La tabla de precios se recibe como parámetro, con la tabla oficial como valor por defecto | Los tests pueden probar otros precios sin tocar el código, y la tabla por defecto nunca se modifica |
| D14 | Las validaciones lanzan `ErrorDeValidacion` con `campo` y `mensaje` | La API puede mostrar cada error junto al campo del formulario |
| D15 | La posición del visitante en los errores es 1-based (`visitantes.2.edad`) | Coincide con cómo lo ve la persona que carga el formulario |
| D16 | La hora actual entra como `ahora` (datetime con zona horaria) y se convierte a UTC-3 fijo | Argentina no tiene horario de verano, y evita depender de la base de zonas horarias, que en Windows requiere instalar un paquete extra |
| D17 | La fecha de visita acepta `date` o texto ISO (AAAA-MM-DD) | Es el formato que envía un campo de fecha o un datepicker |
| D18 | Una sola función (`motivo_no_disponible`) alimenta la validación y la lista de días deshabilitados del calendario | El frontend y el backend no pueden contradecirse |
| D19 | Edad máxima de 120 años como constante | Supuesto S6, pendiente de confirmar con el PO |
| D20 | Para acelerar, los tests se escriben por grupo: un commit RED con todos los tests del grupo y un commit GREEN con el código | Se pierde el ciclo test por test, pero se conserva la evidencia Red-Green por grupo |
| D21 | `crear_compra` acumula todos los errores y los lanza juntos en `ErroresDeValidacion`; la falta de sesión se rechaza de inmediato | El formulario puede marcar todos los campos incorrectos de una vez |
| D22 | Los estados de la compra son un enum y las transiciones están en una función pura (`aplicar_resultado_de_pago`); una transición inválida deja el estado como está | Es idempotente si el resultado del pago llega más de una vez (doble clic en "Pagar y finalizar" o reenvío desde el navegador) |
| D23 | `RepositorioEnMemoria` define el contrato de repositorio (`siguiente_numero_de_orden`, `guardar`, `buscar`, `compras_de`) | El repositorio SQLite tendrá que cumplir el mismo contrato (caso BD-12) |
| D24 | El límite de 10 cuenta las entradas de las compras no fallidas del usuario para esa fecha | Supuestos S2, S3 y S4 |
| D25 | La conversión a entero se extrajo a `conversiones.py` (refactor) | Evita repetir la lógica en edad y cantidad |
| D26 | El mail es un objeto `Mail` (destinatario, asunto, cuerpo) armado en el dominio; enviarlo es tarea de un adaptador | El dominio no depende de SMTP y se puede probar sin enviar nada |
| D27 | `Compra` es inmutable (`frozen=True`) | Un cambio de estado produce una compra nueva, sin modificar la original |
| D28 | Se simula la pasarela de Mercado Pago con una página propia en vez de integrarla | Evita credenciales y servicios externos, y la FAQ 4 autoriza simular el pago |
| D29 | Cada pago con tarjeta tiene una sesión de pago identificada por un token aleatorio | La pasarela no necesita conocer al usuario y nadie puede adivinar otra sesión |
| D30 | El resultado del pago simulado se elige con el nombre del titular, como en las tarjetas de prueba de Mercado Pago | Permite demostrar aprobaciones y rechazos sin interfaces extra |
| D31 | Todas las validaciones de la compra se hacen antes de crear la sesión de pago; la pasarela solo valida la tarjeta | El visitante no llega a pagar una compra inválida |
| D32 | Los datos de la tarjeta nunca se persisten: solo se conservan marca y últimos 4 dígitos | Seguridad básica, aunque el pago sea simulado |
| D33 | El número de tarjeta se valida con largo de 13 a 19 dígitos y el algoritmo de Luhn; la marca se detecta por el primer dígito (4 Visa, 5 Mastercard, otra "Tarjeta") | Son las reglas que usan las pasarelas reales y detectan errores de tipeo sin consultar ningún servicio |
| D34 | El titular acepta letras (con acentos y ñ) separadas por espacios, apóstrofos o guiones | Admite nombres como "O'Connor" o "Ana-Lía" y rechaza números o símbolos |
| D35 | La persistencia usa SQLite (`sqlite3` de la biblioteca estándar) en vez de archivos CSV | No requiere instalar nada, resuelve con consultas el límite de 10 por fecha y con transacciones el doble clic y los guardados a medias; la consigna no exige CSV |
| D36 | El mail de confirmación se simula: un notificador registra el mail y la app muestra un modal "Mail enviado a …" | La FAQ 5 lo permite; evita credenciales y servidores SMTP, y la interfaz `Notificador` deja abierta la opción de un envío real |
| D37 | `RepositorioSQLite` abre una conexión por operación dentro de una transacción, y el número de orden sale de una tabla `secuencia` | Si algo falla no queda una compra a medias, y dos pedidos simultáneos nunca reciben el mismo número |
| D38 | Las sesiones de pago viven en memoria dentro de `PasarelaSimulada` y no en la base de datos | Simulan un servicio externo: la app solo guarda la compra y su estado; si se reinicia el servidor, una sesión sin pagar se pierde y hay que hacer una compra nueva |
| D39 | `ServicioDeCompra` recibe el repositorio, la pasarela y el notificador por constructor y devuelve un `ResultadoDeCompra` (compra, URL de pago, mail enviado, mensaje final o motivo de rechazo) | Se prueba con implementaciones en memoria o SQLite sin cambiar nada, y la capa Flask solo traduce ese resultado a pantallas |
| D40 | Si se intenta pagar una sesión ya resuelta, el servicio devuelve el resultado anterior en vez de un error | Un doble clic o una recarga muestran la misma pantalla de resultado, sin cobrar ni enviar el mail dos veces |
| D41 | `crear_app` recibe el repositorio, la pasarela, el notificador, el reloj y el usuario; sin argumentos usa SQLite en `data/ecoharmony.db` y la hora real | Los tests levantan la app con datos en memoria y reloj fijo, y `run.py` la levanta de verdad sin cambiar código |
| D42 | La compra se envía como JSON a `/api/compras`; la pasarela usa formularios HTML comunes con redirecciones | El formulario de compra necesita recalcular el total en vivo (JavaScript), y la pasarela imita una página externa que vuelve a la app al terminar |

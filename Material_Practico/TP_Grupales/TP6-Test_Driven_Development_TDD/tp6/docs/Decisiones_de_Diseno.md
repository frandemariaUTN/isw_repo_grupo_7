# Decisiones de diseño: US "Comprar entradas"

TP6 - TDD | Grupo 7. Documento vivo: se completa a medida que avanzan los ciclos.

| ID | Decisión | Motivo |
| --- | --- | --- |
| D1 | Backend en Python 3.11+ con Flask | Simple y suficiente para una US con CSV |
| D2 | Tests con pytest | Parametrización y fixtures, menos código repetitivo |
| D3 | Dominio puro separado de Flask y del CSV (`src/ecoharmony/dominio`) | El TDD se concentra en reglas de negocio sin I/O |
| D4 | Persistencia detrás de una interfaz de repositorio | Se puede probar con repositorio en memoria y cambiar el CSV sin tocar el dominio |
| D5 | Reloj inyectable | Las reglas dependen de "ahora" (17:30, un mes): los tests no deben depender de la fecha real |
| D6 | Pasarela de pago y mail detrás de interfaces, con adaptador real y falso | Los tests no llaman a internet; lo real se prueba aparte |
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
| D22 | Los estados de la compra son un enum y las transiciones están en una función pura (`aplicar_resultado_de_pago`); una transición inválida deja el estado como está | Es idempotente ante avisos repetidos de Mercado Pago |
| D23 | `RepositorioEnMemoria` define el contrato de repositorio (`siguiente_numero_de_orden`, `guardar`, `buscar`, `compras_de`) | El repositorio CSV tendrá que cumplir el mismo contrato (caso CSV-13) |
| D24 | El límite de 10 cuenta las entradas de las compras no fallidas del usuario para esa fecha | Supuestos S2, S3 y S4 |
| D25 | La conversión a entero se extrajo a `conversiones.py` (refactor) | Evita repetir la lógica en edad y cantidad |
| D26 | El mail es un objeto `Mail` (destinatario, asunto, cuerpo) armado en el dominio; enviarlo es tarea de un adaptador | El dominio no depende de SMTP y se puede probar sin enviar nada |
| D27 | `Compra` es inmutable (`frozen=True`) | Un cambio de estado produce una compra nueva, sin modificar la original |
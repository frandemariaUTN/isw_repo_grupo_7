# Decisiones de diseño por tema

TP6 - TDD | Grupo 7 | US "Comprar entradas" de EcoHarmony Park.

Resumen de las decisiones tomadas, agrupadas por tema y con su justificación. Cada punto indica de dónde sale:

- **CA:** criterio de aceptación de la US.
- **FAQ n:** respuesta de los PO en el documento de FAQs.
- **S n:** supuesto consultado con el PO (S1 a S10, respondidos el 20/10/2026) o decisión del grupo sobre la pasarela (S11 a S15). Están en `Casos_de_Prueba.md`.
- **D n:** fila del registro completo en `Decisiones_de_Diseno.md`.

## 1. Tecnología y arquitectura

- **Python con Flask y pytest** (D1, D2). Flask alcanza para una sola US con una API chica; pytest permite parametrizar casos límite (edades, fechas) sin repetir código.
- **Dominio puro, separado de la web, la base y el mail** (D3, D4, D6). Las reglas de negocio están en `dominio/` y no usan Flask, SQLite ni internet. Así el TDD se concentra en las reglas, y cada pieza externa (base, pasarela, mail) se reemplaza por una versión en memoria en los tests.
- **Las dependencias se inyectan** (D39, D41). El servicio de compra y la app reciben el repositorio, la pasarela, el notificador, el reloj y el usuario. Los tests arman la app con datos en memoria y `run.py` la arma con los reales, sin cambiar código.
- **Nombres en español y PEP8 con flake8** (D7). El código usa el mismo vocabulario que el PO (visitante, pase, boletería).
- **Usuario de sesión fijo ("Salva")** (D52). La FAQ 19 dice que el login no es parte de la US y se puede mockear. Así se cumple el CA "solo usuarios registrados" sin construir un registro.

## 2. Forma de trabajo con TDD

- **Ciclo por grupos de casos** (D20). Un commit RED con todos los tests del grupo (por ejemplo PRE, precios) y un commit GREEN con el código. Se pierde el detalle test por test, pero queda la evidencia Red-Green de cada grupo en el historial: antes de cada commit RED se verifica que los tests fallan por el motivo esperado, y en el GREEN pasan con toda la suite en verde. Los refactors van en commits aparte.
- **Commits con prefijos del README** (D9): `feat: [RED]`, `feat: [GREEN]`, `refactor:`, `docs:`.
- **Tres niveles de prueba.** Unitarias para el dominio, de integración para las piezas conectadas (SQLite, pasarela, mail, API) y de sistema en el navegador. Cada test lleva el ID de su caso en `Casos_de_Prueba.md`.

## 3. Precios y descuentos

- **Precios y edades límite como constantes con nombre** (D10). Común $10.000 y VIP $20.000 (FAQ 6). Hasta 3 años gratis; hasta 15 y desde 60, 50% (FAQ 7). Si el PO cambia un valor, se cambia en un solo lugar.
- **Montos como enteros en pesos** (D8, D11). Los precios no tienen centavos, y así se evitan errores de redondeo. El 50% se calcula con división entera, que es exacta porque los precios son pares.
- **La tabla de precios entra por parámetro** (D13), con la oficial por defecto. Los tests pueden probar otros precios sin tocar el código.
- **VIP y Común solo difieren en el precio** (FAQ 21). El pase se elige por visitante y se pueden combinar en una compra (S1).
- **Edad válida de 0 a 120** (D19). El PO dijo que no hay límite, pero que se puede usar 120 (S6).

## 4. Fechas y calendario

- **El reloj se inyecta** (D5, D16). Las reglas dependen de la hora actual (17:30, un mes adelante), así que los tests usan un reloj fijo y nunca la fecha real. Se usa UTC-3 fijo porque Argentina no tiene horario de verano.
- **Reglas de apertura:**
  - El parque cierra los lunes, el 25/12 y el 1/1 (FAQ 1, CA5).
  - Se compra hasta un mes adelante (FAQ 25).
  - Para el mismo día, la compra se acepta hasta las 17:30 (FAQ 26), aunque sea antes de la apertura (S7).
- **Una sola función decide si un día está disponible** (D18). La misma regla valida la compra en el backend y deshabilita los días en el calendario, así que la pantalla y el servidor no pueden contradecirse.
- **Calendario propio** (D45). La FAQ 2 pide que los días cerrados no se puedan elegir, y el selector de fecha nativo del navegador no permite deshabilitar días sueltos.

## 5. Cantidad de entradas (límite de 10)

- **Máximo 10 entradas por usuario y por fecha, sumando compras** (D24, FAQ 27, CA7).
  - Las entradas gratuitas cuentan (S2).
  - Las compras pendientes cuentan (S3).
  - Las compras fallidas no cuentan, porque liberan el cupo (S4).
- **Pendiente:** en el mail del 20/10/2026 el PO habló de "10 por transacción", lo que contradice la FAQ 27. Hasta que lo aclare, se mantiene la FAQ 27.

## 6. Validaciones y errores

- **Se validan todos los datos juntos** (D14, D21). Cada error indica el campo afectado (`fecha_visita`, `visitantes.2.edad`, etc.), así el formulario marca todos los errores de una vez y junto a cada campo. La posición del visitante empieza en 1, como la ve la persona (D15).
- **Se valida todo antes de pagar** (D31). La fecha, la cantidad, las edades y el límite de 10 se controlan antes de abrir la pasarela, así el visitante no llega a pagar una compra inválida.
- **Objetos inmutables** (D12, D27). `Visitante` y `Compra` no cambian después de creados: un cambio de estado produce una compra nueva, y eso hace el código más predecible.

## 7. Pago y pasarela simulada

- **Pasarela de Mercado Pago simulada** (D28). El CA4 pide redirigir a Mercado Pago, y la FAQ 4 autoriza simularlo. Se hizo una página propia con su aspecto, sin credenciales ni servicios externos.
- **Formas de pago y estados** (D22, CA6):
  - En efectivo, la compra queda pendiente de pago en boletería (S3).
  - Con tarjeta, queda pendiente hasta que se resuelve el pago, aunque el total sea $0 (D50, S8, pedido del PO).
  - Las transiciones de estado están en una función pura: si el resultado del pago llega dos veces, el estado no cambia.
- **Sesión de pago con un código aleatorio (token)** (D29, D38). La pasarela no necesita saber quién es el usuario y nadie puede adivinar la sesión de otro. Las sesiones viven en memoria, como si fueran de un servicio externo.
- **El resultado se elige con el nombre del titular** (D30, S12), como en las tarjetas de prueba de Mercado Pago: `OTHE` rechaza, `CONT` queda pendiente y cualquier otro nombre válido aprueba. Así se pueden demostrar los rechazos sin pantallas extra.
- **Rechazo o cancelación** (D51, S4, S13). La compra pasa a fallida, no se reintenta y se informa con un pop-up, como pidió el PO.
- **Doble clic seguro** (D40). Si se paga una sesión ya resuelta, se muestra el resultado anterior sin cobrar ni enviar el mail dos veces.

## 8. Tarjeta y seguridad

- **Los datos de la tarjeta nunca se guardan** (D32, S15). Solo se conservan la marca y los últimos 4 dígitos, aunque el pago sea simulado.
- **Número de 16 dígitos con control de Luhn** (D33). Es el largo de Visa y Mastercard, las marcas que muestra la pasarela. Luhn detecta errores de tipeo sin consultar ningún servicio.
- **Titular solo con letras** (D34): acepta acentos, ñ, espacios, apóstrofos y guiones ("O'Connor", "Ana-Lía").
- **Documento: solo DNI de 7 u 8 dígitos** (FAQ 32).

## 9. Base de datos

- **SQLite en vez de archivos CSV** (D35). Viene con Python, no hay que instalar nada, y la consigna no exige CSV. Con consultas resuelve el límite de 10 por fecha.
- **Una transacción por operación y número de orden desde una tabla propia** (D37). Si algo falla no queda una compra a medias, y dos compras simultáneas nunca reciben el mismo número (FAQ 18).
- **Mismo contrato que el repositorio en memoria** (D23). Las mismas pruebas se corren contra los dos, y así se garantiza que son intercambiables.

## 10. Mail de confirmación y QR

- **El mail se envía de verdad por Gmail (SMTP)** (D36, D49).
  - El CA3 pide un mail de confirmación, y la prueba de usuario 1 pide verificar que llegue.
  - La FAQ 5 permitía simularlo con un modal, pero el grupo decidió enviarlo de verdad.
  - La cuenta se configura en un archivo `.env` que nunca se sube a git. Sin `.env`, el mail se simula, y eso usan los tests.
- **Cuándo se envía** (S9). En efectivo, al crear la compra; con tarjeta, cuando se aprueba el pago.
- **Contenido** (FAQ 18): número de orden, fecha, detalle de visitantes con subtotales, total y QR de acceso. En efectivo, recuerda abonar en boletería.
- **QR con texto legible** (D47, S5): orden, fecha, total y entradas agrupadas por pase y edad (por ejemplo "2 VIP menor", "5 Común adulto"). El dominio arma el texto y el notificador lo dibuja como imagen dentro del mail y como adjunto, así el dominio no depende de librerías externas.
- **Si el mail falla, la compra se mantiene** (D49, S10). La compra ya está registrada, así que se muestra un aviso en lugar de perderla.
- **El mail lo arma el dominio y lo envía un adaptador** (D26). Su contenido se prueba sin enviar nada.

## 11. Frontend

- **Web responsive, pensada primero para celular** (D43, FAQ 24). El PO pide una app mobile y acepta una web responsive. Se diseñó para un ancho de 390 px (un celular común) y se adapta a la computadora.
- **HTML, CSS y JavaScript sin frameworks** (D43). Alcanza para una sola pantalla de compra, no agrega dependencias y Flask la sirve directo.
- **La compra se envía como JSON y la pasarela usa formularios** (D42, S11). La pantalla de compra recalcula el total en vivo con JavaScript. La pasarela se abre en la misma pestaña y vuelve a la app, como una página externa real.
- **Paleta y fuente del PO** (D44, FAQ 3). Usa los colores `#386641`, `#6A994E`, `#A7C957`, `#F2E8CF` y `#BC4749` y la fuente Lato.
  - Una rana de ojos rojos como mascota y un logo aprobado por el PO (FAQ 17).
  - Las animaciones son cortas y se desactivan si el sistema pide reducir el movimiento.
- **Al finalizar se informan la cantidad de entradas y la fecha** (CA8), junto con el número de orden y la dirección a la que se envió el mail.

## 12. Pruebas de sistema

- **Playwright con el Edge instalado** (D46). No hay que descargar otro navegador. Se fijó la versión 1.50 porque las más nuevas exceden el largo de ruta que permite Windows.
- **Solo 8 casos.** Cubren las 4 pruebas de usuario de la US y los flujos principales; el resto ya está cubierto por las pruebas unitarias y de integración, que son más rápidas.

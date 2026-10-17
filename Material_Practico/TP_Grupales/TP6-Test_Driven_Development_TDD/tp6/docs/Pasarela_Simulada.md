# Pasarela de pago simulada

TP6 - TDD | Grupo 7. Diseño de la página que simula la pasarela de Mercado Pago para la compra de entradas con tarjeta.

> La FAQ 4 autoriza simular la redirección a Mercado Pago. Esta pasarela es una página **propia**, con aspecto similar al de Mercado Pago, que no se conecta con ningún servicio externo ni realiza cobros reales.

---

## 1. Objetivo

Cuando el visitante elige pagar con tarjeta, la app lo lleva a una página aparte que imita una pasarela de pago: muestra el monto ya calculado, pide los datos de la tarjeta y, al pagar, devuelve al visitante a la app con el resultado. Si el pago se aprueba, el visitante ya dispone de sus entradas.

**Lo que muestra:** resumen de la compra (cantidad de entradas y total), formulario de tarjeta y botón "Pagar y finalizar".

**Lo que no incluye** (aparece en la pasarela real pero queda afuera): descuentos, cupones, datos de envío o ubicación, suscripciones, combinar medios de pago, dinero disponible y cuotas.

---

## 2. Flujo

```text
App (formulario)                     Pasarela simulada                    App (resultado)
────────────────                     ─────────────────                    ───────────────
1. El visitante completa
   fecha, cantidad, edades,
   pases y forma de pago.
2. Pulsa "Confirmar".
3. El backend valida TODO.
   ├─ con errores: se muestran
   │  en el formulario y NO se
   │  redirige.
   ├─ efectivo: compra pendiente
   │  en boletería, mail y
   │  mensaje final.
   └─ tarjeta: se crea la compra
      pendiente de pago y una
      sesión de pago con token.
4. Redirección ─────────────────────► 5. Pantalla "Finalizá tu compra":
                                         resumen + formulario de tarjeta.
                                      6. El visitante completa la tarjeta
                                         y pulsa "Pagar y finalizar".
                                         ├─ datos inválidos: errores en
                                         │  la misma pantalla, sin cerrar
                                         │  la sesión.
                                         ├─ aprobado ──────────────────► 7a. Compra pagada, mail y
                                         │                                   "Compraste N entradas
                                         │                                   para el dd/mm/aaaa."
                                         ├─ rechazado ─────────────────► 7b. Compra fallida y mensaje
                                         │                                   con el motivo.
                                         ├─ pendiente ─────────────────► 7c. Mensaje de pago pendiente.
                                         └─ flecha "volver" ───────────► 7d. Compra fallida (cancelada),
                                                                             cupo liberado.
```

**Regla clave:** todas las validaciones de la compra (fecha, cantidad, edades, pases y forma de pago, más el límite de 10 entradas por fecha) se hacen **antes** de crear la sesión de pago. La pasarela solo valida la tarjeta.

---

## 3. Rutas

| Ruta | Método | Qué hace |
| --- | --- | --- |
| `/api/compras` | POST | Valida y crea la compra. Con tarjeta devuelve `url_pago` (`/pasarela/<token>`) |
| `/pasarela/<token>` | GET | Muestra la pantalla de pago de esa sesión |
| `/pasarela/<token>/pagar` | POST | Valida la tarjeta, resuelve el pago y redirige al resultado |
| `/pasarela/<token>/cancelar` | POST | Cancela la sesión y redirige a la app |
| `/compras/<n>/resultado` | GET | Pantalla de éxito, rechazo o pago pendiente |

La redirección ocurre en **la misma pestaña** (decisión S11), lo que además es más cómodo en celulares.

---

## 4. Pantalla de la pasarela

Diseño tomado de la captura de la pasarela de Mercado Pago, adaptado a una sola opción de pago (tarjeta). Pensada primero para celular (375 px de ancho).

### Disposición, de arriba hacia abajo

1. **Encabezado amarillo** con flecha "volver" a la izquierda y el título **"Finalizá tu compra"**.
2. **Medios de pago:** una única opción, "Tarjeta de crédito o débito", seleccionada, con el formulario debajo:
   - Número de tarjeta, que se muestra en grupos de 4 y con el ícono de la marca detectada (Visa o Mastercard).
   - Nombre y apellido del titular, tal como figura en la tarjeta.
   - Vencimiento (`MM/AA`) y código de seguridad, en la misma fila.
   - DNI del titular (FAQ 32: solo DNI).
3. **Resumen de compra:** una línea "Entradas EcoHarmony Park x N" con su monto, y debajo **Total** en grande (`$ 35.000` con los centavos `,00` en superíndice, como en la captura).
4. **Texto legal chico:** "Simulación con fines académicos. No se realiza ningún cobro real."
5. **Botón fijo abajo:** "Pagar y finalizar", ancho completo. Mientras se procesa pasa a "Procesando..." y se deshabilita.

### Estilo (muestreado de la captura)

| Elemento | Valor |
| --- | --- |
| Encabezado | Amarillo `#FFE600` (en la captura salió `#FDE700` por la compresión de la imagen) |
| Botón y enlaces | Azul `#3483FA` (en la captura `#3384F9`) |
| Fondo | Blanco |
| Separadores | Gris muy claro `#F2F2F2` |
| Texto | Gris oscuro; secundario en gris medio |
| Tipografía | La del sistema (`-apple-system, "Segoe UI", Roboto, Arial, sans-serif`) |
| Botón | Bordes redondeados (unos 8 px), alto de 48 px o más |

La pasarela usa su identidad visual propia y **no** la de la app (Lato y la paleta del PO), para que se perciba como una página externa (caso SIS-35). No se usa el logo oficial de Mercado Pago: alcanza con el texto del encabezado.

### Mensajes de error junto a cada campo

| Campo | Ejemplo de mensaje |
| --- | --- |
| Número | "Revisá el número de tarjeta." |
| Vencimiento | "La tarjeta está vencida." / "Ingresá el vencimiento como MM/AA." |
| Código de seguridad | "Ingresá los 3 dígitos del código de seguridad." |
| Titular | "Ingresá el nombre tal como figura en la tarjeta." |
| DNI | "Ingresá un DNI de 7 u 8 dígitos." |

---

## 5. Resultado del pago

El resultado se elige con el **nombre del titular**, igual que en las tarjetas de prueba de Mercado Pago. Cualquier otro nombre con una tarjeta válida se aprueba, así que una compra normal funciona sin conocer ningún código.

| Titular | Resultado | Mensaje en la app |
| --- | --- | --- |
| Cualquier nombre válido, o `APRO` | Aprobado | "Compraste N entradas para el dd/mm/aaaa." |
| `OTHE` | Rechazado por error general | "El pago fue rechazado." |
| `FUND` | Rechazado por fondos insuficientes | "La tarjeta no tiene fondos suficientes." |
| `SECU` | Rechazado por código de seguridad | "El código de seguridad es inválido." |
| `EXPI` | Rechazado por vencimiento | "Hay un problema con la fecha de vencimiento." |
| `CONT` | Pendiente | "Tu pago está pendiente de acreditación." |

Tras un rechazo o una cancelación, la compra pasa a `FALLIDA`, el cupo se libera y el visitante vuelve a la app para intentar una compra nueva (supuestos S4 y S13).

### Datos de prueba

| Dato | Valor |
| --- | --- |
| Tarjeta Mastercard | `5031 7557 3453 0604` |
| Tarjeta Visa | `4509 9535 6623 3704` |
| Código de seguridad | `123` |
| Vencimiento | `11/30` |
| Titular | `APRO` |
| DNI | `12345678` |

---

## 6. Seguridad y diseño

- **Los datos de la tarjeta nunca se guardan:** ni en la base de datos ni en logs. Tras validarlos solo se conservan la marca y los últimos 4 dígitos (casos TAR-25 y PSM-19).
- **La sesión de pago se identifica con un token aleatorio** de al menos 32 caracteres, imposible de adivinar (PSM-03).
- **Una sesión se procesa una sola vez:** reintentar el pago o recargar la página no duplica el pago ni el mail (PSM-13, SRV-07, API-18, SIS-31, SIS-34).
- **Dominio puro:** la validación de tarjeta (`tarjetas.py`) y la lógica de la sesión de pago (`pasarela.py`) no dependen de Flask, así que se prueban sin servidor.

---

## 7. Decisiones del grupo asociadas

Ver supuestos S11 a S15 en `Casos_de_Prueba.md`: misma pestaña (S11), resultado por titular (S12), sin reintento tras rechazo o cancelación (S13), la sesión no vence por tiempo (S14) y la tarjeta no se guarda (S15).

/* Formulario de compra: calendario, visitantes, total en vivo y envio.
 * El backend vuelve a validar todo: aca solo se guia al visitante. */
(() => {
  "use strict";

  const MAXIMO = 10;
  const MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "septiembre", "octubre", "noviembre", "diciembre",
  ];
  const DIAS = [
    "domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
  ];

  const $ = (selector) => document.querySelector(selector);
  const estado = {
    precios: null,
    reglas: null,
    desde: null,
    hasta: null,
    cerrados: new Set(),
    mes: null,
    fecha: null,
    visitantes: [{ edad: "", pase: "COMUN" }],
    forma: null,
    enviando: false,
  };

  const monto = (n) => `$${n.toLocaleString("es-AR")}`;
  const aIso = (f) => [
    f.getFullYear(),
    String(f.getMonth() + 1).padStart(2, "0"),
    String(f.getDate()).padStart(2, "0"),
  ].join("-");
  const deIso = (texto) => {
    const [a, m, d] = texto.split("-").map(Number);
    return new Date(a, m - 1, d);
  };
  const fechaLarga = (f) =>
    `${DIAS[f.getDay()]} ${f.getDate()} de ${MESES[f.getMonth()]}`;

  /* ---------- Calendario ---------- */

  function dibujarCalendario() {
    const { anio, mes } = estado.mes;
    const contenedor = $("#calendario-dias");
    contenedor.innerHTML = "";
    $("#calendario-mes").textContent = `${MESES[mes]} ${anio}`;

    const desplazamiento = (new Date(anio, mes, 1).getDay() + 6) % 7;
    for (let i = 0; i < desplazamiento; i += 1) {
      contenedor.appendChild(document.createElement("span"));
    }
    const diasDelMes = new Date(anio, mes + 1, 0).getDate();
    for (let d = 1; d <= diasDelMes; d += 1) {
      const fecha = new Date(anio, mes, d);
      const clave = aIso(fecha);
      const fueraDeRango = clave < estado.desde || clave > estado.hasta;
      const cerrado = estado.cerrados.has(clave);
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "dia";
      boton.textContent = d;
      boton.dataset.fecha = clave;
      boton.setAttribute("aria-label", fechaLarga(fecha));
      if (fueraDeRango || cerrado) {
        boton.disabled = true;
        if (cerrado && !fueraDeRango) {
          boton.classList.add("dia--cerrado");
          boton.title = "No disponible";
        }
      }
      if (clave === estado.desde) boton.classList.add("dia--hoy");
      if (clave === estado.fecha) {
        boton.classList.add("dia--elegido");
        boton.setAttribute("aria-pressed", "true");
      }
      boton.addEventListener("click", () => elegirFecha(clave));
      contenedor.appendChild(boton);
    }
    const actual = anio * 12 + mes;
    const primero = deIso(estado.desde);
    const ultimo = deIso(estado.hasta);
    $("#mes-anterior").disabled =
      actual <= primero.getFullYear() * 12 + primero.getMonth();
    $("#mes-siguiente").disabled =
      actual >= ultimo.getFullYear() * 12 + ultimo.getMonth();
  }

  function cambiarMes(salto) {
    const fecha = new Date(estado.mes.anio, estado.mes.mes + salto, 1);
    estado.mes = { anio: fecha.getFullYear(), mes: fecha.getMonth() };
    dibujarCalendario();
  }

  function elegirFecha(clave) {
    estado.fecha = clave;
    limpiarError("fecha_visita");
    dibujarCalendario();
    $("#fecha-elegida").textContent = `Venís el ${fechaLarga(deIso(clave))}`;
  }

  /* ---------- Visitantes y precios ---------- */

  function precioDe(visitante) {
    if (visitante.edad === "") return null;
    const edad = Number(visitante.edad);
    if (!Number.isInteger(edad) || edad < 0) return null;
    const base = estado.precios[visitante.pase];
    if (edad <= estado.reglas.gratis) return { monto: 0, insignia: "Gratis" };
    if (edad <= estado.reglas.menor || edad >= estado.reglas.mayor) {
      return { monto: base / 2, insignia: "50% off" };
    }
    return { monto: base, insignia: "" };
  }

  function dibujarVisitantes(nuevo = false) {
    const lista = $("#visitantes");
    lista.innerHTML = "";
    const total = estado.visitantes.length;
    estado.visitantes.forEach((visitante, i) => {
      const n = i + 1;
      const tarjeta = document.createElement("div");
      tarjeta.className = "visitante";
      if (nuevo && n === total) tarjeta.classList.add("visitante--nuevo");
      tarjeta.innerHTML = `
        <div class="visitante__cabecera">
          <span class="visitante__numero">Visitante ${n}</span>
          ${total > 1 ? `<button type="button" class="visitante__quitar"
            aria-label="Quitar visitante ${n}">&times;</button>` : ""}
        </div>
        <div class="visitante__campos">
          <label class="campo">
            <span>Edad</span>
            <input type="number" inputmode="numeric" min="0" step="1"
              placeholder="Ej: 30" value="${visitante.edad}"
              aria-label="Edad del visitante ${n}">
          </label>
          <div class="campo">
            <span id="pase-${n}">Pase</span>
            <div class="segmento" role="radiogroup" aria-labelledby="pase-${n}">
              <button type="button" role="radio" data-pase="COMUN"
                aria-checked="${visitante.pase === "COMUN"}">Común</button>
              <button type="button" role="radio" data-pase="VIP"
                aria-checked="${visitante.pase === "VIP"}">VIP</button>
            </div>
          </div>
        </div>
        <div class="visitante__pie">
          <span class="insignia" data-insignia></span>
          <strong data-subtotal></strong>
        </div>
        <p class="error" data-error="visitantes.${n}.edad" role="alert"></p>
        <p class="error" data-error="visitantes.${n}.pase" role="alert"></p>`;

      const edad = tarjeta.querySelector("input");
      edad.addEventListener("input", () => {
        visitante.edad = edad.value.trim();
        edad.classList.remove("invalido");
        limpiarError(`visitantes.${n}.edad`);
        actualizarTotales();
      });
      tarjeta.querySelectorAll("[data-pase]").forEach((boton) => {
        boton.addEventListener("click", () => {
          visitante.pase = boton.dataset.pase;
          tarjeta.querySelectorAll("[data-pase]").forEach((b) => {
            b.setAttribute("aria-checked", String(b === boton));
          });
          actualizarTotales();
        });
      });
      const quitar = tarjeta.querySelector(".visitante__quitar");
      if (quitar) {
        quitar.addEventListener("click", () => {
          estado.visitantes.splice(i, 1);
          dibujarVisitantes();
        });
      }
      lista.appendChild(tarjeta);
    });

    $("#cantidad-valor").textContent = total;
    $("#menos").disabled = total <= 1;
    $("#mas").disabled = total >= MAXIMO;
    $("#aviso-maximo").hidden = total < MAXIMO;
    actualizarTotales();
  }

  function cambiarCantidad(salto) {
    const total = estado.visitantes.length + salto;
    if (total < 1 || total > MAXIMO) return;
    limpiarError("cantidad");
    if (salto > 0) estado.visitantes.push({ edad: "", pase: "COMUN" });
    else estado.visitantes.pop();
    dibujarVisitantes(salto > 0);
    if (salto > 0) {
      const inputs = document.querySelectorAll("#visitantes input");
      inputs[inputs.length - 1].focus({ preventScroll: true });
    }
  }

  function actualizarTotales() {
    let total = 0;
    document.querySelectorAll("#visitantes .visitante").forEach((t, i) => {
      const precio = precioDe(estado.visitantes[i]);
      t.querySelector("[data-subtotal]").textContent =
        precio ? monto(precio.monto) : "—";
      t.querySelector("[data-insignia]").textContent =
        precio ? precio.insignia : "";
      if (precio) total += precio.monto;
    });
    const cantidad = estado.visitantes.length;
    const totalTexto = monto(total);
    const elemento = $("#total");
    if (elemento.textContent !== totalTexto) {
      elemento.textContent = totalTexto;
      elemento.classList.remove("pulso");
      void elemento.offsetWidth;
      elemento.classList.add("pulso");
    }
    $("#total-detalle").textContent =
      `${cantidad} ${cantidad === 1 ? "entrada" : "entradas"}`;
  }

  /* ---------- Forma de pago ---------- */

  function elegirForma(boton) {
    estado.forma = boton.dataset.forma;
    document.querySelectorAll("[data-forma]").forEach((b) => {
      b.setAttribute("aria-checked", String(b === boton));
    });
    limpiarError("forma_de_pago");
    $("#confirmar").textContent =
      estado.forma === "tarjeta" ? "Ir a pagar" : "Confirmar compra";
  }

  /* ---------- Errores ---------- */

  function limpiarError(campo) {
    const elemento = document.querySelector(`[data-error="${campo}"]`);
    if (!elemento) return;
    elemento.textContent = "";
    elemento.classList.remove("visible");
    const seccion = elemento.closest(".tarjeta");
    if (seccion && !seccion.querySelector(".error.visible")) {
      seccion.classList.remove("tarjeta--error");
    }
  }

  function limpiarErrores() {
    document.querySelectorAll("[data-error]").forEach((elemento) => {
      limpiarError(elemento.dataset.error);
    });
  }

  function mostrarErrores(errores) {
    let primero = null;
    errores.forEach(({ campo, mensaje }) => {
      const elemento = document.querySelector(`[data-error="${campo}"]`) ||
        document.querySelector('[data-error="general"]');
      elemento.textContent = elemento.textContent
        ? `${elemento.textContent} ${mensaje}` : mensaje;
      elemento.classList.add("visible");
      const seccion = elemento.closest(".tarjeta");
      if (seccion) seccion.classList.add("tarjeta--error");
      const coincidencia = campo.match(/^visitantes\.(\d+)\.edad$/);
      if (coincidencia) {
        const inputs = document.querySelectorAll("#visitantes input");
        const input = inputs[Number(coincidencia[1]) - 1];
        if (input) input.classList.add("invalido");
      }
      primero = primero || elemento;
    });
    if (primero) {
      (primero.closest(".tarjeta") || primero)
        .scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  /* ---------- Envio ---------- */

  async function confirmar() {
    if (estado.enviando) return;
    limpiarErrores();
    const boton = $("#confirmar");
    const textoOriginal = boton.textContent;
    estado.enviando = true;
    boton.disabled = true;
    boton.textContent = "Procesando...";
    const datos = {
      fecha_visita: estado.fecha || "",
      cantidad: estado.visitantes.length,
      visitantes: estado.visitantes.map((v) => ({ edad: v.edad, pase: v.pase })),
      forma_de_pago: estado.forma || "",
    };
    try {
      const respuesta = await fetch("/api/compras", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      });
      const cuerpo = await respuesta.json();
      if (respuesta.status === 400) {
        mostrarErrores(cuerpo.errores);
      } else if (!respuesta.ok) {
        throw new Error(String(respuesta.status));
      } else if (cuerpo.url_pago) {
        window.location.assign(cuerpo.url_pago);
        return;
      } else {
        mostrarExito(cuerpo);
        return;
      }
    } catch (error) {
      mostrarErrores([{
        campo: "general",
        mensaje: "No pudimos procesar la compra. Intentá de nuevo.",
      }]);
    }
    estado.enviando = false;
    boton.disabled = false;
    boton.textContent = textoOriginal;
  }

  function mostrarExito(cuerpo) {
    $("#barra-total").classList.add("oculta");
    $("#vista-compra").hidden = true;
    $("#exito-mensaje").textContent = cuerpo.mensaje;
    $("#exito-orden").textContent = `Orden N° ${cuerpo.numero_orden}`;
    $("#exito-boleteria").hidden = cuerpo.estado !== "PENDIENTE_BOLETERIA";
    $("#vista-exito").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
    const aviso = $("#exito-mail");
    if (cuerpo.mail_enviado_a) {
      aviso.textContent =
        `Te enviamos la confirmación con tu QR a ${cuerpo.mail_enviado_a}`;
    } else if (cuerpo.aviso_mail) {
      aviso.textContent = cuerpo.aviso_mail;
      aviso.classList.add("aviso-mail--error");
    }
    aviso.hidden = !aviso.textContent;
    EcoHarmony.lanzarHojas();
  }

  /* ---------- Inicio ---------- */

  async function iniciar() {
    $("#mes-anterior").addEventListener("click", () => cambiarMes(-1));
    $("#mes-siguiente").addEventListener("click", () => cambiarMes(1));
    $("#menos").addEventListener("click", () => cambiarCantidad(-1));
    $("#mas").addEventListener("click", () => cambiarCantidad(1));
    document.querySelectorAll("[data-forma]").forEach((boton) => {
      boton.addEventListener("click", () => elegirForma(boton));
    });
    $("#confirmar").addEventListener("click", confirmar);

    try {
      const [dias, precios] = await Promise.all([
        fetch("/api/dias-no-disponibles").then((r) => r.json()),
        fetch("/api/precios").then((r) => r.json()),
      ]);
      estado.desde = dias.desde;
      estado.hasta = dias.hasta;
      estado.cerrados = new Set(dias.dias);
      const inicio = deIso(dias.desde);
      estado.mes = { anio: inicio.getFullYear(), mes: inicio.getMonth() };
      estado.precios = precios.precios;
      estado.reglas = {
        gratis: precios.edad_max_gratis,
        menor: precios.edad_max_menor_con_descuento,
        mayor: precios.edad_min_mayor_con_descuento,
      };
      dibujarCalendario();
      dibujarVisitantes();
    } catch (error) {
      mostrarErrores([{
        campo: "general",
        mensaje: "No pudimos cargar los datos del parque. Recargá la página.",
      }]);
    }
  }

  iniciar();
})();

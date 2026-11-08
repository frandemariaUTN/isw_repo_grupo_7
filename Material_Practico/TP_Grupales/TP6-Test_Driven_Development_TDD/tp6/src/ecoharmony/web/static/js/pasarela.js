/* Pasarela simulada: formato de los campos y bloqueo del doble envio.
 * La validacion real de la tarjeta la hace el backend. */
(() => {
  "use strict";

  const soloDigitos = (texto) => texto.replace(/\D/g, "");
  const numero = document.getElementById("numero");
  const marca = document.getElementById("marca");
  const vencimiento = document.getElementById("vencimiento");

  numero.addEventListener("input", () => {
    const digitos = soloDigitos(numero.value).slice(0, 16);
    numero.value = digitos.replace(/(\d{4})(?=\d)/g, "$1 ");
    if (digitos.startsWith("4")) marca.textContent = "VISA";
    else if (digitos.startsWith("5")) marca.textContent = "MASTERCARD";
    else marca.textContent = "";
  });

  vencimiento.addEventListener("input", (evento) => {
    const digitos = soloDigitos(vencimiento.value).slice(0, 4);
    const borrando = evento.inputType === "deleteContentBackward";
    vencimiento.value = digitos.length > 2 || (digitos.length === 2 && !borrando)
      ? `${digitos.slice(0, 2)}/${digitos.slice(2)}` : digitos;
  });

  ["codigo", "dni"].forEach((id) => {
    const campo = document.getElementById(id);
    campo.addEventListener("input", () => {
      campo.value = soloDigitos(campo.value);
    });
  });

  document.querySelectorAll(".mp-campo input").forEach((campo) => {
    campo.addEventListener("input", () => {
      const contenedor = campo.closest(".mp-campo");
      contenedor.classList.remove("mp-campo--error");
      const error = contenedor.querySelector(".mp-error");
      if (error) error.remove();
    });
  });

  document.getElementById("form-pago").addEventListener("submit", () => {
    const boton = document.getElementById("pagar");
    boton.disabled = true;
    boton.textContent = "Procesando...";
  });

  document.getElementById("form-cancelar").addEventListener("submit", (e) => {
    if (!window.confirm("¿Querés cancelar el pago? La compra se va a cancelar.")) {
      e.preventDefault();
    }
  });
})();

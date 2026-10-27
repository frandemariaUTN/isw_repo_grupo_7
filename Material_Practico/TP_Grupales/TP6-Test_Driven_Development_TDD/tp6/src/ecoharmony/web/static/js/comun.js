/* Utilidades compartidas: hojas que caen y pop-ups. */
window.EcoHarmony = (() => {
  "use strict";

  const COLORES = ["#386641", "#6A994E", "#A7C957", "#BC4749"];

  function lanzarHojas(cantidad = 28) {
    const contenedor = document.querySelector(".hojas");
    if (!contenedor) return;
    for (let i = 0; i < cantidad; i += 1) {
      const hoja = document.createElement("span");
      hoja.className = "hoja";
      hoja.style.left = `${Math.random() * 100}%`;
      hoja.style.background = COLORES[i % COLORES.length];
      hoja.style.animationDuration = `${2.4 + Math.random() * 2}s`;
      hoja.style.animationDelay = `${Math.random() * 0.8}s`;
      hoja.style.setProperty("--deriva", `${(Math.random() - 0.5) * 160}px`);
      hoja.style.setProperty("--giro", `${360 + Math.random() * 540}deg`);
      contenedor.appendChild(hoja);
      hoja.addEventListener("animationend", () => hoja.remove());
    }
  }

  function abrirModal(id, demora = 0) {
    const modal = document.getElementById(id);
    if (!modal) return;
    setTimeout(() => {
      if (typeof modal.showModal === "function") modal.showModal();
      else modal.setAttribute("open", "");
    }, demora);
  }

  return { lanzarHojas, abrirModal };
})();

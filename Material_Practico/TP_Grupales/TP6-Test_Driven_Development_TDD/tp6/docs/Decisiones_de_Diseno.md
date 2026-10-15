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
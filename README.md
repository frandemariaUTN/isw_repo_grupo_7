# isw_repo_grupo_7
# DISEÑO DEL REPOSITORIO

```text
isw_repo_grupo_7/
├── Informacion_De_La_Catedra/
├── Material_De_Estudio/
│   ├── Bibliografia/
│   │   ├── Agilismo/
│   │   ├── Ing_De_Software/
│   │   ├── Lean_Y_Kanban/
│   │   ├── SCM/
│   │   ├── TDD/
│   │   └── Testing_De_Software/
│   ├── Clases_Grabadas/
│   ├── Filminas/
│   ├── Notas_De_Clase/
│   └── Resumenes/
├── Material_Practico/
│   ├── Casos_De_Estudio/
│   │   ├── Casos_Intensivo/
│   │   └── Ejercicios_Practicos/
│   ├── TI_Grupales/
│   │   ├── TIG1-Exposicion_Despliegue_De_Producto/
│   │   └── TIG2-Poster_Cientifico_Frameworks_Lean_Agile/
│   ├── TP_Grupales/
│   │   ├── TP4-SCM_Herramientas_De_SCM/
│   │   ├── TP5-SCM_Uso_De_Repositorio/
│   │   ├── TP6-Test_Driven_Development_TDD/
│   │   ├── TP7-DINAMICA_SCRUM/
│   │   ├── TP11-TESTING/
│   │   ├── TP12-KANBAN/
│   │   ├── TP14-Retrospectiva/
│   │   └── TP15-Design_Thinking/
│   └── Templates/
└── README.md
```

Link al repositorio: https://github.com/frandemariaUTN/isw_repo_grupo_7

# CRITERIO DE DETERMINACIÓN DE LA ESTRUCTURA

● **Informacion_De_La_Catedra/:** Este directorio funciona como el espacio administrativo del repositorio. Su función principal es almacenar todos los ítems de configuración de gestión. Aquí se guardan documentos formales de la materia, como los programas, cronogramas y reglas de la cátedra que dictan el orden y desarrollo de la cursada.

● **Material_De_Estudio/:** Actúa como el centro de acumulación y almacenamiento de la información teórica. Esta carpeta centraliza todo el contenido pasivo necesario para el aprendizaje, dividiéndose lógicamente en subcarpetas para facilitar la búsqueda:

○ **Material_De_Estudio/Bibliografia/:** Contiene los libros de texto y referencias oficiales, separados por unidades temáticas (ej: Agilismo, SCM, TDD).

○ **Material_De_Estudio/Clases_Grabadas/:** Almacena los registros audiovisuales de las clases dictadas en años anteriores.

○ **Material_De_Estudio/Filminas/:** Destinado a organizar las presentaciones visuales utilizadas por los docentes.

○ **Material_De_Estudio/Notas_De_Clase/:** Espacio para los apuntes directos generados durante las clases.

○ **Material_De_Estudio/Resumenes/:** Punto clave del repositorio donde el equipo comparte los resúmenes consolidados de estudio. Estos documentos son ítems de configuración "vivos" que sufren cambios y mejoras a lo largo del cuatrimestre.

● **Material_Practico/:** Contiene todos los artefactos, entregables y documentos producidos por el equipo o provistos por la cátedra para la aplicación práctica de los conocimientos:

○ **Material_Practico/Casos_De_Estudio/:** Almacena los escenarios y ejemplos prácticos brindados por los docentes.

○ **Material_Practico/TI_Grupales/:** Separa los "Trabajos de Investigación" de los prácticos comunes. Como dicta la teoría, un trabajo de investigación (desarrollo de concepto) tiene metas, formalidad y un proceso distinto al de un desarrollo normal, por lo que sus ítems deben gestionarse de forma independiente.

○ **Material_Practico/TP_Grupales/:** Contiene las entregas de los Trabajos Prácticos Evaluables, que representan el "desarrollo de una aplicación" con mayor rigor y orientación al producto.

○ **Material_Practico/Templates/:** Funciona como una biblioteca de plantillas estandarizadas provistas por la cátedra o creadas por el equipo para mantener la uniformidad en las entregas.

# ITEMS DE CONFIGURACIÓN

| Nombre                                    | Regla de nombrado                                         | Ubicación                                                   | Tipo              |
| ----------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------- | ----------------- |
| Consigna de Trabajos de Investigación     | `TP-Investigacion-<NroTPI>-<NombreTPI>.pdf`               | `/Material_Practico/TI_Grupales/TIG<NroTPI>-<NombreTPI>/`   | Cátedra           |
| Documento de Estructura del Repositorio   | `Estructura_Repositorio.pdf`                              | `/`                                                         | Producción propia |
| Documento de Presentación del Repositorio | `README.md`                                               | `/`                                                         | Producción propia |
| Entrega de Trabajo de Investigación       | `TP-Investigacion-<NroTPI>-<NombreTPI>-G7.<extensión>`    | `/Material_Practico/TI_Grupales/TIG<NroTPI>-<NombreTPI>/`   | Producción propia |
| Consignas de Trabajos Prácticos           | `TP-Grupal-<NroTPG>-<NombreTPG>.pdf`                      | `/Material_Practico/TP_Grupales/TP<NroTPG>-<NombreTGP>/`    | Cátedra           |
| Entrega de Trabajo Práctico               | `TP-Grupal-<NroTPG>-<NombreTPG>-G7.<Extension>`           | `/Material_Practico/TP_Grupales/TP<NroTPG>-<NombreTGP>/`    | Producción propia |
| Guia de TP Evaluables                     | `Guia_TPS.pdf`                                            | `/Material_Practico/TP_Grupales/`                           | Cátedra           |
| Templates Prácticos                       | `Template-<NombreTemplate>.docx/xlsx`                     | `/Material_Practico/Templates/`                             | Cátedra           |
| Casos de Estudio para Intensivo           | `CEI-<NombreCaso>.pdf`                                    | `/Material_Practico/Casos_De_Estudio/Casos_Intensivo/`      | Cátedra           |
| Guía de Ejercicios Prácticos              | `GEP-<NombreGuia>.pdf`                                    | `/Material_Practico/Casos_De_Estudio/Ejercicios_Practicos/` | Cátedra           |
| Archivo de Información de la Cátedra      | `Info_Catedra-<NombreInfo>.pdf/xlsx`                      | `/Informacion_De_La_Catedra/`                               | Cátedra           |
| Bibliografía de la cátedra                | `BIBL-<NombreBibliografia>.pdf`                           | `/Material_De_Estudio/Bibliografia/<TemaBibliografia>/`     | Cátedra           |
| Presentaciones Teóricas de Clase          | `Presentacion-<NroPresentacion>-<NombrePresentacion>.pdf` | `/Material_De_Estudio/Filminas/`                            | De Clase          |
| Enlaces a clases grabadas                 | `Links_Clases_Grabadas-<Año>.xlsx`                        | `/Material_De_Estudio/Clases_Grabadas/`                     | De Clase          |
| Resúmenes                                 | `Resumen-<NroParcial>-<Año>.pdf/docx`                     | `/Material_De_Estudio/Resumenes/`                           | Producción propia |
| Notas de clases                           | `Notas-Clase-<Fecha>.pdf/docx/jpg`                        | `/Material_De_Estudio/Notas_De_Clase/`                      | De clase          |

# GLOSARIO

| Siglas                 | Significado                                                                                                                                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| TP                     | Trabajo Práctico                                                                                                                                                                                       |
| TIG                    | Trabajo Investigación Grupal                                                                                                                                                                           |
| CEI                    | Casos de Estudio para Intensivo                                                                                                                                                                        |
| GEP                    | Guia de Ejercicios Prácticos                                                                                                                                                                           |
| G7                     | Grupo 7                                                                                                                                                                                                |
| BIBL                   | Bibliografía                                                                                                                                                                                           |
| `<Extensión>`          | Extensión del archivo (pdf, zip, docx, etc)                                                                                                                                                            |
| `<NroTPI>`             | Número de trabajo práctico de investigación                                                                                                                                                            |
| `<NroTPG>`             | Número del trabajo práctico grupal                                                                                                                                                                     |
| `<NroParcial>`         | Número de Parcial                                                                                                                                                                                      |
| `<NombreTPI>`          | Nombre de trabajo práctico de Investigación                                                                                                                                                            |
| `<NombreTPG>`          | Nombre de trabajo práctico grupal                                                                                                                                                                      |
| `<NombreCaso>`         | Nombre del caso de estudio                                                                                                                                                                             |
| `<NombreGuia>`         | Refiere al título/nombre de la guía de ejercicios                                                                                                                                                      |
| `<NombreInfo>`         | Nombre del archivo informativo referente a Pautas generales del cursado de la cátedra e Información Relevante destacada en la UV (ej: Cronograma, presentación de la materia, pautas de envio de Mail) |
| `<NombreBibliografia>` | Nombre del Libro/Informe/Material Bibliográfico                                                                                                                                                        |
| `<TemaBibliografia>`   | Nombre del tema conceptual bajo el cual se agrupan varios materiales Bibliográficos de la cátedra                                                                                                      |
| `<NroPresentacion>`    | Número de la Presentación según el orden propuesto por la cátedra                                                                                                                                      |
| `<NombrePresentacion>` | Nombre de la presentación según los temas estipulados en la misma                                                                                                                                      |

# NOMBRADO DE COMMITS

Proponemos la siguiente estructura de nombrado de los commits según la/s actividad/es que pueden contemplar los mismos:

| Prefijo    | Uso                                                                                          | Ejemplo                                                        |
| ---------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `feat`     | Agregar un nuevo archivo, directorio, resolución o código                                    | `feat: agregado Resumen-1-2026.pdf`                            |
| `docs`     | Crear o modificar documentación                                                              | `docs: modificada Estructura_del_repositorio.pdf`              |
| `refactor` | Reorganizar carpetas o estructura sin cambiar contenido                                      | `refactor: agregada carpeta Notas_de_clase/`                   |
| `fix`      | Corregir errores o bugs en el código o en la funcionalidad                                   | `fix: corregido error en validación del formulario`            |
| `chore`    | Cambios en tareas de mantenimiento, configuración o dependencias (sin afectar funcionalidad) | `chore: Actualizado .gitignore Para ignorar archivos de logs.` |

# DEFINICION Y GESTION DE LINEAS BASE

● **Criterio de Creación**

○ Se establecerá una nueva Línea Base (marcada mediante un tag en el motor de control de versiones) cada vez que un Trabajo Práctico sea entregado, corregido y aprobado por la cátedra, ya que esto representa una configuración revisada formalmente.

○ A partir de ese punto, los archivos de esa entrega servirán como base estable para desarrollos posteriores.

○ **Nota de Excepción:** La primera Línea Base del proyecto se establecerá de manera anticipada al finalizar la entrega y configuración inicial de la estructura del repositorio correspondiente al Trabajo Practico número 4.

● **Reglas de Nomenclatura e Identificación**

○ Se utilizarán etiquetas (tags de Git) para marcar las Lineas Base en el repositorio.

○ Las versiones tendrán un identificador único compuesto por la letra "v" (versión) seguida del número del Trabajo Práctico correspondiente y un sub-número de revisión.

○ **Formato del Tag:** `v[NroTP].0`

| Versión (Tag) | Fecha    | Autor           | Descripción del Hito      |
| ------------- | -------- | --------------- | ------------------------- |
| v4.0          | 25/08/26 | Tomás Santillán | Entrega de Práctico 4 SCM |

Universidad Tecnológica Nacional - Facultad Regional Córdoba | Ingeniería y Calidad de Software - 2026

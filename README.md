# Análisis Espacial y Temporal de la Calidad del Aire en el Gran Santiago (2013–2023)

## Integrantes
* Alex Cordero
* Matias Fernandez
* Jose Saavedra
* Luis Sarsuri

---

## 1. Descripción del Problema y Motivación
La cuenca del Gran Santiago presenta condiciones geográficas y meteorológicas particulares: al estar rodeada por la Cordillera de los Andes y la Cordillera de la Costa, se produce un estancamiento de masas de aire durante los meses fríos debido al fenómeno de inversión térmica. Esto genera episodios recurrentes de alta concentración de material particulado fino ($MP_{2.5}$ y $MP_{10}$), con severos riesgos para la salud pública.

El objetivo de este proyecto es analizar la evolución temporal, la estacionalidad climática y las disparidades espaciales en los niveles de contaminación del aire en cinco sectores estratégicos de la capital durante la última década (2013–2023), identificando brechas territoriales y factores meteorológicos que gatillan alertas ambientales.

---

## 2. Pregunta de Investigación
> **¿Cómo varían las concentraciones de material particulado ($MP_{2.5}$ y $MP_{10}$) entre los distintos sectores geográficos del Gran Santiago y las estaciones del año durante el período 2013–2023?**

---

## 3. Delimitación del Alcance (Estructura X, Y y T)

- **Unidad de observación:** Un registro diario consolidado por estación de monitoreo.
- **Variables explicativas / Contexto ($X$):**
  - *Espacial:* Estación de monitoreo (`Estacion`: Pudahuel, El Bosque, Santiago Centro, La Florida, Las Condes).
  - *Temporal / Meteorológico:* Mes del año, estación climática, `Temperatura` (°C) y `Viento_v` ($m/s$).
- **Variables objetivo ($Y$):**
  - Concentración de material particulado fino y grueso (`MP2_5` y `MP10` en $\mu g/m^3$).
  - Cumplimiento/superación de la norma primaria de calidad del aire diaria ($50\text{ }\mu g/m^3$ para $MP_{2.5}$).
- **Contexto temporal ($T$):** Período de 10 años continuos comprendido entre 2013 y 2023.
- **Límites del alcance:** Análisis descriptivo, exploratorio y comparativo de superficie. No incluye modelos numéricos de dinámica de fluidos ni pronóstico químico atmosférico en tiempo real.

---

## 4. Descripción de los Datos

- **Fuente:** Red de Monitoreo del Sistema de Información Nacional de Calidad del Aire (SINCA), dependiente del Ministerio del Medio Ambiente (MMA) de Chile.
- **Archivo crudo:** `data/raw/Calidad del aire.csv` (~2.68 MB).
- **Volumen total:** 47.953 observaciones históricas (1997–2023); 19.271 observaciones correspondientes a la ventana de estudio delimitada (2013–2023).
- **Variables registradas:**
  - `Estacion`: Comuna/sector de la estación de monitoreo.
  - `FECHA (YYMMDD)` / `HORA (HHMM)`: Estampas temporales del reporte.
  - `MP10`, `MP2_5`: Concentración de material particulado ($\mu g/m^3$).
  - `CO`, `NO`, `NO2`, `O3`: Gases contaminantes complementarios.
  - `Temperatura`, `Humedad`, `Viento_v`: Parámetros meteorológicos locales.

### Observaciones preliminares de calidad de datos
En la inspección inicial se identificaron valores nulos en sensores meteorológicos para las estaciones El Bosque y La Florida, así como factores de escala atípicos en registros de temperatura y velocidad de viento, los cuales serán tratados y saneados durante el preprocesamiento formal (Avance 2).

---

## 5. Estructura del Repositorio

```text
proyecto-calidad-aire-santiago/
├── data/
│   ├── raw/                 # Datos originales sin procesar (Calidad del aire.csv)
│   └── processed/           # Datos filtrados y transformados para análisis
├── notebooks/
│   └── 01_exploracion.ipynb # Notebook de carga inicial, formateo y validación preliminar
├── figures/                 # Gráficos generados para informes y presentaciones
├── src/                     # Funciones y scripts auxiliares reutilizables
├── app/                     # Código del producto interactivo final (Streamlit / Plotly)
├── .gitignore               # Exclusión de temporales y cachés
└── README.md                # Documentación del proyecto
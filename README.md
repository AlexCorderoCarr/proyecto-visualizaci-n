# Análisis Espacial y Temporal de la Calidad del Aire en el Gran Santiago (2013–2023)

## Integrantes
* Alex Cordero
* Matias Fernandez
* Jose Saavedra
* Luis Sarsuri

## 1. Contexto y Motivación
La contaminación atmosférica por material particulado ($MP_{10}$ y $MP_{2.5}$) en la cuenca de Santiago constituye uno de los problemas ambientales más críticos de Chile debido a su impacto en la salud respiratoria. Este proyecto analiza la evolución temporal, la estacionalidad climática y las disparidades espaciales de la calidad del aire en cinco sectores estratégicos de la capital durante la última década.

## 2. Pregunta de Investigación
¿Cómo varían las concentraciones de material particulado fino ($MP_{2.5}$ y $MP_{10}$) entre los distintos sectores geográficos del Gran Santiago y las estaciones del año durante el período 2013–2023?

## 3. Delimitación del Alcance (X, Y, T)
- **Unidad de observación:** Medición diaria por estación de monitoreo.
- **Variables disponibles (X):** Estación de monitoreo (`Pudahuel`, `El Bosque`, `Santiago`, `La Florida`, `Las Condes`), mes, estación climática, `Temperatura`, `Humedad`, `Viento_v`.
- **Variable objetivo (Y):** Concentraciones de `MP2_5` y `MP10` ($\mu g/m^3$) y categorización según límites normativos.
- **Contexto temporal (T):** Período 2013 - 2023.
- **Límites:** Análisis analítico-visual retrospectivo basado en mediciones terrestres; no incluye modelos de dinámica de fluidos en tiempo real.

## 4. Dataset
- **Fuente:** Red de Monitoreo del Sistema de Información Nacional de Calidad del Aire (SINCA) / Ministerio del Medio Ambiente (MMA).
- **Dimensiones:** 47.953 observaciones, 12 columnas.
- **Variables principales:** `Estacion`, `FECHA (YYMMDD)`, `MP10`, `MP2_5`, `CO`, `NO`, `NO2`, `O3`, `Humedad`, `Temperatura`, `Viento_v`.

## 5. Estructura del Repositorio
- `data/raw/`: Datos originales (`Calidad del aire.csv`).
- `data/processed/`: Tablas limpias y filtradas temporalmente.
- `notebooks/`: Notebooks de análisis exploratorio (`01_exploracion.ipynb`).
- `figures/`: Gráficos y prototipos visuales exportados.
- `src/`: Funciones auxiliares de carga y procesamiento.
- `app/`: Aplicación interactiva final (Plotly / Streamlit).
# Análisis Espacial y Temporal de la Calidad del Aire en el Gran Santiago (2013–2023)

## Integrantes
* Alex Cordero
* Matias Fernandez
* Jose Saavedra
* Luis Sarsuri

---

## 1. Descripción del Problema y Motivación
La cuenca del Gran Santiago presenta condiciones geográficas y meteorológicas particulares: al estar rodeada por la Cordillera de los Andes y la Cordillera de la Costa, se produce un estancamiento de masas de aire durante los meses fríos debido al fenómeno de inversión térmica. Esto genera episodios recurrentes de alta concentración de material particulado fino ($MP_{2.5}$ y $MP_{10}$), con severos riesgos para la salud pública.

El objetivo de este proyecto es analizar la evolución temporal, la estacionalidad climática y las disparidades espaciales en los niveles de contaminación del aire en cinco sectores estratégicos de la capital durante la última década (2013–2023), transitando desde la exploración descriptiva hacia un enfoque predictivo y explicativo orientado a sistemas de alerta temprana.

---

## 2. Pregunta de Investigación
> **¿Cómo varían las concentraciones de material particulado ($MP_{2.5}$ y $MP_{10}$) entre los distintos sectores geográficos del Gran Santiago y las estaciones del año, y qué tan predecibles son los episodios críticos mediante variables meteorológicas y temporales?**

---

## 3. Delimitación del Alcance (Estructura X, Y y T)

- **Unidad de observación:** Un registro diario consolidado por estación de monitoreo.
- **Variables explicativas / Contexto ($X$):**
  - *Espacial:* Estación de monitoreo (`Estacion`: Pudahuel, El Bosque, Santiago Centro, La Florida, Las Condes).
  - *Temporal / Meteorológico:* Mes del año, estación climática, `Temperatura_C`, `Viento_ms` y gases complementarios (`CO`, `NO2`, `O3`, etc.).
- **Variables objetivo ($Y$):**
  - Concentración de material particulado fino y grueso (`MP2_5` y `MP10` en $\mu g/m^3$).
- **Contexto temporal ($T$):** Período de 10 años continuos comprendido entre 2013 y 2023.

---

## 4. Descripción de los Datos

- **Fuente:** Red de Monitoreo del Sistema de Información Nacional de Calidad del Aire (SINCA), dependiente del Ministerio del Medio Ambiente (MMA) de Chile.
- **Archivo crudo:** `data/raw/Calidad del aire.csv` (~2.68 MB).
- **Tratamiento:** Se implementó un pipeline de preprocesamiento (`src/data_cleaning.py`) para sanear nulos e inconsistencias en sensores meteorológicos, generando el archivo limpio `data/processed/calidad_aire_limpia.parquet`.

---

## 5. Avance 3: Rendimiento y Explicabilidad de Modelos
En esta etapa se incorporó una solución predictiva para estimar las concentraciones de $MP_{2.5}$:
* **Modelos evaluados:** Se contrastó una **Regresión Lineal** (modelo base) frente a un **Random Forest Regressor** (ensamble no lineal).
* **Rendimiento:** El modelo Random Forest demostró superioridad al disminuir el error métrico (RMSE de 104.49 frente a 111.32 de la regresión lineal) y capturar mejor la varianza de los datos ($R^2$ de 0.476).
* **Explicabilidad (SHAP):** Se aplicó análisis SHAP global (identificando la tendencia histórica del año, la velocidad del viento y la temperatura como factores críticos) y local (analizando mediante gráficos *Waterfall* aciertos y errores de predicción en días específicos).

---

## 6. Estructura del Repositorio
```text
proyecto-visualizacion/
├── data/
│   ├── raw/Calidad del aire.csv            # Dataset original (Ignorado en git)
│   └── processed/calidad_aire_limpia.parquet # Datos procesados para la App y Modelos
├── notebooks/
│   ├── 01_exploracion.ipynb                # EDA y pruebas iniciales
│   └── 02_modelos.ipynb                    # Entrenamiento, métricas y explicabilidad SHAP
├── src/
│   └── data_cleaning.py                    # Script de saneamiento de datos
├── app/
│   ├── app.py                              # Entrypoint de Streamlit
│   └── pages/
│       ├── 1_Contexto_y_Calidad.py         # Análisis de estructura de datos
│       ├── 2_Analisis_Univariado.py        # Distribuciones y sesgos
│       └── 3_Analisis_Multivariable.py     # Territorio, Estacionalidad e Inversión Térmica
├── requirements.txt                        # Dependencias del proyecto
└── README.md
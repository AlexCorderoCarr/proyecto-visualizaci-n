# Análisis Espacial, Temporal y Predicción de Calidad del Aire en el Gran Santiago (2018–2023)

## Integrantes
* Alex Cordero
* Matias Fernandez
* Jose Saavedra
* Luis Sarsuri

---

## 1. Descripción del Problema y Motivación
La cuenca del Gran Santiago presenta condiciones geográficas y meteorológicas particulares: al estar rodeada por la Cordillera de los Andes y la Cordillera de la Costa, durante los meses fríos se produce estancamiento atmosférico por **inversión térmica**. Esto genera episodios recurrentes de alta concentración de material particulado fino ($MP_{2.5}$), superando la norma primaria diaria chilena (**50 $\mu g/m^3$**, D.S. N°12 MMA) con severos riesgos para la salud pública.

El proyecto integra una narrativa visual interactiva en **Power BI** (exploración territorial, estacional e inversión térmica) con una aplicación operativa en **Streamlit** que evalúa el modelo predictivo final y ejecuta predicciones en vivo.

---

## 2. Pregunta de Investigación
> **¿Cómo varían las concentraciones de material particulado fino ($MP_{2.5}$) entre los distintos sectores geográficos del Gran Santiago y las estaciones del año, y qué tan predecibles son mediante variables meteorológicas, temporales y espaciales?**

---

## 3. Depuración Metodológica y Datos (SINCA)
- **Fuente:** Red de Monitoreo del Sistema de Información Nacional de Calidad del Aire (SINCA), Ministerio del Medio Ambiente de Chile (`data/raw/Calidad del aire.csv`).
- **Auditoría 2013–2023 (`19.271` registros) → Tramo Homogéneo 2018–2023 (`10.141` registros):** al auditar la serie original se detectó un corrimiento de escala en los registros previos a mayo de 2017 (medianas de $MP_{2.5}$ entre 177 y 206 frente a 17–20 $\mu g/m^3$ en 2018–2023). Para garantizar probidad física y estadística respecto al Avance 3, se acotó el estudio al período homogéneo **2018–2023** (`2018-01-01` a `2023-07-27`) y se decodificaron los factores ×10/×100 de temperatura (`Temperatura_C`), `Humedad` (%) y velocidad del viento (`Viento_ms`) en `src/data_cleaning.py`.
- **Cobertura de estaciones:**
  - *Análisis territorial (5 estaciones):* El Bosque, La Florida, Pudahuel, Santiago y Las Condes (`10.141` registros diarios).
  - *Análisis climático y modelado predictivo (3 estaciones):* **Pudahuel, Santiago y Las Condes** (`5.505` observaciones completas), dado que El Bosque y La Florida carecen de sensores meteorológicos en el registro SINCA.
- **Variables del modelo (5 entradas → 1 salida):**
  - **Entradas ($X$):** `Estacion`, `Month`, `Temperatura_C`, `Humedad`, `Viento_ms` (se excluyeron contaminantes co-medidos como $MP_{10}$ y gases para evaluar capacidad predictiva exclusivamente desde clima, mes y ubicación).
  - **Objetivo ($Y$):** concentración promedio diaria de `MP2_5` ($\mu g/m^3$).

---

## 4. Evaluación del Modelo Final y Comparación con Soluciones Base
Se aplicó una **división temporal estricta**:
- **Entrenamiento (`2018–2021`):** `3.870` observaciones diarias (media de $MP_{2.5}$ = `23.37 µg/m³`).
- **Prueba futura (`2022–2023`):** `1.635` observaciones diarias evaluadas de forma equivalente en todos los modelos.

| Modelo | Referencia / Tipo | MAE ($\mu g/m^3$) | RMSE ($\mu g/m^3$) | MAPE (%) | $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Base 1: Media de entrenamiento** | Constante (`23.37 µg/m³`) | 13.18 | 16.98 | 76.2% | -0.000 |
| **Base 2: Regresión Lineal (1 variable)** | `Temperatura_C` | 10.89 | 15.36 | 63.6% | 0.181 |
| **Regresión Lineal Múltiple** | 5 variables | 10.49 | 14.29 | 63.4% | 0.292 |
| **Random Forest Regressor (Final)** | 5 variables (`200` árboles, `max_depth=10`) | **8.09** | **12.05** | **43.4%** | **0.496** |

El **Random Forest** reduce el **RMSE en 29.0%** frente a la media de entrenamiento y en **21.6%** frente a la regresión de una variable, capturando la interacción no lineal entre bajas temperaturas invernales, viento en calma y sector de la cuenca.

---

## 5. Ejecución Local del Pipeline y la Aplicación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Regenerar dataset limpio (2018-2023), auditoría y fuentes para Power BI
python src/data_cleaning.py

# 3. Entrenar modelo Random Forest, evaluar referencias base y guardar artefactos
python src/train_model.py

# 4. Ejecutar aplicación Streamlit (Presentación Final)
streamlit run app/app.py
```

---

## 6. Estructura del Repositorio
```text
proyecto-visualizacion/
├── app/
│   ├── app.py                              # Portada ejecutiva de Streamlit
│   ├── utils.py                            # Carga cacheada de datos/modelo y helpers MMA
│   └── pages/
│       ├── 1_Modelo_y_Metricas.py          # Evaluación justa vs. soluciones base
│       ├── 2_Prediccion_en_Vivo.py         # Simulador operativo en vivo + limitaciones
│       ├── 3_EDA_Contexto_y_Calidad.py     # Auditoría 2013-2023 y decodificación de sensores
│       ├── 4_EDA_Analisis_Univariado.py    # Distribución MP2.5 y brecha territorial
│       └── 5_EDA_Analisis_Multivariable.py # Estacionalidad, inversión térmica y viento
├── data/
│   ├── raw/Calidad del aire.csv            # Dataset original SINCA (ignorado en git)
│   └── processed/
│       ├── calidad_aire_limpia.parquet     # Dataset limpio 2018-2023
│       └── auditoria_calidad_2013_2023.json
├── models/
│   ├── rf_mp25_model.joblib                # Pipeline entrenado
│   ├── model_metadata.json                 # Métricas, split, importancias y medianas
│   └── test_predictions.parquet            # Predicciones 2022-2023
├── notebooks/
│   ├── 01_exploracion.ipynb
│   └── 02_modelos.ipynb                    # Reproducción del modelo final y análisis SHAP
├── powerbi/
│   ├── Calidad_Aire_Santiago.pbix          # Tablero Power BI Desktop (3 páginas interactivas)
│   ├── Calidad_Aire_Santiago.pbip          # Proyecto Power BI (PBIR + TMDL)
│   ├── Calidad_Aire_Santiago.Report/       # Definición de visuales y páginas
│   ├── Calidad_Aire_Santiago.SemanticModel/ # Modelo semántico y medidas DAX
│   ├── calidad_aire_santiago_pbi.xlsx      # Tabla consolidada para Power BI
│   └── data/                               # Modelo estrella CSV (fact + 2 dimensiones)
├── src/
│   ├── data_cleaning.py
│   └── train_model.py
├── requirements.txt
└── README.md
```

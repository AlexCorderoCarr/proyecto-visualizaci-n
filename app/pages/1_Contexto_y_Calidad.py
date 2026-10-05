import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Contexto y Calidad", layout="wide")

st.title("Contexto y Calidad de los Datos")

@st.cache_data
def load_data():
    return pd.read_parquet('data/processed/calidad_aire_limpia.parquet')

df = load_data()

st.markdown("### 1. Estructura General del Dataset Consolidado")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Observaciones Totales", f"{len(df):,}")
col2.metric("Período de Estudio", "2013 - 2023")
col3.metric("Estaciones", df['Estacion'].nunique())
col4.metric("Variables", df.shape[1])

st.markdown("### 2. Detección y Tratamiento de Anomalías (Sensores SINCA)")
st.info("**Hallazgo Crítico de Calidad:** Las estaciones *El Bosque* y *La Florida* no cuentan con registros meteorológicos en este decenio. Para garantizar la probidad estadística, se optó por una **estrategia mixta**: análisis de contaminantes en las 5 comunas y análisis meteorológico profundo en las 3 estaciones con anemómetro y termómetro operativo (Pudahuel, Santiago, Las Condes).")

tab1, tab2 = st.tabs(["Filtros Meteorológicos Aplicados", "Estado Actual de Datos (Nulos)"])

with tab1:
    st.markdown("""
    *   **Temperatura:** En el dataset crudo (`raw`), ciertas estaciones registraban la temperatura multiplicada por un factor de 10 (ej. reportando $171.6^\circ\text{C}$ en invierno). Se aplicó una función correctiva (`formatear_celsius`) para reescalar la variable, descartando valores físicos inviables.
    *   **Velocidad del Viento:** Se detectó la mezcla de lecturas de velocidad real con grados de dirección azimutal. Se truncaron mediante `limpiar_viento()` los valores superiores a $15\text{ m/s}$ por ser atípicos en cuenca cerrada.
    """)
    
with tab2:
    st.write("Recuento de valores válidos (no nulos) por estación de monitoreo en el período de estudio:")
    df_missing = df.groupby('Estacion')[['MP2_5', 'Temperatura_C', 'Viento_ms']].count().reset_index()
    st.dataframe(df_missing, use_container_width=True)

st.markdown("### 3. Muestra de Datos Preprocesados (Vista Parcial)")
st.dataframe(df.sample(5).sort_values('Fecha'), use_container_width=True)
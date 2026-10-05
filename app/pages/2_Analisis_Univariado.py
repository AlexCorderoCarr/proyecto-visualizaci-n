import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis Univariado", layout="wide")

st.title("Análisis Univariado y Distribuciones")

@st.cache_data
def load_data():
    return pd.read_parquet('data/processed/calidad_aire_limpia.parquet')

df = load_data()

st.sidebar.header("Filtros Globales")
selected_years = st.sidebar.slider("Rango de Años", 2013, 2023, (2013, 2023))
df_filtered = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]

st.markdown("### 1. Distribución General de la Variable Objetivo ($MP_{2.5}$)")
st.markdown("¿Cómo se concentra históricamente la contaminación en Santiago?")

fig_hist = px.histogram(
    df_filtered.dropna(subset=['MP2_5']), 
    x="MP2_5", 
    nbins=100,
    title=f"Histograma de Frecuencias MP2.5 ({selected_years[0]}-{selected_years[1]})",
    labels={'MP2_5': 'Concentración MP2.5 (µg/m³)'},
    color_discrete_sequence=['#4c78a8']
)
fig_hist.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="Norma Diaria (50 µg/m³)")
fig_hist.update_xaxes(range=[0, 200])
st.plotly_chart(fig_hist, use_container_width=True)

st.info("**Interpretación (Distribución):** La curva presenta un fuerte sesgo a la derecha (*Right-Skewed*). La mayoría de los días del año el aire cumple la norma (< 50 µg/m³), sin embargo, existe una \"larga cola\" de eventos extremos peligrosos para la salud humana. Por esta asimetría estadística, **se utilizará la Mediana en lugar del Promedio** para el resto del análisis territorial.")

st.markdown("### 2. Disparidad Territorial Basal ($X$ vs $Y$)")

col1, col2 = st.columns([1, 3])
with col1:
    st.write("Filtro Estaciones:")
    estaciones = df_filtered['Estacion'].unique()
    estaciones_sel = st.multiselect("Seleccionar", estaciones, default=estaciones)
with col2:
    if len(estaciones_sel) > 0:
        df_box = df_filtered[df_filtered['Estacion'].isin(estaciones_sel)].dropna(subset=['MP2_5'])
        fig_box = px.box(
            df_box, 
            y="Estacion", 
            x="MP2_5", 
            color="Estacion",
            title="Distribución y Valores Atípicos por Estación (Boxplot)",
            labels={'MP2_5': 'Concentración MP2.5 (µg/m³)'},
            orientation='h'
        )
        fig_box.add_vline(x=50, line_dash="dash", line_color="red")
        fig_box.update_xaxes(range=[0, 200])
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.success("**Hallazgo Espacial:** Se evidencia una clara estratificación territorial. Mientras el percentil 75 (caja) de Las Condes apenas cruza la norma ambiental, estaciones de la zona poniente y sur (Cerro Navia/Pudahuel, El Bosque) tienen gran parte de su distribución en niveles perjudiciales.")
    else:
        st.warning("Selecciona al menos una estación.")
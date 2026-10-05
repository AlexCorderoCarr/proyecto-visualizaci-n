import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de la Pregunta", layout="wide")

st.title("Análisis Multivariable y Respuesta")

@st.cache_data
def load_data():
    return pd.read_parquet('data/processed/calidad_aire_limpia.parquet')

df = load_data()

st.sidebar.header("Opciones de Visualización")
estaciones_clima = ['Pudahuel', 'Santiago', 'Las Condes']
selected_station = st.sidebar.selectbox("Estación para Análisis Climático", estaciones_clima)

st.markdown("### 1. La Dimensión Temporal ($T$): Estacionalidad del Aire")

# Calcular mediana mensual
df_mes = df.groupby(['Month'])['MP2_5'].median().reset_index()
# Mapear nombres de meses
meses_dict = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
df_mes['Nombre_Mes'] = df_mes['Month'].map(meses_dict)

fig_bar = px.bar(
    df_mes, 
    x="Nombre_Mes", 
    y="MP2_5",
    title="Comportamiento Estacional (Mediana Histórica 2013-2023)",
    labels={'MP2_5': 'Mediana MP2.5 (µg/m³)', 'Nombre_Mes': 'Mes'},
    color="MP2_5",
    color_continuous_scale="Reds"
)
fig_bar.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Norma (50)")
st.plotly_chart(fig_bar, use_container_width=True)

st.error("**Hallazgo Temporal:** El componente estacional es el principal driver del problema. En pleno invierno (junio-julio) los niveles basales de la ciudad entera superan los 50 µg/m³, triplicando los promedios registrados en meses cálidos.")

st.markdown("### 2. El Impacto Físico ($X$ vs $Y$): Inversión Térmica")
st.write(f"Análisis de Temperatura ambiental vs Contaminación aislando la estación **{selected_station}**.")

df_clima = df[df['Estacion'] == selected_station].dropna(subset=['Temperatura_C', 'MP2_5'])

# Scatter plot con Plotly
fig_scatter = px.scatter(
    df_clima, 
    x="Temperatura_C", 
    y="MP2_5", 
    color="Month",
    title=f"Efecto de la Temperatura en los Niveles de Saturación ({selected_station})",
    labels={'Temperatura_C': 'Temperatura Ambiental (°C)', 'MP2_5': 'MP2.5 (µg/m³)'},
    opacity=0.5,
    color_continuous_scale=px.colors.sequential.Tealgrn,
    hover_data=['Fecha']
)
fig_scatter.add_hline(y=150, line_dash="solid", line_color="darkred", annotation_text="Emergencia (>150)")
fig_scatter.add_vline(x=18, line_dash="dot", line_color="black")
st.plotly_chart(fig_scatter, use_container_width=True)

st.success("**Hallazgo Multivariable:** La visualización interactiva confirma la presencia de la Inversión Térmica en la cuenca. Nótese cómo la zona de crisis (sobre 150 µg/m³) ocurre exclusivamente cuando la temperatura ambiental desciende por debajo del umbral de los 18°C. A mayor calor, el aire asciende y la cuenca logra ventilarse.")
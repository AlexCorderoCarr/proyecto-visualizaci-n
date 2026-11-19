"""Página 5 (Respaldo EDA): Estacionalidad, inversión térmica y ventilación (2018-2023)."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

APP_DIR = str(Path(__file__).resolve().parents[1])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils import (
    ESTACIONES_MODELO,
    MESES_CORTOS,
    NORMA_DIARIA_MP25,
    UMBRAL_ALERTA_MP25,
    load_clean_data,
)

st.set_page_config(page_title="EDA · Análisis Multivariable", layout="wide")

df = load_clean_data()

st.title("EDA · Estacionalidad, Inversión Térmica y Ventilación (2018–2023)")
st.caption("Relaciones físicas que justifican las 5 variables seleccionadas para el modelo Random Forest.")

st.sidebar.header("Controles Multivariables")
estaciones_todas = ["Todas (5 estaciones)"] + sorted(df["Estacion"].unique().tolist())
filtro_est = st.sidebar.selectbox("Estación para estacionalidad mensual", estaciones_todas)
selected_station = st.sidebar.selectbox("Estación para análisis climático", ESTACIONES_MODELO)

st.markdown("### 1. La Dimensión Temporal ($T$): Estacionalidad Invernal")

df_estac = df if filtro_est.startswith("Todas") else df[df["Estacion"] == filtro_est]
df_mes = (
    df_estac.dropna(subset=["MP2_5"])
    .groupby("Month")["MP2_5"]
    .agg(Mediana="median", Pct_Sobre_Norma=lambda s: (s > NORMA_DIARIA_MP25).mean() * 100)
    .reset_index()
)
df_mes["Nombre_Mes"] = df_mes["Month"].map(MESES_CORTOS)
df_mes = df_mes.sort_values("Month")

c1, c2 = st.columns(2)
with c1:
    fig_bar = px.bar(
        df_mes,
        x="Nombre_Mes",
        y="Mediana",
        color="Mediana",
        color_continuous_scale="Reds",
        text_auto=".1f",
        title=f"Mediana Mensual de MP2.5 ({filtro_est})",
        labels={"Mediana": "Mediana MP2.5 (µg/m³)", "Nombre_Mes": "Mes"},
    )
    fig_bar.add_hline(y=NORMA_DIARIA_MP25, line_dash="dash", line_color="red", annotation_text="Norma (50)")
    fig_bar.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_pct = px.bar(
        df_mes,
        x="Nombre_Mes",
        y="Pct_Sobre_Norma",
        color="Pct_Sobre_Norma",
        color_continuous_scale="OrRd",
        text_auto=".1f",
        title=f"% de Días Sobre la Norma (> 50 µg/m³) ({filtro_est})",
        labels={"Pct_Sobre_Norma": "% Días > 50 µg/m³", "Nombre_Mes": "Mes"},
    )
    fig_pct.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_pct, use_container_width=True)

st.error(
    "**Hallazgo temporal:** Entre **mayo y agosto**, la mediana mensual de la ciudad supera los **32–41 µg/m³** "
    "(triplicando la mediana estival de 13–14 µg/m³), concentrando prácticamente todos los días sobre la norma de 50 µg/m³."
)

st.markdown(f"### 2. Impacto Físico en **{selected_station}**: Inversión Térmica y Ventilación")

df_clima = df[df["Estacion"] == selected_station].dropna(subset=["Temperatura_C", "Viento_ms", "MP2_5"]).copy()
df_clima["Mes"] = df_clima["Month"].map(MESES_CORTOS)

sc1, sc2 = st.columns(2)
with sc1:
    fig_temp = px.scatter(
        df_clima,
        x="Temperatura_C",
        y="MP2_5",
        color="Month",
        opacity=0.55,
        hover_data=["Fecha", "Mes", "Humedad", "Viento_ms"],
        color_continuous_scale="RdYlBu_r",
        title=f"Inversión Térmica: Temperatura vs. MP2.5 ({selected_station})",
        labels={"Temperatura_C": "Temperatura promedio diaria (°C)", "MP2_5": "MP2.5 (µg/m³)"},
    )
    fig_temp.add_hline(y=NORMA_DIARIA_MP25, line_dash="dash", line_color="red", annotation_text="Norma (50)")
    fig_temp.add_hline(y=UMBRAL_ALERTA_MP25, line_dash="dot", line_color="#b71c1c", annotation_text="Alerta (80)")
    fig_temp.add_vline(x=13, line_dash="dot", line_color="gray", annotation_text="Umbral frío (~13°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

with sc2:
    fig_wind = px.scatter(
        df_clima,
        x="Viento_ms",
        y="MP2_5",
        color="Month",
        opacity=0.55,
        hover_data=["Fecha", "Mes", "Temperatura_C", "Humedad"],
        color_continuous_scale="RdYlBu_r",
        title=f"Ventilación: Velocidad del Viento vs. MP2.5 ({selected_station})",
        labels={"Viento_ms": "Velocidad del viento diaria (m/s)", "MP2_5": "MP2.5 (µg/m³)"},
    )
    fig_wind.add_hline(y=NORMA_DIARIA_MP25, line_dash="dash", line_color="red", annotation_text="Norma (50)")
    fig_wind.add_hline(y=UMBRAL_ALERTA_MP25, line_dash="dot", line_color="#b71c1c", annotation_text="Alerta (80)")
    fig_wind.add_vline(x=0.5, line_dash="dot", line_color="gray", annotation_text="Calma (<0.5 m/s)")
    st.plotly_chart(fig_wind, use_container_width=True)

st.success(
    "**Hallazgo físico clave para el modelado:** Los episodios sobre 50 y 80 µg/m³ ocurren en una relación "
    "**no lineal**: se disparan cuando convergen **bajas temperaturas (< 12–13 °C)** y **viento muy débil (< 0.5 m/s)**. "
    "Esta interacción explica por qué el Random Forest supera ampliamente a las regresiones lineales."
)

"""Página 4 (Respaldo EDA): Distribuciones y brecha territorial de MP2.5 (2018-2023)."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

APP_DIR = str(Path(__file__).resolve().parents[1])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils import NORMA_DIARIA_MP25, UMBRAL_ALERTA_MP25, load_clean_data

st.set_page_config(page_title="EDA · Análisis Univariado", layout="wide")

df = load_clean_data()

st.title("EDA · Análisis Univariado y Brecha Territorial (2018–2023)")
st.caption("Distribución real de MP2.5 en µg/m³ y comparación entre las 5 estaciones de Santiago.")

st.sidebar.header("Filtros del EDA")
selected_years = st.sidebar.slider("Rango de Años", 2018, 2023, (2018, 2023))
df_filtered = df[(df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1])]

st.markdown("### 1. Distribución General de la Variable Objetivo ($MP_{2.5}$)")
df_mp = df_filtered.dropna(subset=["MP2_5"])

fig_hist = px.histogram(
    df_mp,
    x="MP2_5",
    nbins=60,
    title=f"Distribución de Frecuencias Diarias de MP2.5 ({selected_years[0]}–{selected_years[1]})",
    labels={"MP2_5": "Concentración MP2.5 (µg/m³)"},
    color_discrete_sequence=["#4c78a8"],
)
fig_hist.add_vline(
    x=NORMA_DIARIA_MP25,
    line_dash="dash",
    line_color="red",
    annotation_text="Norma Diaria (50 µg/m³)",
)
fig_hist.add_vline(
    x=UMBRAL_ALERTA_MP25,
    line_dash="dot",
    line_color="#b71c1c",
    annotation_text="Alerta (80 µg/m³)",
)
fig_hist.update_xaxes(range=[0, 150])
fig_hist.update_layout(yaxis_title="Cantidad de días-estación")
st.plotly_chart(fig_hist, use_container_width=True)

pct_sobre = float((df_mp["MP2_5"] > NORMA_DIARIA_MP25).mean() * 100) if len(df_mp) else 0.0
st.info(
    f"**Interpretación estadística:** La distribución presenta fuerte sesgo positivo (*right-skewed*): "
    f"la mayoría de los días cumple la norma, pero un **{pct_sobre:.1f}%** de las mediciones supera los **50 µg/m³**, "
    f"concentrando episodios críticos en una cola derecha hasta **145 µg/m³**. Por esta asimetría se utiliza la **Mediana** "
    f"como indicador principal."
)

st.markdown("### 2. Disparidad Territorial Basal ($X$ vs. $Y$)")
col1, col2 = st.columns([1, 3])
with col1:
    estaciones = sorted(df_filtered["Estacion"].unique())
    estaciones_sel = st.multiselect("Seleccionar estaciones", estaciones, default=estaciones)

with col2:
    if estaciones_sel:
        df_box = df_filtered[df_filtered["Estacion"].isin(estaciones_sel)].dropna(subset=["MP2_5"])
        orden_est = (
            df_box.groupby("Estacion")["MP2_5"]
            .median()
            .sort_values(ascending=True)
            .index.tolist()
        )
        fig_box = px.box(
            df_box,
            y="Estacion",
            x="MP2_5",
            color="Estacion",
            category_orders={"Estacion": orden_est},
            title="Distribución de MP2.5 por Estación de Monitoreo",
            labels={"MP2_5": "Concentración MP2.5 (µg/m³)", "Estacion": ""},
            orientation="h",
        )
        fig_box.add_vline(
            x=NORMA_DIARIA_MP25,
            line_dash="dash",
            line_color="red",
            annotation_text="Norma (50)",
        )
        fig_box.add_vline(
            x=UMBRAL_ALERTA_MP25,
            line_dash="dot",
            line_color="#b71c1c",
            annotation_text="Alerta (80)",
        )
        fig_box.update_xaxes(range=[0, 150])
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

        resumen_est = (
            df_box.groupby("Estacion")["MP2_5"]
            .agg(
                Mediana="median",
                Promedio="mean",
                Percentil_90=lambda s: s.quantile(0.90),
                Dias_Sobre_50=lambda s: int((s > 50).sum()),
                Pct_Sobre_50=lambda s: (s > 50).mean() * 100,
                Dias_Alerta_80_o_mas=lambda s: int((s >= 80).sum()),
            )
            .round(1)
            .sort_values("Mediana", ascending=False)
            .reset_index()
        )
        st.dataframe(resumen_est, use_container_width=True, hide_index=True)

        st.success(
            "**Hallazgo espacial:** Existe una brecha clara entre el sector **Sur/Poniente** (*El Bosque* y *Pudahuel*, "
            "con la mayor frecuencia de días sobre norma y episodios ≥ 80 µg/m³) y el sector **Oriente** (*Las Condes*, "
            "donde rara vez se supera la norma diaria)."
        )
    else:
        st.warning("Selecciona al menos una estación.")

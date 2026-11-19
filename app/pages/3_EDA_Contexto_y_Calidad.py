"""Página 3 (Respaldo EDA): Contexto, auditoría 2013-2023 y calidad de sensores."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = str(Path(__file__).resolve().parents[1])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils import load_audit_data, load_clean_data

st.set_page_config(page_title="EDA · Contexto y Calidad", layout="wide")

df = load_clean_data()
audit = load_audit_data()

st.title("EDA · Contexto y Calidad de los Datos (2018–2023)")
st.caption("Respaldo técnico de la depuración del dataset SINCA antes del análisis y modelado final.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros Válidos (2018–2023)", f"{len(df):,}", f"De {audit['filas_2013_2023']:,} en 2013–2023")
col2.metric("Rango Temporal Homogéneo", "2018 – 2023", f"{audit['fecha_min_2018_2023']} a {audit['fecha_max_2018_2023']}")
col3.metric("Estaciones de Monitoreo", df["Estacion"].nunique(), "3 con meteorología completa")
col4.metric("Variables Consolidadas", df.shape[1], "Incluye indicadores norma MMA")

st.info(
    "**Estrategia de integridad estadística:** *El Bosque* y *La Florida* disponen de material particulado "
    "($MP_{2.5}$ y $MP_{10}$) pero carecen de sensores meteorológicos en el archivo SINCA. Por eso el análisis "
    "territorial usa las **5 estaciones**, mientras que el análisis climático y el modelo predictivo operan sobre "
    "las **3 estaciones con meteorología completa** (*Pudahuel*, *Santiago*, *Las Condes*)."
)

tab1, tab2, tab3 = st.tabs(
    [
        "Auditoría 2013–2023 (Corte en 2018)",
        "Reglas de Decodificación de Sensores",
        "Cobertura por Estación (3 vs. 5)",
    ]
)

with tab1:
    df_anual = pd.DataFrame(audit["resumen_anual_2013_2023"])
    df_anual["Tramo"] = df_anual["es_rango_homogeneo"].map(
        {True: "Tramo homogéneo usado (2018–2023)", False: "Escala desfasada excluida (2013–2017)"}
    )
    fig_audit = px.bar(
        df_anual,
        x="year",
        y="mp25_mediana",
        color="Tramo",
        text="mp25_mediana",
        title="Mediana anual de MP2.5 en el archivo original (evidencia del salto de escala previo a mayo 2017)",
        labels={"year": "Año", "mp25_mediana": "Mediana MP2.5"},
        color_discrete_map={
            "Escala desfasada excluida (2013–2017)": "#b0bec5",
            "Tramo homogéneo usado (2018–2023)": "#1f4e78",
        },
    )
    fig_audit.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    st.plotly_chart(fig_audit, use_container_width=True)
    st.markdown(
        """
        En el archivo crudo de SINCA, los registros previos a mayo de 2017 arrastran un corrimiento decimal en la
        lectura (medianas entre **177 y 206** y máximos cercanos a **1.000**). Desde **2018 a 2023**, la serie es
        totalmente consistente con la realidad física de Santiago (mediana entre **17 y 20 µg/m³** y máximo de **145 µg/m³**).
        """
    )

with tab2:
    st.markdown(
        """
        En el tramo válido **2018–2023** se aplicaron reglas físicas determinísticas en `src/data_cleaning.py` para
        corregir las potencias de 10 introducidas por la exportación cruda de sensores:
        - **Temperatura (`Temperatura_C`):** valores `≤ 30` se conservan en °C; entre `30` y `260` se dividen por `10`; sobre `260` se dividen por `100` (rango final resultante: `0.3 °C` a `26.8 °C`).
        - **Humedad relativa (`Humedad`):** valores `≤ 100` se conservan en `%`; valores `> 100` (escalados ×10) se dividen por `10` (rango final: `10%` a `100%`).
        - **Velocidad del viento (`Viento_ms`):** valores `< 10` se conservan en `m/s`; entre `10` y `100` se dividen por `10`; `≥ 100` se dividen por `100` (rango final: `0.00 m/s` a `3.95 m/s`).
        """
    )
    resumen_vars = (
        df[["MP2_5", "MP10", "Temperatura_C", "Humedad", "Viento_ms"]]
        .describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
        .T[["count", "min", "25%", "50%", "75%", "max"]]
        .round(2)
        .reset_index()
        .rename(columns={"index": "Variable", "count": "Válidos", "50%": "Mediana"})
    )
    st.dataframe(resumen_vars, use_container_width=True, hide_index=True)

with tab3:
    st.write("Conteo de observaciones válidas por estación en el período depurado **2018–2023**:")
    df_cov = pd.DataFrame(audit["validos_por_estacion_2018_2023"])
    st.dataframe(df_cov, use_container_width=True, hide_index=True)

st.markdown("### Muestra del Dataset Depurado (2018–2023)")
st.dataframe(
    df[["Fecha", "Estacion", "MP2_5", "MP10", "Temperatura_C", "Humedad", "Viento_ms", "Categoria_MP25"]]
    .dropna(subset=["Temperatura_C"])
    .tail(8),
    use_container_width=True,
    hide_index=True,
)

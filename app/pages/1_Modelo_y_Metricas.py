"""Página 1: Evaluación del modelo final y comparación justa contra referencias base."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = str(Path(__file__).resolve().parents[1])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils import (
    ESTACIONES_MODELO,
    NORMA_DIARIA_MP25,
    load_model_metadata,
    load_test_predictions,
)

st.set_page_config(page_title="Modelo y Métricas | MP2.5", layout="wide")

meta = load_model_metadata()
df_preds = load_test_predictions()
split = meta["split"]
mejoras = meta["mejoras"]

st.title("Modelo Predictivo Final y Comparación con Soluciones Base")
st.caption(
    "Evaluación justa sobre el mismo conjunto futuro de prueba (2022–2023) para comprobar "
    "cuánto valor agrega el Random Forest respecto a referencias de baja complejidad."
)

# Identificación explícita del problema y conjunto de evaluación
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tipo de Problema", "Regresión", "Objetivo: MP2.5 (µg/m³)")
    c2.metric("Conjunto Entrenamiento", f"{split['n_train']:,} obs.", f"Período {split['train_years']}")
    c3.metric("Conjunto Prueba (Común)", f"{split['n_test']:,} obs.", f"Período {split['test_years']}")
    c4.metric("Estaciones Cubiertas", "3 estaciones", "Pudahuel, Santiago, Las Condes")
    st.caption(
        f"**Entradas del modelo (5 variables):** Estación de monitoreo, Mes (`Month`), Temperatura (`°C`), "
        f"Humedad relativa (`%`) y Velocidad del viento (`m/s`). Partición temporal estricta: entrenamiento "
        f"{split['train_fecha_min']} a {split['train_fecha_max']} y evaluación futura "
        f"{split['test_fecha_min']} a {split['test_fecha_max']}."
    )

st.markdown("### Ganancia del Modelo Final frente a Soluciones Base")
k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "Reducción RMSE vs. Media",
    f"-{mejoras['vs_media']['reduccion_rmse_pct']:.1f}%",
    f"De {meta['metricas_comparacion'][0]['RMSE']:.2f} a {meta['metricas_comparacion'][3]['RMSE']:.2f} µg/m³",
)
k2.metric(
    "Reducción MAE vs. Media",
    f"-{mejoras['vs_media']['reduccion_mae_pct']:.1f}%",
    f"De {meta['metricas_comparacion'][0]['MAE']:.2f} a {meta['metricas_comparacion'][3]['MAE']:.2f} µg/m³",
)
k3.metric(
    "Reducción RMSE vs. Reg. 1 Var",
    f"-{mejoras['vs_reg_1var']['reduccion_rmse_pct']:.1f}%",
    f"De {meta['metricas_comparacion'][1]['RMSE']:.2f} a {meta['metricas_comparacion'][3]['RMSE']:.2f} µg/m³",
)
k4.metric(
    "Salto en R² (vs. Reg. Lineal Múlt.)",
    f"+{mejoras['vs_reg_multiple']['ganancia_r2']:.3f}",
    f"Lineal {meta['metricas_comparacion'][2]['R2']:.3f} → RF {meta['metricas_comparacion'][3]['R2']:.3f}",
)

st.markdown("### Tabla Comparativa Oficial (Mismas 1.635 Observaciones de Prueba)")
df_metrics = pd.DataFrame(meta["metricas_comparacion"]).rename(
    columns={
        "MAE": "MAE (µg/m³)",
        "RMSE": "RMSE (µg/m³)",
        "MAPE": "MAPE (%)",
        "R2": "R²",
    }
)


def highlight_final_row(row: pd.Series) -> list[str]:
    if "Random Forest" in str(row["Modelo"]):
        return ["background-color: #e8f5e9; font-weight: bold; color: #1b5e20"] * len(row)
    return [""] * len(row)


styled_table = (
    df_metrics[["Modelo", "Tipo", "Variables", "MAE (µg/m³)", "RMSE (µg/m³)", "MAPE (%)", "R²"]]
    .style.apply(highlight_final_row, axis=1)
    .format(
        {
            "MAE (µg/m³)": "{:.2f}",
            "RMSE (µg/m³)": "{:.2f}",
            "MAPE (%)": "{:.1f}%",
            "R²": "{:.3f}",
        }
    )
)
st.dataframe(styled_table, use_container_width=True, hide_index=True)

col_int1, col_int2 = st.columns(2)
with col_int1:
    st.success(
        f"""
        **Por qué mejora el Random Forest y para qué sirve:**
        - **Media de entrenamiento ({meta['y_train_mean']:.2f} µg/m³):** ignora totalmente el clima y la época del año (`R² ≈ 0.000`).
        - **Regresión con 1 variable (`Temperatura_C`):** captura solo la tendencia lineal inversa (`R² = 0.181`).
        - **Regresión Lineal Múltiple (`R² = 0.292`):** mejora al sumar estación y mes, pero asume efectos aditivos lineales.
        - **Random Forest Final (`R² = 0.496`, `MAE = 8.09 µg/m³`):** captura **interacciones no lineales**
          (ej. frío intenso + viento casi nulo en Pudahuel durante invierno = disparo de $MP_{{2.5}}$), reduciendo
          el RMSE en **{mejoras['vs_media']['reduccion_rmse_pct']:.1f}%** frente a la media y en
          **{mejoras['vs_reg_1var']['reduccion_rmse_pct']:.1f}%** frente a la regresión simple.
        """
    )

with col_int2:
    st.warning(
        """
        **Limitaciones que conserva el modelo:**
        - **Sin eventos extraordinarios ni emisiones puntuales:** al usar solo clima, mes y estación, no detecta
          incendios forestales, humaredas puntuales o cambios de tráfico, por lo que tiende a suavizar picos extremos.
        - **Cobertura espacial limitada a 3 estaciones:** *El Bosque* y *La Florida* no cuentan con sensores de
          temperatura, humedad y viento en SINCA, por lo que quedan excluidas del predictor.
        - **Resolución diaria:** trabaja con promedios diarios; las alzas horarias nocturnas se promedian en el día.
        """
    )

st.divider()

tab1, tab2, tab3 = st.tabs(
    [
        "Comparación visual de métricas",
        "Real vs. Predicho en Prueba (2022–2023)",
        "Importancia de variables",
    ]
)

with tab1:
    c_left, c_right = st.columns(2)
    with c_left:
        df_err = df_metrics.melt(
            id_vars="Modelo",
            value_vars=["MAE (µg/m³)", "RMSE (µg/m³)"],
            var_name="Métrica",
            value_name="Error (µg/m³)",
        )
        fig_err = px.bar(
            df_err,
            x="Modelo",
            y="Error (µg/m³)",
            color="Métrica",
            barmode="group",
            title="Comparación de Error (menor es mejor)",
            text_auto=".2f",
            color_discrete_sequence=["#5c8ab8", "#1f4e78"],
        )
        fig_err.update_layout(xaxis_title="", legend_title="")
        st.plotly_chart(fig_err, use_container_width=True)

    with c_right:
        fig_r2 = px.bar(
            df_metrics,
            x="Modelo",
            y="R²",
            color="R²",
            color_continuous_scale="Teal",
            title="Varianza Explicada R² (mayor es mejor)",
            text_auto=".3f",
        )
        fig_r2.update_layout(xaxis_title="", coloraxis_showscale=False)
        fig_r2.update_yaxes(range=[-0.05, 0.65])
        st.plotly_chart(fig_r2, use_container_width=True)

with tab2:
    est_sel = st.multiselect(
        "Filtrar estaciones en el conjunto de prueba (2022–2023):",
        ESTACIONES_MODELO,
        default=ESTACIONES_MODELO,
    )
    df_p = df_preds[df_preds["Estacion"].isin(est_sel)] if est_sel else df_preds
    max_axis = float(max(df_p["y_real"].max(), df_p["pred_rf"].max(), 90)) + 5

    fig_scatter = px.scatter(
        df_p,
        x="y_real",
        y="pred_rf",
        color="Estacion",
        opacity=0.6,
        hover_data=["Fecha", "Temperatura_C", "Humedad", "Viento_ms"],
        labels={
            "y_real": "MP2.5 Real observado (µg/m³)",
            "pred_rf": "MP2.5 Predicho por Random Forest (µg/m³)",
        },
        title="Random Forest: Valor Real vs. Predicho (Conjunto de Prueba 2022–2023)",
    )
    fig_scatter.add_trace(
        go.Scatter(
            x=[0, max_axis],
            y=[0, max_axis],
            mode="lines",
            name="Predicción ideal (y = x)",
            line=dict(color="black", dash="dash"),
        )
    )
    fig_scatter.add_vline(
        x=NORMA_DIARIA_MP25,
        line_dash="dot",
        line_color="crimson",
        annotation_text="Norma diaria (50)",
    )
    fig_scatter.add_hline(y=NORMA_DIARIA_MP25, line_dash="dot", line_color="crimson")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    imp_df = pd.DataFrame(
        {
            "Variable": list(meta["importancia_variables_pct"].keys()),
            "Importancia (%)": list(meta["importancia_variables_pct"].values()),
        }
    ).sort_values("Importancia (%)", ascending=True)
    nombres_legibles = {
        "Temperatura_C": "Temperatura (°C)",
        "Month": "Mes del año",
        "Estacion": "Estación / Comuna",
        "Viento_ms": "Velocidad del viento (m/s)",
        "Humedad": "Humedad relativa (%)",
    }
    imp_df["Variable legible"] = imp_df["Variable"].map(nombres_legibles)

    fig_imp = px.bar(
        imp_df,
        x="Importancia (%)",
        y="Variable legible",
        orientation="h",
        text_auto=".1f",
        title="Peso relativo de cada entrada en el Random Forest (%)",
        color="Importancia (%)",
        color_continuous_scale="Blues",
    )
    fig_imp.update_layout(yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig_imp, use_container_width=True)

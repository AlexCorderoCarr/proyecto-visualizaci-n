"""Página 2: Simulador operativo y predicción en vivo con Random Forest."""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = str(Path(__file__).resolve().parents[1])
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils import (
    ESTACIONES_MODELO,
    MESES_NOMBRES,
    NORMA_DIARIA_MP25,
    UMBRAL_ALERTA_MP25,
    clasificar_mp25,
    load_model,
    load_model_metadata,
)

st.set_page_config(page_title="Predicción en Vivo | MP2.5", layout="wide")

model = load_model()
meta = load_model_metadata()

st.title("Simulador de Alerta Temprana: Predicción en Vivo ($MP_{2.5}$)")
st.caption(
    "Modelo cargado: `models/rf_mp25_model.joblib` (Random Forest · 200 árboles · entrenado 2018–2021)."
)

# Estado inicial de controles para permitir escenarios rápidos modificables en vivo
DEFAULTS = {
    "pred_estacion": "Pudahuel",
    "pred_mes": 6,
    "pred_temp": 6.0,
    "pred_hum": 85.0,
    "pred_viento": 0.20,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

ESCENARIOS = {
    "Invierno crítico (Pudahuel)": {
        "pred_estacion": "Pudahuel",
        "pred_mes": 6,
        "pred_temp": 6.0,
        "pred_hum": 85.0,
        "pred_viento": 0.20,
    },
    "Mismo clima en Las Condes": {
        "pred_estacion": "Las Condes",
        "pred_mes": 6,
        "pred_temp": 6.0,
        "pred_hum": 85.0,
        "pred_viento": 0.20,
    },
    "Invierno moderado (Santiago)": {
        "pred_estacion": "Santiago",
        "pred_mes": 7,
        "pred_temp": 7.5,
        "pred_hum": 80.0,
        "pred_viento": 0.35,
    },
    "Verano ventilado (Pudahuel)": {
        "pred_estacion": "Pudahuel",
        "pred_mes": 1,
        "pred_temp": 22.0,
        "pred_hum": 45.0,
        "pred_viento": 1.50,
    },
}

st.markdown("#### Escenarios de demostración rápida (luego puedes ajustar cualquier control)")
btn_cols = st.columns(len(ESCENARIOS))
for col, (label, vals) in zip(btn_cols, ESCENARIOS.items()):
    with col:
        if st.button(label, use_container_width=True):
            for k, v in vals.items():
                st.session_state[k] = v
            st.rerun()

st.divider()

col_in, col_out = st.columns([1, 1.35], gap="large")

with col_in:
    st.subheader("1. Condiciones de entrada")
    estacion = st.selectbox(
        "Estación de monitoreo (Comuna)",
        options=ESTACIONES_MODELO,
        key="pred_estacion",
    )
    mes = st.selectbox(
        "Mes del año",
        options=list(MESES_NOMBRES.keys()),
        format_func=lambda m: f"{m:02d} · {MESES_NOMBRES[m]}",
        key="pred_mes",
    )
    temperatura = st.slider(
        "Temperatura promedio diaria (°C)",
        min_value=1.0,
        max_value=26.0,
        step=0.5,
        key="pred_temp",
        help="Rango observado 2018–2023: 0.3 °C a 26.8 °C.",
    )
    humedad = st.slider(
        "Humedad relativa promedio (%)",
        min_value=15.0,
        max_value=100.0,
        step=1.0,
        key="pred_hum",
        help="Rango observado 2018–2023: 10% a 100%.",
    )
    viento = st.slider(
        "Velocidad del viento promedio diaria (m/s)",
        min_value=0.0,
        max_value=3.5,
        step=0.05,
        key="pred_viento",
        help="Valores bajo 0.4 m/s reflejan estancamiento severo en la cuenca.",
    )

    st.caption(
        "Nota: Las Condes, Santiago y Pudahuel representan el gradiente Oriente → Centro → Poniente de la cuenca."
    )

# Inferencia real ejecutada en vivo
X_input = pd.DataFrame(
    [
        {
            "Estacion": estacion,
            "Month": int(mes),
            "Temperatura_C": float(temperatura),
            "Humedad": float(humedad),
            "Viento_ms": float(viento),
        }
    ]
)
pred_val = float(model.predict(X_input)[0])
categoria = clasificar_mp25(pred_val)
delta_norma = pred_val - NORMA_DIARIA_MP25
mediana_hist = float(meta["medianas_historicas_estacion_mes"][estacion][str(int(mes))])
delta_hist = pred_val - mediana_hist

with col_out:
    st.subheader("2. Resultado de la predicción en vivo")

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Concentración Estimada (MP2.5)",
        f"{pred_val:.1f} µg/m³",
        f"{delta_norma:+.1f} µg/m³ vs. norma (50)",
        delta_color="inverse",
    )
    m2.metric(
        f"Mediana histórica ({MESES_NOMBRES[mes]})",
        f"{mediana_hist:.1f} µg/m³",
        f"{delta_hist:+.1f} µg/m³ vs. histórico",
        delta_color="off",
    )
    m3.metric(
        "Estado Calidad del Aire (MMA)",
        categoria["nivel"],
        "Supera norma diaria" if pred_val > NORMA_DIARIA_MP25 else "Dentro de norma",
        delta_color="inverse" if pred_val > NORMA_DIARIA_MP25 else "normal",
    )

    st.markdown(
        f"""
        <div style="background-color:{categoria['bg']}; border-left: 6px solid {categoria['color']};
                    padding: 12px 16px; border-radius: 6px; margin-bottom: 12px;">
            <strong style="color:{categoria['color']}; font-size: 1.05rem;">
                Nivel estimado: {categoria['nivel']} ({pred_val:.1f} µg/m³)
            </strong><br/>
            <span style="color:#222222;">{categoria['descripcion']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pred_val,
            number={"suffix": " µg/m³", "valueformat": ".1f"},
            title={"text": f"Escala MP2.5 diaria — {estacion} ({MESES_NOMBRES[mes]})"},
            gauge={
                "axis": {"range": [0, 140], "tickwidth": 1},
                "bar": {"color": categoria["color"]},
                "steps": [
                    {"range": [0, 50], "color": "#dcedc8"},
                    {"range": [50, 80], "color": "#fff9c4"},
                    {"range": [80, 110], "color": "#ffe0b2"},
                    {"range": [110, 140], "color": "#ffcdd2"},
                ],
                "threshold": {
                    "line": {"color": "#b71c1c", "width": 3},
                    "thickness": 0.8,
                    "value": NORMA_DIARIA_MP25,
                },
            },
        )
    )
    fig_gauge.update_layout(height=270, margin=dict(l=25, r=25, t=55, b=15))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Interpretación contextual dinámica
    factores = []
    if mes in (5, 6, 7, 8):
        factores.append("mes frío propenso a inversión térmica")
    else:
        factores.append("mes de mayor radiación y altura de capa de mezcla")
    if temperatura <= 10:
        factores.append(f"baja temperatura ({temperatura:.1f} °C)")
    elif temperatura >= 18:
        factores.append(f"temperatura alta ({temperatura:.1f} °C) que favorece dispersión")
    if viento <= 0.35:
        factores.append(f"viento débil ({viento:.2f} m/s, escasa ventilación)")
    elif viento >= 1.0:
        factores.append(f"buena ventilación ({viento:.2f} m/s)")

    st.info(
        f"**Interpretación en contexto:** En **{estacion}** durante **{MESES_NOMBRES[mes]}**, "
        f"combinar {', '.join(factores)} proyecta un nivel promedio diario de **{pred_val:.1f} µg/m³** "
        f"(frente a la norma chilena de **{NORMA_DIARIA_MP25:.0f} µg/m³** y umbral de alerta de **{UMBRAL_ALERTA_MP25:.0f} µg/m³**). "
        f"En la práctica, este resultado orienta medidas preventivas de calidad del aire cuando el valor se acerca o supera los 50 µg/m³."
    )

    if mes in (6, 7, 8) and temperatura > 18:
        st.warning(
            "Combinación climática poco frecuente: temperatura > 18 °C en invierno no es habitual en el histórico 2018–2023; la predicción extrapola fuera del patrón típico invernal."
        )
    elif mes in (12, 1, 2) and temperatura < 9:
        st.warning(
            "Combinación climática poco frecuente: temperatura < 9 °C en verano es atípica en el histórico 2018–2023."
        )

st.divider()
with st.expander("Condiciones y limitaciones relevantes de uso del predictor", expanded=True):
    st.markdown(
        """
        1. **Cobertura geográfica (3 estaciones):** el modelo solo puede predecir en **Pudahuel, Santiago y Las Condes**,
           porque *El Bosque* y *La Florida* no disponen de sensores meteorológicos (temperatura, humedad y viento) en SINCA.
        2. **Sin eventos extraordinarios no meteorológicos:** el modelo estima concentraciones esperadas a partir de clima,
           mes y ubicación; no anticipa incendios forestales ni fuentes puntuales anómalas y tiende a suavizar picos extremos
           (`MAE = 8.09 µg/m³` en evaluación futura 2022–2023).
        3. **Escala temporal diaria:** la predicción corresponde al **promedio diario**, no al máximo horario nocturno,
           por lo que valores cercanos a 45–55 µg/m³ ya representan riesgo de episodios horarios elevados.
        """
    )

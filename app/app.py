"""Portada ejecutiva de la aplicación Streamlit — Presentación Final."""

import streamlit as st

from utils import load_audit_data, load_model_metadata

st.set_page_config(
    page_title="Calidad del Aire Santiago | Presentación Final",
    layout="wide",
    initial_sidebar_state="expanded",
)

meta = load_model_metadata()
audit = load_audit_data()
rf_metrics = next(m for m in meta["metricas_comparacion"] if "Random Forest" in m["Modelo"])
mejora_media = meta["mejoras"]["vs_media"]

st.title("Calidad del Aire en el Gran Santiago: Solución Predictiva ($MP_{2.5}$)")
st.caption("Visualización de Datos (EIN092B) · Presentación Final · Fuente oficial SINCA (MMA Chile)")

# 4 KPIs ejecutivos alineados con el cierre de Power BI
col1, col2, col3, col4 = st.columns(4)
col1.metric("Período Homogéneo Válido", "2018 – 2023", f"{audit['filas_2018_2023']:,} obs. diarias")
col2.metric("Modelo Final", "Random Forest", "5 entradas climáticas/espaciales")
col3.metric(
    "Error Medio (MAE / RMSE)",
    f"{rf_metrics['MAE']:.2f} / {rf_metrics['RMSE']:.2f} µg/m³",
    f"-{mejora_media['reduccion_rmse_pct']:.1f}% RMSE vs. media",
)
col4.metric(
    "Capacidad Explicativa (R²)",
    f"{rf_metrics['R2']:.3f}",
    "Evaluado en futuro (2022–2023)",
)

st.divider()

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Conexión desde la exploración (Power BI) hacia la predicción")
    st.markdown(
        """
        **Problema abordado:** La cuenca cerrada de Santiago sufre episodios críticos de contaminación por
        material particulado fino (**$MP_{2.5}$**) durante los meses fríos debido a la **inversión térmica**
        y la baja ventilación, con brechas territoriales marcadas entre comunas como Pudahuel/El Bosque y Las Condes.

        **Pregunta de investigación:**
        > *¿Cómo varían las concentraciones de $MP_{2.5}$ entre sectores y estaciones del año, y qué tan
        > predecibles son mediante variables meteorológicas, temporales y espaciales?*

        **Objetivo de esta aplicación:** demostrar el rendimiento real del modelo **Random Forest** frente
        a soluciones simples de referencia y ejecutar **predicciones en vivo** ingresando escenario comunal,
        mes y condiciones meteorológicas.
        """
    )

with right:
    st.subheader("Depuración metodológica respecto al Avance 3")
    st.info(
        f"""
        Al auditar el histórico completo 2013–2023 (`{audit['filas_2013_2023']:,}` registros) se detectaron dos sesgos críticos:
        1. **Salto de escala 2013–abril 2017:** el archivo fuente SINCA presentaba valores de $MP_{{2.5}}$
           desfasados (~180–206 de mediana frente a 17–21 µg/m³ en 2018–2023). Se acotó al tramo
           **homogéneo 2018–2023** (`{audit['filas_2018_2023']:,}` registros) y se decodificaron las escalas de temperatura, humedad y viento.
        2. **Variables explicativas válidas:** se excluyeron contaminantes co-medidos ($MP_{{10}}$ y gases) para
           evaluar la capacidad predictiva real usando únicamente **Estación, Mes, Temperatura, Humedad y Viento**.
        """
    )

st.divider()
st.subheader("Navegación de la aplicación")

nav1, nav2 = st.columns(2)
with nav1:
    st.markdown("### Presentación Final (Solución Predictiva)")
    st.markdown(
        """
        - **1. Modelo y Métricas:** definición de entradas/salida, partición temporal `2018–2021` vs. `2022–2023`,
          tabla comparativa obligatoria (**Media**, **Regresión 1 variable**, **Regresión Lineal Múltiple** y **Random Forest**),
          gráficos de ajuste e importancia de variables.
        - **2. Predicción en Vivo:** simulador operativo con el modelo `.joblib` cargado, escenarios de ejemplo
          modificables en vivo, nivel de alerta MMA y limitaciones de uso.
        """
    )
    btn_a, btn_b = st.columns(2)
    with btn_a:
        st.page_link("pages/1_Modelo_y_Metricas.py", label="Ir a Modelo y Métricas", icon="📊")
    with btn_b:
        st.page_link("pages/2_Prediccion_en_Vivo.py", label="Ir a Predicción en Vivo", icon="🎯")

with nav2:
    st.markdown("### Respaldo EDA Clarificado (Datos Válidos 2018–2023)")
    st.markdown(
        """
        - **3. EDA · Contexto y Calidad:** auditoría 2013–2023 que justifica el corte 2018–2023, decodificación de sensores
          y cobertura por estación (3 estaciones con meteorología vs. 5 con material particulado).
        - **4. EDA · Análisis Univariado:** distribución sesgada de $MP_{2.5}$, norma diaria (50 µg/m³) y brecha comunal.
        - **5. EDA · Análisis Multivariable:** estacionalidad invernal, inversión térmica y ventilación.
        """
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/3_EDA_Contexto_y_Calidad.py", label="3. Calidad", icon="🧹")
    with c2:
        st.page_link("pages/4_EDA_Analisis_Univariado.py", label="4. Univariado", icon="📈")
    with c3:
        st.page_link("pages/5_EDA_Analisis_Multivariable.py", label="5. Multivariable", icon="🌡️")

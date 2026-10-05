import streamlit as st

st.set_page_config(
    page_title="Aire Santiago | Avance 2",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Calidad del Aire en el Gran Santiago (2013-2023)")
st.subheader("Análisis Exploratorio de Datos (EDA) - Avance 2")

st.markdown("""
Bienvenido a la aplicación interactiva del proyecto de Visualización de Datos (EIN092B).

### Problema Central
La cuenca de Santiago presenta ventilación deficiente en invierno, concentrando material particulado fino ($MP_{2.5}$) con severos riesgos para la salud pública. 

### Pregunta del Proyecto
¿Cómo varían las concentraciones de material particulado fino ($MP_{2.5}$ y $MP_{10}$) entre los distintos sectores geográficos del Gran Santiago y las estaciones del año durante el período 2013-2023?

### Estructura del Análisis Exploratorio (EDA)
Para responder esta pregunta y demostrar empíricamente los hallazgos en nuestros datos, navegue por el menú lateral:
1. **Contexto y Calidad (Página 1):** Estructura del dataset, revisión de nulos y justificación técnica de la limpieza de sensores.
2. **Análisis Univariado (Página 2):** Exploración de las distribuciones (variable objetivo $Y$) y diferencias basales entre estaciones de monitoreo.
3. **Análisis Multivariable (Página 3):** Cruce interactivo para evidenciar la dimensión temporal ($T$), la brecha territorial ($X$) y el impacto meteorológico de la inversión térmica.

---
**Asignatura:** Visualización de Datos (UTFSM)
""")
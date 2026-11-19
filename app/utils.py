"""Utilidades compartidas, carga cacheada de datos/modelo y helpers de dominio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NORMA_DIARIA_MP25 = 50.0
UMBRAL_ALERTA_MP25 = 80.0
ESTACIONES_MODELO = ["Pudahuel", "Santiago", "Las Condes"]

MESES_NOMBRES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

MESES_CORTOS = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}


@st.cache_data
def load_clean_data() -> pd.DataFrame:
    """Carga el dataset limpio 2018-2023 desde ruta absoluta."""
    return pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "calidad_aire_limpia.parquet")


@st.cache_data
def load_audit_data() -> dict[str, Any]:
    """Carga la auditoría de transición de escala 2013-2023."""
    path = PROJECT_ROOT / "data" / "processed" / "auditoria_calidad_2013_2023.json"
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_model_metadata() -> dict[str, Any]:
    """Carga métricas, split, rangos e importancias del modelo entrenado."""
    path = PROJECT_ROOT / "models" / "model_metadata.json"
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_test_predictions() -> pd.DataFrame:
    """Carga predicciones sobre el conjunto de prueba temporal (2022-2023)."""
    return pd.read_parquet(PROJECT_ROOT / "models" / "test_predictions.parquet")


@st.cache_resource
def load_model():
    """Carga el Pipeline Random Forest preentrenado."""
    return joblib.load(PROJECT_ROOT / "models" / "rf_mp25_model.joblib")


def clasificar_mp25(valor: float) -> dict[str, str]:
    """Retorna categoría oficial MMA (D.S. N°12), color y significado operativo."""
    if valor <= 50:
        return {
            "nivel": "Bueno",
            "color": "#2e7d32",
            "bg": "#e8f5e9",
            "descripcion": "Cumple la norma primaria diaria chilena (≤ 50 µg/m³).",
        }
    if valor < 80:
        return {
            "nivel": "Regular",
            "color": "#b26a00",
            "bg": "#fff8e1",
            "descripcion": "Supera la norma diaria (50 µg/m³), sin alcanzar umbral de episodio crítico.",
        }
    if valor < 110:
        return {
            "nivel": "Alerta Ambiental",
            "color": "#ef6c00",
            "bg": "#fff3e0",
            "descripcion": "Episodio crítico Nivel 1 (80–109 µg/m³): exposición relevante para grupos sensibles.",
        }
    if valor < 170:
        return {
            "nivel": "Preemergencia Ambiental",
            "color": "#c62828",
            "bg": "#ffebee",
            "descripcion": "Episodio crítico Nivel 2 (110–169 µg/m³): medidas estrictas por alta saturación atmosférica.",
        }
    return {
        "nivel": "Emergencia Ambiental",
        "color": "#6a1b9a",
        "bg": "#f3e5f5",
        "descripcion": "Episodio crítico máximo (≥ 170 µg/m³): riesgo agudo para la salud pública.",
    }

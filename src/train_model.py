"""Entrenamiento reproducible del modelo final (2018-2023) y comparación con referencias base."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURES = ["Estacion", "Month", "Temperatura_C", "Humedad", "Viento_ms"]
CAT_FEATURES = ["Estacion"]
NUM_FEATURES = ["Month", "Temperatura_C", "Humedad", "Viento_ms"]
TARGET = "MP2_5"
TRAIN_END_YEAR = 2021


def build_preprocessor() -> ColumnTransformer:
    """Construye el preprocesador OneHot + passthrough para las 5 variables."""
    return ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False),
                CAT_FEATURES,
            ),
            ("num", "passthrough", NUM_FEATURES),
        ],
        verbose_feature_names_out=False,
    )


def compute_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    """Calcula MAE, RMSE, MAPE (%) y R2 sobre un mismo conjunto de evaluación."""
    return {
        "MAE": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 3),
        "MAPE": round(float(mean_absolute_percentage_error(y_true, y_pred) * 100), 2),
        "R2": round(float(r2_score(y_true, y_pred)), 4),
    }


def pct_error_reduction(baseline_val: float, final_val: float) -> float:
    """Calcula porcentaje de reducción de error respecto a una referencia."""
    if baseline_val == 0:
        return 0.0
    return round(float((baseline_val - final_val) / baseline_val * 100), 2)


def aggregate_importances(pipeline: Pipeline) -> dict[str, float]:
    """Agrupa importancias del Random Forest por variable original."""
    prep: ColumnTransformer = pipeline.named_steps["prep"]
    rf: RandomForestRegressor = pipeline.named_steps["model"]
    feat_names = list(prep.get_feature_names_out())
    raw_imp = dict(zip(feat_names, rf.feature_importances_))

    grouped: dict[str, float] = {
        "Estacion": 0.0,
        "Month": 0.0,
        "Temperatura_C": 0.0,
        "Humedad": 0.0,
        "Viento_ms": 0.0,
    }
    for name, imp in raw_imp.items():
        if name.startswith("Estacion_"):
            grouped["Estacion"] += float(imp)
        elif name in grouped:
            grouped[name] += float(imp)

    return {
        k: round(v * 100, 2)
        for k, v in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    }


def train_and_evaluate(
    data_path: Path | None = None,
    models_dir: Path | None = None,
) -> dict:
    """Entrena Random Forest y referencias base en split temporal y guarda artefactos."""
    data_path = data_path or (PROJECT_ROOT / "data" / "processed" / "calidad_aire_limpia.parquet")
    models_dir = models_dir or (PROJECT_ROOT / "models")
    models_dir.mkdir(parents=True, exist_ok=True)

    df_full = pd.read_parquet(data_path)
    df_model = (
        df_full.dropna(subset=FEATURES + [TARGET])
        .sort_values(["Fecha", "Estacion"])
        .reset_index(drop=True)
    )

    train_mask = df_model["Year"] <= TRAIN_END_YEAR
    df_train = df_model[train_mask].copy()
    df_test = df_model[~train_mask].copy()

    X_train, y_train = df_train[FEATURES], df_train[TARGET]
    X_test, y_test = df_test[FEATURES], df_test[TARGET]

    # 1. Referencia 1: Predicción constante = media de Y en entrenamiento
    y_train_mean = float(y_train.mean())
    pred_media = np.full(shape=len(y_test), fill_value=y_train_mean, dtype=float)

    # 2. Referencia 2: Regresión lineal con una sola característica (Temperatura_C)
    lr_1var = LinearRegression()
    lr_1var.fit(X_train[["Temperatura_C"]], y_train)
    pred_lr1 = lr_1var.predict(X_test[["Temperatura_C"]])

    # 3. Regresión Lineal Múltiple (5 variables)
    pipe_lr_mult = Pipeline([("prep", build_preprocessor()), ("model", LinearRegression())])
    pipe_lr_mult.fit(X_train, y_train)
    pred_lr_mult = pipe_lr_mult.predict(X_test)

    # 4. Modelo Final: Random Forest Regressor (5 variables)
    pipe_rf = Pipeline(
        [
            ("prep", build_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_leaf=4,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    pipe_rf.fit(X_train, y_train)
    pred_rf = pipe_rf.predict(X_test)

    # Métricas sobre exactamente las mismas observaciones de prueba
    metrics_media = compute_metrics(y_test, pred_media)
    metrics_lr1 = compute_metrics(y_test, pred_lr1)
    metrics_lr_mult = compute_metrics(y_test, pred_lr_mult)
    metrics_rf = compute_metrics(y_test, pred_rf)

    comparison_table = [
        {
            "Modelo": "Base 1: Media de entrenamiento",
            "Tipo": "Referencia constante",
            "Variables": "Ninguna (promedio Y train)",
            **metrics_media,
        },
        {
            "Modelo": "Base 2: Regresión Lineal (1 variable)",
            "Tipo": "Referencia simple",
            "Variables": "Temperatura_C",
            **metrics_lr1,
        },
        {
            "Modelo": "Regresión Lineal Múltiple",
            "Tipo": "Modelo lineal completo",
            "Variables": "5 variables (Estación + Mes + Clima)",
            **metrics_lr_mult,
        },
        {
            "Modelo": "Random Forest Regressor (Final)",
            "Tipo": "Ensamble no lineal (Final)",
            "Variables": "5 variables (Estación + Mes + Clima)",
            **metrics_rf,
        },
    ]

    mejoras = {
        "vs_media": {
            "reduccion_mae_pct": pct_error_reduction(metrics_media["MAE"], metrics_rf["MAE"]),
            "reduccion_rmse_pct": pct_error_reduction(metrics_media["RMSE"], metrics_rf["RMSE"]),
            "reduccion_mape_pct": pct_error_reduction(metrics_media["MAPE"], metrics_rf["MAPE"]),
            "ganancia_r2": round(metrics_rf["R2"] - metrics_media["R2"], 4),
        },
        "vs_reg_1var": {
            "reduccion_mae_pct": pct_error_reduction(metrics_lr1["MAE"], metrics_rf["MAE"]),
            "reduccion_rmse_pct": pct_error_reduction(metrics_lr1["RMSE"], metrics_rf["RMSE"]),
            "reduccion_mape_pct": pct_error_reduction(metrics_lr1["MAPE"], metrics_rf["MAPE"]),
            "ganancia_r2": round(metrics_rf["R2"] - metrics_lr1["R2"], 4),
        },
        "vs_reg_multiple": {
            "reduccion_mae_pct": pct_error_reduction(metrics_lr_mult["MAE"], metrics_rf["MAE"]),
            "reduccion_rmse_pct": pct_error_reduction(metrics_lr_mult["RMSE"], metrics_rf["RMSE"]),
            "reduccion_mape_pct": pct_error_reduction(metrics_lr_mult["MAPE"], metrics_rf["MAPE"]),
            "ganancia_r2": round(metrics_rf["R2"] - metrics_lr_mult["R2"], 4),
        },
    }

    rangos_variables = {}
    for col in NUM_FEATURES:
        s = df_model[col]
        rangos_variables[col] = {
            "min": round(float(s.min()), 2),
            "p05": round(float(s.quantile(0.05)), 2),
            "median": round(float(s.median()), 2),
            "p95": round(float(s.quantile(0.95)), 2),
            "max": round(float(s.max()), 2),
        }

    correlaciones_train = {
        col: round(float(X_train[col].corr(y_train)), 3) for col in NUM_FEATURES
    }

    estaciones_modelo = sorted(df_model["Estacion"].unique().tolist())
    medianas_est_mes: dict[str, dict[str, float]] = {}
    df_est_valid = df_full[df_full["Estacion"].isin(estaciones_modelo)].dropna(subset=[TARGET])
    for est in estaciones_modelo:
        sub_est = df_est_valid[df_est_valid["Estacion"] == est]
        medianas_est_mes[est] = {
            str(int(m)): round(float(val), 1)
            for m, val in sub_est.groupby("Month")[TARGET].median().items()
        }

    metadata = {
        "problema": "Regresión",
        "target": TARGET,
        "unidad": "µg/m³",
        "features": FEATURES,
        "estaciones_disponibles": estaciones_modelo,
        "estaciones_excluidas": ["El Bosque", "La Florida"],
        "split": {
            "tipo": "División temporal estricta",
            "train_years": "2018-2021",
            "test_years": "2022-2023",
            "n_total": int(len(df_model)),
            "n_train": int(len(df_train)),
            "n_test": int(len(df_test)),
            "train_fecha_min": str(df_train["Fecha"].min().date()),
            "train_fecha_max": str(df_train["Fecha"].max().date()),
            "test_fecha_min": str(df_test["Fecha"].min().date()),
            "test_fecha_max": str(df_test["Fecha"].max().date()),
            "estaciones_test_counts": {
                str(k): int(v) for k, v in df_test["Estacion"].value_counts().items()
            },
        },
        "hiperparametros_rf": {
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_leaf": 4,
            "random_state": 42,
        },
        "y_train_mean": round(y_train_mean, 2),
        "reg_1var_feature": "Temperatura_C",
        "reg_1var_coef": round(float(lr_1var.coef_[0]), 4),
        "reg_1var_intercept": round(float(lr_1var.intercept_), 4),
        "metricas_comparacion": comparison_table,
        "mejoras": mejoras,
        "importancia_variables_pct": aggregate_importances(pipe_rf),
        "correlaciones_train_mp25": correlaciones_train,
        "rangos_variables": rangos_variables,
        "medianas_historicas_estacion_mes": medianas_est_mes,
    }

    # Guardar artefactos
    model_path = models_dir / "rf_mp25_model.joblib"
    metadata_path = models_dir / "model_metadata.json"
    preds_path = models_dir / "test_predictions.parquet"

    joblib.dump(pipe_rf, model_path)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    df_preds = df_test[["Fecha", "Year", "Month", "Estacion", "Temperatura_C", "Humedad", "Viento_ms"]].copy()
    df_preds["y_real"] = y_test.values
    df_preds["pred_media"] = np.round(pred_media, 2)
    df_preds["pred_lr1"] = np.round(pred_lr1, 2)
    df_preds["pred_lr_mult"] = np.round(pred_lr_mult, 2)
    df_preds["pred_rf"] = np.round(pred_rf, 2)
    df_preds.to_parquet(preds_path, index=False)

    print(f"Modelo guardado en: {model_path}")
    print(f"Metadatos guardados en: {metadata_path}")
    print(f"Predicciones de prueba ({len(df_preds)} filas) en: {preds_path}")
    print("\n--- Tabla Comparativa en Prueba (2022-2023) ---")
    print(pd.DataFrame(comparison_table)[["Modelo", "MAE", "RMSE", "MAPE", "R2"]].to_string(index=False))
    return metadata


if __name__ == "__main__":
    train_and_evaluate()

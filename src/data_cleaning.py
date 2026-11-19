"""Pipeline de saneamiento y generación de datasets para Streamlit y Power BI."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

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

MESES_LARGOS = {
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

ESTACIONES_META = [
    {
        "Estacion": "El Bosque",
        "Zona_Geografica": "Sur",
        "Tiene_Meteorologia": "No",
        "Latitud": -33.5461,
        "Longitud": -70.6662,
    },
    {
        "Estacion": "La Florida",
        "Zona_Geografica": "Sur-Oriente",
        "Tiene_Meteorologia": "No",
        "Latitud": -33.5161,
        "Longitud": -70.5881,
    },
    {
        "Estacion": "Las Condes",
        "Zona_Geografica": "Oriente",
        "Tiene_Meteorologia": "Sí",
        "Latitud": -33.3764,
        "Longitud": -70.5235,
    },
    {
        "Estacion": "Pudahuel",
        "Zona_Geografica": "Poniente",
        "Tiene_Meteorologia": "Sí",
        "Latitud": -33.4379,
        "Longitud": -70.7504,
    },
    {
        "Estacion": "Santiago",
        "Zona_Geografica": "Centro",
        "Tiene_Meteorologia": "Sí",
        "Latitud": -33.4641,
        "Longitud": -70.6608,
    },
]


def formatear_celsius(valor: float) -> float:
    """Decodifica temperatura diaria (°C) corrigiendo corrimientos decimales de SINCA."""
    if pd.isna(valor) or valor < -5 or valor > 1000:
        return np.nan
    if valor <= 30:
        return round(float(valor), 2)
    if valor <= 260:
        return round(float(valor) / 10, 2)
    return round(float(valor) / 100, 2)


def limpiar_humedad(valor: float) -> float:
    """Decodifica humedad relativa (%) a rango físico (0, 100]."""
    if pd.isna(valor) or valor <= 0 or valor > 1000:
        return np.nan
    if valor <= 100:
        return round(float(valor), 2)
    return round(float(valor) / 10, 2)


def limpiar_viento(valor: float) -> float:
    """Decodifica velocidad del viento diaria (m/s) corrigiendo corrimientos x10/x100."""
    if pd.isna(valor) or valor < 0 or valor > 1000:
        return np.nan
    if valor < 10:
        return round(float(valor), 2)
    if valor < 100:
        return round(float(valor) / 10, 2)
    return round(float(valor) / 100, 2)


def obtener_estacion_anio(mes: int) -> tuple[str, int]:
    """Asigna estación astronómica/climática del hemisferio sur y su orden."""
    if mes in (12, 1, 2):
        return "Verano", 1
    if mes in (3, 4, 5):
        return "Otoño", 2
    if mes in (6, 7, 8):
        return "Invierno", 3
    return "Primavera", 4


def clasificar_mp25_mma(valor: float) -> str:
    """Clasifica concentración diaria de MP2.5 según tramos MMA (D.S. N°12 / GEC)."""
    if pd.isna(valor):
        return "Sin Dato"
    if valor <= 50:
        return "Bueno (0-50)"
    if valor < 80:
        return "Regular (51-79)"
    if valor < 110:
        return "Alerta (80-109)"
    if valor < 170:
        return "Preemergencia (110-169)"
    return "Emergencia (>=170)"


def construir_auditoria(df_2013_2023: pd.DataFrame, df_2018_2023: pd.DataFrame) -> dict:
    """Genera resumen auditable del cambio de escala 2013-2017 vs 2018-2023."""
    resumen_anual = []
    for year, grp in df_2013_2023.groupby("Year"):
        mp25 = pd.to_numeric(grp["MP2_5"], errors="coerce").dropna()
        resumen_anual.append(
            {
                "year": int(year),
                "registros": int(len(grp)),
                "mp25_validos": int(len(mp25)),
                "mp25_mediana": round(float(mp25.median()), 2) if len(mp25) else None,
                "mp25_promedio": round(float(mp25.mean()), 2) if len(mp25) else None,
                "mp25_max": round(float(mp25.max()), 2) if len(mp25) else None,
                "es_rango_homogeneo": bool(year >= 2018),
            }
        )

    validos_estacion = []
    cols_check = ["MP2_5", "MP10", "Temperatura_C", "Humedad", "Viento_ms"]
    for est, grp in df_2018_2023.groupby("Estacion"):
        row = {"Estacion": str(est), "Registros": int(len(grp))}
        for c in cols_check:
            row[c] = int(grp[c].notna().sum())
        validos_estacion.append(row)

    return {
        "filas_2013_2023": int(len(df_2013_2023)),
        "filas_2018_2023": int(len(df_2018_2023)),
        "fecha_min_2018_2023": str(df_2018_2023["Fecha"].min().date()),
        "fecha_max_2018_2023": str(df_2018_2023["Fecha"].max().date()),
        "resumen_anual_2013_2023": resumen_anual,
        "validos_por_estacion_2018_2023": validos_estacion,
    }


def exportar_powerbi(df_clean: pd.DataFrame, powerbi_data_dir: Path) -> None:
    """Exporta modelo estrella (fact + dim_calendario + dim_estaciones) en CSV UTF-8-SIG."""
    powerbi_data_dir.mkdir(parents=True, exist_ok=True)

    fact = df_clean[
        [
            "Fecha",
            "Estacion",
            "MP2_5",
            "MP10",
            "Temperatura_C",
            "Humedad",
            "Viento_ms",
            "Supera_Norma_MP25",
            "Es_Alerta_o_Superior",
            "Categoria_MP25",
        ]
    ].copy()
    fact["Fecha"] = fact["Fecha"].dt.strftime("%Y-%m-%d")
    fact.to_csv(powerbi_data_dir / "fact_calidad_aire.csv", index=False, encoding="utf-8-sig")

    fechas_unicas = pd.DataFrame({"Fecha_dt": sorted(df_clean["Fecha"].unique())})
    fechas_unicas["Fecha"] = fechas_unicas["Fecha_dt"].dt.strftime("%Y-%m-%d")
    fechas_unicas["Anio"] = fechas_unicas["Fecha_dt"].dt.year
    fechas_unicas["Mes_Num"] = fechas_unicas["Fecha_dt"].dt.month
    fechas_unicas["Nombre_Mes"] = fechas_unicas["Mes_Num"].map(MESES_LARGOS)
    fechas_unicas["Mes_Corto"] = fechas_unicas["Mes_Num"].map(MESES_CORTOS)
    fechas_unicas["Trimestre"] = "T" + fechas_unicas["Fecha_dt"].dt.quarter.astype(str)
    est_orden = fechas_unicas["Mes_Num"].map(obtener_estacion_anio)
    fechas_unicas["Estacion_Anio"] = [x[0] for x in est_orden]
    fechas_unicas["Orden_Estacion_Anio"] = [x[1] for x in est_orden]
    fechas_unicas["Anio_Mes"] = fechas_unicas["Fecha_dt"].dt.strftime("%Y-%m")
    fechas_unicas["Es_Invierno"] = np.where(fechas_unicas["Mes_Num"].isin([6, 7, 8]), "Sí", "No")

    dim_calendario = fechas_unicas[
        [
            "Fecha",
            "Anio",
            "Mes_Num",
            "Nombre_Mes",
            "Mes_Corto",
            "Trimestre",
            "Estacion_Anio",
            "Orden_Estacion_Anio",
            "Anio_Mes",
            "Es_Invierno",
        ]
    ]
    dim_calendario.to_csv(powerbi_data_dir / "dim_calendario.csv", index=False, encoding="utf-8-sig")

    dim_estaciones = pd.DataFrame(ESTACIONES_META)
    dim_estaciones.to_csv(powerbi_data_dir / "dim_estaciones.csv", index=False, encoding="utf-8-sig")

    exportar_excel_powerbi(
        df_clean=df_clean,
        dim_estaciones=dim_estaciones,
        excel_path=powerbi_data_dir.parent / "calidad_aire_santiago_pbi.xlsx",
    )


def exportar_excel_powerbi(
    df_clean: pd.DataFrame,
    dim_estaciones: pd.DataFrame,
    excel_path: Path,
) -> None:
    """Exporta una tabla plana única en Excel (.xlsx) lista para Power BI sin DAX ni relaciones."""
    df_merged = df_clean.merge(dim_estaciones, on="Estacion", how="left")

    df_excel = pd.DataFrame(
        {
            "Fecha": df_merged["Fecha"].dt.date,
            "Anio": df_merged["Year"].astype(int),
            "Mes": [f"{int(m):02d} {MESES_CORTOS[int(m)]}" for m in df_merged["Month"]],
            "Anio_Mes": df_merged["Fecha"].dt.strftime("%Y-%m"),
            "Estacion_Anio": df_merged["Estacion_Anio"],
            "Estacion": df_merged["Estacion"],
            "Zona": df_merged["Zona_Geografica"],
            "Tiene_Clima": df_merged["Tiene_Meteorologia"],
            "MP2_5": df_merged["MP2_5"],
            "MP10": df_merged["MP10"],
            "Temperatura_C": df_merged["Temperatura_C"],
            "Humedad_pct": df_merged["Humedad"],
            "Viento_ms": df_merged["Viento_ms"],
            "Dia_Sobre_Norma": df_merged["Supera_Norma_MP25"].astype("Int64"),
            "Dia_Alerta": df_merged["Es_Alerta_o_Superior"].astype("Int64"),
            "Categoria_Calidad": df_merged["Categoria_MP25"],
            "Latitud": df_merged["Latitud"],
            "Longitud": df_merged["Longitud"],
        }
    )

    with pd.ExcelWriter(excel_path, engine="openpyxl", date_format="yyyy-mm-dd") as writer:
        df_excel.to_excel(writer, sheet_name="Datos", index=False)


def clean_data(
    input_path: Path | None = None,
    output_path: Path | None = None,
    audit_path: Path | None = None,
    powerbi_data_dir: Path | None = None,
) -> pd.DataFrame:
    """Ejecuta limpieza completa, auditoría 2013-2023 y exportación a Parquet y Power BI."""
    input_path = input_path or (PROJECT_ROOT / "data" / "raw" / "Calidad del aire.csv")
    output_path = output_path or (PROJECT_ROOT / "data" / "processed" / "calidad_aire_limpia.parquet")
    audit_path = audit_path or (PROJECT_ROOT / "data" / "processed" / "auditoria_calidad_2013_2023.json")
    powerbi_data_dir = powerbi_data_dir or (PROJECT_ROOT / "powerbi" / "data")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Cargando datos desde {input_path}...")
    df = pd.read_csv(input_path, sep=";", decimal=",", low_memory=False)

    # 1. Reconstruir fecha
    fecha_str = df["FECHA (YYMMDD)"].astype(str).str.zfill(6)
    yy = fecha_str.str[:2].astype(int)
    df["Year"] = yy.apply(lambda y: 1900 + y if y >= 90 else 2000 + y)
    df["Month"] = fecha_str.str[2:4].astype(int)
    df["Day"] = fecha_str.str[4:6].astype(int)
    df["Fecha"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=df["Day"]))

    # 2. Subconjunto histórico del proyecto (2013-2023) y rango homogéneo válido (2018-2023)
    df_2013_2023 = df[(df["Year"] >= 2013) & (df["Year"] <= 2023)].copy()
    df_sub = df_2013_2023[df_2013_2023["Year"] >= 2018].copy()

    # 3. Decodificación física de sensores meteorológicos en 2018-2023
    for col_num in ["MP10", "MP2_5", "CO", "NO", "NO2", "O3", "Humedad", "Temperatura", "Viento_v"]:
        df_sub[col_num] = pd.to_numeric(df_sub[col_num], errors="coerce")

    df_sub["Temperatura_C"] = df_sub["Temperatura"].apply(formatear_celsius)
    df_sub["Humedad"] = df_sub["Humedad"].apply(limpiar_humedad)
    df_sub["Viento_ms"] = df_sub["Viento_v"].apply(limpiar_viento)

    # 4. Variables derivadas coherentes con la norma chilena MMA (D.S. N°12)
    df_sub["Nombre_Mes"] = df_sub["Month"].map(MESES_CORTOS)
    df_sub["Estacion_Anio"] = [obtener_estacion_anio(m)[0] for m in df_sub["Month"]]
    df_sub["Supera_Norma_MP25"] = np.where(
        df_sub["MP2_5"].isna(),
        np.nan,
        np.where(df_sub["MP2_5"] > 50, 1.0, 0.0),
    )
    df_sub["Es_Alerta_o_Superior"] = np.where(
        df_sub["MP2_5"].isna(),
        np.nan,
        np.where(df_sub["MP2_5"] >= 80, 1.0, 0.0),
    )
    df_sub["Categoria_MP25"] = df_sub["MP2_5"].apply(clasificar_mp25_mma)

    columnas_finales = [
        "Fecha",
        "Year",
        "Month",
        "Day",
        "Estacion",
        "Nombre_Mes",
        "Estacion_Anio",
        "MP10",
        "MP2_5",
        "CO",
        "NO",
        "NO2",
        "O3",
        "Humedad",
        "Temperatura_C",
        "Viento_ms",
        "Supera_Norma_MP25",
        "Es_Alerta_o_Superior",
        "Categoria_MP25",
    ]
    df_clean = df_sub[columnas_finales].sort_values(["Fecha", "Estacion"]).reset_index(drop=True)

    # 5. Guardar auditoría, parquet y modelo estrella Power BI
    auditoria = construir_auditoria(df_2013_2023, df_clean)
    audit_path.write_text(json.dumps(auditoria, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Guardando {len(df_clean):,} registros limpios (2018-2023) en {output_path}...")
    df_clean.to_parquet(output_path, index=False)

    print(f"Exportando CSVs para Power BI en {powerbi_data_dir}...")
    exportar_powerbi(df_clean, powerbi_data_dir)
    print("Proceso completado exitosamente.")
    return df_clean


if __name__ == "__main__":
    clean_data()

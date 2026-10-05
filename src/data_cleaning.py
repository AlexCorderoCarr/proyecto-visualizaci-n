import pandas as pd
import numpy as np
import os

def formatear_celsius(valor):
    if pd.isna(valor):
        return np.nan
    if valor > 450 or valor < -10:
        return np.nan
    if valor > 45:
        return round(valor / 10, 2)
    return round(valor, 2)

def limpiar_viento(v):
    if pd.isna(v) or v > 15 or v < 0:
        return np.nan
    return round(v, 2)

def clean_data(input_path, output_path):
    print(f"Cargando datos desde {input_path}...")
    df = pd.read_csv(input_path, sep=';', decimal=',', low_memory=False)
    
    # 1. Parse date
    fecha_str = df['FECHA (YYMMDD)'].astype(str).str.zfill(6)
    yy = fecha_str.str[:2].astype(int)
    df['Year'] = yy.apply(lambda y: 1900 + y if y >= 90 else 2000 + y)
    df['Month'] = fecha_str.str[2:4].astype(int)
    df['Day'] = fecha_str.str[4:6].astype(int)
    df['Fecha'] = pd.to_datetime(dict(year=df['Year'], month=df['Month'], day=df['Day']))
    
    # 2. Filter study period
    df = df[(df['Year'] >= 2013) & (df['Year'] <= 2023)].copy()
    
    # 3. Clean meteorology
    df['Temperatura_C'] = df['Temperatura'].apply(formatear_celsius)
    df['Viento_ms'] = df['Viento_v'].apply(limpiar_viento)
    
    # 4. Sort and select columns
    columnas_finales = [
        'Fecha', 'Year', 'Month', 'Day', 'Estacion', 
        'MP10', 'MP2_5', 'CO', 'NO', 'NO2', 'O3', 
        'Humedad', 'Temperatura_C', 'Viento_ms'
    ]
    df_clean = df[columnas_finales].sort_values(['Fecha', 'Estacion'])
    
    # 5. Save processed data
    print(f"Guardando {len(df_clean)} registros procesados en {output_path}...")
    df_clean.to_parquet(output_path, index=False)
    print("Proceso completado exitosamente.")

if __name__ == '__main__':
    raw_file = '../data/raw/Calidad del aire.csv'
    processed_file = '../data/processed/calidad_aire_limpia.parquet'
    
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)
    clean_data(raw_file, processed_file)
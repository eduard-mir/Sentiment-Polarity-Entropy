# -*- coding: utf-8 -*-
import os, warnings
from typing import Dict, Optional, List
import pandas as pd
from unidecode import unidecode
from tqdm import tqdm

warnings.filterwarnings("ignore", category=UserWarning)

# ====== CONFIG ======
# Procesa un archivo por vez para ir más ágil
INPUT_XLSX = r"C:\Users\Edu\PycharmProjects\Sentiment_Triclass\mis_excels\adverbios.xlsx"
SUFIJO_SALIDA = "_con_triclase.xlsx"

# Columnas de salida (porcentajes 0..100)
COL_POS = "pos_pct"
COL_NEU = "neu_pct"
COL_NEG = "neg_pct"

# Variantes aceptadas de encabezados
VARIANTES = {
    "palabra":   {"palabra", "termino", "término", "word"},
    "izquierda": {"izquierda", "izquierdo", "contexto izquierdo", "izq"},
    "objetivo":  {"objetivo", "frase objetivo", "target", "oracion objetivo", "oración objetivo"},
    "derecha":   {"derecha", "derecho", "contexto derecho", "der"},
}

def _norm(s: str) -> str:
    return " ".join(unidecode(str(s)).strip().lower().split())

def encontrar_columnas(df: pd.DataFrame) -> Dict[str, str]:
    norm_cols = {c: _norm(c) for c in df.columns}
    m: Dict[str, str] = {}
    for rol, opciones in VARIANTES.items():
        variantes_norm = {_norm(x) for x in opciones}
        elegido: Optional[str] = None
        for real, nrm in norm_cols.items():
            if nrm in variantes_norm:
                elegido = real; break
        if elegido is None:
            for real, nrm in norm_cols.items():
                if rol in nrm:
                    elegido = real; break
        if elegido is None:
            raise ValueError(f"No encuentro columna '{rol}'. Encabezados: {list(df.columns)}")
        m[rol] = elegido
    return m

# ====== clasificador (pysentimiento) ======
from pysentimiento import create_analyzer
_ANALYZER = None

def get_analyzer():
    global _ANALYZER
    if _ANALYZER is None:
        print("Cargando modelo pysentimiento (puede tardar la primera vez)…")
        _ANALYZER = create_analyzer(task="sentiment", lang="es")
        print("Modelo cargado.")
    return _ANALYZER

def probas_triclase(texto: str) -> Dict[str, float]:
    """Devuelve dict {'POS': p, 'NEU': p, 'NEG': p} en 0..1; normaliza por seguridad."""
    if texto is None or not str(texto).strip():
        return {"POS": 0.0, "NEU": 0.0, "NEG": 0.0}
    r = get_analyzer().predict(str(texto))
    pos = float(r.probas.get("POS", 0.0))
    neu = float(r.probas.get("NEU", 0.0))
    neg = float(r.probas.get("NEG", 0.0))
    s = pos + neu + neg
    if s > 0:
        pos, neu, neg = pos/s, neu/s, neg/s
    return {"POS": pos, "NEU": neu, "NEG": neg}

def procesa_hoja(df: pd.DataFrame) -> pd.DataFrame:
    """Añade pos_pct, neu_pct, neg_pct sobre la columna 'objetivo'."""
    if df.empty:
        return df
    df = df.copy()
    m = encontrar_columnas(df)
    col_obj = m["objetivo"]

    # Evitar colisiones
    col_pos = COL_POS if COL_POS not in df.columns else COL_POS + "_nuevo"
    col_neu = COL_NEU if COL_NEU not in df.columns else COL_NEU + "_nuevo"
    col_neg = COL_NEG if COL_NEG not in df.columns else COL_NEG + "_nuevo"

    textos = df[col_obj].fillna("").astype(str).tolist()

    pos_vals: List[Optional[float]] = []
    neu_vals: List[Optional[float]] = []
    neg_vals: List[Optional[float]] = []

    for txt in tqdm(textos, desc="   Calculando POS/NEU/NEG", leave=False):
        p = probas_triclase(txt)
        pos_vals.append(round(p["POS"] * 100.0, 6))
        neu_vals.append(round(p["NEU"] * 100.0, 6))
        neg_vals.append(round(p["NEG"] * 100.0, 6))

    df[col_pos] = pd.Series(pos_vals, index=df.index)
    df[col_neu] = pd.Series(neu_vals, index=df.index)
    df[col_neg] = pd.Series(neg_vals, index=df.index)
    return df

def procesa_archivo(path_xlsx: str):
    print(f"→ Procesando {os.path.basename(path_xlsx)}")
    xls = pd.ExcelFile(path_xlsx, engine="openpyxl")

    # Procesamos primero todas las hojas en memoria para evitar dejar el libro vacío si algo falla
    hojas_salida = {}
    for hoja in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=hoja, dtype=str)
        except Exception as e:
            print(f"   ⚠️ No pude leer la hoja '{hoja}': {e}")
            hojas_salida[hoja] = pd.DataFrame()
            continue

        try:
            hojas_salida[hoja] = procesa_hoja(df)
        except Exception as e:
            print(f"   ⚠️ Hoja '{hoja}' sin cambios: {e}")
            hojas_salida[hoja] = df  # escribimos tal cual

    # Ahora sí, escribimos a disco (siempre habrá al menos una hoja)
    out_path = os.path.splitext(path_xlsx)[0] + SUFIJO_SALIDA
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for hoja, df_out in hojas_salida.items():
            df_out.to_excel(writer, sheet_name=hoja, index=False)

    print(f"   ✓ Guardado: {out_path}")

def main():
    if not os.path.exists(INPUT_XLSX):
        print("No existe el archivo:", INPUT_XLSX)
        return
    # Carga del modelo (descarga la 1ª vez)
    get_analyzer()
    procesa_archivo(INPUT_XLSX)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import os, warnings
from typing import Dict, Optional, List
import re

import pandas as pd
from unidecode import unidecode
from tqdm import tqdm

warnings.filterwarnings("ignore", category=UserWarning)

# ====== CONFIG ======
# Cambia esta ruta por el Excel que quieras procesar
INPUT_XLSX = r"C:\Users\Edu\PycharmProjects\Sentiment_triclass_Word\mis_excels\nombres.xlsx"
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
    """
    Intenta mapear automáticamente las columnas reales del Excel a los roles:
    'palabra', 'izquierda', 'objetivo', 'derecha', usando VARIANTES.
    """
    norm_cols = {c: _norm(c) for c in df.columns}
    m: Dict[str, str] = {}
    for rol, opciones in VARIANTES.items():
        variantes_norm = {_norm(x) for x in opciones}
        elegido: Optional[str] = None

        # 1) Coincidencia exacta con alguna variante conocida
        for real, nrm in norm_cols.items():
            if nrm in variantes_norm:
                elegido = real
                break

        # 2) Si no se encuentra, buscar que el rol aparezca dentro del nombre normalizado
        if elegido is None:
            for real, nrm in norm_cols.items():
                if rol in nrm:
                    elegido = real
                    break

        if elegido is None:
            raise ValueError(f"No encuentro columna '{rol}'. Encabezados: {list(df.columns)}")

        m[rol] = elegido
    return m


# ====== clasificador (pysentimiento) ======
from pysentimiento import create_analyzer
_ANALYZER = None


def get_analyzer():
    """
    Carga el analizador de pysentimiento (una sola vez).
    """
    global _ANALYZER
    if _ANALYZER is None:
        print("Cargando modelo pysentimiento (puede tardar la primera vez)…")
        _ANALYZER = create_analyzer(task="sentiment", lang="es")
        print("Modelo cargado.")
    return _ANALYZER


def probas_triclase_target(palabra: str, contexto: str, ventana_chars: int = 80) -> Dict[str, float]:
    """
    Devuelve dict {'POS': p, 'NEU': p, 'NEG': p} en 0..1,
    calculando el sentimiento sobre un fragmento del contexto
    centrado en la PALABRA objetivo.

    - 'palabra' corresponde a la expresión evaluativa (columna A).
    - 'contexto' corresponde a la oración objetivo (columna C).
    - 'ventana_chars' controla cuántos caracteres a izquierda/derecha se toman.
    """
    if contexto is None or not str(contexto).strip():
        return {"POS": 0.0, "NEU": 0.0, "NEG": 0.0}

    texto = str(contexto)
    objetivo = str(palabra) if palabra is not None else ""

    if not objetivo.strip():
        # Si no hay palabra objetivo, usamos toda la oración como fallback
        texto_snippet = texto
    else:
        # Buscar la palabra como "token" aproximado (delimitada por bordes de palabra)
        patron = re.compile(r'\b{}\b'.format(re.escape(objetivo)), re.IGNORECASE)
        m = patron.search(texto)

        if m is None:
            # Si no la encontramos, usamos toda la oración
            texto_snippet = texto
        else:
            start, end = m.start(), m.end()
            left = max(0, start - ventana_chars)
            right = min(len(texto), end + ventana_chars)
            texto_snippet = texto[left:right]

    r = get_analyzer().predict(texto_snippet)
    pos = float(r.probas.get("POS", 0.0))
    neu = float(r.probas.get("NEU", 0.0))
    neg = float(r.probas.get("NEG", 0.0))

    s = pos + neu + neg
    if s > 0:
        pos, neu, neg = pos / s, neu / s, neg / s

    return {"POS": pos, "NEU": neu, "NEG": neg}


def procesa_hoja(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade pos_pct, neu_pct, neg_pct calculados sobre la PALABRA
    (columna 'palabra') en el CONTEXTO de la 'oración objetivo'
    (columna 'objetivo').
    """
    if df.empty:
        return df

    df = df.copy()
    m = encontrar_columnas(df)
    col_pal = m["palabra"]
    col_obj = m["objetivo"]

    # Evitar colisiones en nombres de columnas de salida
    col_pos = COL_POS if COL_POS not in df.columns else COL_POS + "_nuevo"
    col_neu = COL_NEU if COL_NEU not in df.columns else COL_NEU + "_nuevo"
    col_neg = COL_NEG if COL_NEG not in df.columns else COL_NEG + "_nuevo"

    palabras = df[col_pal].fillna("").astype(str).tolist()
    contextos = df[col_obj].fillna("").astype(str).tolist()

    pos_vals: List[Optional[float]] = []
    neu_vals: List[Optional[float]] = []
    neg_vals: List[Optional[float]] = []

    for palabra, contexto in tqdm(
        list(zip(palabras, contextos)),
        desc="   Calculando POS/NEU/NEG (target)",
        leave=False
    ):
        p = probas_triclase_target(palabra, contexto)
        pos_vals.append(round(p["POS"] * 100.0, 6))
        neu_vals.append(round(p["NEU"] * 100.0, 6))
        neg_vals.append(round(p["NEG"] * 100.0, 6))

    df[col_pos] = pd.Series(pos_vals, index=df.index)
    df[col_neu] = pd.Series(neu_vals, index=df.index)
    df[col_neg] = pd.Series(neg_vals, index=df.index)

    return df


def procesa_archivo(path_xlsx: str):
    """
    Procesa todas las hojas de un archivo Excel y les añade
    las columnas de polaridad triclase (POS/NEU/NEG) target-based.
    """
    print(f"→ Procesando {os.path.basename(path_xlsx)}")
    xls = pd.ExcelFile(path_xlsx, engine="openpyxl")

    # Procesamos primero todas las hojas en memoria
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

    # Escritura a disco
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

    # Procesa el archivo de entrada
    procesa_archivo(INPUT_XLSX)


if __name__ == "__main__":
    main()

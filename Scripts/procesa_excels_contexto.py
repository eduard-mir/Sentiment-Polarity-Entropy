# -*- coding: utf-8 -*-
"""
Procesa uno o varios archivos Excel (.xlsx/.xls) con DOS columnas:
  1) palabra evaluativa
  2) texto en contexto (no segmentado)

Para cada fila, segmenta el contexto en oraciones (spaCy, español),
localiza la oración que contiene la palabra evaluativa y exporta un
Excel con CUATRO columnas:
  - palabra        (la evaluativa original)
  - izquierda      (oración anterior si existe, si no, vacío)
  - objetivo       (oración que contiene la evaluativa)
  - derecha        (oración siguiente si existe, si no, vacío)

USO (desde Terminal / PowerShell):
  # Un archivo
  python procesa_excels_contexto.py --excel adjetivos.xlsx --salida out_adjetivos.xlsx --hoja "Sheet1" --col-palabra "keyword" --col-contexto "concordance"

  # Una carpeta con varios Excels (procesa todos los .xlsx/.xls)
  python procesa_excels_contexto.py --carpeta ./mis_excels --salida-carpeta ./salidas --hoja "Sheet1" --col-palabra "keyword" --col-contexto "concordance"

Requisitos:
  - pandas, openpyxl, spacy (instalados)
  - modelo spaCy: es_core_news_sm
"""
import argparse
import sys
import unicodedata
import re
from pathlib import Path
from typing import Optional, Tuple, List

import pandas as pd
import spacy

# ------------------ utilidades ------------------
def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower() if isinstance(s, str) else s

def strip_accents(s: str) -> str:
    if not isinstance(s, str):
        return s
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in nfkd if unicodedata.category(ch) != 'Mn')

def contiene_evaluativa(sent_text: str, evaluativa: str, sent_spacy) -> Optional[str]:
    """
    Devuelve la forma encontrada si la oración contiene la evaluativa.
    Primero por tokens (forma y lema), luego una búsqueda leniente sin acentos.
    """
    ev_norm = norm(evaluativa)
    ev_norm_strip = strip_accents(ev_norm)

    # tokens
    for tok in sent_spacy:
        t = norm(tok.text)
        l = norm(tok.lemma_)
        if t == ev_norm or l == ev_norm:
            return tok.text
        if strip_accents(t) == ev_norm_strip or strip_accents(l) == ev_norm_strip:
            return tok.text

    # respaldo regex leniente
    sent_noacc = strip_accents(norm(sent_text or ""))
    ev_noacc = re.escape(ev_norm_strip)
    if re.search(rf"\b{ev_noacc}\b", sent_noacc, flags=re.UNICODE):
        return evaluativa
    return None

def extrae_ventana(oraciones, idx: int) -> Tuple[Optional[str], str, Optional[str]]:
    prev_text = oraciones[idx-1].text.strip() if idx-1 >= 0 else None
    tgt_text  = oraciones[idx].text.strip()
    next_text = oraciones[idx+1].text.strip() if idx+1 < len(oraciones) else None
    return prev_text, tgt_text, next_text

def procesa_dataframe(df: pd.DataFrame, nlp, col_palabra: str, col_contexto: str, verbose: bool=False) -> pd.DataFrame:
    rows = []
    total = len(df)
    encontrados = 0
    for idx, fila in df.iterrows():
        palabra = str(fila[col_palabra]) if pd.notna(fila[col_palabra]) else ""
        contexto = str(fila[col_contexto]) if pd.notna(fila[col_contexto]) else ""
        if not palabra or not contexto:
            continue
        doc = nlp(contexto)
        sents = list(doc.sents)
        encontrada = None
        prev_text = tgt_text = next_text = None
        for i, sent in enumerate(sents):
            hallada = contiene_evaluativa(sent.text, palabra, sent)
            if hallada:
                encontrada = hallada
                prev_text, tgt_text, next_text = extrae_ventana(sents, i)
                break
        if encontrada and tgt_text:
            encontrados += 1
            rows.append({
                "palabra": palabra,
                "izquierda": prev_text or "",
                "objetivo": tgt_text,
                "derecha": next_text or ""
            })
        if verbose and (idx % 50 == 0):
            print(f"[Progreso] fila {idx+1}/{total} | matches acumulados: {encontrados}", flush=True)
    if verbose:
        print(f"[Resumen] filas totales: {total} | coincidencias: {encontrados}", flush=True)
    return pd.DataFrame(rows, columns=["palabra", "izquierda", "objetivo", "derecha"])

def procesa_excel(ruta_excel: Path, salida_xlsx: Path, nlp, col_palabra: str, col_contexto: str, hoja: Optional[str] = None, verbose: bool=False) -> Path:
    # Lee Excel con control de hoja
    if hoja:
        df = pd.read_excel(ruta_excel, sheet_name=hoja)
    else:
        df = pd.read_excel(ruta_excel)  # si hay varias hojas, pandas puede devolver dict; fuera se controla

    if isinstance(df, dict):
        raise ValueError(f"El archivo {ruta_excel.name} tiene varias hojas. Indica una con --hoja. Hojas: {list(df.keys())}")

    if col_palabra not in df.columns or col_contexto not in df.columns:
        raise ValueError(f"En {ruta_excel.name} no se encuentran las columnas requeridas "
                         f"('{col_palabra}', '{col_contexto}'). Disponibles: {list(df.columns)}")

    if verbose:
        print(f"[Info] Procesando {ruta_excel.name} | filas: {len(df)} | columnas: {list(df.columns)}", flush=True)

    out_df = procesa_dataframe(df, nlp, col_palabra, col_contexto, verbose=verbose)

    if verbose:
        print(f"[Info] Coincidencias encontradas: {len(out_df)}", flush=True)

    salida_xlsx.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(salida_xlsx, engine="openpyxl") as writer:
        out_df.to_excel(writer, index=False, sheet_name="salida")
    return salida_xlsx

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Procesa Excel(es) y extrae oraciones (izquierda/objetivo/derecha) con evaluativas.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--excel", help="Ruta a un archivo Excel (.xlsx/.xls).")
    g.add_argument("--carpeta", help="Carpeta con Excel(s) a procesar (toma todos los .xlsx/.xls).")
    ap.add_argument("--salida", help="Ruta del Excel de salida (solo si usas --excel).")
    ap.add_argument("--salida-carpeta", help="Carpeta donde dejar salidas (obligatorio si usas --carpeta).")
    ap.add_argument("--col-palabra", default="evaluativa", help="Nombre de la columna con la palabra evaluativa (por defecto: 'evaluativa').")
    ap.add_argument("--col-contexto", default="contexto", help="Nombre de la columna con el texto en contexto (por defecto: 'contexto').")
    ap.add_argument("--hoja", default=None, help="Nombre de la hoja del Excel (opcional, pero recomendable si hay varias).")
    ap.add_argument("--modelo", default="es_core_news_sm", help="Modelo spaCy (por defecto: es_core_news_sm).")
    ap.add_argument("--verbose", action="store_true", help="Muestra progreso y resumen.")

    args = ap.parse_args()

    # Carga spaCy
    try:
        nlp = spacy.load(args.modelo)
    except OSError:
        print(f"ERROR: No se encontró el modelo '{args.modelo}'. Instálalo con:", file=sys.stderr)
        print(f"    python -m spacy download {args.modelo}", file=sys.stderr)
        sys.exit(1)

    if args.excel:
        ruta = Path(args.excel)
        if not ruta.exists():
            print(f"ERROR: No existe el archivo: {ruta}", file=sys.stderr); sys.exit(1)
        salida = Path(args.salida) if args.salida else ruta.with_name(ruta.stem + "_salida.xlsx")
        out = procesa_excel(ruta, salida, nlp, args.col_palabra, args.col_contexto, args.hoja, verbose=args.verbose)
        print(f"Procesado: {ruta.name} → {out.name}")
    else:
        carpeta = Path(args.carpeta)
        if not carpeta.exists() or not carpeta.is_dir():
            print(f"ERROR: Carpeta no válida: {carpeta}", file=sys.stderr); sys.exit(1)
        if not args.salida_carpeta:
            print("ERROR: Debes indicar --salida-carpeta cuando usas --carpeta", file=sys.stderr); sys.exit(1)
        out_dir = Path(args.salida_carpeta)
        out_dir.mkdir(parents=True, exist_ok=True)
        archivos: List[Path] = sorted(list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls")))
        if not archivos:
            print(f"No se encontraron .xlsx/.xls en {carpeta}", file=sys.stderr); sys.exit(1)
        for ruta in archivos:
            salida = out_dir / f"{ruta.stem}_salida.xlsx"
            try:
                out = procesa_excel(ruta, salida, nlp, args.col_palabra, args.col_contexto, args.hoja, verbose=args.verbose)
                print(f"Procesado: {ruta.name} → {out}")
            except Exception as e:
                print(f"[AVISO] Saltando {ruta.name}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

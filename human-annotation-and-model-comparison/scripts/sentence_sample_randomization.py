import pandas as pd
import numpy as np
from pathlib import Path


# =========================
# CONFIGURACIÓN
# =========================

INPUT_FILE = Path("sample_1000_sentences_for_manual_annotation.xlsx")
OUTPUT_FILE = Path("sample_1000_sentences_for_manual_annotation_randomized.xlsx")

SHEET_NAME = "sample_1000"

RANDOM_SEED = 20260423


# =========================
# LECTURA DEL ARCHIVO
# =========================

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)


# =========================
# CONTROL DE TRAZABILIDAD
# =========================

# Guarda el orden original antes de mezclar.
# Esto permite reconstruir el orden inicial si hiciera falta.
df.insert(0, "original_order", range(1, len(df) + 1))


# =========================
# ALEATORIZACIÓN REPRODUCIBLE
# =========================

rng = np.random.default_rng(RANDOM_SEED)

random_order = rng.permutation(len(df))

df_randomized = df.iloc[random_order].reset_index(drop=True)

# Nuevo orden de presentación para la anotación manual
df_randomized.insert(0, "annotation_order", range(1, len(df_randomized) + 1))


# =========================
# EXPORTACIÓN
# =========================

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df_randomized.to_excel(
        writer,
        index=False,
        sheet_name="randomized_sample"
    )

    # Hoja de control metodológico
    info = pd.DataFrame({
        "parameter": [
            "input_file",
            "input_sheet",
            "output_file",
            "random_seed",
            "n_rows_randomized",
            "method"
        ],
        "value": [
            str(INPUT_FILE),
            SHEET_NAME,
            str(OUTPUT_FILE),
            RANDOM_SEED,
            len(df_randomized),
            "Random permutation without replacement"
        ]
    })

    info.to_excel(
        writer,
        index=False,
        sheet_name="randomization_info"
    )


# =========================
# CONTROL FINAL
# =========================

print(f"Archivo creado correctamente: {OUTPUT_FILE}")
print(f"Filas aleatorizadas: {len(df_randomized)}")
print(f"Semilla utilizada: {RANDOM_SEED}")
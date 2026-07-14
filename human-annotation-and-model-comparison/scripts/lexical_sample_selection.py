import pandas as pd
import numpy as np
from pathlib import Path


# =========================
# CONFIGURACIÓN
# =========================

INPUT_FILE = Path("Adj_entropy.xlsx")
OUTPUT_FILE = Path("selected_200_adjectives.csv")

RANDOM_SEED = 20260423
N_TOTAL = 200

# Si quieres muestreo equilibrado entre polaridades:
CLASS_QUOTAS = {
    "NEG": 67,
    "NEU": 67,
    "POS": 66,
}

# Columna de entropía que se usará para crear bandas baja/media/alta.
# Si has añadido la nueva columna "Entropy_of_mean", puedes cambiarlo aquí.
ENTROPY_COL = "Entropy - Mean"

WORD_COL = "palabra"
POS_COL = "POS - Mean"
NEU_COL = "NEU - Mean"
NEG_COL = "NEG - Mean"


# =========================
# LECTURA DEL ARCHIVO
# =========================

df = pd.read_excel(INPUT_FILE)

required_columns = [WORD_COL, POS_COL, NEU_COL, NEG_COL, ENTROPY_COL]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(
        f"Faltan columnas en el archivo: {missing}\n"
        f"Columnas disponibles: {list(df.columns)}"
    )


# =========================
# CONVERSIÓN SEGURA A NÚMEROS
# =========================

def to_numeric_safe(series):
    """
    Convierte una columna a número.
    Sirve tanto si Excel la ha leído como número como si la ha leído como texto.
    """
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(float)

    return pd.to_numeric(
        series.astype(str).str.replace(",", ".", regex=False),
        errors="raise"
    )


for col in [POS_COL, NEU_COL, NEG_COL, ENTROPY_COL]:
    df[col] = to_numeric_safe(df[col])


# =========================
# IDENTIFICADOR DE FILA ORIGINAL
# =========================

# +2 porque en Excel la fila 1 es el encabezado y los datos empiezan en la fila 2.
df["source_excel_row"] = df.index + 2


# =========================
# POLARIDAD DOMINANTE
# =========================

polarity_columns = {
    POS_COL: "POS",
    NEU_COL: "NEU",
    NEG_COL: "NEG",
}

df["dominant_class"] = df[[POS_COL, NEU_COL, NEG_COL]].idxmax(axis=1)
df["dominant_class"] = df["dominant_class"].map(polarity_columns)


# =========================
# BANDAS DE ENTROPÍA
# =========================

# Crea tres bandas de entropía dentro de cada polaridad dominante:
# low, mid, high.
df["entropy_band"] = (
    df
    .groupby("dominant_class")[ENTROPY_COL]
    .transform(
        lambda s: pd.qcut(
            s.rank(method="first"),
            q=3,
            labels=["low", "mid", "high"]
        )
    )
)


# =========================
# COMPROBACIÓN DE DISPONIBILIDAD
# =========================

available_by_class = df["dominant_class"].value_counts().to_dict()

for cls, quota in CLASS_QUOTAS.items():
    available = available_by_class.get(cls, 0)
    if available < quota:
        raise ValueError(
            f"No hay suficientes palabras de la clase {cls}: "
            f"se necesitan {quota}, pero solo hay {available}."
        )


# =========================
# MUESTREO ESTRATIFICADO
# =========================

rng = np.random.default_rng(RANDOM_SEED)

selected_parts = []

entropy_bands = ["low", "mid", "high"]

for cls, class_quota in CLASS_QUOTAS.items():

    class_df = df[df["dominant_class"] == cls].copy()

    # Repartimos la cuota de cada clase entre low/mid/high.
    base = class_quota // len(entropy_bands)
    remainder = class_quota % len(entropy_bands)

    band_quotas = {
        band: base for band in entropy_bands
    }

    # El sobrante se reparte de forma determinista.
    for band in entropy_bands[:remainder]:
        band_quotas[band] += 1

    selected_indices = []

    for band in entropy_bands:
        band_df = class_df[class_df["entropy_band"] == band].copy()

        # Orden estable para que el proceso no dependa del orden original del Excel.
        band_df = band_df.sort_values(WORD_COL, kind="mergesort")

        n_to_select = band_quotas[band]

        if len(band_df) < n_to_select:
            raise ValueError(
                f"No hay suficientes palabras en el estrato {cls}-{band}: "
                f"se necesitan {n_to_select}, pero solo hay {len(band_df)}."
            )

        chosen = rng.choice(
            band_df.index.to_numpy(),
            size=n_to_select,
            replace=False
        )

        selected_indices.extend(chosen)

    selected_parts.append(df.loc[selected_indices])


selected = pd.concat(selected_parts, axis=0)

# Orden final estable y legible
selected = selected.sort_values(
    ["dominant_class", "entropy_band", WORD_COL],
    kind="mergesort"
).reset_index(drop=True)

selected.insert(
    0,
    "sample_word_id",
    [f"W{i:03d}" for i in range(1, len(selected) + 1)]
)


# =========================
# EXPORTACIÓN
# =========================

selected.to_csv(
    OUTPUT_FILE,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# =========================
# RESUMEN DE CONTROL
# =========================

print("Archivo creado:", OUTPUT_FILE)
print()
print("Distribución por polaridad dominante:")
print(selected["dominant_class"].value_counts())
print()
print("Distribución por polaridad y banda de entropía:")
print(pd.crosstab(selected["dominant_class"], selected["entropy_band"]))
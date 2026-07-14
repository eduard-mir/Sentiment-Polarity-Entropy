import pandas as pd
import numpy as np
from pathlib import Path


# =========================
# CONFIGURACIÓN
# =========================

SELECTED_ADJECTIVES_FILE = Path("selected_200_adjectives.csv")
CORPUS_FILE = Path("adj_polarity_entropy_corpus.csv")

OUTPUT_FILE = Path("sample_1000_sentences_for_manual_annotation.xlsx")

RANDOM_SEED = 20260423
N_SENTENCES_PER_ADJECTIVE = 5

# Si alguna palabra tiene menos de 5 oraciones:
# False = detener el script con error
# True = tomar las que haya disponibles
ALLOW_FEWER_THAN_5 = False


# =========================
# FUNCIONES AUXILIARES
# =========================

def normalize_word(value):
    """
    Normaliza mínimamente la palabra para hacer coincidir los dos archivos:
    - convierte a texto
    - elimina espacios iniciales/finales
    - pasa a minúsculas
    """
    return str(value).strip().lower()


def read_selected_adjectives(path):
    """
    Lee el archivo de los 200 adjetivos seleccionados.

    Si existe una columna llamada 'palabra', usa esa columna.
    Si no existe, usa la primera columna del archivo.
    """

    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")

    if "palabra" in df.columns:
        word_col = "palabra"
    else:
        word_col = df.columns[0]

    adjectives = (
        df[word_col]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    # Elimina duplicados conservando el orden original
    adjectives_unique = list(dict.fromkeys(adjectives))

    if len(adjectives_unique) != len(adjectives):
        print(
            f"Advertencia: había {len(adjectives)} entradas, "
            f"pero solo {len(adjectives_unique)} adjetivos únicos."
        )

    return adjectives_unique, df, word_col


def read_corpus(path):
    """
    Lee el corpus de polaridad y entropía.

    El archivo está separado por punto y coma y usa coma decimal.
    """

    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
        decimal=","
    )

    if "palabra" not in df.columns:
        raise ValueError(
            "No se encontró la columna 'palabra' en el corpus. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    return df


# =========================
# LECTURA DE ARCHIVOS
# =========================

selected_adjectives, selected_df, selected_word_col = read_selected_adjectives(
    SELECTED_ADJECTIVES_FILE
)

corpus_df = read_corpus(CORPUS_FILE)


# =========================
# PREPARACIÓN DEL CORPUS
# =========================

# Guarda la fila original del corpus.
# +2 porque en el CSV la fila 1 es el encabezado y los datos empiezan en la fila 2.
corpus_df["source_corpus_row"] = corpus_df.index + 2

# Clave normalizada para hacer el cruce
corpus_df["_word_key"] = corpus_df["palabra"].apply(normalize_word)

selected_keys = [normalize_word(w) for w in selected_adjectives]


# =========================
# COMPROBACIONES
# =========================

available_words = set(corpus_df["_word_key"])

missing_words = [
    word for word, key in zip(selected_adjectives, selected_keys)
    if key not in available_words
]

if missing_words:
    raise ValueError(
        "Hay adjetivos seleccionados que no aparecen en el corpus:\n"
        + "\n".join(missing_words[:50])
        + (
            f"\n... y {len(missing_words) - 50} más."
            if len(missing_words) > 50
            else ""
        )
    )


# =========================
# MUESTREO REPRODUCIBLE
# =========================

rng = np.random.default_rng(RANDOM_SEED)

sampled_parts = []

for adjective, key in zip(selected_adjectives, selected_keys):

    adjective_rows = corpus_df[corpus_df["_word_key"] == key].copy()

    n_available = len(adjective_rows)

    if n_available < N_SENTENCES_PER_ADJECTIVE:
        message = (
            f"El adjetivo '{adjective}' solo tiene {n_available} oraciones "
            f"disponibles, pero se necesitan {N_SENTENCES_PER_ADJECTIVE}."
        )

        if not ALLOW_FEWER_THAN_5:
            raise ValueError(message)
        else:
            print("Advertencia:", message)
            n_to_sample = n_available
    else:
        n_to_sample = N_SENTENCES_PER_ADJECTIVE

    # Orden estable antes del muestreo.
    # Esto ayuda a que la selección sea reproducible incluso si cambia el orden interno.
    adjective_rows = adjective_rows.sort_values(
        ["palabra", "oracion", "source_corpus_row"],
        kind="mergesort"
    )

    chosen_indices = rng.choice(
        adjective_rows.index.to_numpy(),
        size=n_to_sample,
        replace=False
    )

    sampled = corpus_df.loc[chosen_indices].copy()

    sampled["selected_adjective"] = adjective
    sampled["n_available_for_adjective"] = n_available

    sampled_parts.append(sampled)


sample_df = pd.concat(sampled_parts, axis=0)


# =========================
# ORDEN Y COLUMNAS DE CONTROL
# =========================

sample_df["_selected_order"] = sample_df["selected_adjective"].apply(
    lambda x: selected_keys.index(normalize_word(x))
)

sample_df = sample_df.sort_values(
    ["_selected_order", "source_corpus_row"],
    kind="mergesort"
).reset_index(drop=True)

sample_df.insert(
    0,
    "sample_sentence_id",
    [f"S{i:04d}" for i in range(1, len(sample_df) + 1)]
)

# Número de oración dentro de cada adjetivo: 1, 2, 3, 4, 5
sample_df.insert(
    1,
    "sentence_number_for_adjective",
    sample_df.groupby("selected_adjective").cumcount() + 1
)

# Elimina columnas técnicas internas
sample_df = sample_df.drop(columns=["_word_key", "_selected_order"])


# =========================
# EXPORTACIÓN A EXCEL
# =========================

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    sample_df.to_excel(writer, index=False, sheet_name="sample_1000")

    # También guardamos una hoja de resumen para control metodológico
    summary = (
        sample_df
        .groupby("selected_adjective")
        .agg(
            n_sentences_selected=("oracion", "count"),
            n_available_for_adjective=("n_available_for_adjective", "first")
        )
        .reset_index()
    )

    summary.to_excel(writer, index=False, sheet_name="summary")


# =========================
# CONTROL FINAL
# =========================

print(f"Archivo creado correctamente: {OUTPUT_FILE}")
print(f"Adjetivos seleccionados: {len(selected_adjectives)}")
print(f"Oraciones extraídas: {len(sample_df)}")
print()
print("Distribución de oraciones por adjetivo:")
print(sample_df["selected_adjective"].value_counts().describe())
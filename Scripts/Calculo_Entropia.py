import pandas as pd
import numpy as np

# === CONFIGURACIÓN ===
RUTA_EXCEL = r"C:\Users\Edu\PycharmProjects\Entropía_OK\adjetivos_con_polaridad.xlsx"  # cambia si el archivo se llama distinto
HOJA = 0  # o el nombre de la hoja, por ejemplo "Hoja1"

# Bins semánticos:
# 0–0.33 → negativo
# 0.33–0.66 → neutral
# 0.66–1 → positivo
# Ponemos 1.0000001 al final para asegurar que el valor 1.0 entra en el último bin
BINS = np.array([0.0, 0.33, 0.66, 1.0000001])


def calcular_entropia(p):
    """
    Calcula la entropía de Shannon (base 2) de un vector de probabilidades.
    p: iterable de probabilidades (ej. [0.2, 0.5, 0.3])
    """
    p = np.array(p, dtype=float)
    p = p[p > 0]  # evitar log(0)
    if len(p) == 0:
        return 0.0
    return float(-(p * np.log2(p)).sum())


def main():
    # === 1. Cargar el Excel original ===
    df = pd.read_excel(RUTA_EXCEL, sheet_name=HOJA)

    # Columna A = palabra, columna H = polaridad continua [0,1]
    col_palabra = df.columns[0]   # columna A
    col_pol = df.columns[7]       # columna H

    # Nos quedamos con lo que necesitamos para el cálculo
    datos = df[[col_palabra, col_pol]].copy()
    datos.columns = ["palabra", "polaridad"]

    # Eliminar filas sin palabra o sin polaridad
    datos = datos.dropna(subset=["palabra", "polaridad"])
    datos["polaridad"] = datos["polaridad"].astype(float)

    # Entropía máxima con 3 bins (para normalizar a 0–1)
    H_max = np.log2(3)

    # === 2. Función para calcular entropía por palabra usando 3 bins ===
    def entropia_de_grupo(grupo):
        vals = grupo["polaridad"].values
        counts, _ = np.histogram(vals, bins=BINS)
        total = counts.sum()
        if total == 0:
            return pd.Series({
                "entropia_3bins": 0.0,
                "entropia_3bins_norm": 0.0
            })
        p = counts / total
        H = calcular_entropia(p)
        H_norm = H / H_max if H_max > 0 else 0.0
        return pd.Series({
            "entropia_3bins": H,
            "entropia_3bins_norm": H_norm
        })

    # === 3. Calcular entropía (y entropía normalizada) por palabra ===
    entropias = datos.groupby("palabra").apply(entropia_de_grupo)

    # === 4. Añadir las entropías al dataframe original ===
    df_nuevo = df.copy()
    df_nuevo["entropia_3bins"] = df_nuevo[col_palabra].map(entropias["entropia_3bins"])
    df_nuevo["entropia_3bins_norm"] = df_nuevo[col_palabra].map(entropias["entropia_3bins_norm"])

    # === 5. Guardar resultado en un nuevo Excel ===
    salida = r"C:\Users\Edu\PycharmProjects\Entropía_OK\salida_sentimientos_3bins.xlsx"
    df_nuevo.to_excel(salida, index=False)

    print(f"Listo. Archivo creado: {salida}")


if __name__ == "__main__":
    main()

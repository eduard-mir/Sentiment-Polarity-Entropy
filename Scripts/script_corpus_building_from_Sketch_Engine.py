# === CONFIGURA QUI ===

API_KEY = "ad68b79942f1c7dadba443c92cb48ca2"
CORPUS = "preloaded/estenten23_fl6"  # confermato da te
KEYWORD_FILE = "KEYWORD_FILE_VERB.txt"     # file con lista di parole (una per riga)
PAGE_SIZE = 500                       # numero di esempi per keyword
KWIC_LEFT = 200                       # contesto sinistro
KWIC_RIGHT = 200                      # contesto destro
OUTPUT_XLSX = "concordances_VERB.xlsx"
SLEEP_BETWEEN = 10                    # secondi di pausa tra le query
QUERY_MODE = "word"                  # "word", "lemma", o "pos"
# ======================

import requests
import pandas as pd
import time

BASE = "https://api.sketchengine.eu/search"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def obtener_concordancias(keyword, pagesize=5, left=200, right=200):
    # Costruzione della query a seconda della modalità scelta
    if QUERY_MODE == "word":
        query = f'q[word="{keyword}"]'
    elif QUERY_MODE == "lemma":
        query = f'q[lemma="{keyword}"]'
    elif QUERY_MODE == "pos":
        # Cerca avverbi taggati come RG (standard nei corpus spagnoli TenTen)
        query = f'q[word="{keyword}" & tag="RG"]'
    else:
        query = f'q[word="{keyword}"]'  # fallback

    params = {
        "corpname": CORPUS,
        "format": "json",
        "pagesize": pagesize,
        "fromp": 1,
        "kwicleftctx": str(left) + "#",
        "kwicrightctx": str(right) + "#",
        "q": query,
    }

    try:
        r = requests.get(f"{BASE}/concordance", params=params, headers=HEADERS, timeout=60)
    except requests.RequestException as e:
        print(f"❌ Errore di rete per '{keyword}': {e}")
        return []

    if r.status_code == 429:
        print("⚠️ Troppe richieste – SketchEngine ti ha temporaneamente bloccato.")
        print("   Attendi 10 minuti e riprova.")
        return []

    if r.status_code != 200:
        print(f"⚠️ Errore {r.status_code} per '{keyword}' → {r.text[:200]}")
        return []

    try:
        data = r.json()
    except Exception as e:
        print(f"⚠️ Errore nel parsing JSON per '{keyword}':", e)
        print(r.text[:400])
        return []

    # Debug opzionale (puoi commentare queste righe)
    concsize = data.get("concsize", "N/A")
    print(f"→ Query: {query}")
    print(f"→ Risultati trovati: {concsize}")

    lines = data.get("Lines", [])
    if not lines:
        print(f"⚠️ Nessun risultato per '{keyword}'")
        return []

    kwic_lines = []
    for it in lines:
        L = " ".join(tok.get("str", "") for tok in it.get("Left", []))
        K = " ".join(tok.get("str", "") for tok in it.get("Kwic", []))
        R = " ".join(tok.get("str", "") for tok in it.get("Right", []))
        frase = " ".join(f"{L} {K} {R}".split())
        kwic_lines.append(frase)

    return kwic_lines


def main():
    try:
        with open(KEYWORD_FILE, "r", encoding="utf-16") as f:
            keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File non trovato: {KEYWORD_FILE}")
        return

    all_rows = []
    print(f"🔍 Inizio estrazione per {len(keywords)} parole...\n")

    for kw in keywords:
        print(f"🔍 Elaboro '{kw}'...")
        examples = obtener_concordancias(kw, PAGE_SIZE, KWIC_LEFT, KWIC_RIGHT)

        for ex in examples:
            all_rows.append({"keyword": kw, "concordance": ex})

        # Pausa per non superare i limiti API
        time.sleep(SLEEP_BETWEEN)

    if not all_rows:
        print("⚠️ Nessun risultato trovato.")
        return

    df = pd.DataFrame(all_rows)
    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"\n✅ File salvato: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
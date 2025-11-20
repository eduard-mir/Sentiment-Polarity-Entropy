# Sentiment-Polarity-Entropy
En este proyecto analizamos la variación de la polaridad de sentimiento de una palabra en diferentes contextos para obtener la medición de la estabilidad semántica de un término en función de su comportamiento.

## Licencias
- El **código** (carpeta /scripts) está bajo licencia **MIT License** (ver archivo LICENSE).
- Los **datos lingüísticos** (carpeta /data) están bajo **CC BY 4.0** (ver archivo LICENSE-DATA).


---

## 1. Recopilación del corpus
El corpus se obtuvo mediante la API de **SketchEngine** utilizando listas de palabras semilla contenidas en: Lexicons
Los scripts utilizados para automatizar este proceso están disponibles en: Scripts

## 2. Segmentación oracional
El corpus bruto se segmentó en oraciones utilizando spaCy (es_core_news_sm). Para cada fila del corpus, el script:
divide el texto en oraciones, identifica la oración que contiene la palabra evaluativa (por forma, lema y coincidencias lenientes), y extrae una ventana contextual formada por la oración anterior, la oración objetivo y la oración siguiente.
El resultado es un Excel con tres niveles de contexto necesarios para los análisis posteriores.
Los scripts utilizados para automatizar este proceso están disponibles en: Scripts

## 3. Análisis de sentimiento
El cálculo de polaridad (POS / NEU / NEG) se realiza utilizando el modelo de análisis de sentimiento en español incluido en pysentimiento (Pérez, et al., 2021).
from pysentimiento import create_analyzer
analyzer = create_analyzer(task="sentiment", lang="es")
Los scripts utilizados para automatizar este proceso están disponibles en: Scripts

Este script utiliza el analizador de sentimiento triclase de pysentimiento
(Pérez, Giudici & Luque 2021), basado en un modelo transformer para español
que devuelve probabilidades POS / NEU / NEG.

## 4. Cálculo Entropía
Para cada palabra del corpus, calculamos la entropía de polaridad midiendo cuánta variación muestran sus valores de polaridad a lo largo de todas sus ocurrencias. El script agrupa esos valores en tres categorías (negativa, neutra y positiva), cuenta cómo se distribuyen y obtiene una medida que indica hasta qué punto la polaridad de la palabra es estable o, por el contrario, fluctúa entre distintos usos. El resultado se añade al Excel final en forma de dos columnas: la entropía calculada y su versión normalizada entre 0 y 1.
Los scripts utilizados para automatizar este proceso están disponibles en: Scripts


Si utiliza este repositorio o alguno de los scripts/datos incluidos, por favor cite el proyecto de la siguiente manera:
Mir-Neira, E. (2025). *Sentiment-Polarity-Entropy* (versión X.X). GitHub.  
https://github.com/USUARIO/Sentiment-Polarity-Entropy


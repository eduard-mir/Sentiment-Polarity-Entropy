# Sentiment-Polarity-Entropy
# 1. Overview
This project investigates sentiment polarity entropy by analysing lexical items across multiple corpora and computing entropy-based sentiment distributions using Orange Data Mining. The aim is to quantify the semantic stability or variability of lexical items in terms of their association with positive, negative and neutral sentiment, based on evidence from real corpus data. The repository includes the full computational workflow, datasets, extracted concordances and visualisations.

## Licenses:
The code (the /scripts directory) is released under the MIT License (see the LICENSE file).
The linguistic data (the /data directory) is released under the CC BY 4.0 License (see the LICENSE-DATA file).

# 2. Objectives
The main objectives of the project are:
To construct a corpus-based resource for analysing sentiment polarity entropy.
To extract lexical occurrences and concordances from Sketch Engine.
To compute probabilistic sentiment distributions for each lexical item.
To calculate entropy as a measure of semantic dispersion across polarity classes.
To visualise polarity distributions and entropy groupings using Orange Data Mining.
To provide a reproducible and extensible framework for further research in sentiment analysis and lexical semantics.

# 3. Data Components
## 3.1 Lexicons
The project includes the following lexical datasets, each representing one part of speech:
nombres_entropia_Orange.csv (nouns)
verbos_entropia_Orange.csv (verbs)
adjetivos_entropia_Orange.csv (adjectives)
adverbios_entropia_Orange.csv (adverbs)

Each file contains the list of lexical items evaluated for polarity entropy.

## 3.2 Corpora
Several datasets derived from corpus analysis are included:
Triclass Polarity Corpus: distributions of positive, negative and neutral probabilities.
Polarity Entropy Corpus: entropy values derived from the polarity distributions.
Sketch Engine Occurrences Corpus: concordances extracted from Sketch Engine, used as the empirical basis for probability estimation.

All supplementary materials associated with this repository, including the full set of concordances extracted from Sketch Engine, the trinary sentiment annotations, and the entropy computations for adjectives, adverbs, nouns and verbs are available in the following Zenodo record:

Mir-Neira, E. (2025). Sentiment Polarity Entropy Dataset and Supplementary Materials [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17768537

This dataset complements the code and resources hosted in this GitHub project and provides complete reproducibility for all analyses.

## 3.3 Orange Workflow
The workflow is provided in:
Polaridad_Entropy_Representacion.ows
This file contains the complete Orange pipeline used for:
importing polarity probability data,
computing and normalising entropy values,
generating two-dimensional scatterplots (POS vs. NEG median probabilities),
applying entropy-based colour coding,
producing density-enhanced visual representations of the polarity space.

# 4. Visualisation
The project includes visualisations representing the distribution of polarity probabilities for individual lexical items. A typical representation plots median positive probability on the x-axis and median negative probability on the y-axis, with colour encoding the entropy interval. These visualisations facilitate the identification of lexical patterns such as sentiment asymmetry, polarity ambiguity and semantic clustering.

# 5. Methodology
## 5.1 Data Extraction
The corpus was obtained through the Sketch Engine API, using seed word lists contained in the SO-CAL (Semantic Orientation CALculator)Lexicon (Taboada et al., 2011). For each lexical item, occurrences and context windows were retrieved programmatically.
All scripts used to automate this process are provided in the Scripts directory.

## 5.2 Sentence Segmentation and Context Extraction
The raw corpus was segmented into sentences using spaCy (es_core_news_sm). For each row in the corpus, the script:
splits the text into sentences,
identifies the sentence containing the evaluative word (based on form, lemma or fuzzy matching),
extracts a contextual window consisting of the previous sentence, the target sentence and the following sentence.
The resulting dataset is exported as an Excel file containing the three levels of context required for downstream analyses.
The corresponding automation scripts are available in the Scripts directory.

## 5.3 Sentiment Analysis
Sentiment polarity (POS / NEU / NEG) is computed using the pysentimiento sentiment analysis model for Spanish (Pérez et al., 2021):
from pysentimiento import create_analyzer
analyzer = create_analyzer(task="sentiment", lang="es")
This model is a transformer-based trinary sentiment classifier (Pérez, Giudici & Luque 2021) that returns probability scores for positive, neutral and negative sentiment.
All scripts implementing this step are available in the Scripts directory.

## 5.4 Probability Computation
For each lexical item, the probabilities
𝑃(POS), 𝑃(NEG), 𝑃(NEU) 
were derived from corpus frequencies and normalised across sentiment classes.

## 5.5 Entropy Calculation
Entropy values were computed using Shannon's entropy formula:
$$ H = -\sum_i P_i \log_2 P_i $$
Higher entropy values reflect greater dispersion across sentiment classes, whereas lower values indicate stronger association with a specific polarity.

## 5.6 Visualisation and Analysis
The datasets were imported into Orange Data Mining, where scatterplots and density fields were generated to represent the probabilistic behaviour of lexical items. Entropy groups were incorporated into the visualisation to highlight semantic tendencies and contrast lexical categories.

# 6. Repository Structure
/data

    nombres_entropia_Orange.csv
    verbos_entropia_Orange.csv
    adjetivos_entropia_Orange.csv
    adverbios_entropia_Orange.csv
    
/orange

    Polaridad_Entropy_Representacion.ows
    
/figures

    visualisations of polarity distributions
    
README.md
LICENSE

# 7. Usage Instructions
## 7.1 Opening the Workflow in Orange
Install Orange Data Mining.
Open Polaridad_Entropy_Representacion.ows.
Load the CSV datasets included in the repository.
Run the workflow to reproduce the entropy calculations and visualisations.

## 7.2 Reproducibility and Adaptation
The workflow and datasets may be adapted to:
extend lexical lists,
incorporate additional corpora,
modify entropy thresholds,
explore alternative visualisation techniques,
integrate new sentiment classification resources.

# 8. Citation
If this project or its datasets are used in academic work, please cite the corresponding Zenodo DOI once published:
Mir-Neira, E. (2025). eduard-mir/Sentiment-Polarity-Entropy: v.1.2 (v.1.2). Zenodo. https://doi.org/10.5281/zenodo.17768392

# 9. Acknowledgements
This work makes use of:
Sketch Engine for concordance extraction,
Orange Data Mining for analysis and visualisation,
Various corpora used to derive polarity probabilities and entropy values.

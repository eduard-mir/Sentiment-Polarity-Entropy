# Sentiment-Polarity-Entropy

# 1. Overview
This project investigates sentiment polarity entropy by analysing lexical items extracted from a large Spanish web corpus (esTenTen) and computing entropy-based sentiment distributions using Orange Data Mining. The aim is to quantify the semantic stability or variability of lexical items in terms of their association with positive, negative and neutral sentiment, based on evidence from real corpus data, and to distinguish lexically encoded polarity from context-dependent polarity.

The repository also includes an independent validation of this entropy-based diagnostic through human annotation and comparison with additional automatic sentiment classifiers, documented in the `/human-annotation-and-model-comparison` folder (see Section 3.4).

## Licenses
The code (the /Scripts directory and the /human-annotation-and-model-comparison/scripts directory) is released under the MIT License (see the LICENSE file).
The annotations, scores, and derived data (lexicon word lists, polarity/entropy values, human annotations, Gold Human Label, and model outputs, found in the /Lexicons directory and the /human-annotation-and-model-comparison/excel_files directory) are released under the CC BY 4.0 License (see the LICENSE-DATA file).
The corpus sentences included for context throughout this project's tabular data (in this repository and in the associated Zenodo records) are extracted from the esTenTen corpus (Jakubíček et al., 2013) via Sketch Engine and are not covered by the CC BY 4.0 license; they remain subject to Sketch Engine's terms of use and are shared here solely to support the reproducibility of this study.

# 2. Objectives
The main objectives of the project are:
- To construct a corpus-based resource for analysing sentiment polarity entropy.
- To extract lexical occurrences and concordances from Sketch Engine.
- To compute probabilistic sentiment distributions for each lexical item.
- To calculate entropy as a measure of semantic dispersion across polarity classes.
- To visualise polarity distributions and entropy groupings using Orange Data Mining.
- To validate the entropy-based diagnostic against independent human judgment and additional automatic classifiers, including large language models.
- To provide a reproducible and extensible framework for further research in sentiment analysis and lexical semantics.

# 3. Data Components

## 3.1 Lexicons
The project includes the following lexical datasets, each representing one part of speech, contained in the /Lexicons folder:

adj_dict_spa.md (adjectives)
adv_dict_spa.md (adverbs)
noun_dict_spa.md (nouns)
verb_dict_spa.txt (verbs)

Each file contains the seed lexical list evaluated for polarity entropy, drawn from the SO-CAL Spanish lexicon (Taboada et al., 2011). The full probability and entropy data computed for these items are available in the Zenodo record described in Section 3.2.

## 3.2 Corpora
Several datasets derived from corpus analysis are included:
- Triclass Polarity Corpus: distributions of positive, negative and neutral probabilities.
- Polarity Entropy Corpus: entropy values derived from the polarity distributions.
- Sketch Engine Occurrences Corpus: concordances extracted from Sketch Engine (esTenTen; Jakubíček et al., 2013), used as the empirical basis for probability estimation.

All supplementary materials associated with this repository, including the full set of concordances extracted from Sketch Engine, the trinary sentiment annotations, and the entropy computations for adjectives, adverbs, nouns and verbs are available in the following Zenodo record:

Mir-Neira, E. (2025). Sentiment Polarity Entropy Dataset and Supplementary Materials [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17768537

This dataset complements the code and resources hosted in this GitHub project and provides complete reproducibility for all analyses.

## 3.3 Orange Workflow
The Orange workflow project and all associated files are available in the Zenodo deposit linked to this repository. The workflow file included there (Polaridad_Entropy_Representacion.ows) contains the complete Orange pipeline used for importing polarity-probability data, computing and normalising entropy values, generating two-dimensional scatterplots (POS vs. NEG median probabilities), applying entropy-based colour coding, and producing density-enhanced visual representations of the polarity space.

## 3.4 Human-Annotated Benchmark and Cross-Model Comparison
The `/human-annotation-and-model-comparison` folder contains an independent validation of the entropy-based diagnostic, built on a stratified sample of 200 adjectives (959 sentences) balanced by dominant polarity and entropy tercile. It includes the triple human annotation used to construct the Gold Human Label, and a comparison of automatic polarity assignment across four systems: the original classifier (pysentimiento/robertuito-sentiment-analysis; Section 5.3), a second transformer-based model (cardiffnlp/twitter-xlm-roberta-base-sentiment; Barbieri, Espinosa-Anke, and Camacho-Collados, 2022), and two general-purpose large language models, ChatGPT (GPT-5.5 Thinking; OpenAI, 2026) and Claude (Claude Sonnet 5; Anthropic, 2026). See the dedicated README inside that folder for full methodological details.

# 4. Visualisation
The project includes visualisations representing the distribution of polarity probabilities for individual lexical items. A typical representation plots median positive probability on the x-axis and median negative probability on the y-axis, with colour encoding the entropy interval. These visualisations facilitate the identification of lexical patterns such as sentiment asymmetry, polarity ambiguity and semantic clustering.

# 5. Methodology

## 5.1 Data Extraction
The corpus was obtained through the Sketch Engine API, querying the esTenTen web corpus (Jakubíček et al., 2013), using seed word lists contained in the SO-CAL (Semantic Orientation CALculator) Lexicon (Taboada et al., 2011). For each lexical item, 500 occurrences and their context windows were retrieved programmatically.

All scripts used to automate this process are provided in the Scripts directory.

## 5.2 Sentence Segmentation and Context Extraction
The raw corpus was segmented into sentences using spaCy (es_core_news_sm; Honnibal and Montani, 2017). For each row in the corpus, the script:
- splits the text into sentences,
- identifies the sentence containing the evaluative word (based on form, lemma or fuzzy matching),
- extracts a contextual window consisting of the previous sentence, the target sentence and the following sentence.

The resulting dataset is exported as an Excel file containing the three levels of context required for downstream analyses.

The corresponding automation scripts are available in the Scripts directory.

## 5.3 Sentiment Analysis
Sentiment polarity (POS / NEU / NEG) is computed using the pysentimiento/robertuito-sentiment-analysis model, accessed through the pysentimiento library (Pérez et al., 2021, 2022):

```python
from pysentimiento import create_analyzer
analyzer = create_analyzer(task="sentiment", lang="es")
```

This is a trinary sentiment classifier fine-tuned on the TASS 2020 corpus, based on RoBERTuito (Pérez et al., 2022), a RoBERTa-style transformer pretrained on Spanish user-generated text, and returns probability scores for positive, neutral and negative sentiment. We report the exact model identifier here to avoid ambiguity between the pysentimiento toolkit and the underlying RoBERTuito model.

All scripts implementing this step are available in the Scripts directory.

## 5.4 Probability Computation
For each lexical item, the probabilities P(POS), P(NEG), P(NEU) were derived from corpus frequencies and normalised across sentiment classes.

## 5.5 Entropy Calculation
Entropy values were computed using Shannon's entropy formula (Shannon, 1948):

$$ H = -\sum_i P_i \log_2 P_i $$

Higher entropy values reflect greater dispersion across sentiment classes, whereas lower values indicate stronger association with a specific polarity.

## 5.6 Visualisation and Analysis
The datasets were imported into Orange Data Mining, where scatterplots and density fields were generated to represent the probabilistic behaviour of lexical items. Entropy groups were incorporated into the visualisation to highlight semantic tendencies and contrast lexical categories.

## 5.7 Human Annotation and Cross-Model Validation
To assess whether the entropy-based diagnostic reflects a genuine property of the polarity-assignment task rather than an artefact of a single classifier, a stratified sample of 200 adjectives (959 sentences) was manually annotated by three human annotators, and their labels were resolved into a Gold Human Label. This label was then compared against four automatic systems: pysentimiento/robertuito-sentiment-analysis (Pérez et al., 2021, 2022), cardiffnlp/twitter-xlm-roberta-base-sentiment (Barbieri, Espinosa-Anke, and Camacho-Collados, 2022), ChatGPT (GPT-5.5 Thinking; OpenAI, 2026) and Claude (Claude Sonnet 5; Anthropic, 2026), stratified by entropy band. Full methodology, scripts and annotation files are documented in `/human-annotation-and-model-comparison`.

# 6. Repository Structure
/Lexicons
    adj_dict_spa.md
    adv_dict_spa.md
    noun_dict_spa.md
    verb_dict_spa.txt

/Scripts
    (corpus extraction, segmentation and sentiment analysis scripts; see Section 5)

/human-annotation-and-model-comparison
    README
    /scripts
        (sample selection, accuracy and agreement computation scripts)
    /excel_files
        (human annotation files, Gold Human Label, and per-model outputs)

README.md
LICENSE
LICENSE-DATA

# 7. Usage Instructions

## 7.1 Opening the Workflow in Orange
- Install Orange Data Mining.
- Download Polaridad_Entropy_Representacion.ows from the Zenodo record (Section 3.3), as it is not included in this GitHub repository.
- Open the file in Orange.
- Load the CSV datasets included in the repository.
- Run the workflow to reproduce the entropy calculations and visualisations.

## 7.2 Reproducing the Human Annotation Benchmark
- See `/human-annotation-and-model-comparison/README.md` for instructions on reproducing the stratified sample selection, the Gold Human Label construction, and the accuracy/F1 comparison across models.

## 7.3 Reproducibility and Adaptation
The workflow and datasets may be adapted to:
- extend lexical lists,
- incorporate additional corpora,
- modify entropy thresholds,
- explore alternative visualisation techniques,
- integrate new sentiment classification resources.

# 8. Citation
If this project or its datasets are used in academic work, please cite:

Eduard Mir Neira. (2026). eduard-mir/Sentiment-Polarity-Entropy: Entropy-Based Polarity Analysis with Human Annotation and Cross-Model Comparison (Version v.2) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21373896

Mir-Neira, E. (2025). Sentiment Polarity Entropy Dataset and Supplementary Materials [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17768537

A citation for the accompanying journal article will be added here upon publication in *Computational Linguistics*.

# 9. Acknowledgements
This work makes use of:
- Sketch Engine, for concordance extraction from the esTenTen corpus (Jakubíček et al., 2013),
- Orange Data Mining, for analysis and visualisation,
- pysentimiento and RoBERTuito (Pérez et al., 2021, 2022), for sentiment classification,
- cardiffnlp/twitter-xlm-roberta-base-sentiment (Barbieri, Espinosa-Anke, and Camacho-Collados, 2022), OpenAI's ChatGPT and Anthropic's Claude, for the cross-model validation reported in `/human-annotation-and-model-comparison`,
- the SO-CAL lexicon (Taboada et al., 2011), as the source of the evaluative lexical items analysed throughout the project.

# 10. References
Anthropic. 2026. System card: Claude Sonnet 5. Technical report, Anthropic. https://www.anthropic.com/claude-sonnet-5-system-card

Barbieri, Francesco, Luis Espinosa-Anke, and Jose Camacho-Collados. 2022. XLM-T: Multilingual language models in Twitter for sentiment analysis and beyond. In *Proceedings of the Thirteenth Language Resources and Evaluation Conference*, pages 258–266, Marseille, France.

Honnibal, Matthew and Ines Montani. 2017. spaCy 2: Natural language processing with Python. https://spacy.io

Jakubíček, Miloš, Adam Kilgarriff, Vojtěch Kovář, Pavel Rychlý, and Vít Suchomel. 2013. The TenTen corpus family. In *Proceedings of the 7th International Corpus Linguistics Conference*, pages 125–127, Lancaster, UK.

OpenAI. 2026. GPT-5.5 system card. Technical report, OpenAI. https://openai.com/index/gpt-5-5-system-card/

Pérez, Juan Manuel, Mariela Rajngewerc, Juan Carlos Giudici, Damián A. Furman, Franco Luque, Laura Alonso Alemany, and María Vanina Martínez. 2021. pysentimiento: A Python toolkit for opinion mining and social NLP tasks. arXiv:2106.09462.

Pérez, Juan Manuel, Damián Ariel Furman, Laura Alonso Alemany, and Franco M. Luque. 2022. RoBERTuito: A pre-trained language model for social media text in Spanish. In *Proceedings of the Thirteenth Language Resources and Evaluation Conference*, pages 7235–7243, Marseille, France.

Shannon, Claude E. 1948. A mathematical theory of communication. *Bell System Technical Journal*, 27(3):379–423.

Taboada, Maite, Julian Brooke, Milan Tofiloski, Kimberly Voll, and Manfred Stede. 2011. Lexicon-based methods for sentiment analysis. *Computational Linguistics*, 37(2):267–307.

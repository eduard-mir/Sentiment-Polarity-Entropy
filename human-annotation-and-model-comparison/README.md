# Human Annotation and Model Comparison

This folder contains the human-annotated benchmark and the cross-model validation associated with this project. It documents how a stratified sample of adjectives and sentences was drawn from the corpus, how it was manually annotated for polarity, how a Gold Human Label was derived from multiple annotators, and how four automatic systems (pysentimiento/RoBERTuito, Cardiff NLP's twitter-xlm-roberta-base-sentiment, ChatGPT, and Claude) were evaluated against that gold standard.

## Folder structure

```
human-annotation-and-model-comparison/
├── README.md
├── scripts/
│   ├── lexical_sample_selection.py
│   ├── sentence_sample_selection.py
│   ├── sentence_sample_randomization.py
│   ├── 01_human_raw_agreement.py
│   ├── 02_auto_label.py
│   ├── 03_create_gold_human_label.py
│   ├── 04_auto_vs_gold_accuracy.py
│   ├── 05_add_entropy_band_to_sample.py
│   ├── 06_accuracy_by_entropy_band.py
│   ├── 07_precision_recall_f1.py
│   ├── 08_precision_recall_f1_by_entropy_band.py
│   ├── 09_accuracy_auto_pos_neg_only.py
│   └── model_comparison/
│       ├── 01_cardiff_context_sentiment.py
│       ├── 02_cardiff_accuracy_vs_gold.py
│       ├── 03_cardiff_precision_recall_f1_vs_gold.py
│       ├── 04_Accuracy_by_entropy_band.py
│       ├── 05_cardiff_precision_recall_f1_by_entropy_band.py
│       ├── 06_Accuracy_LLM_GPT.py
│       └── Accuracy_LLM_Claude.py
└── excel_files/
    ├── selected_200_adjectives.csv
    ├── excluded_sentences.xlsx
    ├── sample_1000_sentences_for_manual_annotation.xlsx
    ├── sample_1000_sentences_for_manual_annotation_randomized.xlsx
    ├── sample_1000_sentences_for_manual_annotation_randomized_auto_label_gold_entropy_band.xlsx
    ├── sample_1000_sentences_for_manual_annotation_randomized_auto_label_gold_entropy_band_Comparsion.xlsx
    ├── LLM_prueba_anotation_CHATGPT.xlsx
    ├── LLM_prueba_anotation_Claude.xlsx
    └── model_evaluation_summary.csv
```

## 1. Sample construction

**`lexical_sample_selection.py`** draws a stratified sample of 200 adjectives from the corpus. Adjectives are stratified by dominant polarity class (NEG/NEU/POS, with quotas 67/67/66) and, independently within each dominant class, by entropy tercile (`low`/`mid`/`high`), computed with `pd.qcut` on the rank of the entropy value. `RANDOM_SEED = 20260423` is fixed throughout the pipeline for reproducibility. Output: `selected_200_adjectives.csv`.

**`sentence_sample_selection.py`** samples 5 sentences per adjective (`N_SENTENCES_PER_ADJECTIVE = 5`) from the full corpus (`adj_polarity_entropy_corpus.csv`) using the same random seed, producing an initial pool of 1,000 sentences. Output: `sample_1000_sentences_for_manual_annotation.xlsx`.

**`sentence_sample_randomization.py`** shuffles the row order of the 1,000-sentence sample (same seed) so annotators see items in randomized order, blind to the original stratification. It preserves the original order in an `original_order` column and adds an `annotation_order` column. Output: `sample_1000_sentences_for_manual_annotation_randomized.xlsx`.

Of the original 1,000 sentences, 41 were subsequently excluded as non-adjectival uses (verbal participles, nominal uses, discourse markers), leaving the final annotated sample at 959 sentences. The excluded occurrences are documented in `excluded_sentences.xlsx`, included in this folder's `excel_files/` directory.

## 2. Human annotation and Gold Human Label

Each sentence was independently labeled POS/NEU/NEG by three annotators (columns *Human Annotation 1/2/3*).

**`01_human_raw_agreement.py`** classifies each of the 959 cases by raw agreement:

- **full_agreement** — all three annotators coincide: 575 cases (60.0%)
- **partial_agreement** — two of three coincide: 359 cases (37.4%)
- **no_majority** — all three annotators differ: 25 cases (2.6%)

For the 25 no_majority cases, two additional annotators (*Human Annotation 4 & 5*) adjudicated the final label.

**`02_auto_label.py`** derives the primary automatic label (`auto_label`) as the argmax of the POS/NEU/NEG probability scores already attached to each sentence from the pysentimiento/RoBERTuito classification used in the main entropy study (Pérez et al., see main repository README for the full citation).

**`03_create_gold_human_label.py`** builds the **Gold Human Label** for each sentence:

- full_agreement → the shared label of the three annotators
- partial_agreement → the majority label (2 of 3)
- no_majority → the adjudicated label from annotators 4 and 5

## 3. Evaluation of the primary classifier (pysentimiento) against the Gold Human Label

- **`04_auto_vs_gold_accuracy.py`** — overall accuracy of `auto_label` vs. Gold Human Label.
- **`05_add_entropy_band_to_sample.py`** — merges the `entropy_band` (low/mid/high) from `selected_200_adjectives.csv` into the annotated sample, matched by lexical item.
- **`06_accuracy_by_entropy_band.py`** — accuracy stratified by entropy band.
- **`07_precision_recall_f1.py`** — precision, recall, F1 per label (NEG/NEU/POS), confusion matrix, and macro-F1.
- **`08_precision_recall_f1_by_entropy_band.py`** — the same precision/recall/F1/confusion-matrix breakdown computed separately within each entropy band.
- **`09_accuracy_auto_pos_neg_only.py`** — accuracy computed only over cases where the classifier predicted POS or NEG (excluding NEU predictions), corresponding to the polarity-only accuracy figure reported in the paper.

## 4. Cross-model comparison (`model_comparison/`)

The same 959-sentence sample and Gold Human Label were used to evaluate three additional systems under identical conditions.

**Cardiff (cardiffnlp/twitter-xlm-roberta-base-sentiment, Barbieri et al. 2022).** `01_cardiff_context_sentiment.py` extracts a ±5-word context window around each target adjective (handling Spanish morphological variants — gender/number endings and stem changes), runs batched inference (batch size 16, max length 128), and writes the model's label, class probabilities, context window, and a target-found flag. `02_cardiff_accuracy_vs_gold.py`, `03_cardiff_precision_recall_f1_vs_gold.py`, `04_Accuracy_by_entropy_band.py`, and `05_cardiff_precision_recall_f1_by_entropy_band.py` reproduce the same accuracy / precision-recall-F1 / entropy-band analyses described in Section 3, applied to Cardiff's predictions.

**ChatGPT.** `06_Accuracy_LLM_GPT.py` reads the pre-labeled file `LLM_prueba_anotation_CHATGPT.xlsx` (identical sentences, identical prompt structure) and computes overall and by-entropy-band accuracy against the Gold Human Label.

**Claude.** `Accuracy_LLM_Claude.py` performs the equivalent computation on `LLM_prueba_anotation_Claude.xlsx`.

### Summary of results (`excel_files/model_evaluation_summary.csv`)

| System | Overall accuracy |
|---|---|
| pysentimiento (RoBERTuito) | 66.53% |
| Cardiff (twitter-xlm-roberta-base-sentiment) | 66.21% |
| ChatGPT | 86.65% |
| Claude | 84.05% |

All four systems were evaluated on the same 959-sentence sample with the same instruction text; only the output column name differed between prompts. Full per-band and per-label precision/recall/F1 figures are in `model_evaluation_summary.csv` and in the corresponding script outputs above.

## 5. Reproducibility notes

- `RANDOM_SEED = 20260423` is used consistently across sampling and randomization scripts.
- All scripts read/write `.xlsx` files with fixed column letters and row ranges (rows 2–960, i.e., the 959 sentences plus header), documented at the top of each script.
- Model versions: pysentimiento/robertuito-sentiment-analysis and cardiffnlp/twitter-xlm-roberta-base-sentiment were run locally via the scripts in this folder; ChatGPT and Claude were queried through their respective chat interfaces using the identical prompt and sentence list (not reproducible via script, but the exact input/output pairs are preserved in `LLM_prueba_anotation_CHATGPT.xlsx` and `LLM_prueba_anotation_Claude.xlsx`).

## Licensing

Code in this folder is released under the repository's MIT License. Annotation and derived data (labels, agreement statistics, accuracy/precision/recall/F1 tables) are released under CC BY 4.0. Sentences reproduced from the esTenTen corpus (Jakubíček et al. 2013) remain subject to Sketch Engine's terms of use and are **not** covered by the CC BY 4.0 grant — see `LICENSE-DATA` in the repository root for the full scope statement.

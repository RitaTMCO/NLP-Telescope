# NLP-Telescope

NLP-Telescope is a comparative analysis tool which is an updated and extended version of MT-Telescope [(rei, et al 2021)](https://aclanthology.org/2021.acl-demo.9/). Like MT-Telescope, it aims to facilitate researchers and developers to analyze their systems by offering features such as:

1) SOTA MT evaluation metrics such as COMET  [(rei, et al 2020)](https://aclanthology.org/2020.emnlp-main.213/).
2) Statistical tests such as bootstrap resampling [(Koehn, et al 2004)](https://aclanthology.org/W04-3250/).
3) Dynamic Filters to select parts of your testset with specific phenomena
4) Visual interface/plots to compare systems side-by-side segment-by-segment.

NLP-Telescope also offers new features compared to MT-Telescope such as:

1) Analyze and compare the results of N systems from M references. **N and M are numbers greater than or equal to 1.** This functionality is updated from MT-Telescope which analyzes two systems from one reference;

2) Being able to analyze four Natural Language Processing (NLP) tasks such as: **machine translation**, **text summarization**, **dialogue system** and **text classification**. Provide visual analysis interface appropriate for each task. This functionality is updated from MT-Telescope which analyzes machine translation systems;

3) Having metrics that **calculate and indicate the model’s
sensitivity to biases**. An extended functionality of MT-Telescope; (coming soon)

4) Having a metric that ranks the compared systems based on the **aggregation of the scores of the metrics selected by the user**. (coming soon)

For all tasks and for each reference, the tool offers a table with system metrics scores. For Natural Language Generation (NLG) tasks such as machine translation, text summarization and dialogue system, we have three types of visual interface:

1) **Error-type analysis:** To evaluate system utility, the tool divides the errors into four parts through the stacked bar plot. Only available if COMET or BERTScore are selected for segment-level metrics;

2) **Segment-level scores histogram:** With a histogram plot, one may observe general evaluation of the distribution of scores between models.

3) **Segment-level comparison:** With bubble plot, the user may check the comparison of the sentence scores of the two models through the differences;

For the classification task, we have following visual interfaces:

1) Confusion matrix of each system;
2) Confusion matrix of each label;
3) Scores of each category for each system through the stacked bar plot.

In this document, we will explain how to install and run NLP-Telescope. To run the NLP-Telescope tool you can use:

1. A web browser
2. The command line interface


## Install:

Make sure you have [poetry](https://python-poetry.org/docs/#installation) installed.

Create a virtual environment. Run:

```bash
git clone https://github.com/RitaTMCO/NLP-Telescope
git checkout development_v_2
cd NLP-Telescope
poetry install --without dev
```

## Before running the tool:

Activate virtual environment. Run:

```bash
cd NLP-Telescope
poetry shell
```

Some metrics like COMET can take some time. You can switch the COMET model to a more lightweight model with the following env variable:
```bash
export COMET_MODEL=wmt21-cometinho-da
```
## Web Interface:

To run a web interface simply run:
```bash
telescope streamlit
```

## Command Line Interface (CLI):
### Comparing NLG systems:

For running system comparisons with CLI you should use the `telescope n-compare-nlg` command.

```
Usage: telescope n-compare-nlg [OPTIONS]

Options:
  -s, --source FILENAME           Source segments.  [required]
  -c, --system_output FILENAME    System candidate.  [required]
  -r, --reference FILENAME        Reference segments.  [required]
  -t, --task [machine-translation|dialogue-system|summarization]
                                  NLG to evaluate.  [required]
  -l, --language TEXT             Language of the evaluated text.  [required]
  -m, --metric [COMET|BLEU|chrF|ZeroEdit|BERTScore|TER|GLEU|ROUGE-1|ROUGE-2|ROUGE-L|Accuracy|Precision|Recall|F1-score]
                                  Metric to run.  [required]
  -f, --filter [named-entities|length|duplicates]
                                  Filter to run.
  --length_min_val FLOAT          Min interval value for length filtering.
  --length_max_val FLOAT          Max interval value for length filtering.
  --seg_metric [COMET|ZeroEdit|BERTScore|GLEU|ROUGE-L|Accuracy]
                                  Segment-level metric to use for segment-
                                  level analysis.
  -o, --output_folder TEXT        Folder you wish to use to save plots.
  --bootstrap
  -x, --system_x FILENAME         System X NLG outputs for segment-level
                                  comparison and bootstrap resampling.
  -y, --system_y FILENAME         System Y NLG outputs for segment-level
                                  comparison and bootstrap resampling.
  --num_splits INTEGER            Number of random partitions used in
                                  Bootstrap resampling.
  --sample_ratio FLOAT            Proportion (P) of the initial sample.
  --help                          Show this message and exit.
```

#### Example 1: Running several metrics

Running BLEU, chrF BERTScore and COMET to compare three MT systems with two references:

```bash
telescope n-compare-nlg \
  -s path/to/src/file.txt \
  -c path/to/system-x/file.txt \
  -c path/to/system-y/file.txt \
  -c path/to/system-z/file.txt \
  -r path/to/ref-1/file.txt \
  -r path/to/ref-2/file.txt \
  -t machine-translation\
  -l en \
  -m BLEU -m chrF -m BERTScore -m COMET
```

#### Example 2: Saving a comparison report

```bash
telescope n-compare-nlg \
  -s path/to/src/file.txt \
  -c path/to/system-x/file.txt \
  -c path/to/system-y/file.txt \
  -c path/to/system-z/file.txt \
  -r path/to/ref-1/file.txt \
  -r path/to/ref-2/file.txt \
  -t machine-translation\
  -l en \
  -m BLEU -m chrF -m BERTScore -m COMET \
  --output_folder FOLDER-PATH
```

For FOLDER-PATH location, a folder is created for each reference that contains the report.

### Comparing Classification systems:

For running system comparisons with CLI you should use the `telescope n-compare-classification` command.

```
Usage: telescope n-compare-classification [OPTIONS]

Options:
  -s, --source FILENAME           Source segments.  [required]
  -c, --system_output FILENAME    System candidate.  [required]
  -r, --reference FILENAME        Reference segments.  [required]
  -l, --label TEXT                Existing labels  [required]
  -m, --metric [Accuracy|Precision|Recall|F1-score]
                                  Metric to run.  [required]
  -f, --filter [duplicates]       Filter to run.
  --seg_metric [Accuracy]         Segment-level metric to use for segment-
                                  level analysis.
  -o, --output_folder TEXT        Folder you wish to use to save plots.
  --help                          Show this message and exit.
```

#### Example 1: Running two metrics

Running Accuracy and F1-score to compare three systems with two references:

```bash
telescope telescope n-compare-classification \
  -s path/to/src/file.txt \
  -c path/to/system-x/file.txt \
  -c path/to/system-y/file.txt \
  -c path/to/system-z/file.txt \
  -r path/to/ref-1/file.txt \
  -r path/to/ref-2/file.txt \
  -l label-1 \
  -l label-2 \
  -l label-3 \
  -m Accuracy -m F1-score
```

#### Example 2: Saving a comparison report

```bash
telescope telescope n-compare-classification \
  -s path/to/src/file.txt \
  -c path/to/system-x/file.txt \
  -c path/to/system-y/file.txt \
  -c path/to/system-z/file.txt \
  -r path/to/ref-1/file.txt \
  -r path/to/ref-2/file.txt \
  -l label-1 \
  -l label-2 \
  -l label-3 \
  -m Accuracy -m F1-score
  --output_folder FOLDER-PATH
```

For FOLDER-PATH location, a folder is created for each reference that contains the report

### Scoring:

To get the system level scores for a particular MT simply run `telescope score`.

```bash
telescope score -s {path/to/sources} -t {path/to/translations} -r {path/to/references} -l {target_language} -m COMET -m chrF
```

### Comparing two MT systems:

For running MT system comparisons with CLI you should use the `telescope compare` command.

```
Usage: telescope compare [OPTIONS]

Options:
  -s, --source FILENAME           Source segments.  [required]
  -x, --system_x FILENAME         System X MT outputs.  [required]
  -y, --system_y FILENAME         System Y MT outputs.  [required]
  -r, --reference FILENAME        Reference segments.  [required]
  -l, --language TEXT             Language of the evaluated text.  [required]
  -m, --metric [COMET|BLEU|chrF|TER|GLEU|ZeroEdit|BERTScore]
                                  MT metric to run.  [required]
  -f, --filter [named-entities|length|duplicates]
                                  MT metric to run.
  --length_min_val FLOAT          Min interval value for length filtering.
  --length_max_val FLOAT          Max interval value for length filtering.
  --seg_metric [COMET|GLEU|ZeroEdit|BERTScore]
                                  Segment-level metric to use for segment-
                                  level analysis.
  -o, --output_folder TEXT        Folder you wish to use to save plots.
  --bootstrap
  --num_splits INTEGER            Number of random partitions used in
                                  Bootstrap resampling.
  --sample_ratio FLOAT            Folder you wish to use to save plots.
  --help                          Show this message and exit.

```


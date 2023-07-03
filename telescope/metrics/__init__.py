import yaml

from .sacrebleu import sacreBLEU
from .chrf import chrF
from .zero_edit import ZeroEdit

# from .bleurt import BLEURT
from .bertscore import BERTScore
from .comet import COMET
from .ter import TER
# from .prism import Prism
from .gleu import GLEU

from .rouge_one import ROUGEOne
from .rouge_two import ROUGETwo
from .rouge_l import ROUGEL

from .accuracy import Accuracy
from .precision import Precision
from .recall import Recall
from .f1_score import F1Score

from .result import MetricResult, PairwiseResult, BootstrapResult

from telescope import read_yaml_file

metrics_yaml = metrics_yaml = read_yaml_file("metrics.yaml")

AVAILABLE_METRICS = [
    COMET,
    sacreBLEU,
    chrF,
    ZeroEdit,
    # BLEURT,
    BERTScore,
    TER,
    # Prism,
    GLEU,
    ROUGEOne, 
    ROUGETwo, 
    ROUGEL,
    Accuracy,
    Precision,
    Recall,
    F1Score
]

names_availabels_metrics = {metric.name:metric for metric in AVAILABLE_METRICS}
metrics_weight = {}
for metric_w in metrics_yaml["Weights"]:
    metric = list(metric_w.keys())[0]
    weight = list(metric_w.values())[0]
    metrics_weight[metric] = weight


AVAILABLE_NLP_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["NLP metrics"]]

AVAILABLE_NLG_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["NLG metrics"]] + AVAILABLE_NLP_METRICS

AVAILABLE_MT_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["Machine Translation metrics"]]  + AVAILABLE_NLG_METRICS

AVAILABLE_SUMMARIZATION_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["Summarization metrics"]] + AVAILABLE_NLG_METRICS

AVAILABLE_DIALOGUE_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["Dialogue System metrics"]] + AVAILABLE_NLG_METRICS

AVAILABLE_CLASSIFICATION_METRICS = [names_availabels_metrics[metric_name] for metric_name in metrics_yaml["Classification metrics"]] + AVAILABLE_NLP_METRICS

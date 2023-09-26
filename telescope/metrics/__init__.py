import yaml
import sys

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

from .demographic_parity import DemographicParity

from .fd_rate import FDRate
from .fp_rate import FPRate
from .fo_rate import FORate
from .fn_rate import FNRate
from .np_value import NPValue
from .tn_rate import TNRate

from .result import MetricResult, PairwiseResult, BootstrapResult

from telescope.utils import read_yaml_file

metrics_yaml = read_yaml_file("metrics.yaml")
universal_metrics_yaml = read_yaml_file("universal_metrics.yaml")
bias_evaluations_yaml = bias_evaluations_yaml = read_yaml_file("bias_evaluations.yaml")

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
    F1Score,
]

AVAILABLE_BIAS_METRICS = [
    Accuracy,
    Precision,
    Recall,
    F1Score,
    DemographicParity

]

SUM_METRICS_WEIGHTS = {}
for name, sum in universal_metrics_yaml["Weighted Sum Weights"].items():
    if name not in SUM_METRICS_WEIGHTS:
        SUM_METRICS_WEIGHTS[name] = {}
        for metric, weight in sum.items():
            if metric not in SUM_METRICS_WEIGHTS[name]:
                SUM_METRICS_WEIGHTS[name][metric] = weight

MEAN_METRICS_WEIGHTS = {}
for name, mean in universal_metrics_yaml["Weighted Mean Weights"].items():
    if name not in MEAN_METRICS_WEIGHTS:
        sum_weight = 0
        MEAN_METRICS_WEIGHTS[name] = {}
        for metric, weight in mean.items():
            if metric not in MEAN_METRICS_WEIGHTS[name]:
                if weight < 0:
                    print("The weight for the " + metric + " must not be negative (" + name + ").")
                    sys.exit(1)
                MEAN_METRICS_WEIGHTS[name][metric] = weight
                sum_weight += weight
        if sum_weight == 0:
            print("All weights are zeros (" + name + ").")
            sys.exit(1)   

AVAILABLE_METRICS_NAMES = {metric.name:metric for metric in AVAILABLE_METRICS}

AVAILABLE_BIAS_METRICS_NAMES = {metric.name:metric for metric in AVAILABLE_BIAS_METRICS}

try:
    AVAILABLE_NLP_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["NLP metrics"]]

    AVAILABLE_NLG_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["NLG metrics"]] + AVAILABLE_NLP_METRICS

    AVAILABLE_MT_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["Machine Translation metrics"]]  + AVAILABLE_NLG_METRICS

    AVAILABLE_SUMMARIZATION_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["Summarization metrics"]] + AVAILABLE_NLG_METRICS

    AVAILABLE_DIALOGUE_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["Dialogue System metrics"]] + AVAILABLE_NLG_METRICS

    AVAILABLE_CLASSIFICATION_METRICS = [AVAILABLE_METRICS_NAMES[metric_name] for metric_name in metrics_yaml["Classification metrics"]] + AVAILABLE_NLP_METRICS

    AVAILABLE_BIAS_EVALUATION_METRICS = [AVAILABLE_BIAS_METRICS_NAMES[metric_name] for metric_name in bias_evaluations_yaml["Bias Evaluation metrics"]] 

except KeyError as error:
    print("Error (yaml): " + str(error) + " as a metric is not available.")
    sys.exit(1)

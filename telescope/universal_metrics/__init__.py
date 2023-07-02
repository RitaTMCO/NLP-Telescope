from .average import Average
from .median import Median
from .weighted_mean import WeightedMean
from .pairwise_comparison import PairwiseComparison
from .social_choice_theory import SocialChoiceTheory

from .universal_metric_results import UniversalMetricResult

from telescope import read_yaml_file

universal_metrics_yaml = universal_metrics_yaml = read_yaml_file("universal_metrics.yaml")

AVAILABLE_UNIVERSAL_METRICS  = [ 
    Average,
    Median,
    WeightedMean,
    PairwiseComparison,
    SocialChoiceTheory
]

names_availabels_universal_metrics = {universal_metric.name:universal_metric for universal_metric in AVAILABLE_UNIVERSAL_METRICS}

AVAILABLE_NLP_UNIVERSAL_METRICS = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["NLP universal metrics"]]

AVAILABLE_NLG_UNIVERSAL_METRICS  = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["NLG universal metrics"]]  + AVAILABLE_NLP_UNIVERSAL_METRICS

AVAILABLE_MT_UNIVERSAL_METRICS = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["Machine Translation universal metrics"]] + AVAILABLE_NLG_UNIVERSAL_METRICS

AVAILABLE_SUMMARIZATION_UNIVERSAL_METRICS = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["Summarization universal metrics"]] + AVAILABLE_NLG_UNIVERSAL_METRICS

AVAILABLE_DIALOGUE_UNIVERSAL_METRICS = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["Dialogue System universal metrics"]] + AVAILABLE_NLG_UNIVERSAL_METRICS 

AVAILABLE_CLASSIFICATION_UNIVERSAL_METRICS  = [names_availabels_universal_metrics[universal_metric_name] for universal_metric_name in universal_metrics_yaml["Classification universal metrics"]] + AVAILABLE_NLP_UNIVERSAL_METRICS
from .sacrebleu import sacreBLEU
from .chrf import chrF
from .zero_edit import ZeroEdit

# from .bleurt import BLEURT
from .bertscore import BERTScore
from .comet import COMET
from .ter import TER
# from .prism import Prism
from .gleu import GLEU
from .result import MetricResult, PairwiseResult, BootstrapResult


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
]

AVAILABLE_NLG_METRICS = [
    BERTScore,
    ZeroEdit,
    #BLEURT,
]

AVAILABLE_MT_METRICS = [
    COMET,
    sacreBLEU,
    chrF,
    TER,
    # Prism,
    GLEU,
]

AVAILABLE_SUMMARIZATION_METRICS = []

AVAILABLE_DIALOGUE_METRICS = []

AVAILABLE_CLASSIFICATION_METRICS = [
    ZeroEdit,
]

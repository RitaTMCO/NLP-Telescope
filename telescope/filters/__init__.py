from .ner import NERFilter
from .length import LengthFilter
from .duplicates import DuplicatesFilter

AVAILABLE_FILTERS = [NERFilter, LengthFilter, DuplicatesFilter]

AVAILABLE_NLP_FILTERS = [DuplicatesFilter]

AVAILABLE_MT_FILTERS = [NERFilter, LengthFilter]

AVAILABLE_SUMMARIZATION_FILTERS = []

AVAILABLE_DIALOGUE_FILTERS = []

AVAILABLE_CLASSIFICATION_FILTERS = []


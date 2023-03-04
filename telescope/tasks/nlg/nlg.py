from telescope.tasks.task import Task
from telescope.testset import NLPTestsets
from telescope.metrics import AVAILABLE_NLG_METRICS

class NLG(Task):
    name = None
    metrics = AVAILABLE_NLG_METRICS 
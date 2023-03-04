from telescope.tasks.task import Task
from telescope.testset import NLPTestsets, ClassTestsets
from telescope.metrics import AVAILABLE_CLASSIFICATION_METRICS

class Classification(Task):
    name = "classification"
    metrics = AVAILABLE_CLASSIFICATION_METRICS

    @staticmethod
    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        class_testset = ClassTestsets.read_data()
        return class_testset
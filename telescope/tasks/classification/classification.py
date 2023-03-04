import abc

from telescope.tasks.task import Task
from telescope.testset import NLPTestsets, ClassTestsets

class Classification(Task):
    name = "classification"

    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        class_testset = ClassTestsets.read_data()
        return class_testset
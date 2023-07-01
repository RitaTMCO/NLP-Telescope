from .machine_translation import MachineTranslation
from .dialogue_system import DialogueSystem
from .summarization import Summarization

from telescope import read_yaml_file

AVAILABLE_TASKS = [
    MachineTranslation, 
    DialogueSystem, 
    Summarization
]

names_availabels_tasks = {task.name:task for task in AVAILABLE_TASKS}

tasks_yaml = read_yaml_file("tasks.yaml")

AVAILABLE_NLG_TASKS = [names_availabels_tasks[task_name] for task_name in tasks_yaml["NLG tasks"]]
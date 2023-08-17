from .machine_translation import MachineTranslation
from .dialogue_system import DialogueSystem
from .summarization import Summarization

AVAILABLE_NLG_TASKS = [
    MachineTranslation, 
    DialogueSystem, 
    Summarization
]
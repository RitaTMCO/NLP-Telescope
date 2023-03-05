from telescope.tasks.task import Task
from telescope.testset import NLPTestsets
from telescope.plotting import NLGPlot
from telescope.metrics import AVAILABLE_NLG_METRICS

class NLG(Task):
    name = None
    metrics = AVAILABLE_NLG_METRICS 

    @staticmethod
    def plots_interface(metric:str, metrics:list, available_metrics:dict, results:dict, 
                        testsets: NLPTestsets, ref_file: str, num_samples: int, 
                        sample_ratio: float) -> None:
        """ Interfave to display the plots"""
        return NLGPlot(metric,metrics,available_metrics,results,testsets,
                        ref_file,num_samples,sample_ratio).display_plots()


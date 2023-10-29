import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult

class SocialChoiceTheory(UniversalMetric):

    name = "social-choice-theory"
    title = "Social Choice Theory"


    @staticmethod
    def points_sum(systems_ids:List[str], points_systems_per_metrics: Dict[str,dict], metrics: List[str]):
        sum_points = {sys_id:0.0 for sys_id in systems_ids}
    
        for metric in metrics:
            points_systems = points_systems_per_metrics[metric]
            for sys_id in systems_ids:
                sum_points[sys_id] += points_systems[sys_id]
        return sum_points
    
    @staticmethod
    def point_assignment(systems_ids:List[str], ranking_systems_per_metrics: Dict[str,dict], metrics: List[str]):
        points_systems_per_metrics = {}
        n = len(systems_ids)

        for metric in metrics:
            ranking_systems = ranking_systems_per_metrics[metric]
            points_systems = {}
            for sys_id in systems_ids:
                points_systems[sys_id] = n + 1 - ranking_systems[sys_id]["rank"]
            points_systems_per_metrics[metric] = points_systems

        return points_systems_per_metrics

    @staticmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, normalize:bool=True) -> Dict[str,float]:
        metrics = list(metrics_scores.keys())
        ranking_systems_per_metrics= {}
    
        for metric, sys_metrics_score in metrics_scores.items():
            scores = {}
            for sys_key, sys_score in sys_metrics_score.items():
                if normalize:
                    scores[sys_key] = UniversalMetric.normalize_score(metric,sys_score)
                else:
                    scores[sys_key] = sys_score
            
            rank_scores = UniversalMetric.ranking_systems(scores)
            ranking_systems_per_metrics[metric] = rank_scores
        
        points_systems_per_metrics = SocialChoiceTheory.point_assignment(systems_keys,ranking_systems_per_metrics, metrics)
        sum_points = SocialChoiceTheory.points_sum(systems_keys,points_systems_per_metrics, metrics)
            
        return sum_points
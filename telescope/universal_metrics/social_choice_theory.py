import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult

class SocialChoiceTheory(UniversalMetric):

    name = "social-choice-theory"
    title = "Social Choice Theory"


    def points_sum(self,systems_ids:List[str], points_systems_per_metrics: Dict[str,dict]):
        metrics = list(self.multiple_metrics_results.keys())
        sum_points = {sys_id:0.0 for sys_id in systems_ids}
    
        for metric in metrics:
            points_systems = points_systems_per_metrics[metric]
            for sys_id in systems_ids:
                sum_points[sys_id] += points_systems[sys_id]
        return sum_points
    
    def point_assignment(self,systems_ids:List[str], ranking_systems_per_metrics: Dict[str,dict]):
        points_systems_per_metrics = {}
        n = len(systems_ids)
        metrics = list(self.multiple_metrics_results.keys())

        for metric in metrics:
            ranking_systems = ranking_systems_per_metrics[metric]
            points_systems = {}
            for sys_id in systems_ids:
                points_systems[sys_id] = n - ranking_systems[sys_id]["rank"]
            points_systems_per_metrics[metric] = points_systems

        return points_systems_per_metrics




    def universal_score(self,testset:MultipleTestset) -> Dict[str,float]:
        systems_outputs = testset.systems_output
        systems_ids = list(systems_outputs.keys())
        ranking_systems_per_metrics= {}
    
        for metric_results in list(self.multiple_metrics_results.values()):
            scores = {}
            for sys_id, result in metric_results.systems_metric_results.items():
                scores[sys_id] = result.sys_score
            
            metric = metric_results.metric
            if metric == "TER":
                rank_scores = self.ranking_systems(scores,False)
            else:
                rank_scores = self.ranking_systems(scores)
            ranking_systems_per_metrics[metric] = rank_scores
        
        points_systems_per_metrics = self.point_assignment(systems_ids,ranking_systems_per_metrics)
        sum_points = self.points_sum(systems_ids,points_systems_per_metrics)
            
        return sum_points
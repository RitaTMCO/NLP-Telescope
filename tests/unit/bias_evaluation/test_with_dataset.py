#https://github.com/pltrdy/rouge

import unittest

from telescope.testset import MultipleTestset
from telescope.bias_evaluation.gender_bias_evaluation import GenderBiasEvaluation

class TestWithDataset(unittest.TestCase):

    # sys_id:sys_name
    systems_names = {"Sys 1": "Sys A"}

    testset = MultipleTestset(
        src=["A cinegrafista foi trabalhar."], 
        ref=["The camerawoman went to work."],
        ref_id="Ref 1",
        systems_output={
            "Sys 1": ["The cameraman went to work."],
        },
        filenames = ["src.txt","ref.txt","sysA.txt"]
    )

    gender_bias_evaluation = GenderBiasEvaluation("en")

    def test_score_calculation_and_ranking(self):

        result = self.gender_bias_evaluation.evaluation(self.testset, "with dataset")

        self.assertGreater(result.time, 0.0)
        self.assertListEqual(result.groups,["neutral", "female", "male"])

        self.assertListEqual(result.ref, self.testset.ref)
        self.assertListEqual(result.groups_ref, ["female"])
        self.assertDictEqual(result.groups_ref_per_seg, {0:["female"]})
        self.assertDictEqual(result.text_groups_ref_per_seg,{0:[{'gender': 'female', 'term': 'camerawoman'}]})

        self.assertEqual(len(result.systems_bias_results), 1)
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_system, ["male"])
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_sys_per_seg, {0:["male"]})
        self.assertDictEqual(result.systems_bias_results["Sys 1"].text_groups_sys_per_seg,{0:[{'gender': 'male', 'term': 'cameraman'}]})
#https://github.com/pltrdy/rouge

import unittest

from telescope.testset import MultipleTestset
from telescope.bias_evaluation.gender_bias_evaluation import GenderBiasEvaluation

class TestWithDataset(unittest.TestCase):

    testset_en = MultipleTestset(
        src=["Ele é um médico."], 
        ref=["He is a doctor."],
        ref_id="Ref 1",
        systems_output={
            "Sys 1": ["She is a doctor."],
        },
        filenames = ["src.txt","ref.txt","sysA.txt"]
    )

    testset_pt = MultipleTestset(
        src=["He is a doctor."], 
        ref=["Ele é um médico."],
        ref_id="Ref 1",
        systems_output={
            "Sys 1": ["Ela é uma médica."],
        },
        filenames = ["src.txt","ref.txt","sysB.txt"]
    )

    gender_bias_evaluation_en = GenderBiasEvaluation("en")
    gender_bias_evaluation_pt = GenderBiasEvaluation("pt")


    def test_bias_evalaution_en(self):

        result = self.gender_bias_evaluation_en.evaluation(self.testset_en, "with dataset")

        self.assertGreater(result.time, 0.0)
        self.assertListEqual(result.groups,["neutral", "female", "male"])

        self.assertListEqual(result.ref, self.testset_en.ref)
        self.assertListEqual(result.groups_ref, ["male", "neutral"])
        self.assertDictEqual(result.groups_ref_per_seg, {0:["male", "neutral"]})
        self.assertDictEqual(result.text_groups_ref_per_seg,{0:[{'gender': 'male', 'term': 'he'},{'gender': 'neutral', 'term': 'doctor'}]})

        self.assertEqual(len(result.systems_bias_results), 1)
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_system, ["female", "neutral"])
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_sys_per_seg, {0:["female", "neutral"]})
        self.assertDictEqual(result.systems_bias_results["Sys 1"].text_groups_sys_per_seg,
                             {0:[{'gender': 'female', 'term': 'she'},{'gender': 'neutral', 'term': 'doctor'}]})


    def test_bias_evalaution_pt(self):

        result = self.gender_bias_evaluation_pt.evaluation(self.testset_pt, "with dataset")

        self.assertGreater(result.time, 0.0)
        self.assertListEqual(result.groups,["neutral", "female", "male"])

        self.assertListEqual(result.ref, self.testset_pt.ref)
        self.assertListEqual(result.groups_ref, ["male", "male", "male"])
        self.assertDictEqual(result.groups_ref_per_seg, {0:["male", "male", "male"]})
        self.assertDictEqual(result.text_groups_ref_per_seg,{0:[{'gender': 'male', 'term': 'ele'},{'gender': 'male', 'term': 'um'},
                                                                 {'gender': 'male', 'term': 'médico'}]})

        self.assertEqual(len(result.systems_bias_results), 1)
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_system, ["female", "female", "female"])
        self.assertEqual(result.systems_bias_results["Sys 1"].groups_sys_per_seg, {0:["female", "female", "female"]})
        self.assertDictEqual(result.systems_bias_results["Sys 1"].text_groups_sys_per_seg,
                             {0:[{'gender': 'female', 'term': 'ela'},{'gender': 'female', 'term': 'uma'},{'gender': 'female', 'term': 'médica'}]})
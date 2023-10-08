# -*- coding: utf-8 -*-
# Copyright (C) 2020 Unbabel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest

from click.testing import CliRunner
from telescope.cli import n_compare_nlg
from telescope.utils import (
    FILENAME_SYSTEM_LEVEL_SCORES,
    FILENAME_ANALYSIS_METRICS_STACKED,
    FILENAME_ERROR_TYPE_ANALYSIS,
    FILENAME_DISTRIBUTION_SEGMENT,
    FILENAME_SEGMENT_COMPARISON,
    FILENAME_BOOTSTRAP,
    FILENAME_RATES,
    FILENAME_ANALYSIS_LABELS,
)
from tests.data import DATA_PATH


class TestCompareCli(unittest.TestCase):

    system_a = os.path.join(DATA_PATH, "cs_en/Online-A.txt")
    system_b = os.path.join(DATA_PATH, "cs_en/Online-B.txt")
    system_g = os.path.join(DATA_PATH, "cs_en/Online-G.txt")
    src = os.path.join(DATA_PATH, "cs_en/cs-en.txt")
    ref_b = os.path.join(DATA_PATH, "cs_en/cs-en.refB.txt")
    ref_c = os.path.join(DATA_PATH, "cs_en/cs-en.refC.txt")
    sys_names_file = os.path.join(DATA_PATH, "systems_names.txt")
    task = "machine-translation"
    refs = [ref_b,ref_c]
    sys_names = ["Sys A", "Sys B", "Sys C"]

    def setUp(self):
        self.runner = CliRunner()

    def test_with_seg_metric(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU"
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_systems_names_file(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-n",
            self.sys_names_file
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_bootstrap(self):
        args = [
            "-t",
            self.task,           
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "--bootstrap",
            "-x",
            self.system_b,
            "-y",
            self.system_g,
            "--num_splits",
            10,
            "--sample_ratio",
            0.3
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_length_filter(self):
        args = [
            "-t",
            self.task,            
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-f",
            "length",
            "--length_min_val",
            0.5,
            "--length_max_val",
            0.7
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertIn("Filters Successfully applied. Corpus reduced in", result.stdout)
        self.assertEqual(result.exit_code, 0)

    
    def test_with_seg_level_comparison(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-x",
            self.system_b,
            "-y",
            self.system_g,
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
    
    def test_with_gender_bias_evaluation(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-b",
            "Gender",
            "--option_gender_bias_evaluation",
            "linguistic approach"
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_ranking(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-u",
            "pairwise-comparison"
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_output_comet_gender_bias_evaluation_and_ranking(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "--seg_metric",
            "COMET",
            "-f",
            "length",
            "--length_min_val",
            0.5,
            "--length_max_val",
            0.7,
            "-x",
            self.system_b,
            "-y",
            self.system_g,
            "--bootstrap",
            "--num_splits",
            10,
            "--sample_ratio",
            0.3,
            "-n",
            self.sys_names_file,
            "-b",
            "Gender",
            "--option_gender_bias_evaluation",
            "dictionary-based approach",
            "-u",
            "social-choice-theory",
            "--output_folder",
            DATA_PATH
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

        for ref in self.refs:
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/social-choice-theory_ranks_systems.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/COMET" + FILENAME_ERROR_TYPE_ANALYSIS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_DISTRIBUTION_SEGMENT)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/Sys B-Sys C" + FILENAME_SEGMENT_COMPARISON)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_SYSTEM_LEVEL_SCORES)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_ANALYSIS_METRICS_STACKED)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/Sys B-Sys C" + FILENAME_BOOTSTRAP)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/bias_evaluations_information.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Accuracy" + FILENAME_ANALYSIS_LABELS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Accuracy_results-by-label-table.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/F1-score" + FILENAME_ANALYSIS_LABELS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/F1-score_results-by-label-table.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Recall" + FILENAME_ANALYSIS_LABELS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Recall_results-by-label-table.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Precision" + FILENAME_ANALYSIS_LABELS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Precision_results-by-label-table.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/number-of-correct-labels-of-each-system.png")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/number-of-incorrect-labels-of-each-system.png")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/bias_results.csv")))
            for sys_name in ["Sys A", "Sys B", "Sys C"]:
                dir = ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/" + sys_name
                self.assertTrue(
                    os.path.isfile(os.path.join(
                        DATA_PATH, dir + "/confusion-matrix-" + sys_name.replace(" ","_") + ".png"))
                    )
                self.assertTrue(
                    os.path.isfile(os.path.join(
                        DATA_PATH, dir + "/" + FILENAME_RATES))
                    )
                self.assertTrue(
                    os.path.isfile(os.path.join(
                        DATA_PATH, dir + "/" + sys_name.replace(" ","_") + "-bias-segments.csv"))
                    )
                for group in ["male", "female", "neutral"]:
                    self.assertTrue(
                        os.path.isfile(os.path.join(
                            DATA_PATH, dir + "/singular_confusion_matrix/" + sys_name.replace(" ","_") + "-label-" + group + ".png"))
                        )
                    
            os.remove(DATA_PATH + "/" + ref.replace("/","_") + "/metrics_results/Sys B-Sys C" + FILENAME_SEGMENT_COMPARISON)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_DISTRIBUTION_SEGMENT)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/COMET" + FILENAME_ERROR_TYPE_ANALYSIS)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_SYSTEM_LEVEL_SCORES)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_ANALYSIS_METRICS_STACKED)
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/bias_evaluations_information.csv")
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Accuracy" + FILENAME_ANALYSIS_LABELS)
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/F1-score" + FILENAME_ANALYSIS_LABELS)
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Recall" + FILENAME_ANALYSIS_LABELS)
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Precision" + FILENAME_ANALYSIS_LABELS)
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Accuracy_results-by-label-table.csv")
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/F1-score_results-by-label-table.csv")
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Recall_results-by-label-table.csv")
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/Precision_results-by-label-table.csv")
            os.remove(DATA_PATH + "/" +ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/number-of-correct-labels-of-each-system.png")
            os.remove(DATA_PATH + "/" + ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/number-of-incorrect-labels-of-each-system.png")
            os.remove(DATA_PATH + "/" + ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/bias_results.csv")
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/Sys B-Sys C" + FILENAME_BOOTSTRAP)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") + "/social-choice-theory_ranks_systems.csv")
            for sys_name in ["Sys A", "Sys B", "Sys C"]:
                dir = ref.replace("/","_")  + "/bias_results/gender/dictionary-based approach/" + sys_name
                os.remove(DATA_PATH + "/" + dir + "/confusion-matrix-" + sys_name.replace(" ","_") + ".png")
                os.remove(DATA_PATH + "/" + dir +  "/" + FILENAME_RATES)
                os.remove(DATA_PATH + "/" + dir + "/" + sys_name.replace(" ","_") + "-bias-segments.csv")
                for group in ["male", "female", "neutral"]:
                    os.remove(DATA_PATH + "/" + dir + "/singular_confusion_matrix/" + sys_name.replace(" ","_")  + "-label-" + group + ".png")
                os.rmdir(DATA_PATH + "/" + dir + "/singular_confusion_matrix/")
                os.rmdir(DATA_PATH + "/" + dir + "/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_") + "/bias_results/gender/dictionary-based approach/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_") + "/bias_results/gender/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_") + "/bias_results/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_") + "/metrics_results/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_"))
            
    def test_with_output_bertscore(self):
        args = [
            "-t",
            self.task,
            "-s",
            self.src,
            "-c",
            self.system_a,
            "-c",
            self.system_b,
            "-c",
            self.system_g,
            "-r",
            self.ref_b,
            "-r",
            self.ref_c,
            "-l",
            "en",
            "-m",
            "chrF",
            "-f",
            "length",
            "--length_min_val",
            0.5,
            "--length_max_val",
            0.7,
            "-x",
            self.system_b,
            "-y",
            self.system_g,
            "--bootstrap",
            "--num_splits",
            10,
            "--sample_ratio",
            0.3,
            "-u",
            "social-choice-theory",
            "--output_folder",
            DATA_PATH
        ]
        result = self.runner.invoke(n_compare_nlg, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

        for ref in self.refs:
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/social-choice-theory_ranks_systems.csv")))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/BERTScore" + FILENAME_ERROR_TYPE_ANALYSIS)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_DISTRIBUTION_SEGMENT)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/Sys 2-Sys 3" + FILENAME_SEGMENT_COMPARISON)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_SYSTEM_LEVEL_SCORES)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/metrics_results/" + FILENAME_ANALYSIS_METRICS_STACKED)))
            self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, ref.replace("/","_")  + "/Sys 2-Sys 3" + FILENAME_BOOTSTRAP)))
            os.remove(DATA_PATH + "/" + ref.replace("/","_") + "/metrics_results/Sys 2-Sys 3" + FILENAME_SEGMENT_COMPARISON)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_DISTRIBUTION_SEGMENT)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/BERTScore" + FILENAME_ERROR_TYPE_ANALYSIS)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_SYSTEM_LEVEL_SCORES)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/metrics_results/" + FILENAME_ANALYSIS_METRICS_STACKED)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") +  "/Sys 2-Sys 3" + FILENAME_BOOTSTRAP)
            os.remove(DATA_PATH + "/" + ref.replace("/","_") + "/social-choice-theory_ranks_systems.csv")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_") + "/metrics_results/")
            os.rmdir(DATA_PATH + "/" + ref.replace("/","_"))
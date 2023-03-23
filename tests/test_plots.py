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

from telescope.testset import MultipleTestset
from telescope.metrics.result import MetricResult, PairwiseResult, MultipleResult
from telescope.plotting import (plot_bucket_comparison,
                                plot_bucket_multiple_comparison_comet,
                                plot_bucket_multiple_comparison_bertscore,
                                plot_pairwise_distributions,
                                plot_multiple_distributions,
                                plot_segment_comparison,
                                plot_multiple_segment_comparison,
                                overall_confusion_matrix_table,
                                singular_confusion_matrix_table,
                                analysis_labels,
                                incorrect_examples
                                )

from tests.data import DATA_PATH


class TestPlots(unittest.TestCase):

    result = PairwiseResult(
        x_result=MetricResult(
            sys_score=0.5,
            seg_scores=[0, 0.5, 1],
            src=["a", "b", "c"],
            cand=["a", "b", "c"],
            ref=["a", "b", "c"],
            metric="mock",
        ),
        y_result=MetricResult(
            sys_score=0.25,
            seg_scores=[0, 0.25, 0.5],
            src=["a", "b", "c"],
            cand=["a", "k", "c"],
            ref=["a", "b", "c"],
            metric="mock",
        ),
    )

    testset = MultipleTestset(
        src=["a", "b", "c"],
        ref=["a", "b", "c"],
        systems_output={
            "Sys 1": ["a", "d", "c"],
            "Sys 2": ["a", "k", "c"],
            "Sys 3": ["a", "p", "c"]
        },
        filenames = ["src.txt","ref.txt","sys1.txt","sys2.txt","sys3.txt"]
    )

    multiple_result = MultipleResult(
        systems_metric_results = {
            "Sys 1": MetricResult(
                sys_score=0.833,
                seg_scores=[1, 0.5, 1],
                src=testset.src,
                cand=testset.systems_output["Sys 1"],
                ref=testset.ref,
                metric="mock",
            ),
            "Sys 2": MetricResult(
                sys_score=0.750,
                seg_scores=[1, 0.25, 1],
                src=testset.src,
                cand=testset.systems_output["Sys 2"],
                ref=testset.ref,
                metric="mock",
            ),
            "Sys 3": MetricResult(
                sys_score=0.916,
                seg_scores=[1, 0.75, 1],
                src=testset.src,
                cand=testset.systems_output["Sys 3"],
                ref=testset.ref,
                metric="mock",
            )
        }
    )


    labels = ['a', 'b', 'c']

    testset_class = MultipleTestset(
        src=["a", "b", "c"],
        ref=["a", "b", "c"],
        systems_output={
            "Sys 1": ["a", "d", "c"],
            "Sys 2": ["a", "b", "c"],
            "Sys 3": ["a", "p", "c"]
        },
        filenames = ["src.txt","ref.txt","sys1.txt","sys2.txt","sys3.txt"],
    )

    multiple_result_class = MultipleResult(
        systems_metric_results = {
            "Sys 1": MetricResult(
                sys_score=0.833,
                seg_scores=[1, 0.5, 1],
                src=testset_class.src,
                cand=testset_class.systems_output["Sys 1"],
                ref=testset_class.ref,
                metric="mock",
            ),
            "Sys 2": MetricResult(
                sys_score=1.000,
                seg_scores=[1, 1, 1],
                src=testset_class.src,
                cand=testset_class.systems_output["Sys 2"],
                ref=testset_class.ref,
                metric="mock",
            ),
            "Sys 3": MetricResult(
                sys_score=0.916,
                seg_scores=[1, 0.75, 1],
                src=testset_class.src,
                cand=testset_class.systems_output["Sys 3"],
                ref=testset_class.ref,
                metric="mock",
            )
        }
    )


    @classmethod
    def tearDownClass(cls):
        os.remove(DATA_PATH + "/segment-comparison.html")
        os.remove(DATA_PATH + "/scores-distribution.html")
        os.remove(DATA_PATH + "/bucket-analysis.png")
        os.remove(DATA_PATH + "/multiple-segment-comparison.html")
        os.remove(DATA_PATH + "/multiple-scores-distribution.html")
        os.remove(DATA_PATH + "/multiple-bucket-analysis-comet.png")
        os.remove(DATA_PATH + "/multiple-bucket-analysis-bertscore.png")
        os.remove(DATA_PATH + "/overall-confusion-matrix.json")
        os.remove(DATA_PATH + "/label-a.json")
        os.remove(DATA_PATH + "/label-b.json")
        os.remove(DATA_PATH + "/label-c.json")
        os.remove(DATA_PATH + "/analysis-labels-bucket.png")
        os.remove(DATA_PATH + "/incorrect-examples.json")

    def test_segment_comparison(self):
        plot_segment_comparison(self.result, DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "segment-comparison.html"))
        )
    
    def test_multiple_segment_comparison(self):
        plot_multiple_segment_comparison(self.multiple_result,"Sys 1", "Sys 2", DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "multiple-segment-comparison.html"))
        )
        os.remove(DATA_PATH + "/multiple-segment-comparison.html")
        plot_multiple_segment_comparison(self.multiple_result,"Sys 2", "Sys 3", DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "multiple-segment-comparison.html"))
        )
        os.remove(DATA_PATH + "/multiple-segment-comparison.html")
        plot_multiple_segment_comparison(self.multiple_result,"Sys 3", "Sys 1", DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "multiple-segment-comparison.html"))
        )

    def test_pairwise_distributions(self):
        plot_pairwise_distributions(self.result, DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "scores-distribution.html"))
        )

    def test_multiple_distributions(self):
        plot_multiple_distributions(self.multiple_result, DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "multiple-scores-distribution.html"))
        )

    def test_bucket_comparison(self):
        plot_bucket_comparison(self.result, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "bucket-analysis.png")))

    def test_bucket_multiple_comparison_comet(self):        
        plot_bucket_multiple_comparison_comet(self.multiple_result, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "multiple-bucket-analysis-comet.png")))

    def test_bucket_multiple_comparison_bertscore(self):        
        plot_bucket_multiple_comparison_bertscore(self.multiple_result, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "multiple-bucket-analysis-bertscore.png")))
    
    def test_overall_confusion_matrix_table(self):
        overall_confusion_matrix_table(self.testset_class, "Sys 1", self.labels, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "overall-confusion-matrix.json")))
        os.remove(DATA_PATH + "/overall-confusion-matrix.json")

        overall_confusion_matrix_table(self.testset_class, "Sys 2", self.labels, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "overall-confusion-matrix.json")))
        os.remove(DATA_PATH + "/overall-confusion-matrix.json")

        overall_confusion_matrix_table(self.testset_class, "Sys 3", self.labels, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "overall-confusion-matrix.json")))
    
    def test_singular_confusion_matrix_table_label_a(self):
        label = "a"
        singular_confusion_matrix_table(self.testset_class, "Sys 1", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-a.json")))
        os.remove(DATA_PATH + "/label-a.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 2", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-a.json")))
        os.remove(DATA_PATH + "/label-a.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 3", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-a.json")))

    def test_singular_confusion_matrix_table_label_b(self):
        label = "b"
        
        singular_confusion_matrix_table(self.testset_class, "Sys 1", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-b.json")))
        os.remove(DATA_PATH + "/label-b.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 2", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-b.json")))
        os.remove(DATA_PATH + "/label-b.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 3", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-b.json")))

    def test_singular_confusion_matrix_table_label_c(self):
        label = "c"
        
        singular_confusion_matrix_table(self.testset_class, "Sys 1", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-c.json")))
        os.remove(DATA_PATH + "/label-c.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 2", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-c.json")))
        os.remove(DATA_PATH + "/label-c.json")

        singular_confusion_matrix_table(self.testset_class, "Sys 3", self.labels, label, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "label-c.json")))
    
    def test_analysis_labels(self):
        analysis_labels(self.multiple_result_class, self.labels, DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "analysis-labels-bucket.png"))
            )
    
    def test_incorrect_examples(self):
        incorrect_examples(self.testset_class, "Sys 1", DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "incorrect-examples.json"))
            )
        os.remove(DATA_PATH + "/incorrect-examples.json")
    
        incorrect_examples(self.testset_class, "Sys 2", DATA_PATH)
        self.assertFalse(
            os.path.isfile(os.path.join(DATA_PATH, "incorrect-examples.json"))
            )
        
        incorrect_examples(self.testset_class, "Sys 3", DATA_PATH)
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, "incorrect-examples.json"))
            )

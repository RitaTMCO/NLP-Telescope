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

from telescope.metrics.result import MetricResult, PairwiseResult, MultipleResult
from telescope.plotting import (plot_bucket_comparison,
                                plot_bucket_multiple_comparison,
                                plot_pairwise_distributions,
                                plot_multiple_distributions,
                                plot_segment_comparison,
                                plot_multiple_segment_comparison
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

    multiple_result = MultipleResult(
        systems_metric_results = {
            "Sys 1": MetricResult(
                sys_score=0.5,
                seg_scores=[0, 0.5, 1],
                src=["a", "b", "c"],
                cand=["a", "d", "c"],
                ref=["a", "b", "c"],
                metric="mock",
            ),
            "Sys 2": MetricResult(
                sys_score=0.25,
                seg_scores=[0, 0.25, 0.5],
                src=["a", "b", "c"],
                cand=["a", "k", "c"],
                ref=["a", "b", "c"],
                metric="mock",
            ),
            "Sys 3": MetricResult(
                sys_score=0.25,
                seg_scores=[0, 0.25, 0.5],
                src=["a", "b", "c"],
                cand=["a", "p", "c"],
                ref=["a", "b", "c"],
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
        os.remove(DATA_PATH + "/multiple-bucket-analysis.png")

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

    def test_bucket_multiple_comparison(self):        
        plot_bucket_multiple_comparison(self.multiple_result, DATA_PATH)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, "multiple-bucket-analysis.png")))
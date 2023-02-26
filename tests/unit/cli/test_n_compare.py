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
from telescope.cli import n_compare
from tests.data import DATA_PATH


class TestCompareCli(unittest.TestCase):

    system_a = os.path.join(DATA_PATH, "cs_en/Online-A.txt")
    system_b = os.path.join(DATA_PATH, "cs_en/Online-B.txt")
    system_g = os.path.join(DATA_PATH, "cs_en/Online-G.txt")
    src = os.path.join(DATA_PATH, "cs_en/cs-en.txt")
    ref_b = os.path.join(DATA_PATH, "cs_en/cs-en.refB.txt")
    ref_c = os.path.join(DATA_PATH, "cs_en/cs-en.refC.txt")

    def setUp(self):
        self.runner = CliRunner()

    def test_with_seg_metric(self):
        args = [
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
            "cs",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU"
        ]
        result = self.runner.invoke(n_compare, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_bootstrap(self):
        args = [
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
            "cs",
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
        result = self.runner.invoke(n_compare, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_duplicates_filter(self):
        args = [
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
            "cs",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "-f"
            "duplicates"
        ]
        result = self.runner.invoke(n_compare, args, catch_exceptions=False)
        self.assertIn("Filters Successfully applied. Corpus reduced in", result.stdout)
        self.assertEqual(result.exit_code, 0)

    
    def test_with_seg_level_comparison(self):
        args = [
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
            "cs",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "--seg_level_comparison",
            "-x",
            self.system_b,
            "-y",
            self.system_g,
        ]
        result = self.runner.invoke(n_compare, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_with_output(self):
        args = [
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
            "cs",
            "-m",
            "chrF",
            "--seg_metric",
            "GLEU",
            "--seg_level_comparison",
            "-x",
            self.system_b,
            "-y",
            self.system_g,
            "--bootstrap",
            "--num_splits",
            10,
            "--sample_ratio",
            0.3,
            "--output_folder",
            DATA_PATH
        ]
        result = self.runner.invoke(n_compare, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, self.ref_b.replace("/","_")  + "/multiple-bucket-analysis.png")))
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_b.replace("/","_")  + "/multiple-scores-distribution.html"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_b.replace("/","_")  + "/multiple-segment-comparison.html"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_b.replace("/","_")  + "/results.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_b.replace("/","_")  + "/bootstrap_results.json"))
        )
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, self.ref_c.replace("/","_")  + "/multiple-bucket-analysis.png")))
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_c.replace("/","_")  + "/multiple-scores-distribution.html"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_c.replace("/","_")  + "/multiple-segment-comparison.html"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_c.replace("/","_")  + "/results.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref_c.replace("/","_")  + "/bootstrap_results.json"))
        )

        os.remove(DATA_PATH + "/" + self.ref_b.replace("/","_") + "/multiple-segment-comparison.html")
        os.remove(DATA_PATH + "/" + self.ref_b.replace("/","_") +  "/multiple-scores-distribution.html")
        os.remove(DATA_PATH + "/" + self.ref_b.replace("/","_") +  "/multiple-bucket-analysis.png")
        os.remove(DATA_PATH + "/" + self.ref_b.replace("/","_") +  "/results.json")
        os.remove(DATA_PATH + "/" + self.ref_b.replace("/","_") +  "/bootstrap_results.json")
        os.rmdir(DATA_PATH + "/" + self.ref_b.replace("/","_"))

        os.remove(DATA_PATH + "/" + self.ref_c.replace("/","_") + "/multiple-segment-comparison.html")
        os.remove(DATA_PATH + "/" + self.ref_c.replace("/","_") +  "/multiple-scores-distribution.html")
        os.remove(DATA_PATH + "/" + self.ref_c.replace("/","_") +  "/multiple-bucket-analysis.png")
        os.remove(DATA_PATH + "/" + self.ref_c.replace("/","_") +  "/results.json")
        os.remove(DATA_PATH + "/" + self.ref_c.replace("/","_") +  "/bootstrap_results.json")
        os.rmdir(DATA_PATH + "/" + self.ref_c.replace("/","_"))

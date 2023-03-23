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
from telescope.cli import n_compare_classification
from tests.data import DATA_PATH


class TestCompareCli(unittest.TestCase):

    system_1 = os.path.join(DATA_PATH, "class/sys1-class.txt")
    system_2 = os.path.join(DATA_PATH, "class/sys2-class.txt")
    system_3 = os.path.join(DATA_PATH, "class/ref-c.txt")
    src = os.path.join(DATA_PATH, "class/src-c.txt")
    ref = os.path.join(DATA_PATH, "class/ref-c.txt")
    labels = ["positive", "negative", "neutral"]

    def setUp(self):
        self.runner = CliRunner()

    def test_with_seg_metric(self):
        args = [
            "-s",
            self.src,
            "-c",
            self.system_1,
            "-c",
            self.system_2,
            "-c",
            self.system_3,
            "-r",
            self.ref,
            "-l",
            self.labels[0],
            "-l",
            self.labels[1],
            "-l",
            self.labels[2],
            "-m",
            "F1-score",
            "--seg_metric",
            "Accuracy"
        ]
        result = self.runner.invoke(n_compare_classification, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

    def test_duplicates_filter(self):
        args = [            
            "-s",
            self.src,
            "-c",
            self.system_1,
            "-c",
            self.system_2,
            "-c",
            self.system_3,
            "-r",
            self.ref,
            "-l",
            self.labels[0],
            "-l",
            self.labels[1],
            "-l",
            self.labels[2],
            "-m",
            "F1-score",
            "-f",
            "duplicates"
        ]
        result = self.runner.invoke(n_compare_classification, args, catch_exceptions=False)
        self.assertIn("Filters Successfully applied. Corpus reduced in", result.stdout)
        self.assertEqual(result.exit_code, 0)


    def test_with_output(self):
        args = [
            "-s",
            self.src,
            "-c",
            self.system_1,
            "-c",
            self.system_2,
            "-c",
            self.system_3,
            "-r",
            self.ref,
            "-l",
            self.labels[0],
            "-l",
            self.labels[1],
            "-l",
            self.labels[2],
            "-m",
            "F1-score",
            "--seg_metric",
            "Accuracy",
            "-f",
            "duplicates",
            "--output_folder",
            DATA_PATH
        ]

        result = self.runner.invoke(n_compare_classification, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)

        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/results.json")))
        self.assertTrue(os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/analysis-labels-bucket.png")))

        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_1/incorrect-examples.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_2/incorrect-examples.json"))
        )
        self.assertFalse(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_3/incorrect-examples.json"))
        )

        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_1/overall-confusion-matrix.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_2/overall-confusion-matrix.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_3/overall-confusion-matrix.json"))
        )

        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_1/singular_confusion_matrix/label-positive.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_2/singular_confusion_matrix/label-positive.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_3/singular_confusion_matrix/label-positive.json"))
        )

        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_1/singular_confusion_matrix/label-negative.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_2/singular_confusion_matrix/label-negative.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_3/singular_confusion_matrix/label-negative.json"))
        )

        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_1/singular_confusion_matrix/label-neutral.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_2/singular_confusion_matrix/label-neutral.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(DATA_PATH, self.ref.replace("/","_")  + "/Sys_3/singular_confusion_matrix/label-neutral.json"))
        )

        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/singular_confusion_matrix/label-neutral.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/singular_confusion_matrix/label-neutral.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_3/singular_confusion_matrix/label-neutral.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/singular_confusion_matrix/label-negative.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/singular_confusion_matrix/label-negative.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_3/singular_confusion_matrix/label-negative.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/singular_confusion_matrix/label-positive.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/singular_confusion_matrix/label-positive.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_3/singular_confusion_matrix/label-positive.json")
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/singular_confusion_matrix/")
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/singular_confusion_matrix/")
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_3/singular_confusion_matrix/")

        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/incorrect-examples.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/incorrect-examples.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_1/overall-confusion-matrix.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_2/overall-confusion-matrix.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") +  "/Sys_3/overall-confusion-matrix.json")
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") + "/Sys_1/" )
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") + "/Sys_2/" )
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_") + "/Sys_3/" )

        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") + "/results.json")
        os.remove(DATA_PATH + "/" + self.ref.replace("/","_") + "/analysis-labels-bucket.png")
        os.rmdir(DATA_PATH + "/" + self.ref.replace("/","_"))

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
import yaml
from io import StringIO

PATH_USER = "user/" 

FILENAME_SYSTEM_LEVEL_SCORES = "systems-metrics-scores.csv"
FILENAME_ANALYSIS_METRICS_STACKED = "analysis-metrics-stacked-bar-plot.png"
FILENAME_SIMILAR_SOURCE_SENTENCES = "_similar-source-sentences.csv"
FILENAME_ERROR_TYPE_ANALYSIS = "-multiple-bucket-analysis.png"
FILENAME_DISTRIBUTION_SEGMENT  = "multiple-scores-distribution.html"
FILENAME_SEGMENT_COMPARISON = "_multiple-segment-comparison.html"
FILENAME_BOOTSTRAP = "_bootstrap_results.csv"
FILENAME_RATES = "rates.csv"
FILENAME_ANALYSIS_LABELS = "-analysis-labels-bucket.png"


def telescope_cache_folder():
    if "HOME" in os.environ:
        cache_directory = os.environ["HOME"] + "/.cache/mt-telescope/"
        if not os.path.exists(cache_directory):
            os.makedirs(cache_directory)
        return cache_directory
    else:
        raise Exception("HOME environment variable is not defined.")


def read_lines(file):
    if file is not None:
        file = StringIO(file.getvalue().decode())
        lines = [line.strip() for line in file.readlines()]
        return lines
    return None

def read_yaml_file(file_yaml):
    file = open(PATH_USER + file_yaml, "r")
    data = yaml.safe_load(file)
    file.close()
    return data

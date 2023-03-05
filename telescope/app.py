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
import streamlit as st
import requests

from PIL import Image

from telescope.tasks import AVAILABLE_TASKS
from telescope.metrics.result import MultipleResult
from telescope.plotting import (
    plot_bootstraping_result
)
from telescope.testset import NLPTestsets

available_tasks = {t.name: t for t in AVAILABLE_TASKS}


@st.cache
def load_image(image_url):
    img = Image.open(requests.get(image_url, stream=True).raw)
    return img

#logo = load_image("https://github.com/Unbabel/MT-Telescope/blob/master/data/mt-telescope-logo.jpg?raw=true")
st.sidebar.image("data/nlp-telescope-logo.png")

# --------------------  APP Settings --------------------
task = st.sidebar.selectbox(
    "Select the natural language processing task:",
    list(t.name for t in available_tasks.values()),
    index=0,
)

available_metrics = {m.name: m for m in available_tasks[task].metrics}
available_filters = {f.name: f for f in available_tasks[task].filters}

metrics = st.sidebar.multiselect(
    "Select the system-level metric you wish to run:",
    list(available_metrics.keys()),
    default=list(available_metrics.keys())[0],
)

metric = st.sidebar.selectbox(
    "Select the segment-level metric you wish to run:",
    list(m.name for m in available_metrics.values() if m.segment_level),
    index=0,
)

filters = st.sidebar.multiselect(
    "Select testset filters:", list(available_filters.keys()), default=["duplicates"]
)

if "length" in available_filters:
    st.sidebar.subheader("Segment length constraints:")
    length_interval = st.sidebar.slider(
        "Specify the confidence interval for the length distribution:",
        0,
        100,
        step=5,
        value=(0, 100),
        help=(
            "In order to isolate segments according to caracter length "
            "we will create a sequence length distribution that you can constraint "
            "through it's density funcion. This slider is used to specify the confidence interval P(a < X < b)"
        ),
    )
    if length_interval != (0, 100):
        filters = (
            filters
            + [
                "length",
            ]
            if filters is not None
            else [
                "length",
            ]
        )      

st.sidebar.subheader("Bootstrap resampling settings:")
num_samples = st.sidebar.number_input(
    "Number of random partitions:",
    min_value=1,
    max_value=1000,
    value=300,
    step=50,
)
sample_ratio = st.sidebar.slider(
    "Proportion (P) of the initial sample:", 0.0, 1.0, value=0.5, step=0.1
)

# --------------------- Streamlit APP Caching functions! --------------------------

cache_time = 60 * 60  # 1 hour cache time for each object
cache_max_entries = 30  # 1 hour cache time for each object


def hash_metrics(metrics):
    return " ".join([m.name for m in metrics])


@st.cache(
    hash_funcs={NLPTestsets: NLPTestsets.hash_func},
    suppress_st_warning=True,
    show_spinner=False,
    allow_output_mutation=True,
    ttl=cache_time,
    max_entries=cache_max_entries,
)
def apply_filters(testset, filters, ref_name):
    for filter in filters:
        with st.spinner(f"Applying {filter} filter for reference {ref_name}..." ):
            if filter == "length":
                testset.apply_filter(available_filters[filter](testset, *length_interval))
            else:
                testset.apply_filter(available_filters[filter](testset))

    # HACK
    # I'll add a new prefix to all testset filenames to "fool" streamlit cache
    if "length" in filters:
        filter_prefix = " ".join([f for f in filters]) + str(length_interval)
    else:
        filter_prefix = " ".join([f for f in filters])
    testset.filenames = [filter_prefix + f for f in testset.filenames]
    return testset


@st.cache(
    hash_funcs={NLPTestsets: NLPTestsets.hash_func},
    show_spinner=False,
    allow_output_mutation=True,
    ttl=cache_time,
    max_entries=cache_max_entries,
)
def run_metric(testset, metric, ref_filename):
    with st.spinner(f"Running {metric} for reference {ref_filename}..."):
        metric = available_metrics[metric](language=testset.target_language)
        return metric.multiple_comparison(testset)


def run_all_metrics(testset, metrics, filters):
    if filters:
        for ref_name in testset.refs_names:
            corpus_size = len(testset.multiple_testsets[ref_name])
            testset.multiple_testsets[ref_name] = apply_filters(testset.multiple_testsets[ref_name], filters, ref_name)
            st.success("Corpus reduced in {:.2f}%".format((1 - (len(testset.multiple_testsets[ref_name]) / corpus_size)) * 100) + " for reference " + ref_name)

    return {
        ref_name: {metric: run_metric(testset.multiple_testsets[ref_name], metric, ref_name) for metric in metrics}
        for ref_name in testset.refs_names
        }


# --------------------  APP  --------------------

st.title("Welcome to NLP-Telescope!")
testsets = available_tasks[task].input_interface()

if testsets:
    if metric not in metrics:
        metrics = [
            metric,
        ] + metrics
    results_per_ref = run_all_metrics(testsets, metrics, filters)

    text = "Systems:\n"
    for system, index in testsets.systems_indexes.items():
        text += index + ": " + system + " \n"
    
    st.text(text)

    ref_filename = st.selectbox(
    "Select the reference:",
    testsets.refs_names,
    index=0,
    )

    results = results_per_ref[ref_filename]

    if len(results) > 0:
        st.dataframe(MultipleResult.results_to_dataframe(list(results.values()), 
                                                        testsets.systems_names()))
    
    if metric in results:
        available_tasks[task].plots_interface(metric, metrics, available_metrics,
                                                results, testsets, ref_filename, 
                                                num_samples, sample_ratio)
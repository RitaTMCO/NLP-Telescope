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

from telescope.filters import AVAILABLE_FILTERS
from telescope.metrics import AVAILABLE_METRICS
from telescope.metrics.result import MultipleResult
from telescope.plotting import (
    plot_bootstraping_result,
    plot_bucket_multiple_comparison,
    plot_multiple_distributions,
    plot_multiple_segment_comparison,
)
from telescope.testset import MultipleTestset

available_metrics = {m.name: m for m in AVAILABLE_METRICS}
available_filters = {f.name: f for f in AVAILABLE_FILTERS}


@st.cache
def load_image(image_url):
    img = Image.open(requests.get(image_url, stream=True).raw)
    return img

#logo = load_image("https://github.com/Unbabel/MT-Telescope/blob/master/data/mt-telescope-logo.jpg?raw=true")
st.sidebar.image("data/nlp-telescope-logo.png")

# --------------------  APP Settings --------------------
metrics = st.sidebar.multiselect(
    "Select the system-level metric you wish to run:",
    list(available_metrics.keys()),
    default=["COMET", "chrF", "BLEU"],
)

metric = st.sidebar.selectbox(
    "Select the segment-level metric you wish to run:",
    list(m.name for m in available_metrics.values() if m.segment_level),
    index=0,
)

filters = st.sidebar.multiselect(
    "Select testset filters:", list(available_filters.keys()), default=["duplicates"]
)
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
    hash_funcs={MultipleTestset: MultipleTestset.hash_func},
    suppress_st_warning=True,
    show_spinner=False,
    allow_output_mutation=True,
    ttl=cache_time,
    max_entries=cache_max_entries,
)
def apply_filters(testset, filters):
    filters = [available_filters[f](testset, *length_interval) for f in filters]
    for filter in filters:
        with st.spinner(f"Applying {filter.name} filter..."):
            testset.apply_filter(filter)

    # HACK
    # I'll add a new prefix to all testset filenames to "fool" streamlit cache
    filter_prefix = " ".join([f.name for f in filters]) + str(length_interval)
    testset.filenames = [filter_prefix + f for f in testset.filenames]
    return testset


@st.cache(
    hash_funcs={MultipleTestset: MultipleTestset.hash_func},
    show_spinner=False,
    allow_output_mutation=True,
    ttl=cache_time,
    max_entries=cache_max_entries,
)
def run_metric(testset, metric, ref_filename):
    with st.spinner(f"Running {metric} for reference {ref_filename}..."):
        metric = available_metrics[metric](language=testset.target_language)
        return metric.multiple_comparison(testset,ref_filename)


def run_all_metrics(testset, metrics, filters):
    if filters:
        corpus_size = len(testset)
        testset = apply_filters(testset, filters)
        st.success(
            "Corpus reduced in {:.2f}%".format((1 - (len(testset) / corpus_size)) * 100)
        )
    return {
        ref_filename: {metric: run_metric(testset, metric, ref_filename) for metric in metrics}
        for ref_filename in testset.refs_filenames()
        }


# --------------------  APP  --------------------

st.title("Welcome to NLP-Telescope!")
testset = MultipleTestset.read_data()

if testset:
    if metric not in metrics:
        metrics = [
            metric,
        ] + metrics
    results_per_ref = run_all_metrics(testset, metrics, filters)

    text = "Systems:\n"
    for system, index in testset.systems_index.items():
        text += index + ": " + system + " \n"
    
    st.text(text)

    ref_filename = st.selectbox(
    "Select the reference:",
    list(results_per_ref.keys()),
    index=0,
    )

    results = results_per_ref[ref_filename]

    if len(results) > 0:
        st.dataframe(
            MultipleResult.results_to_dataframe(list(results.values()), testset.systems_names())
        )

    if metric in results:
        if metric == "COMET":
            st.subheader("Error-type analysis:")
            plot_bucket_multiple_comparison(results[metric])

        st.subheader("Segment-level scores histogram:")
        plot_multiple_distributions(results[metric])

        st.header("Segment-level comparison:")
        plot_multiple_segment_comparison(results[metric])


        # Bootstrap Resampling
        #_, middle, _ = st.beta_columns(3)
        #if middle.button("Perform Bootstrap Resampling:"):
            #st.warning(
                #"Running metrics for {} partitions of size {}".format(
                    #num_samples, sample_ratio * len(testset)
                #)
            #)
            #st.header("Bootstrap resampling results:")
            #with st.spinner("Running bootstrap resampling..."):
                #for metric in metrics:
                    #bootstrap_result = available_metrics[metric].bootstrap_resampling(
                        #testset, int(num_samples), sample_ratio, results[metric]
                    #)

                    #plot_bootstraping_result(bootstrap_result)

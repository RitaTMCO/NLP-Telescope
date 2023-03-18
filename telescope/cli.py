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
r"""
MT-Telescope command line interface (CLI)
==============
Main commands:
    - score     Used to download Machine Translation metrics.
"""
from typing import List, Union, Tuple
import os
import click
import json
import pandas as pd

from telescope.metrics import AVAILABLE_METRICS, AVAILABLE_CLASSIFICATION_METRICS, PairwiseResult
from telescope.filters import AVAILABLE_FILTERS, AVAILABLE_CLASSIFICATION_FILTERS
from telescope.tasks import AVAILABLE_NLG
from telescope.metrics.result import MultipleResult
from telescope.testset import PairwiseTestset, MultipleTestset
from telescope.collection_testsets import CollectionTestsets
from telescope.plotting import (
    plot_segment_comparison,
    plot_multiple_segment_comparison,
    plot_pairwise_distributions,
    plot_multiple_distributions,
    plot_bucket_comparison,
    plot_bucket_multiple_comparison_comet,
)

available_metrics = {m.name: m for m in AVAILABLE_METRICS}
available_class_metrics = {m.name: m for m in AVAILABLE_CLASSIFICATION_METRICS}
available_filters = {f.name: f for f in AVAILABLE_FILTERS}
available_class_filters = {f.name: f for f in AVAILABLE_CLASSIFICATION_FILTERS}
available_nlg_tasks = {t.name: t for t in AVAILABLE_NLG}


def readlines(ctx, param, file: click.File) -> List[str]:
    return [l.strip() for l in file.readlines()]


def output_folder_exists(ctx, param, output_folder):
    if output_folder != "" and not os.path.exists(output_folder):
        raise click.BadParameter(f"{output_folder} does not exist!")
    return output_folder


@click.group()
def telescope():
    pass


@telescope.command()
@click.option(
    "--source",
    "-s",
    required=True,
    help="Source segments.",
    type=click.File(),
)
@click.option(
    "--system_x",
    "-x",
    required=True,
    help="System X MT outputs.",
    type=click.File(),
)
@click.option(
    "--system_y",
    "-y",
    required=True,
    help="System Y MT outputs.",
    type=click.File(),
)
@click.option(
    "--reference",
    "-r",
    required=True,
    help="Reference segments.",
    type=click.File(),
)
@click.option(
    "--language",
    "-l",
    required=True,
    help="Language of the evaluated text.",
)
@click.option(
    "--metric",
    "-m",
    type=click.Choice(list(available_metrics.keys())),
    required=True,
    multiple=True,
    help="MT metric to run.",
)
@click.option(
    "--filter",
    "-f",
    type=click.Choice(list(available_filters.keys())),
    required=False,
    default=[],
    multiple=True,
    help="MT metric to run.",
)
@click.option(
    "--length_min_val",
    type=float,
    required=False,
    default=0.0,
    help="Min interval value for length filtering.",
)
@click.option(
    "--length_max_val",
    type=float,
    required=False,
    default=0.0,
    help="Max interval value for length filtering.",
)
@click.option(
    "--seg_metric",
    type=click.Choice([m.name for m in available_metrics.values() if m.segment_level]),
    required=False,
    default="COMET",
    help="Segment-level metric to use for segment-level analysis.",
)
@click.option(
    "--output_folder",
    "-o",
    required=False,
    default="",
    callback=output_folder_exists,
    type=str,
    help="Folder you wish to use to save plots.",
)
@click.option("--bootstrap", is_flag=True)
@click.option(
    "--num_splits",
    required=False,
    default=300,
    type=int,
    help="Number of random partitions used in Bootstrap resampling.",
)
@click.option(
    "--sample_ratio",
    required=False,
    default=0.5,
    type=float,
    help="Folder you wish to use to save plots.",
)
def compare(
    source: click.File,
    system_x: click.File,
    system_y: click.File,
    reference: click.File,
    language: str,
    metric: Union[Tuple[str], str],
    filter: Union[Tuple[str], str],
    length_min_val: float,
    length_max_val: float,
    seg_metric: str,
    output_folder: str,
    bootstrap: bool,
    num_splits: int,
    sample_ratio: float,
):
    testset = PairwiseTestset(
        src=[l.strip() for l in source.readlines()],
        system_x=[l.strip() for l in system_x.readlines()],
        system_y=[l.strip() for l in system_y.readlines()],
        ref=[l.strip() for l in reference.readlines()],
        language_pair="X-" + language,
        filenames=[source.name, system_x.name, system_y.name, reference.name],
    )
    corpus_size = len(testset)
    if filter:
        filters = [available_filters[f](testset) for f in filter if f != "length"]
        if "length" in filter:
            filters.append(available_filters["length"](testset, int(length_min_val*100), int(length_max_val*100)))
        
        for filter in filters:
            testset.apply_filter(filter)

        if (1 - (len(testset) / corpus_size)) * 100 == 100:
            click.secho("The current filters reduce the Corpus on 100%!", fg="ref")
            return
    
        click.secho(
            "Filters Successfully applied. Corpus reduced in {:.2f}%.".format(
                (1 - (len(testset) / corpus_size)) * 100
            ),
            fg="green",
        )

    if seg_metric not in metric:
        metric = tuple(
            [
                seg_metric,
            ]
            + list(metric)
        )
    else:
        # Put COMET in first place
        metric = list(metric)
        metric.remove(seg_metric)
        metric = tuple(
            [
                seg_metric,
            ]
            + metric
        )

    results = {
        m: available_metrics[m](language=testset.target_language).pairwise_comparison(
            testset
        )
        for m in metric
    }

    # results_dict = PairwiseResult.results_to_dict(list(results.values()))
    results_df = PairwiseResult.results_to_dataframe(list(results.values()))
    if bootstrap:
        bootstrap_results = []
        for m in metric:
            bootstrap_result = available_metrics[m].bootstrap_resampling(
                testset, num_splits, sample_ratio, results[m]
            )
            bootstrap_results.append(
                available_metrics[m]
                .bootstrap_resampling(testset, num_splits, sample_ratio, results[m])
                .stats
            )
        bootstrap_results = {
            k: [dic[k] for dic in bootstrap_results] for k in bootstrap_results[0]
        }
        for k, v in bootstrap_results.items():
            results_df[k] = v

    click.secho(str(results_df), fg="yellow")
    if output_folder != "":
        if not output_folder.endswith("/"):
            output_folder += "/"
        results_df.to_json(output_folder + "results.json", orient="index", indent=4)
        plot_segment_comparison(results[seg_metric], output_folder)
        plot_pairwise_distributions(results[seg_metric], output_folder)
        plot_bucket_comparison(results[seg_metric], output_folder)


@telescope.command()
@click.option(
    "--source",
    "-s",
    required=True,
    help="Source segments.",
    type=click.File(),
    callback=readlines,
)
@click.option(
    "--translation",
    "-t",
    required=True,
    help="MT outputs.",
    type=click.File(),
    callback=readlines,
)
@click.option(
    "--reference",
    "-r",
    required=True,
    help="Reference segments.",
    type=click.File(),
    callback=readlines,
)
@click.option(
    "--language",
    "-l",
    required=True,
    help="Language of the evaluated text.",
)
@click.option(
    "--metric",
    "-m",
    type=click.Choice(list(available_metrics.keys())),
    required=True,
    multiple=True,
    help="MT metric to run.",
)
def score(
    source: List[str],
    translation: List[str],
    reference: List[str],
    language: str,
    metric: Union[Tuple[str], str],
):
    metrics = metric
    for metric in metrics:
        if not available_metrics[metric].language_support(language):
            raise click.ClickException(f"{metric} does not support '{language}'")
    results = []
    for metric in metrics:
        metric = available_metrics[metric](language)
        results.append(metric.score(source, translation, reference))

    for result in results:
        click.secho(str(result), fg="yellow")


@telescope.command()
@click.pass_context
def streamlit(ctx):
    file_path = os.path.realpath(__file__)
    script_path = "/".join(file_path.split("/")[:-1]) + "/app.py"
    os.system("streamlit run " + script_path)


def seg_metric_in_metrics(seg_metric, metrics):
    if seg_metric not in metrics:
        metrics = tuple(
            [
                seg_metric,
            ]
            + list(metrics)
        )
    else:
        metrics = list(metrics)
        metrics.remove(seg_metric)
        metrics = tuple(
            [
                seg_metric,
            ]
            + metrics
        )
    return metrics

def apply_filter(ref_name,collection,filter):
    for ref_name in collection.refs_names:
        corpus_size = len(collection.multiple_testsets[ref_name])
        
        for f in filter:
            if f != "length":
                fil = available_filters[f](collection.multiple_testsets[ref_name])
            else:
                fil = available_filters["length"](collection.multiple_testsets[ref_name], 
                        int(length_min_val*100), int(length_max_val*100))
            collection.multiple_testsets[ref_name].apply_filter(fil)

        if (1 - (len(collection.multiple_testsets[ref_name]) / corpus_size)) * 100 == 100:
            click.secho("For reference " + ref_name + ", the current filters reduce the Corpus on 100%!", fg="green")
            return
    
        click.secho( "Filters Successfully applied. Corpus reduced in {:.2f}%.".format(
            (1 - (len(collection.multiple_testsets[ref_name]) / corpus_size)) * 100) + " for reference " + ref_name,
                fg="green" )


###################################################
############|Command for N systems|################
###################################################

@telescope.command()
@click.option(
    "--source",
    "-s",
    required=True,
    help="Source segments.",
    type=click.File(),
)
@click.option(
    "--system_output",
    "-c",
    required=True,
    help="System candidate.",
    type=click.File(),
    multiple=True,
)
@click.option(
    "--reference",
    "-r",
    required=True,
    help="Reference segments.",
    type=click.File(),
    multiple=True,
)
@click.option(
    "--task",
    "-t",
    type=click.Choice(list(available_nlg_tasks.keys())),
    required=True,
    help="NLG to evaluate.",
)
@click.option(
    "--language",
    "-p",
    required=False,
    default="X",
    help="Language of the evaluated text.",
)
@click.option(
    "--metric",
    "-m",
    type=click.Choice(list(available_metrics.keys())),
    required=True,
    multiple=True,
    help="Metric to run.",
)
@click.option(
    "--filter",
    "-f",
    type=click.Choice(list(available_filters.keys())),
    required=False,
    default=[],
    multiple=True,
    help="Filter to run.",
)
@click.option(
    "--length_min_val",
    type=float,
    required=False,
    default=0.0,
    help="Min interval value for length filtering.",
)
@click.option(
    "--length_max_val",
    type=float,
    required=False,
    default=0.0,
    help="Max interval value for length filtering.",
)
@click.option(
    "--seg_metric",
    type=click.Choice([m.name for m in available_metrics.values() if m.segment_level]),
    required=False,
    default="BERTScore",
    help="Segment-level metric to use for segment-level analysis.",
)
@click.option(
    "--output_folder",
    "-o",
    required=False,
    default="",
    callback=output_folder_exists,
    type=str,
    help="Folder you wish to use to save plots.",
)
@click.option("--seg_level_comparison", is_flag=True)
@click.option("--bootstrap", is_flag=True)
@click.option(
    "--system_x",
    "-x",
    required=False,
    help="System X NLG outputs for segment-level comparison and bootstrap resampling.",
    type=click.File(),
)
@click.option(
    "--system_y",
    "-y",
    required=False,
    help="System Y NLG outputs for segment-level comparison and bootstrap resampling.",
    type=click.File(),
)
@click.option(
    "--num_splits",
    required=False,
    default=300,
    type=int,
    help="Number of random partitions used in Bootstrap resampling.",
)
@click.option(
    "--sample_ratio",
    required=False,
    default=0.5,
    type=float,
    help="Proportion (P) of the initial sample.",
)
def n_compare_nlg(
    source: click.File,
    system_output: Tuple[click.File],
    reference: Tuple[click.File],
    task: str,
    language: str,
    metric: Union[Tuple[str], str],
    filter: Union[Tuple[str], str],
    length_min_val: float,
    length_max_val: float,
    seg_metric: str,
    output_folder: str,
    bootstrap: bool,
    num_splits: int,
    sample_ratio: float,
    seg_level_comparison: bool,
    system_x: click.File,
    system_y: click.File,
):  
    collection = CollectionTestsets.read_cli(source,system_output,reference,language,
                                                [" "])
    if filter:
        apply_filter(ref_name,collection,filter)   

    metric = seg_metric_in_metrics(seg_metric,metric)


    text = "\nSystems: \n"
    for index, system in collection.systems_indexes.items():
        text += index + ": " + system + " \n"
    
    click.secho(text, fg="bright_blue")

    systems_index = collection.systems_indexes
    
    for ref_filename in list(collection.refs_names):
        results = {
            m: available_metrics[m](language=collection.multiple_testsets[ref_filename].target_language).multiple_comparison(
            collection.multiple_testsets[ref_filename]) for m in metric }

        results_dicts = MultipleResult.results_to_dict(list(results.values()), systems_index)

        click.secho('Reference: ' + ref_filename, fg="yellow")

        for met, systems in results_dicts.items():
            click.secho("metric: " + str(met), fg="yellow")
            click.secho("\t" + "systems:", fg="yellow")
            for sys_name, sys_score in systems.items():
                click.secho("\t" + str(sys_name) + ": " + str(sys_score), fg="yellow")

        bootstrap_df = pd.DataFrame.from_dict({})
        if (bootstrap and (system_x is not None) and (system_y is not None) 
        and system_x.name in list(systems_index.values())
        and system_y.name in list(systems_index.values())):

            indexes = list()

            for index,name in systems_index.items():
                if system_x.name == name or system_y.name == name:
                    indexes.append(index)

            bootstrap_results = []
            for m in metric:
                bootstrap_results.append(
                    available_metrics[m]
                    .multiple_bootstrap_resampling(collection.multiple_testsets[ref_filename], num_splits, sample_ratio, 
                    indexes[0], indexes[1], results[m])
                    .stats
                )
            bootstrap_results = {
                k: [dic[k] for dic in bootstrap_results] for k in bootstrap_results[0]
            }
            
            bootstrap_df = pd.DataFrame.from_dict(bootstrap_results)
            bootstrap_df.index = metric
        
            click.secho("\nBootstrap resampling results:", fg="yellow")
            click.secho(str(bootstrap_df), fg="yellow")
        
        if output_folder != "":
            if not output_folder.endswith("/"):
                output_folder += "/"    

            saving_dir = output_folder + ref_filename.replace("/","_") + "/"

            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)

            with open(saving_dir + "results.json", "w") as result_file:
                json.dump(results_dicts, result_file, indent=4)

            bootstrap_df.to_json(saving_dir + "bootstrap_results.json", orient="index", indent=4)
            plot_bucket_multiple_comparison_comet(results[seg_metric], saving_dir)
            plot_multiple_distributions(results[seg_metric], saving_dir)

            if (seg_level_comparison and (system_x is not None) and (system_y is not None) and system_x.name in list(systems_index.values())
            and system_y.name in list(systems_index.values())):
                plot_multiple_segment_comparison(results[seg_metric], indexes[0], indexes[1],saving_dir)


@telescope.command()
@click.option(
    "--source",
    "-s",
    required=True,
    help="Source segments.",
    type=click.File(),
)
@click.option(
    "--system_output",
    "-c",
    required=True,
    help="System candidate.",
    type=click.File(),
    multiple=True,
)
@click.option(
    "--reference",
    "-r",
    required=True,
    help="Reference segments.",
    type=click.File(),
    multiple=True,
)
@click.option(
    "--label",
    "-l",
    required=False,
    default=[" "],
    multiple=True,
    help="Existing labels"
)
@click.option(
    "--metric",
    "-m",
    type=click.Choice(list(available_class_metrics.keys())),
    required=True,
    multiple=True,
    help="Metric to run.",
)
@click.option(
    "--filter",
    "-f",
    type=click.Choice(list(available_class_filters.keys())),
    required=False,
    default=[],
    multiple=True,
    help="Filter to run.",
)
@click.option(
    "--seg_metric",
    type=click.Choice([m.name for m in available_class_metrics.values() if m.segment_level]),
    required=False,
    default="Accuracy",
    help="Segment-level metric to use for segment-level analysis.",
)
@click.option(
    "--output_folder",
    "-o",
    required=False,
    default="",
    callback=output_folder_exists,
    type=str,
    help="Folder you wish to use to save plots.",
)
def n_compare_classification(
    source: click.File,
    system_output: Tuple[click.File],
    reference: Tuple[click.File],
    label: Union[Tuple[str], str],
    metric: Union[Tuple[str], str],
    filter: Union[Tuple[str], str]
):  
    collection = CollectionTestsets.read_cli(source,system_output,reference,"X-X",
                                                list(label))
    if filter:
        apply_filter(ref_name,collection,filter)   

    metric = seg_metric_in_metrics(seg_metric,metric)

    text = "\nSystems: \n"
    for index, system in collection.systems_indexes.items():
        text += index + ": " + system + " \n"
    
    click.secho(text, fg="bright_blue")

    systems_index = collection.systems_indexes
    
    for ref_filename in list(collection.refs_names):
        results = {
            m: available_metrics[m](language=collection.multiple_testsets[ref_filename].target_language).multiple_comparison(
            collection.multiple_testsets[ref_filename]) for m in metric }

        results_dicts = MultipleResult.results_to_dict(list(results.values()), systems_index)

        click.secho('Reference: ' + ref_filename, fg="yellow")

        for met, systems in results_dicts.items():
            click.secho("metric: " + str(met), fg="yellow")
            click.secho("\t" + "systems:", fg="yellow")
            for sys_name, sys_score in systems.items():
                click.secho("\t" + str(sys_name) + ": " + str(sys_score), fg="yellow")
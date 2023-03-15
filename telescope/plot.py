import abc
import streamlit as st

from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets
from telescope.plotting import (
    plot_bootstraping_result,
    plot_bucket_multiple_comparison_comet,
    plot_bucket_multiple_comparison_bertscore,
    plot_multiple_distributions,
    plot_multiple_segment_comparison,
    overall_confusion_matrix_table,
    singular_confusion_matrix_table,
    analysis_labels,
    incorrect_examples
)

class Plot(metaclass=abc.ABCMeta):
    def __init__(
        self,
        metric: str, 
        metrics: List[str],
        available_metrics: dict,
        results: dict,
        collection_testsets: CollectionTestsets,
        ref_filename: str,
        task: str
    ) -> None:

        self.metric = metric
        self.metrics = metrics
        self.available_metrics = available_metrics
        self.results = results
        self.collection_testsets = collection_testsets
        self.ref_filename = ref_filename
        self.task = task

    @abc.abstractmethod
    def display_plots(self) -> None:
        pass


class NLGPlot(Plot):
    def __init__(
        self,
        metric:str, 
        metrics: List[str],
        available_metrics: dict,
        results:dict, 
        collection_testsets: CollectionTestsets,
        ref_filename: str,
        task: str,
        num_samples: float,
        sample_ratio: float,
    ) -> None:

        super().__init__(metric, metrics, available_metrics, results, collection_testsets, ref_filename, task)
        self.num_samples = num_samples
        self.sample_ratio = sample_ratio


    def display_plots(self) -> None:
        if self.metric == "COMET":
            st.header("Error-type analysis:")
            plot_bucket_multiple_comparison_comet(self.results[self.metric])
        
        if self.metric == "BERTScore":
            st.header("Bucket analysis:")
            plot_bucket_multiple_comparison_bertscore(self.results[self.metric])

        if len(self.collection_testsets.multiple_testsets[self.ref_filename]) > 1:
            st.header("Segment-level scores histogram:")
            plot_multiple_distributions(self.results[self.metric])

        if len(self.results[self.metric].systems_metric_results) > 1:

            st.header("Segment-level comparison:")

            left_1, right_1 = st.columns(2)
    
            system_x = left_1.selectbox(
            "Select the system x:",
            list(self.results[self.metric].systems_metric_results.keys()),
            index=0,
            key = self.ref_filename
            )

            system_y = right_1.selectbox(
            "Select the system y:",
            list(self.results[self.metric].systems_metric_results.keys()),
            index=1,
            key = self.ref_filename
            )
            if system_x == system_y:
                st.warning("The system x cannot be the same as system y")
            
            elif self.task == "machine translation":
                plot_multiple_segment_comparison(self.results[self.metric],system_x,system_y,True)
            
            else:
                plot_multiple_segment_comparison(self.results[self.metric],system_x,system_y)

                #Bootstrap Resampling
                _, middle, _ = st.columns(3)
                if middle.button("Perform Bootstrap Resampling",key = self.ref_filename):
                    st.warning(
                        "Running metrics for {} partitions of size {}".format(
                            self.num_samples, self.sample_ratio * len(self.collection_testsets.multiple_testsets[self.ref_filename])
                        )
                    )
                    st.header("Bootstrap resampling results:")
                    with st.spinner("Running bootstrap resampling..."):
                        for self.metric in self.metrics:
                            bootstrap_result = self.available_metrics[self.metric].multiple_bootstrap_resampling(
                                self.collection_testsets.multiple_testsets[self.ref_filename], int(self.num_samples), 
                                self.sample_ratio, system_x, system_y, self.results[self.metric])

                            plot_bootstraping_result(bootstrap_result)


class ClassificationPlot(Plot):
    def __init__(
        self,
        metric:str, 
        metrics: List[str],
        available_metrics: dict,
        results:dict, 
        collection_testsets: CollectionTestsets,
        ref_filename: str,
        task: str
    ) -> None:
        super().__init__(metric, metrics, available_metrics, results, collection_testsets, ref_filename, task)
    
    def display_plots(self) -> None:

        testset = self.collection_testsets.multiple_testsets[self.ref_filename]
        labels = self.collection_testsets.labels

        st.header("Confusion Matrix")
        system_1 = st.selectbox(
            "Select the system:",
            list(self.collection_testsets.indexes_of_systems()),
            index=0
        )

        st.subheader("Overall Confusion Matrix")
        pred = testset.systems_output[system_1]
        overall_confusion_matrix_table(testset.ref,pred,labels)

        st.subheader("Confusion Matrix For Each Label")
        label = st.selectbox(
            "Select the label:",
            list(labels),
            index=0,
            key = "confusion_matrix"
        )
        singular_confusion_matrix_table(testset.ref,pred,labels,label)


        st.header("Analysis Of Each Label")
        analysis_labels(self.results[self.metric], labels)


        st.header("Examples That Are Incorrectly Labelled")
        system_1 = st.selectbox(
            "Select the system:",
            list(self.collection_testsets.indexes_of_systems()),
            index=0,
            key = "examples"
        )
        pred = testset.systems_output[system_1]
        incorrect_examples(testset.src, testset.ref,pred)
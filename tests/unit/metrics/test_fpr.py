import os
import unittest

from telescope.metrics.fp_rate.metric import FPRate
from tests.data import DATA_PATH


class TestFPR(unittest.TestCase):
    labels = ["a", "b", "c"]
    fpr = FPRate(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.fpr.name, "False Positive Rate")

    def test_score(self):

        expected_seg = [1/3, 1/4, 0]

        result = self.fpr.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


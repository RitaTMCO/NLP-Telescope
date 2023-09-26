import os
import unittest

from telescope.metrics.tn_rate.metric import TNRate
from tests.data import DATA_PATH


class TestFPR(unittest.TestCase):
    labels = ["a", "b", "c"]
    tnr = TNRate(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.tnr.name, "True Negative Rate")

    def test_score(self):

        expected_seg = [2/3, 3/4, 1]

        result = self.tnr.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


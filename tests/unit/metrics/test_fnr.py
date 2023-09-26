import os
import unittest

from telescope.metrics.fn_rate.metric import FNRate
from tests.data import DATA_PATH


class TestFNR(unittest.TestCase):
    labels = ["a", "b", "c"]
    fnr = FNRate(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.fnr.name, "False Negative Rate")

    def test_score(self):

        expected_seg = [0.5, 0, 0.5]

        result = self.fnr.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


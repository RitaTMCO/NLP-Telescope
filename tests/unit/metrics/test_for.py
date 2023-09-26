import os
import unittest

from telescope.metrics.fo_rate.metric import FORate
from tests.data import DATA_PATH


class TestFOR(unittest.TestCase):
    labels = ["a", "b", "c"]
    fo_rate = FORate(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.fo_rate.name, "False Omission Rate")

    def test_score(self):

        expected_seg = [1/3, 0, 1/4]

        result = self.fo_rate.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


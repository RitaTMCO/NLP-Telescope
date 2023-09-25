import os
import unittest

from telescope.metrics.np_value.metric import NPValue
from tests.data import DATA_PATH


class TestFOR(unittest.TestCase):
    labels = ["a", "b", "c"]
    npv = NPValue(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.npv.name, "Negative Predictive Value")

    def test_score(self):

        expected_seg = [2/3, 1, 3/4]

        result = self.npv.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


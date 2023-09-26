import os
import unittest

from telescope.metrics.fd_rate.metric import FDRate
from tests.data import DATA_PATH


class TestFDR(unittest.TestCase):
    labels = ["a", "b", "c"]
    fdr = FDRate(labels=labels)
    pred = [ "a", "b", "a", "b", "c"]
    true = [ "a", "b", "c", "a", "c"]

    def test_name_property(self):
        self.assertEqual(self.fdr.name, "False Discovery Rate")

    def test_score(self):

        expected_seg = [0.5, 0.5, 0]

        result = self.fdr.score([],self.pred,self.true)
        
        for i in range(len(self.labels)):
            self.assertEqual(result.seg_scores[i], expected_seg[i])
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, self.pred)


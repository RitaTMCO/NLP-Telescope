import unittest

from telescope.metrics.demographic_parity.metric import DemographicParity

class TestDemographicParity(unittest.TestCase):
    labels = ["male", "neutral", "female"]
    demographic_parity = DemographicParity(labels=labels)

    pred_1 = ["female", "female", "female","male", "female","male","female","male"]
    pred_0 = ["female", "neutral", "female","neutral", "female","male","female","male"]
    pred_075 = ["female", "neutral", "male","male", "male","male","male","male"]

    true = ["female", "neutral", "female","neutral", "female","male","female","male"]

    def test_name_property(self):
        self.assertEqual(self.demographic_parity.name, "Demographic-Parity")

    def test_score_1(self):

        expected_sys = 1.0
        pred = self.pred_1
        result = self.demographic_parity.score([],pred,self.true)
        self.assertEqual(result.sys_score, expected_sys)
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, pred)
    
    def test_score_0(self):
        expected_sys = 0.0
        pred = self.pred_0
        result = self.demographic_parity.score([],pred,self.true)
        self.assertEqual(result.sys_score, expected_sys)
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, pred)

    def test_score_075(self):
        expected_sys = 0.75
        pred = self.pred_075
        result = self.demographic_parity.score([],pred,self.true)
        self.assertEqual(result.sys_score, expected_sys)
        self.assertListEqual(result.ref, self.true)
        self.assertListEqual(result.src, [])
        self.assertListEqual(result.cand, pred)
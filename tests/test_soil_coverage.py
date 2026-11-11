import unittest
from mars_env.soil_coverage import depth_coverage


class DepthCoverageTests(unittest.TestCase):
    def test_gaps_are_not_filled(self):
        r=depth_coverage([(0,10),(20,25)],[(0,30)])[0]
        self.assertEqual(r['covered_cm'],15)
        self.assertEqual(r['missing_intervals_cm'],[[10,20],[25,30]])
        self.assertFalse(r['fully_covered']);self.assertFalse(r['soil_values_assigned'])

    def test_adjacent_horizons_and_target_clipping(self):
        r=depth_coverage([(0,10),(10,20)],[(5,15),(20,25)])
        self.assertTrue(r[0]['fully_covered']);self.assertEqual(r[0]['covered_cm'],10)
        self.assertEqual(r[1]['covered_cm'],0)

    def test_overlapping_measurements_or_targets_are_rejected(self):
        for measured,target in [([(0,10),(9,20)],[(0,20)]), ([(0,20)],[(0,10),(9,20)])]:
            with self.assertRaises(ValueError):depth_coverage(measured,target)

    def test_invalid_depths_and_empty_target_are_rejected(self):
        for measured,target in [([(-1,10)],[(0,20)]), ([(10,10)],[(0,20)]), ([(0,float('inf'))],[(0,20)]), ([(False,10)],[(0,20)]), ([],[])]:
            with self.assertRaises(ValueError):depth_coverage(measured,target)

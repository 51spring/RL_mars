import unittest
from mars_env.water_storage import water_storage_mm


class WaterStorageTests(unittest.TestCase):
    def test_percent_to_mm_and_partial_layer(self):
        self.assertAlmostEqual(water_storage_mm([20,30],[(0,15),(15,45)],30),75)

    def test_missing_lower_depth_does_not_contaminate_upper_stock(self):
        self.assertEqual(water_storage_mm([20,None],[(0,15),(15,45)],15),30)
        with self.assertRaises(ValueError):water_storage_mm([20,None],[(0,15),(15,45)],45)

    def test_depth_gaps_overlaps_and_extrapolation_rejected(self):
        for layers,depth in [([(1,15)],15), ([(0,15),(16,30)],30), ([(0,15),(14,30)],30), ([(0,15)],20)]:
            with self.assertRaises(ValueError):water_storage_mm([20]*len(layers),layers,depth)

    def test_missing_sentinel_nonfinite_and_invalid_percent_rejected(self):
        for value in (None,-99,101,float('nan'),True):
            with self.assertRaises(ValueError):water_storage_mm([value],[(0,15)],15)
        for depth in (True,None,float('nan'),-1):
            with self.assertRaises(ValueError):water_storage_mm([20],[(0,15)],depth)

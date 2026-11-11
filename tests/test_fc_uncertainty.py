import unittest
from mars_env.fc_uncertainty import summarize_fc_plots


class FCUncertaintyTests(unittest.TestCase):
    def test_correlated_depths_require_covariance(self):
        s=summarize_fc_plots([[10,10],[20,20],[30,30],[40,40]],[10,10])
        self.assertAlmostEqual(s['sample_sd_fc_storage_mm']**2,s['covariance_stock_variance_mm2'])
        self.assertAlmostEqual(s['covariance_stock_variance_mm2'],2*s['variance_if_depths_independent_mm2'])
        self.assertAlmostEqual(s['conditional_se_fc_mean_mm'],s['sample_sd_fc_storage_mm']/2)

    def test_opposed_depths_cancel_in_integrated_storage(self):
        s=summarize_fc_plots([[10,40],[20,30],[30,20],[40,10]],[10,10])
        self.assertEqual(s['sample_sd_fc_storage_mm'],0)
        self.assertGreater(s['variance_if_depths_independent_mm2'],0)
        self.assertFalse(s['daily_swc_uncertainty_available'])

    def test_missing_rows_values_and_invalid_depths_rejected(self):
        for rows,depths in [([[10,20]],[10,10]),([[10],[20,30]],[10,10]),([[None],[20]],[10]),([[-99],[20]],[10]),([[10],[20]],[0]),([[float('nan')],[20]],[10])]:
            with self.assertRaises(ValueError):summarize_fc_plots(rows,depths)

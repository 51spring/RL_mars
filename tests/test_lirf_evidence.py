from datetime import date,timedelta
import unittest
from mars_env.lirf_evidence import temperature_descriptions


def records():
    day=date(2020,1,1)
    return [dict(date=(day+timedelta(days=i)).isoformat(),tmean_c=(day+timedelta(days=i)).month) for i in range(366)]


class EvidenceSummaryTests(unittest.TestCase):
    def test_day_weighted_mean_and_both_range_conventions(self):
        rows=records();r=temperature_descriptions(rows)
        self.assertEqual(r['days'],366)
        self.assertAlmostEqual(r['pooled_daily_mean_air_c'],sum(x['tmean_c'] for x in rows)/366)
        self.assertEqual(r['pooled_full_monthly_range_c'],11)
        self.assertEqual(r['pooled_half_monthly_range_c'],5.5)
        self.assertFalse(r['native_tav_tamp_selected'])

    def test_incomplete_year_is_not_silently_averaged(self):
        with self.assertRaises(ValueError):temperature_descriptions(records()[:-1])

    def test_duplicate_dates_are_rejected(self):
        rows=records();rows[-1]=rows[0]
        with self.assertRaises(ValueError):temperature_descriptions(rows)

    def test_missing_and_sentinel_values_are_rejected(self):
        for value in (None,-999,float('nan')):
            rows=records();rows[0]['tmean_c']=value
            with self.assertRaises(ValueError):temperature_descriptions(rows)


if __name__=='__main__':unittest.main()

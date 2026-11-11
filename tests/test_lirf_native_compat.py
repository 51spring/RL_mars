import unittest
from mars_env.lirf_native_compat import align_y4k_weather_header,require_supported_native_dates


class WeatherHeaderCompatibilityTests(unittest.TestCase):
    def test_observation_rows_and_later_columns_unchanged(self):
        text='@DATE    SRAD  TMAX\n2008001  9.35 -7.24\n'
        changed=align_y4k_weather_header(text)
        self.assertEqual(changed.splitlines()[1],text.splitlines()[1])
        self.assertEqual(changed.splitlines()[0][7:],text.splitlines()[0][7:])
        self.assertTrue(changed.startswith('@  DATE'))

    def test_short_and_mixed_dates_are_not_reformatted(self):
        with self.assertRaises(ValueError):
            align_y4k_weather_header('@DATE    SRAD\n08001    9.35\n')

    def test_unknown_layout_and_double_application_rejected(self):
        for text in ('@DATE SRAD\n2008001 9.35\n','@  DATE  SRAD\n2008001 9.35\n'):
            with self.assertRaises(ValueError):align_y4k_weather_header(text)

    def test_native_date_boundary_rejects_unsupported_initial_day(self):
        with self.assertRaises(ValueError):require_supported_native_dates('20080101','20080412')

    def test_native_date_boundary_accepts_explicit_matching_dates(self):
        require_supported_native_dates('20080101','20080101')


if __name__=='__main__':unittest.main()

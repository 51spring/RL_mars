import unittest
from mars_env.lirf_temperature import station_temperature_fixture


class StationTemperatureTests(unittest.TestCase):
    text='@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT\r\n  CO01    40.44 -104.638  1428   -99   -99   -99   -99\r\n@  DATE  SRAD  TMAX  TMIN  RAIN\r\n2008001  9.35 -7.24 -22.3     0\r\n'

    def test_station_only_change_preserves_daily_bytes_and_coordinates(self):
        result=station_temperature_fixture(self.text,8.575,27.161)
        a=self.text.splitlines(keepends=True);b=result.splitlines(keepends=True)
        self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:])
        self.assertEqual(a[1][:30],b[1][:30]);self.assertEqual(a[1][42:],b[1][42:])
        self.assertEqual(b[1][30],' ');self.assertEqual(b[1][36],' ')
        self.assertEqual(b[1][31:36].strip(),'8.57')
        self.assertEqual(b[1][37:42].strip(),'27.16')

    def test_nonpositive_missing_or_nonfinite_rejected(self):
        for v in (0,-99,None,float('nan'),float('inf'),True):
            with self.assertRaises(ValueError):station_temperature_fixture(self.text,v,5)

    def test_wrong_layout_duplicate_header_and_overflow_rejected(self):
        for text in ('',self.text+self.text,self.text.replace('AMP','XYZ')):
            with self.assertRaises(ValueError):station_temperature_fixture(text,20,5)
        with self.assertRaises(ValueError):station_temperature_fixture(self.text,123456,5)

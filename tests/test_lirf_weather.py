from datetime import date,datetime,timedelta
import unittest
from mars_env.lirf_weather import aggregate_hourly_solar,api_daily_value


class LirfWeatherTests(unittest.TestCase):
    def setUp(self):
        self.day=date(2011,8,11)
        self.rows=[(datetime(2011,8,11)+timedelta(hours=i),10) for i in range(1,25)]
        self.api=dict(which='qc',frequency='daily',units='m',timezone='mst',station='gly04',
                      time=['2011-08-11'],solarRad=[100],tMin=[12])

    def test_hour_end_midnight_belongs_to_preceding_day(self):
        self.assertAlmostEqual(aggregate_hourly_solar(self.day,self.rows),14.4)
        wrong=[(t-timedelta(hours=1),v) for t,v in self.rows]
        with self.assertRaises(ValueError):aggregate_hourly_solar(self.day,wrong)

    def test_incomplete_or_duplicate_hours_are_not_filled(self):
        for rows in (self.rows[:-1],self.rows[:-1]+[self.rows[-2]]):
            with self.assertRaises(ValueError):aggregate_hourly_solar(self.day,rows)

    def test_missing_hourly_values_are_not_zero(self):
        for bad in (None,-999,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                aggregate_hourly_solar(self.day,self.rows[:-1]+[(self.rows[-1][0],bad)])

    def test_api_units_are_distinct_from_workbook_hourly_units(self):
        self.assertAlmostEqual(api_daily_value(self.api,self.day,'solarRad',station='gly04'),8.64)
        self.assertEqual(api_daily_value(self.api,self.day,'tMin',station='gly04'),12)

    def test_signed_sensor_readings_are_preserved_without_clipping(self):
        rows=[(self.rows[0][0],-1)]+self.rows[1:]
        self.assertAlmostEqual(aggregate_hourly_solar(self.day,rows),13.74)

    def test_wrong_station_units_and_timezone_are_rejected(self):
        for key,bad in (('station','ksy01'),('units','us'),('timezone','utc')):
            with self.assertRaises(ValueError):
                api_daily_value({**self.api,key:bad},self.day,'solarRad',station='gly04')

    def test_api_missing_and_duplicate_date_contract(self):
        self.assertIsNone(api_daily_value({**self.api,'tMin':[-999]},self.day,'tMin',station='gly04'))
        with self.assertRaises(ValueError):
            api_daily_value({**self.api,'time':['2011-08-11']*2,'tMin':[12,13]},self.day,'tMin',station='gly04')


if __name__=='__main__':unittest.main()

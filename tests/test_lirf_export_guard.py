from copy import deepcopy
import unittest
from mars_env.lirf_export_guard import validate_export,require_export,UNITS


def fixture():
    return dict(sid='s',soil_id='soil',wid='w',wst_id='wsta',sdat='20080412',endat='20080414',
        soil=dict(sid='s',soil_id='soil',sldr='.5',salb='.13',slro='60',slpf='.95',
            soilLayer=[dict(sllb='30',slll='.1',sldul='.2',slsat='.4',slbdm='1.5',slcly='20',slsil='30',slsnd='50')]),
        initial_conditions=dict(icdat='20080401',soilLayer=[dict(icbl='30',ich2o='.2',icno3='1',icnh4='.1')]),
        management=dict(events=[dict(event='planting',date='20080413',pldp='50',cul_id='IB1068'),
            dict(event='fertilizer',date='20080413',fedep='5',feamn='10')]),
        weather=dict(wid='w',wst_id='wsta',dailyWeather=[dict(w_date=d,tmax='20',tmin='10',srad='15',rain='0')
            for d in ('20080412','20080413','20080414')]))


class ExportGuardTests(unittest.TestCase):
    def check(self,data,units=None,purpose='package_diagnostic',cul='IB1068 cultivar'):
        return validate_export(data,units or UNITS,cul,purpose=purpose,writer_version='1.2.21')

    def test_diagnostic_only_and_source_not_modified(self):
        data=fixture();before=deepcopy(data)
        self.assertEqual(self.check(data),[])
        self.assertTrue(self.check(data,purpose='field_validation'))
        with self.assertRaises(ValueError):
            require_export(data,UNITS,'IB1068 cultivar',purpose='field_validation',writer_version='1.2.21')
        self.assertEqual(data,before)

    def test_bad_depth_never_crosses_conversion_boundary(self):
        for value in (None,'-99','NaN','0','inf'):
            data=fixture();data['management']['events'][0]['pldp']=value
            self.assertTrue(self.check(data))
        self.assertTrue(self.check(fixture(),units={**UNITS,'pldp':'unknown'}))

    def test_texture_and_missing_soil_n_are_rejected(self):
        data=fixture();data['soil']['soilLayer'][0]['slcly']='.2'
        self.assertTrue(self.check(data))
        data=fixture();data['initial_conditions']['soilLayer'][0].pop('icno3')
        self.assertTrue(self.check(data))

    def test_link_and_cultivar_mismatch_are_rejected(self):
        data=fixture();data['wid']='other';self.assertTrue(self.check(data))
        self.assertTrue(self.check(fixture(),cul=''))

    def test_missing_weather_and_reversed_dates_are_rejected(self):
        data=fixture();data['weather']['dailyWeather'].pop();self.assertTrue(self.check(data))
        data=fixture();data['sdat']='20080415';self.assertTrue(self.check(data))

    def test_initial_water_above_saturation_is_rejected(self):
        data=fixture();data['initial_conditions']['soilLayer'][0]['ich2o']='.5'
        self.assertTrue(self.check(data))

    def test_weather_missing_sentinel_and_inverted_extrema_are_rejected(self):
        for minimum in ('-999','21'):
            data=fixture();data['weather']['dailyWeather'][0]['tmin']=minimum
            self.assertTrue(self.check(data))


if __name__=='__main__':unittest.main()

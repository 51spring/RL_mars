import unittest
from mars_env.lirf_input_audit import initial_inventory,soil_schema_flags


def soil(base,bulk=1):return dict(sllb=base,slbdm=bulk)
def initial(base,no3=1,nh4=0,water=.2):return dict(icbl=base,icno3=no3,icnh4=nh4,ich2o=water)


class LirfInputAuditTests(unittest.TestCase):
    def test_ppm_and_centimeter_units(self):
        result=initial_inventory([soil(10)],[initial(10)])
        self.assertEqual(result['no3_kg_n_ha'],1)
        self.assertEqual(result['water_mm'],20)

    def test_nonmatching_boundaries_use_density_of_each_intersection(self):
        result=initial_inventory([soil(15,1),soil(20,2)],[initial(10,1),initial(20,2)])
        self.assertEqual(result['no3_kg_n_ha'],4)
        self.assertEqual(len(result['intersections']),3)

    def test_missing_coverage_is_not_extrapolated(self):
        with self.assertRaises(ValueError):initial_inventory([soil(10)],[initial(20)])

    def test_nonincreasing_layers_are_rejected(self):
        with self.assertRaises(ValueError):initial_inventory([soil(20),soil(10)],[initial(10)])

    def test_missing_or_nonfinite_values_are_rejected(self):
        for bad in (-999,float('nan'),float('inf')):
            with self.assertRaises(ValueError):initial_inventory([soil(10,bad)],[initial(10)])

    def test_invalid_field_capacity_and_fraction_like_texture_are_not_corrected(self):
        layer=dict(sllb=120,slfc1='204836',slcly=.11,slsnd=.81,slsil=.08)
        flags=soil_schema_flags([layer])
        self.assertEqual(len(flags),2)
        self.assertEqual(layer['slfc1'],'204836')
        self.assertTrue(flags[1]['fraction_like'])
        self.assertFalse(flags[1]['automatic_rescaling_allowed'])


if __name__=='__main__':unittest.main()

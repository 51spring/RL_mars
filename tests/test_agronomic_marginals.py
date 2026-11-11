import math
from pathlib import Path
import unittest
from mars_env.agronomic_marginals import dry_grain_mass,build_marginal_targets,require_factorial_observation
ROOT=Path(__file__).resolve().parents[1]


class MarginalEvidenceTests(unittest.TestCase):
    def test_verified_grain_moisture_and_mass_units(self):
        self.assertAlmostEqual(dry_grain_mass(1,unit='t/ha',moisture_fraction=.13,basis_verified=True),870)
        self.assertAlmostEqual(dry_grain_mass(2708.9,unit='kg/ha',moisture_fraction=.13,basis_verified=True),2356.743)

    def test_unknown_moisture_and_pot_units_are_refused(self):
        with self.assertRaises(ValueError):dry_grain_mass(10,unit='kg/ha',moisture_fraction=.13,basis_verified=False)
        with self.assertRaises(ValueError):dry_grain_mass(10,unit='g',moisture_fraction=.13,basis_verified=True)

    def test_missing_invalid_and_boolean_values_are_not_zero(self):
        for bad in (None,True,math.nan,math.inf,-1):
            with self.assertRaises(ValueError):dry_grain_mass(bad,unit='kg/ha',moisture_fraction=.13,basis_verified=True)
        for bad in (None,True,math.nan,-.1,1):
            with self.assertRaises(ValueError):dry_grain_mass(10,unit='kg/ha',moisture_fraction=bad,basis_verified=True)

    def test_marginals_do_not_expand_to_pseudoreplicated_cells(self):
        targets,contrasts=build_marginal_targets(ROOT)
        self.assertEqual(len(targets),9);self.assertEqual(len(contrasts),6)
        self.assertEqual(len({t['target_id'] for t in targets}),9)
        self.assertEqual({t['region'] for t in targets},{'Northern','Upper East','Upper West'})
        for t in targets:
            with self.assertRaises(ValueError):require_factorial_observation(t)
            self.assertFalse(t['ready_for_quantitative_validation']);self.assertFalse(t['calibration_allowed'])

    def test_marginal_sem_scales_but_does_not_become_contrast_se(self):
        targets,contrasts=build_marginal_targets(ROOT)
        self.assertAlmostEqual(targets[0]['derived_dry_marginal_sem_kg_ha'],119.5815)
        self.assertTrue(all(c['contrast_standard_error'] is None and c['confidence_interval'] is None for c in contrasts))
        self.assertTrue(any(c['ratio']>1 for c in contrasts))


if __name__=='__main__':unittest.main()

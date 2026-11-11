from pathlib import Path
import unittest

import yaml

from mars_env.economics import grain_price


def config():
    return yaml.safe_load((Path(__file__).parents[1] / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))


class GrainPriceTests(unittest.TestCase):
    def test_market_price_is_converted_to_dry_matter(self):
        self.assertAlmostEqual(grain_price(config()), 0.158 / 0.845)
        self.assertAlmostEqual(grain_price(config()), 0.18698, places=5)

    def test_invalid_basis_is_rejected(self):
        for moisture in (-0.1, 1.0, float("nan")):
            variant = config()
            variant["economics"]["grain_moisture_fraction"] = moisture
            with self.assertRaises(ValueError):
                grain_price(variant)
        variant = config()
        del variant["economics"]["grain_moisture_fraction"]
        with self.assertRaises(KeyError):
            grain_price(variant)


if __name__ == "__main__":
    unittest.main()

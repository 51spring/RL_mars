"""Grain price on the basis DSSAT reports.

DSSAT HWAH is harvested yield in kg dry matter per ha (DATA.CDE). The configured grain price is a
market price per kg at the market moisture basis (15.5 % for maize), so the price per kg of dry
matter is price / (1 - moisture). decision_project.md section 1.
"""
import math


def grain_price(config):
    """USD per kg of dry grain, from the market price and its moisture basis."""
    economics = config["economics"]
    price, moisture = economics["grain_usd_kg"], economics["grain_moisture_fraction"]
    if not math.isfinite(price) or price < 0 or not math.isfinite(moisture) or not 0 <= moisture < 1:
        raise ValueError("Invalid grain price or moisture basis")
    return price / (1 - moisture)

"""Write reconstructible common-season IDs, not policy observations or results."""
import argparse
import hashlib
import json
from pathlib import Path

import yaml
from mars_env.exogenous import generate_season

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output", type=Path, default=ROOT / 'outputs/exogenous_manifest.json')
    args = parser.parse_args()
    if args.count < 1:
        parser.error("positive count required")
    source = ROOT / "configs/proposal_v2.yaml"
    config = yaml.safe_load(source.read_text(encoding="utf-8"))
    seasons = [generate_season(config, split=split, season_id=i).manifest()
               for split in ("train", "validation", "test") for i in range(args.count)]
    report = {"purpose": "External sampling manifest only; no experiment executed",
              "config_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "generator_sha256": hashlib.sha256((ROOT / "src/mars_env/exogenous.py").read_bytes()).hexdigest(),
              "sampling_config": {k: config[k] for k in ("reproducibility", "scenarios", "pest")},
              "budget_multipliers": config["economics"]["budget_multipliers"],
              "seasons": seasons}
    target = args.output.resolve()
    if not target.is_relative_to((ROOT/'outputs').resolve()):
        raise ValueError('Manifest must remain within this project outputs')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {len(seasons)} season descriptors to {target}")


if __name__ == "__main__":
    main()

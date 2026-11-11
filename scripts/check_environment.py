"""Record software and CUDA availability without claiming DSSAT validation."""
import importlib.metadata as metadata
import json
import platform
import sys
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    assert config["environment"]["frame_size"] * config["environment"]["history_days"] == 315
    assert sum(config["environment"]["action_nvec"]) == 17
    cuda = torch.cuda.is_available()
    if cuda:
        x = torch.ones((32, 32), device="cuda")
        assert (x @ x)[0, 0].item() == 32
    report = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": {n: metadata.version(n) for n in [
            "torch", "gymnasium", "stable-baselines3", "sb3-contrib", "numpy",
            "PyYAML", "tensorboard", "pandas", "scipy", "matplotlib"]},
        "cuda_available": cuda,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if cuda else None,
        "cuda_matrix_check": "passed" if cuda else "not_run",
        "dssat_validated": False,
    }
    output = ROOT / "outputs/environment_check.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

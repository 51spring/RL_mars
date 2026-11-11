"""Measure tiny-batch masked categorical GPU synchronization overhead."""
import json
from pathlib import Path
import sys
import time
import torch
from sb3_contrib.common.maskable.distributions import MaskableMultiCategoricalDistribution
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json


def main():
    run=new_run(ROOT,'cuda_distribution_probe');torch.set_num_threads(1);results=[]
    for device in ('cpu','cuda'):
        for validation in (True,False):
            torch.distributions.Distribution.set_default_validate_args(validation)
            logits=torch.zeros((4,17),device=device);mask=torch.ones((4,17),dtype=torch.bool,device=device)
            if device=='cuda':torch.cuda.synchronize()
            start=time.perf_counter()
            for _ in range(10):
                distribution=MaskableMultiCategoricalDistribution([6,9,2]).proba_distribution(logits)
                distribution.apply_masking(mask)
                sample=distribution.sample();distribution.log_prob(sample)
            if device=='cuda':torch.cuda.synchronize()
            row={'device':device,'distribution_validation':validation,'iterations':10,'seconds':time.perf_counter()-start}
            results.append(row);print(json.dumps(row),flush=True)
    write_json(run/'verification.json',{'passed':True,'cases':results,'note':'Microbenchmark only; not DSSAT throughput or policy-performance evidence'})
    print(run)


if __name__=='__main__':main()

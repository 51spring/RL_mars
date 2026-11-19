import json
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from mars_env.protocol import freeze_json, initialization, validate_split, validate_batch
from mars_env.comparison import table_cells
from mars_env.exogenous import evaluation_conditions, generate_season


class Protocol(unittest.TestCase):
    def setUp(self):
        self.cfg=yaml.safe_load((Path(__file__).parents[1]/'configs/proposal_v2.yaml').read_text(encoding='utf-8'))

    def test_season_partitions_and_selection_overlap(self):
        validate_split(self.cfg,'test',list(range(1000)))
        with self.assertRaises(ValueError):
            validate_split(self.cfg,'validation',[1200])
        with self.assertRaises(ValueError):
            validate_split(self.cfg,'test',[5000])
        weather = {split: generate_season(self.cfg,split=split,season_id=0).backend_seed
                   for split in ('train','validation','test')}
        self.assertEqual(len(set(weather.values())),3)

    def test_identity_rejects_config_or_model_change(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'identity.json'
            freeze_json(p,{'config':'one','models':{'b1':'hash'}})
            freeze_json(p,{'config':'one','models':{'b1':'hash'}})
            for value in ({'config':'two','models':{'b1':'hash'}},{'config':'one','models':{'b1':'changed'}}):
                with self.assertRaises(ValueError):
                    freeze_json(p,value)

    def test_batch_rejects_duplicates_missing_cells_leakage_and_violations(self):
        conditions=evaluation_conditions(self.cfg)
        rows=[]
        for row,col,policy,cond in table_cells(conditions):
            for seed in ([None] if policy in ('0','b0p') else [0,1]):
                shock=conditions[cond]
                rows.append(dict(row=row,column=col,policy=policy,condition=cond,seed=seed,season_id=0,
                    split='test',net_return=1.,resource_violations=0,water_cut_day=None if shock is None else shock.day))
        check=lambda r: validate_batch(r,0,[0,1],conditions,('a','b_none','b_cut','a_cut'),'test')
        check(rows)
        for bad in (rows[:-1],rows+[rows[0]],[dict(r,split='validation') for r in rows],
                    [dict(rows[0],resource_violations=1)]+rows[1:]):
            with self.assertRaises(ValueError):
                check(bad)

    def test_mixed_channel_initialization_is_explicit(self):
        self.cfg['training']['sparse_nonzero_mass']={'irrigation':.13,'nitrogen':.025,'spray':None}
        self.assertEqual(initialization(self.cfg,(0,1,2)),{'irrigation':.13,'nitrogen':.025,'spray':None})
        self.cfg['training']['sparse_nonzero_mass']['spray']=0
        with self.assertRaises(ValueError):
            initialization(self.cfg,(2,))

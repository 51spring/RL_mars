"""Privileged harvest snapshots; does not enable research pest execution."""
from .dssat_backend import DssatBackend
from .leaf_diagnostics import LeafProtocol

HARVEST_FIELDS=('RNMODE','GRAIN_FRACTION','STOVER_FRACTION','GRAIN_DM','GRAIN_N',
    'HARVEST_GRAIN_N','CANOPY_DM','CANOPY_N','ROOT_N','ROOT_DM',
    'DEAD_LEAF_DM_RAW','DEAD_LEAF_N_RAW','RESIDUE_DM','RESIDUE_N')


class HarvestProtocol(LeafProtocol):
    def patch_template(self,template):
        template=super().patch_template(template)
        template=template.replace('          done = False','          mars_harvest_record = None\n          done = False',1)
        marker="          'totir': totir,"
        template=template.replace(marker,marker+"\n          'mars_harvest_boundary': mars_harvest_record,")
        template=template.replace('\ndata:\n','\ndata:\n'+''.join(f'  MARS_H_{name}: float\n' for name in HARVEST_FIELDS),1)
        template=template.replace('    on_data:\n','    on_data:\n'+''.join(
            f'      MARS_H_{name}: |\n        mars_h_{name.lower()} = MARS_H_{name}\n' for name in HARVEST_FIELDS),1)
        fields=', '.join(f"'{name.lower()}': float(mars_h_{name.lower()})" for name in HARVEST_FIELDS)
        event='      mars_harvest_boundary:\n        exec: |\n'+f"          mars_harvest_record = {{'date': int(yrdoy), {fields}}}\n"
        return template.replace('    on_event:\n','    on_event:\n'+event,1)


class HarvestBoundaryBackend(DssatBackend):
    def __init__(self,*,filex_transform=None,run_dssat_location='/opt/mars/run_boundary'):
        super().__init__(filex_transform=filex_transform,run_dssat_location=run_dssat_location)
        self._instrumentation=HarvestProtocol()

    def step_damage(self,water,nitrogen,fraction):
        import math
        if not math.isfinite(fraction) or not 0<=fraction<=1:raise ValueError('Invalid leaf fraction')
        self._instrumentation.fraction=float(fraction)
        return super().step(water,nitrogen)

    def step(self,water,nitrogen):return self.step_damage(water,nitrogen,0.)

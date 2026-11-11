"""Privileged direct ear observations, excluded from policy observations."""
from .sequence_audit import SequenceProtocol,rounded_balance

EAR_FIELDS=('DATE','DYNAMIC','STAGE','EARS','POPULATION','EARWT','LFWT','STMWT','GRNWT',
 'GRAINN','STOVN','STOVWT','TOPWT','PODWT','CANOPY_N','SEED_N','YIELD','GNUP')
BAR_FIELDS=('DATE','DYNAMIC','EARS','POPULATION','GPP','G2','SUMP','IDURP','PSKER')


class EarProtocol(SequenceProtocol):
    def patch_template(self,template):
        template=super().patch_template(template)
        template=template.replace('          done = False',
            '          mars_ear_records = []\n          mars_barrenness_records = []\n          done = False',1)
        marker="          'totir': totir,"
        template=template.replace(marker,marker+"\n          'mars_ear_records': mars_ear_records if done else mars_ear_records[-1:],\n          'mars_barrenness_records': mars_barrenness_records if done else mars_barrenness_records[-1:],")
        for prefix,fields,event,target in [('E',EAR_FIELDS,'mars_ear_output','mars_ear_records'),
                                          ('B',BAR_FIELDS,'mars_barrenness','mars_barrenness_records')]:
            template=template.replace('\ndata:\n','\ndata:\n'+''.join(f'  MARS_{prefix}_{k}: float\n' for k in fields),1)
            template=template.replace('    on_data:\n','    on_data:\n'+''.join(
                f'      MARS_{prefix}_{k}: |\n        mars_{prefix.lower()}_{k.lower()} = MARS_{prefix}_{k}\n' for k in fields),1)
            values=', '.join(f"'{k.lower()}': float(mars_{prefix.lower()}_{k.lower()})" for k in fields)
            code=f'      {event}:\n        exec: |\n          {target}.append({{{values}}})\n'
            template=template.replace('    on_event:\n','    on_event:\n'+code,1)
        return template


def verify_organ_record(r):
    pop,ears=r['population'],r['ears']
    terms={'topwt':(r['lfwt']+r['stmwt']+r['earwt'])*pop,
           'podwt':r['earwt']*ears,'yield':r['grnwt']*ears*10,
           'gnup':r['grainn']*ears*10,'canopy_n':(r['stovn']+r['grainn'])*pop,
           'seed_n':r['grainn']*pop}
    checks={k:rounded_balance(r[k],v,abs(r[k])+abs(v)) for k,v in terms.items()}
    return {'checks':checks,'passed':all(c['passed'] for c in checks.values()),
            'direct_ears_to_population':ears/pop if pop>0 else None}

"""Export complete validation learning curves and final results without claiming convergence."""
import argparse
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mars_env.artifacts import sha256, write_json


def render(run):
    design=json.loads((run/'design.json').read_text())
    records=[json.loads((run/f"{fit['label']}_training.json").read_text()) for fit in design['fits']]
    for fit,record in zip(design['fits'],records):
        assert record['steps']==fit['steps']
        assert sha256(run/f"{fit['label']}.zip")==record['checkpoint_sha256']
    out=run/'report'
    out.mkdir(exist_ok=True)
    curves=[]
    image_names=[]
    for regime in ('a','b'):
        for policy in range(1,5):
            fits=[r for r in records if r['regime']==regime and r['policy']==policy]
            if not fits:
                continue
            conditions=list(fits[0]['selection'][0]['by_condition'])
            fig,axes=plt.subplots(len(conditions),1,figsize=(9,3*len(conditions)),squeeze=False)
            for condition,ax in zip(conditions,axes[:,0]):
                steps=[point['steps'] for point in fits[0]['selection']]
                values=[]
                for record in fits:
                    assert [p['steps'] for p in record['selection']]==steps
                    ys=[p['by_condition'][condition] for p in record['selection']]
                    values.append(ys)
                    ax.plot(steps,ys,alpha=.25,lw=.8)
                    selected=next(p for p in record['selection'] if p['steps']==record['selected_steps'])
                    ax.scatter([record['selected_steps']],[selected['by_condition'][condition]],marker='x',s=18)
                    ax.scatter([steps[-1]],[ys[-1]],marker='o',s=22,facecolors='none',edgecolors='black')
                    for p in record['selection']:
                        curves.append({'fit':record['label'],'seed':record['seed'],'condition':condition,
                            'steps':p['steps'],'validation_net_return':p['by_condition'][condition],
                            'selected':p['steps']==record['selected_steps'], 'final':p['steps']==record['steps'],
                            'completed_seasons_in_chunk':p.get('completed_seasons'),
                            'train_return_mean':p.get('train_return_mean')})
                values=np.asarray(values)
                mean=values.mean(0)
                sd=values.std(0,ddof=1) if len(fits)>1 else np.zeros(len(steps))
                ax.plot(steps,mean,label=f'{len(fits)} seeds: mean',color='black')
                ax.fill_between(steps,mean-sd,mean+sd,color='grey',alpha=.2,label='between-seed SD')
                ax.set(xlabel='Cumulative environment steps',ylabel='Raw net return (USD/ha)',title=f'{regime}{policy}: {condition}')
                ax.legend(fontsize=8)
            fig.tight_layout()
            name=f'learning_{regime}{policy}.png'
            fig.savefig(out/name,dpi=180)
            plt.close(fig)
            image_names.append(name)
    with (out/'learning_curves.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(curves[0]))
        writer.writeheader(); writer.writerows(curves)
    final_path=run/'report_test/verification.json'
    text=['# MARS experiment report','',
        f"Training fits: {len(records)}; completed environment steps: {sum(r['steps'] for r in records):,}.",
        'Policy 1/2/3: learned irrigation/nitrogen/spray in sequence; policy 4: simultaneous learning.',
        'a: trained without cuts; b: trained with random cuts. Frozen networks stay within regime and seed.',
        'Model selection uses validation only. Curves show every saved checkpoint; x marks selected checkpoints, circles mark final checkpoints.',
        'Shading is between-seed standard deviation, not a confidence interval. Convergence is not asserted.',
        'Revenue uses dry grain HWAH / (1 - 0.155) times the configured market grain price.', '',
        '## Validation learning curves','']
    for name in image_names:
        text += [f'![{name}]({name})','']
    if final_path.exists():
        final=json.loads(final_path.read_text())
        assert final['passed'] and final['split']=='test' and final['final_test_split_used']
        text += ['## Independent final evaluation','', (run/'report_test/results_table.md').read_text(),
            '### Contrasts','', '| Contrast | USD/ha | 95% CI | Holm p |','|---|---:|---|---:|']
        for name,value in final['contrasts'].items():
            text.append(f"| {name} | {value['estimate_usd_ha']:.2f} | {value['ci95']} | {value['p_holm']:.5f} |")
        text += ['', 'Primary: H1 early-minus-mid, H1 early-minus-late and H2 early-minus-late; two-sided, Holm across three tests.',
            'H3 is exploratory. H4/H5 test their paired contrasts with within-hypothesis Holm; H6 tests sequential over joint under cuts.',
            'Crossed bootstrap: seed rows and common season columns, 10,000 replicates, 95% percentile intervals.',
            '', '## Sensitivity (no retraining)','']
        for file in sorted((run/'report_test').glob('*.json')):
            if file.name.startswith(('water_supply_','survey_noise_')):
                sensitivity=json.loads(file.read_text())
                text += [f'### {file.stem}', '', '| Cell | Mean USD/ha | Lower 10% mean |', '|---|---:|---:|']
                for cell,value in sensitivity['table'].items():
                    text.append(f"| {cell} | {value['mean']:.2f} | {value['lower_10_mean']:.2f} |")
                text.append('')
    else:
        text += ['## Final evaluation pending', '', 'No test-set results are available; validation scores are not final results.']
    text += ['', '## Interpretation limits','',
        'Single-season results conditional on the current cultivar, soil, weather generator and pest assumptions.',
        'Whole-system carbon and native Q/F nitrogen conservation are not claimed. The candidate harvest image is not used.',
        'Severe defoliation recovery and water × nitrogen × damage interactions lack full independent validation; pest effects require caution.',
        'Cultivar calibration independence, survey measurement error, pesticide efficacy and residual duration remain documented limitations.',
        'Lower learned-policy profit and unsupported hypotheses are retained. Previous pilot curves are separate evidence.',
        'Interrupted training skips incomplete seasons; resumed runs are not claimed bitwise equivalent to uninterrupted runs.']
    (out/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    write_json(out/'reproduction.json',{'design_sha256':sha256(run/'design.json'),
        'config_sha256':sha256(run/'config.yaml'), 'image':design['image'],
        'source_sha256':design['source_sha256'], 'selected_models':{r['label']:r['checkpoint_sha256'] for r in records},
        'final_test_complete':final_path.exists()})
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('run',type=Path)
    print(render(parser.parse_args().run))

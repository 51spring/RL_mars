"""Immutable run directories with locally verifiable provenance."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def new_run(root, purpose, *, image_id=None, config_source=None):
    root = Path(root).resolve()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = root / 'outputs' / 'runs' / f'{stamp}_{purpose}_{uuid.uuid4().hex[:8]}'
    run.mkdir(parents=True, exist_ok=False)
    files = [*sorted((root / 'configs').glob('*.yaml')), *sorted((root / 'configs').glob('*.json')), *sorted((root / 'src/mars_env').glob('*.py')),
             *sorted((root / 'scripts').glob('*.py')), *sorted((root / 'docker').glob('*'))]
    hashes = {}
    for path in files:
        if path.is_file():
            relative=path.relative_to(root)
            data=path.read_bytes()
            hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
            target=run/'source_snapshot'/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    config_source=Path(config_source) if config_source else root/'configs/proposal_v2.yaml'
    config_data=config_source.read_bytes()
    (run / 'config.yaml').write_bytes(config_data)
    write_json(run / 'manifest.json', {'purpose': purpose, 'created_utc': stamp,
        'image_id': image_id or os.environ.get('MARS_IMAGE_ID'), 'source_sha256': hashes,
        'effective_config_source':str(config_source),'effective_config_sha256':hashlib.sha256(config_data).hexdigest(),
        'runtime_environment':{key:os.environ.get(key) for key in ('MARS_DSSAT_RUN_LOCATION',
            'MARS_LEAF_RUN_LOCATION','MARS_CANONICAL_UFGA_METADATA',
            'MARS_SEQUENCE_BINARY','MARS_SEQUENCE_MODE')},
        'research_ready': False})
    return run


def write_json(path, data):
    """Atomic replacement within an owned run; callers never reuse run IDs."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    tmp.replace(path)

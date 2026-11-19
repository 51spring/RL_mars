"""Evidence-pinned parameter-lineage gate; never grants field/research readiness."""
import hashlib
import json
from pathlib import Path


def independent_lineage_status(root,study):
    required=study.get('planned_role','').startswith('independent_')
    result=dict(study_id=study['id'],required=required,parameter_lineage_eligible=None,
        blockers=[],does_not_grant_research_readiness=True)
    if not required:return result
    blockers=result['blockers'];result['parameter_lineage_eligible']=False
    for field in ('exact_package_calibration_lineage_verified','cultivar_calibration_independence_verified','independent_validation_allowed'):
        if study.get(field) is not True:blockers.append(field)
    reference=study.get('calibration_provenance_audit');expected=study.get('calibration_provenance_sha256')
    if not isinstance(reference,str) or not isinstance(expected,str) or not reference or not expected:
        blockers.append('pinned_calibration_provenance_missing');return result
    root=Path(root).resolve();path=(root/reference).resolve()
    if not path.is_relative_to(root):
        blockers.append('evidence_outside_workspace');return result
    try:
        data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=expected:
            blockers.append('evidence_sha256_mismatch');return result
        evidence=json.loads(data)
        if not isinstance(evidence,dict):
            blockers.append('evidence_unreadable');return result
        if evidence.get('study_id')!=study['id']:blockers.append('evidence_study_identity_mismatch')
        for field in ('passed','package_calibration_lineage_verified','whole_study_independence_verified'):
            if evidence.get(field) is not True:blockers.append('evidence_'+field)
    except (OSError,ValueError,TypeError):blockers.append('evidence_unreadable')
    result['parameter_lineage_eligible']=not blockers
    return result

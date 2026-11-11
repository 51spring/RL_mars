import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from mars_env.validation_lineage import independent_lineage_status
ROOT=Path(__file__).resolve().parents[1]


class LineageGateTests(unittest.TestCase):
    def fixture(self,root,qualified):
        report=dict(study_id='s',passed=True,package_calibration_lineage_verified=qualified,whole_study_independence_verified=qualified)
        path=Path(root)/'audit.json';path.write_text(json.dumps(report))
        return dict(id='s',planned_role='independent_validation',exact_package_calibration_lineage_verified=True,
            cultivar_calibration_independence_verified=True,independent_validation_allowed=True,
            calibration_provenance_audit='audit.json',calibration_provenance_sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    def test_unknown_lineage_is_not_promoted_from_planned_role(self):
        s=dict(id='s',planned_role='independent_validation')
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as root:self.assertFalse(independent_lineage_status(root,s)['parameter_lineage_eligible'])

    def test_other_independent_role_names_also_require_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as root:
            for role in ('independent_external_validity','independent_early_damage_qualitative','independent_repeated_damage_qualitative','independent_nitrogen_response'):
                r=independent_lineage_status(root,dict(id='s',planned_role=role))
                self.assertTrue(r['required']);self.assertFalse(r['parameter_lineage_eligible'])

    def test_registry_flags_do_not_override_negative_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as root:
            s=self.fixture(root,False);r=independent_lineage_status(root,s)
            self.assertFalse(r['parameter_lineage_eligible'])
            self.assertIn('evidence_package_calibration_lineage_verified',r['blockers'])

    def test_changed_bytes_wrong_study_or_outside_path_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as root:
            s=self.fixture(root,True);(Path(root)/'audit.json').write_text('{}')
            self.assertIn('evidence_sha256_mismatch',independent_lineage_status(root,s)['blockers'])
            s=self.fixture(root,True);s['id']='other'
            self.assertIn('evidence_study_identity_mismatch',independent_lineage_status(root,s)['blockers'])
            s['calibration_provenance_audit']='../outside.json'
            self.assertIn('evidence_outside_workspace',independent_lineage_status(root,s)['blockers'])
            s=self.fixture(root,True);(Path(root)/'audit.json').write_text('[]')
            s['calibration_provenance_sha256']=hashlib.sha256((Path(root)/'audit.json').read_bytes()).hexdigest()
            self.assertIn('evidence_unreadable',independent_lineage_status(root,s)['blockers'])

    def test_pinned_positive_evidence_only_qualifies_this_gate(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as root:
            s=self.fixture(root,True);r=independent_lineage_status(root,s)
            self.assertTrue(r['parameter_lineage_eligible'])
            self.assertTrue(r['does_not_grant_research_readiness'])
            s['exact_package_calibration_lineage_verified']='true'
            self.assertFalse(independent_lineage_status(root,s)['parameter_lineage_eligible'])

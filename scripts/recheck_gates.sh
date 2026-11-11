#!/bin/sh
# Re-run the comparison-relevant gate verifications against the current code in the current image.
# Each script is tried with the legacy DSSAT interpreter first, then the learner interpreter.
# Usage (inside mars-dssat:ppo-cpu-metadata): sh /workspace/scripts/recheck_gates.sh
cd /workspace || exit 1
for script in verify_gym_integration verify_paired_seasons verify_real_rewards verify_experimental_env \
              verify_native_leaf verify_crop_failure probe_dssat_contract verify_policy_interfaces; do
  status=FAIL
  for py in /opt/gym_dssat_pdi/bin/python /opt/mars_ppo/bin/python; do
    if timeout --kill-after=10s 900s "$py" "scripts/$script.py" > "/tmp/$script.log" 2>&1; then
      status="PASS ($py)"
      break
    fi
    if ! grep -q "ModuleNotFoundError\|ImportError" "/tmp/$script.log"; then
      break
    fi
  done
  echo "GATE_CHECK $script: $status"
  if [ "$status" = FAIL ]; then tail -n 12 "/tmp/$script.log"; fi
done

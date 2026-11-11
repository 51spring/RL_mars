# 잠재함수 보상과 실제 DSSAT PPO 연결

2026-11-05 검증 완료. 아래 결과는 연결 진단이며 농학 검증이나 정책 성능 비교가 아닙니다.

## 보상 계약

`PotentialRewardWrapper`는 공개 관측의 최신 생육단계, 지상부 건물중, 곡물 가격만 사용합니다.

```
Phi(s) = grain_price * eta(istage) * topwt
r_train = (r_raw + Phi(next) - Phi(current)) / 1000
gamma = 1
```

`configs/proposal_v2.yaml`의 eta는 단계 1~10 모두 0.45입니다. 제안서에 수치가 없어 명시적으로 둔 초기 구현 가정이며, 작물 회복을 보정하는 계수가 아닙니다. 본 실험 전에 확정·민감도 검토가 필요합니다.

실제 수확과 작물 실패에서는 종료 잠재값을 0으로 둡니다. 행정적 시간제한에서는 다음 상태의 잠재값을 유지하며 임의 수확 매출을 주지 않습니다. PPO rollout 경계도 작물 종료로 처리하지 않습니다. 모든 경로에서 raw 수익 원장은 유지합니다.

검사식은 `1000 * sum(r_train) = sum(r_raw) + Phi(final) - Phi(initial)`입니다. reset 잠재값과 종료 잠재값, 잔차를 `reward_audit`에 기록합니다.

실제 DSSAT 검증 (`outputs/real_reward_verification.json`):

| 사례 | 정책 단계 | raw 합계 | 최종 잠재값 | 결과 |
|---|---:|---:|---:|---|
| 정상 수확 | 136 | 376.444 | 0 | 원래 관측 궤적·경제 원장 일치 |
| 깊은 파종 실패 | 61 | -21.4 | 0 | 매출 0, 투입 비용 유지 |
| 행정적 시간제한 | 20 | -21.4 | 2.0476798655 | 잠재값 유지, 가상 수확 없음 |

세 사례 모두 망원합 잔차의 절댓값은 1e-12 미만입니다.

## 실행 환경

`mars-dssat:ppo-cpu`는 `mars-dssat:leaf-experimental`을 기반으로 합니다. DSSAT/PDI는 기존 `/opt/gym_dssat_pdi/bin/python`에서 실행하고, PPO는 별도 `/opt/mars_ppo/bin/python`에서 실행합니다. 오래된 Gym 의존성과 현대 학습 패키지를 서로 다른 가상환경으로 분리했습니다.

`LegacyProcessBackend`가 비공개 JSON 파이프를 통해 별도 DSSAT 프로세스를 제어합니다. 실제 밀도·외생 난수는 정책 관측으로 보내지 않습니다. 작업 중단·시간 초과에는 자식 프로세스 그룹도 정리합니다. 현대 PPO 환경의 `pip check`는 통과했으며 잠금 목록과 이미지 ID를 outputs에 기록했습니다.

```powershell
docker build -f docker/Dockerfile.ppo -t mars-dssat:ppo-cpu .
./scripts/verify_real_rewards.ps1
./scripts/smoke_real_ppo.ps1 -Mode no_pest
./scripts/smoke_real_ppo.ps1 -Mode experimental_pest
```

## 실제 학습 검사

CPU, `SubprocVecEnv` 4개, 총 1,024단계, rollout 길이 64, batch 64, epoch 2, 정책 시드 42로 실행했습니다. gamma=1, GAE=0.95, 정책·가치망은 각각 256×256이며 초기 비영 행동 확률 질량은 관수/질소/살포 0.13/0.03/0.03입니다.

| 모드 | PPO 업데이트 | 완료된 학습 시즌 | 예비 처리량 (단계/초) | 검증 시즌 raw 평균 수익 |
|---|---:|---:|---:|---:|
| 무해충 | 8 | 4 | 147.48 | 211.325 |
| 실험용 해충 | 8 | 4 | 130.14 | 158.474 |

학습에는 보조 보상을 적용하고, 마스크 평가는 보조 보상 없는 raw 수익으로 수행했습니다. 학습 마지막 optimizer 업데이트 이후 평가하며, 저장 모델을 다시 불러와 동일한 검증 시즌 2개에서 같은 결과임을 확인했습니다. 최종 시험 split은 사용하지 않았습니다. 완료된 학습 시즌의 raw 합계·경제 원장·보상 망원합도 일치했습니다.

실험용 해충은 온도 기준 10/30°C와 조사 잡음 0.01을 진단 전용으로 사용합니다. 연구 설정의 미보정 값은 null이며 연구용 해충 실행 제한은 유지합니다.

처리량은 짧은 실행에서 평가 콜백 시간을 제외한 참고 수치입니다. 10만~20만 단계 CPU/GPU 비교를 대체하지 않으며, 이 두 모드의 수익으로 정책 우열을 판단할 수 없습니다. 전체 탄소·토양 수지, 농학 보정, 기준선 튜닝, 500만 단계×10시드 본 실험은 남아 있습니다.

근거: `outputs/real_ppo_no_pest_cpu/verification.json`, `outputs/real_ppo_experimental_pest_cpu/verification.json`, 각 폴더의 모델·평가 배열·TensorBoard 기록. 소프트웨어 검사는 총 69개 통과했습니다.

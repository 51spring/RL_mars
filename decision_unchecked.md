# decision_project.md 미검수 항목

`[ ]` 표 행을 절별로 모았다. 생성: 2026-11-11. 원본의 절 번호를 그대로 쓴다.

| 구분 | 항목 수 |
|---|---:|
| A. 결정이 남은 항목 | 3 |
| B. 설정·코드 값 검토 | 223 |
| C. 이번에 결정·반영됨, 체크만 남음 | 48 |
| D. 측정·탐색 결과 기록 | 148 |
| E. 진입 조건·미기록 범위·한계 | 36 |
| 합계 | 458 |

## A. 결정이 남은 항목 (3)

사용자 판단이 필요하다.

### 0. 먼저 결정할 항목 (3)

- [ ] D5 — 살포 횟수 상한
- [ ] D9 — 평가·동결망 행동 방식
- [ ] D10 — 정책 4의 학습 시즌

## B. 설정·코드 값 검토 (223)

값 자체를 하나씩 확인할 항목.

### 1. 시뮬레이터 (DSSAT 시나리오) (24)

- [ ] DSSAT 실행 모드 — `mode="all"` (관수·시비 외부 입력, 파종 고정)
- [ ] 시나리오 — UFGA8201, Gainesville FL, 필드 UFGA0002
- [ ] 처리 번호 — 3 (IRRIGATED LOW NITROGEN 행. 관수·시비 일정은 외부 입력으로 대체)
- [ ] 위도, 경도, 고도 — 29.6380, −82.3689, 40 m
- [ ] 작물·품종 — 옥수수, IB0035 McCurdy 84aa
- [ ] 품종 계수 P1, P2, P5, G2, G3, PHINT — 265.0, 0.300, 920.0, 920.0, 8.00, 43.00
- [ ] 생태형 — IB0001 GENERIC MIDWEST1
- [ ] 생태형 TBASE, TOPT, ROPT, P20, DJTI, GDDE, DSGFT, RUE, KCAN — 8.0, 34.0, 34.0, 12.5, 4.0, 6.0, 170, 4.2, 0.85
- [ ] 토양 — IBMZ910014 Millhopper Fine Sand, 깊이 180 cm
- [ ] 토양 표층 SALB, SLU1, SLDR, SLRO, SLNF, SLPF — 0.18, 2.0, 0.65, 60.0, 1.00, 0.92
- [ ] 모의 시작일, 초기조건일 — 1982년 30일
- [ ] 파종일 — 1982년 57일 (`planting_yrdoy` 1982057)
- [ ] 재식밀도 — 7.2 주/m²
- [ ] 이랑 폭, 파종 깊이 — 61 cm, 7 cm
- [ ] 초기 잔사 ICRES, ICREN — 1000 kg/ha, 0.8 %
- [ ] 수확 — 성숙기 수확 (HARVS M), 수확 종료 한계 83057
- [ ] 기상 — WTHER W, WGEN 확률 기상 (`random_weather=True` 코드 고정)
- [ ] 시뮬레이터 입력 상한 — 관수 50 mm, 질소 200 kg/ha
- [ ] 관수 효율 EFIR, IREFF — 1, 1 (넣은 물이 전량 토양에 도달)
- [ ] FileX 자동관수 계수 (mode all에서는 미사용) — IMDEP 30 cm, ITHRL 50 %, ITHRU 100 %, IRAMT 10 mm
- [ ] 생육 실패 판정 — WARNING.OUT의 실패 문구 3종이면 매출 0
- [ ] 곡실 수량 — Summary.OUT `HWAH` (kg/ha)
- [ ] 실행 이미지 — `mars-dssat:ppo-cpu-metadata` (sha256:11e2650fed75…)
- [ ] 라이브러리 — sb3-contrib 2.7.1, stable-baselines3 2.7.1, torch 2.5.1+cpu, gymnasium 1.2.2

### 1. 시뮬레이터 (DSSAT 시나리오) > 토양층 (8)

- [ ] 5 — 0.026
- [ ] 15 — 0.025
- [ ] 30 — 0.025
- [ ] 60 — 0.025
- [ ] 90 — 0.028
- [ ] 120 — 0.028
- [ ] 150 — 0.029
- [ ] 180 — 0.070

### 2. 환경 설정 (`configs/proposal_v2.yaml`) (90)

- [ ] `source.proposal` — docs/proposal_revised.pdf
- [ ] `source.revised` — 2026-11-05
- [ ] `source.status` — metadata_corrected_runtime_verified_harvest_boundary_mapped_agronomic_validation_pending
- [ ] `environment.backend` — dssat
- [ ] `environment.runtime_profile` — metadata_corrected
- [ ] `environment.mode` — all
- [ ] `environment.scenario` — UFGA8201
- [ ] `environment.random_weather` — true
- [ ] `environment.frame_size` — 28
- [ ] `environment.history_days` — 7
- [ ] `environment.observation_size` — 196
- [ ] `environment.action_nvec` — [6, 9, 2]
- [ ] `environment.mask_size` — 17
- [ ] `environment.irrigation_grid_mm` — [0, 5, 10, 15, 20, 25]
- [ ] `environment.nitrogen_grid_kg_ha` — [0, 10, 20, 27, 35, 40, 54, 60, 80]
- [ ] `environment.pest_enabled` — true
- [ ] `environment.require_live_leaf_damage_writer` — true
- [ ] `economics.grain_usd_kg` — 0.158
- [ ] `economics.water_usd_mm_ha` — 1.1
- [ ] `economics.nitrogen_usd_kg` — 0.79
- [ ] `economics.spray_product_usd_ha` — 35.0
- [ ] `economics.spray_labor_usd_ha` — 15.0
- [ ] `economics.irrigation_labor_usd_event_ha` — 3.0
- [ ] `economics.nitrogen_labor_usd_event_ha` — 5.0
- [ ] `economics.budgets_usd_ha.spray` — 150.0
- [ ] `pest.arrival_probability` — 0.03
- [ ] `pest.arrival_amplitude` — 0.05
- [ ] `pest.growth_low` — 0.05
- [ ] `pest.growth_high` — 0.15
- [ ] `pest.temperature_low_c` — 10
- [ ] `pest.temperature_high_c` — 30
- [ ] `pest.survey_noise_std` — 0.01
- [ ] `management.spray_interval_days` — 7
- [ ] `management.spray_istage_exclusive_upper` — 5
- [ ] `management.input_closed_istage` — 6
- [ ] `management.survey_interval_days` — 7
- [ ] `management.survey_window_days` — 7
- [ ] `baseline_policy.water_stress_threshold` — 0.3
- [ ] `baseline_policy.irrigation_mm` — 10
- [ ] `reduction_response_rule.reserve_mm` — 83.5
- [ ] `reduction_response_rule.flowering_day` — 83
- [ ] `reduction_response_rule.maturity_day` — 130
- [ ] `reduction_response_rule.event_interval_days` — 9.4
- [ ] `reduction_response_rule.remaining_demand_mm` — [[0, 163.6], [42, 163.6], [83, 83.5], [93, 49.5], [130, 0.0]]
- [ ] `reward_shaping.enabled` — true
- [ ] `reward_shaping.scale` — 1000.0
- [ ] `reward_shaping.gamma` — 1.0
- [ ] `reward_shaping.eta_by_stage.1` — 0.45
- [ ] `reward_shaping.eta_by_stage.2` — 0.45
- [ ] `reward_shaping.eta_by_stage.3` — 0.45
- [ ] `reward_shaping.eta_by_stage.4` — 0.45
- [ ] `reward_shaping.eta_by_stage.5` — 0.45
- [ ] `reward_shaping.eta_by_stage.6` — 0.45
- [ ] `reward_shaping.eta_by_stage.7` — 0.45
- [ ] `reward_shaping.eta_by_stage.8` — 0.45
- [ ] `reward_shaping.eta_by_stage.9` — 0.45
- [ ] `reward_shaping.eta_by_stage.10` — 0.45
- [ ] `training.algorithm` — MaskablePPO
- [ ] `training.gamma` — 1.0
- [ ] `training.gae_lambda` — 0.95
- [ ] `training.gae_lambda_candidates` — [0.95, 0.98]
- [ ] `training.policy_layers` — [256, 256]
- [ ] `training.value_layers` — [256, 256]
- [ ] `training.n_envs` — 8
- [ ] `training.n_steps` — 256
- [ ] `training.batch_size` — 256
- [ ] `training.n_epochs` — 10
- [ ] `training.deterministic_policy` — true
- [ ] `training.timesteps_per_seed` — 5000000
- [ ] `training.seeds` — [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- [ ] `training.sparse_nonzero_mass.irrigation` — 0.13
- [ ] `training.sparse_nonzero_mass.nitrogen` — 0.03
- [ ] `training.sparse_nonzero_mass.spray` — 0.03
- [ ] `training.device` — cpu
- [ ] `scenarios.reduction_probability` — 0.75
- [ ] `scenarios.timing` — calendar_day
- [ ] `scenarios.evaluation_beta` — 1.0
- [ ] `scenarios.bootstrap_replicates` — 10000
- [ ] `scenarios.announcement_istages` — [1, 2, 4]
- [ ] `scenarios.delay_days_inclusive` — [0, 5]
- [ ] `scenarios.training_reduction_range` — [0.1, 0.7]
- [ ] `scenarios.evaluation_seasons_per_condition` — 1000
- [ ] `scenarios.evaluation_delay_days` — 3
- [ ] `scenarios.reduction_contract` — remaining_fraction
- [ ] `reproducibility.weather_seed_version` — 1
- [ ] `reproducibility.split_seeds.train` — 11001
- [ ] `reproducibility.split_seeds.validation` — 22001
- [ ] `reproducibility.split_seeds.test` — 33001
- [ ] `reproducibility.streams` — [weather, pest_arrival, survey_noise, reduction, budget]
- [ ] `reproducibility.paired_external_seasons` — true

### 3. 코드에 고정된 값 (30)

- [ ] 해충 온도 하한·상한 — ~~코드 고정~~ → 설정 `pest.temperature_low_c/high_c` (10, 30 °C)에서 읽음 (D1, 2026-11-11)
- [ ] 조사 잡음 표준편차 — ~~코드 고정~~ → 설정 `pest.survey_noise_std` (0.01)에서 읽음 (D2)
- [ ] 조사 주기·창 — 7일, 7일. 설정값이 7이 아니면 실행 거부 (D3)
- [ ] 증식률 g(T) — growth_low + (growth_high − growth_low)×(T−T하한)/(T상한−T하한), 구간 밖은 끝값 고정. 현재 0.05 + 0.10×(T−10)/20
- [ ] 살포 효과 — 효능×exp(−경과일/잔효일). 현재 0.8×exp(−경과일/5), 마지막 살포 기준, 누적 없음
- [ ] 밀도 갱신 — (1−효과)×[밀도 + g×밀도×(1−밀도) + 유입], 0~1로 제한
- [ ] 일 잎 손실 — α×밀도. 현재 α = 0.01 (이전 0.03, 17절)
- [ ] 조사값 — 7일 평균 손실/α + 잡음 표준편차×표준정규, 0~1로 제한, 7의 배수 일 아침
- [ ] 온도 입력 — (Tmin+Tmax)/2
- [ ] 시즌 최대 일수 — 240일
- [ ] 평가 최대 단계 — 240
- [ ] 외생 배열 길이 — 400일
- [ ] 난수 흐름 ID — weather 11, pest_arrival 23, survey_noise 37, reduction 53, budget 71
- [ ] 난수 흐름 버전 — 1
- [ ] WGEN 시드 구간 — train 10001–99998 (89,998개), validation 1–4999, test 5000–9999
- [ ] 학습 시즌 소진 시 — 순서대로 반복 (D10)
- [ ] a 정책 학습 감축 확률 — 0.0
- [ ] 물 감축 시 원장 — 남은 물×(1−감축률), 시즌 1회
- [ ] 예산 차감 — 자재비만(질소·살포). 관수·시비 작업비는 예산 제외, 비용에는 포함. 물은 예산 없이 공급량만 차감(23절)
- [ ] 성숙 뒤 투입 차단 — istage 6에서 관수·시비 0만 허용 (설정 `management.input_closed_istage`)
- [ ] 원장 허용 오차 — 1e-8
- [ ] 보상 — 수확 매출 − 당일 비용. 실패 시 매출 0
- [ ] 잠재함수 Φ — 곡실 단가×η(단계)×`topwt`. 단가는 환경 상수(관측에서 제거, 22절)
- [ ] 학습 보상 — (원보상 + Φ다음 − Φ현재)/1000
- [ ] b0′ 보호 단계 — istage 4, 5
- [ ] b0′ 배분 — 풀/남은 예상 관수 횟수, 최소 5 mm 단위 허용
- [ ] 평가 시작 시즌 — validation 2000번부터
- [ ] 측정 시작 시즌 — validation 1000번부터 120개
- [ ] 최종 시험 구간 접근 — 코드에서 차단
- [ ] 진입 조건 판정 — `research_ready=false`, `main_training_allowed=false`

### 3. 코드에 고정된 값 > PPO에서 지정하지 않아 라이브러리 기본값을 쓰는 항목 (12)

- [ ] learning_rate — 0.0003
- [ ] clip_range — 0.2
- [ ] clip_range_vf — None
- [ ] normalize_advantage — True
- [ ] ent_coef — 0.0
- [ ] vf_coef — 0.5
- [ ] max_grad_norm — 0.5
- [ ] target_kl — None
- [ ] activation_fn — Tanh
- [ ] ortho_init — True
- [ ] optimizer — Adam
- [ ] share_features_extractor — True

### 5. 정책과 실험 구성 (18)

- [ ] 0 (πB) — 규칙
- [ ] a1 / b1 — PPO
- [ ] a2 / b2 — 정책 1 동결
- [ ] a3 / b3 — 정책 1 동결
- [ ] a4 / b4 — PPO
- [ ] b0′ — 감축 전 규칙, 감축 후 예비 배분
- [ ] a — 0, a1~a4
- [ ] b-무 — 0, b1~b4
- [ ] a-유 — a1~a4 (정책망 고정, 당일 관측에 반응)
- [ ] b-유 — 0, b1~b4, b0′
- [ ] 각 칸 지표 — 평균 순수익, 하위 10% 평균(USD/ha)
- [ ] 하위 10% 계산 — 시드별로 하위 ceil(10%) 시즌 평균 후 시드 평균, b-유는 9조건 평균
- [ ] 부트스트랩 — 시드·시즌 교차 복원추출 10,000회, 95% 백분위 구간, 난수 시드 0
- [ ] p값 — 귀무 중심화 부트스트랩. C1·C2 단측, 나머지 양측
- [ ] Holm 검정군 — 가설 2개, 조건별 9개, 대비 비용 4개, 대비 이득 4개, 감축 손실 5개, 효과 5개
- [ ] 대비 비용 — a − (b-무), 정책 1~4 (정책 0은 항상 0이라 제외)
- [ ] 대비 이득 — (b-유) − (a-유), 정책 1~4
- [ ] C1, C2 — b4−b1 기준, 초기 대 후기 시점

### 5. 정책과 실험 구성 > 가설 (2026-11-11 새 비교구조) (6)

- [ ] H1 감축 강도 — 감축률이 커질수록 b4의 b1 대비 추가 가치가 커진다
- [ ] H2 감축 시점 — 초기 감축에서 후기 감축보다 b4의 b1 대비 추가 가치가 크다
- [ ] H3 방제 가치 — 감축은 시비까지 학습한 정책에 방제 학습을 더한 가치를 바꾼다. 해충·회복 검증 전에는 탐색 분석
- [ ] H4 대비 비용과 이득 — 감축에 대비해 학습하면 무감축 때 수익이 낮아지고 감축 때 수익이 높아진다
- [ ] H5 관수 학습의 감축 대응 — 관수 학습의 규칙 대비 이득은 감축 때 더 크고, b0′보다 수익이 높다
- [ ] H6 학습 구조 — 순차 추가와 동시 학습의 효과는 감축 유무에 따라 달라진다

### 7. 검증 게이트 값 (`validation_gates`, 코드 미사용) (35)

- [ ] `validation_gates.metadata_read_store_and_coordinates` — true
- [ ] `validation_gates.corrected_profile_short_ppo` — true
- [ ] `validation_gates.harvest_boundary_observed` — true
- [ ] `validation_gates.experimental_qf_native_residue_handoff` — true
- [ ] `validation_gates.experimental_maize_harvest_unit_adapter` — false
- [ ] `validation_gates.experimental_c_terminal_allocation` — true
- [ ] `validation_gates.native_qf_n_partition_conservation` — false
- [ ] `validation_gates.experimental_harvest_n_candidate` — true
- [ ] `validation_gates.experimental_harvest_scope_audit` — true
- [ ] `validation_gates.harvest_n_candidate_broad_scope` — false
- [ ] `validation_gates.experimental_direct_ear_organ_audit` — true
- [ ] `validation_gates.experimental_actual_harvest_contract_v2` — true
- [ ] `validation_gates.experimental_integrated_crop_soil_n_v2` — true
- [ ] `validation_gates.public_agronomic_scenario_registry` — true
- [ ] `validation_gates.post_harvest_ecosystem_balance` — false
- [ ] `validation_gates.experimental_weather_calendar_action_audit` — true
- [ ] `validation_gates.experimental_soil_output_arithmetic` — true
- [ ] `validation_gates.experimental_maturity_preharvest_n` — true
- [ ] `validation_gates.real_cuda_long_stability` — true
- [ ] `validation_gates.real_cpu_long_stability` — true
- [ ] `validation_gates.controlled_long_cpu_gpu_comparison` — true
- [ ] `validation_gates.baseline_policy_interfaces` — true
- [ ] `validation_gates.potential_reward_telescope` — true
- [ ] `validation_gates.real_cpu_maskableppo_smoke` — true
- [ ] `validation_gates.experimental_plant_n_inventory_balance` — true
- [ ] `validation_gates.experimental_online_pest_survey` — true
- [ ] `validation_gates.experimental_native_leaf_write` — true
- [ ] `validation_gates.whole_season_carbon_nitrogen_balance` — false
- [ ] `validation_gates.deep_planting_failure_handling` — true
- [ ] `validation_gates.paired_external_seasons` — true
- [ ] `validation_gates.live_leaf_damage_write` — false
- [ ] `validation_gates.irrigation_10mm_regression` — true
- [ ] `validation_gates.no_pest_regression` — true
- [ ] `validation_gates.crop_recovery` — false
- [ ] `validation_gates.water_nitrogen_damage_interaction` — false

## C. 이번에 결정·반영됨, 체크만 남음 (48)

결정은 끝났고 표의 체크 칸만 비어 있다.

### 22. 관측 변수 45개 점검 (2026-11-11) (45)

- [ ] 1. dap — 45번 season_day와 99.3 % 같음 (중복)
- [ ] 2. istage — 10은 수확 뒤 마지막 관측에만 나온다
- [ ] 3. vstage — 정상
- [ ] 4. xlai — 정상
- [ ] 5. topwt — 정상
- [ ] 6. grnwt — 정상
- [ ] 7. rtdep — 척도 대비 0~0.38만 사용
- [ ] 8. swfac — 정상
- [ ] 9. nstres — 정상
- [ ] 10. sw — **척도 대비 폭 0.08로 매우 좁다.** 뿌리 영역이 아닌 전체 평균이라 정보도 약하다(12절 3번에서 같은 이유로 규칙 기준에서 제외)
- [ ] 11. wtdep — **사실상 상수** (척도 대비 폭 0.03). 이 토양에 지하수위가 없다
- [ ] 12. ep — 정상
- [ ] 13. rain — 0.4 %가 1을 넘음(최대 2.3). 드물어 문제 작음
- [ ] 14. tmax — 정상
- [ ] 15. srad — 정상
- [ ] 16. dtt — 정상
- [ ] 17. water_used — 20번과 완전 선형 (중복)
- [ ] 18. nitrogen_used — 21번과 완전 선형 (중복)
- [ ] 19. sprays — 22·40번과 완전 상관 (이 정책들은 최대 1회)
- [ ] 20. water_budget_ratio — 17번 중복
- [ ] 21. nitrogen_budget_ratio — 18번 중복
- [ ] 22. spray_budget_ratio — 19번 중복
- [ ] 23. water_left — 정상. 감축량은 이 값의 급감으로 드러남
- [ ] 24. initial_water — **상수**
- [ ] 25. initial_water_budget — **상수** (예산 배율 제거 이후)
- [ ] 26. initial_nitrogen_budget — **상수**
- [ ] 27. initial_spray_budget — **상수**
- [ ] 28. grain_price — **상수**
- [ ] 29. water_price — **상수**
- [ ] 30. nitrogen_price — **상수**
- [ ] 31. spray_price — **상수**
- [ ] 32. irrigation_labor — **상수**
- [ ] 33. nitrogen_labor — **상수**
- [ ] 34. announced — 정상. 감축 당일부터 1
- [ ] 35. reduction_fraction — 정상. 감축 전 0
- [ ] 36. days_since_announcement — 정상
- [ ] 37. survey_value — 정상
- [ ] 38. survey_age — 정상
- [ ] 39. survey_available — **상수** (해충 환경에서는 항상 1)
- [ ] 40. has_sprayed — 19번 중복
- [ ] 41. days_since_spray — 정상. 미살포 시 0이고 40번으로 구분
- [ ] 42. previous_water — 정상 (격자 최대 25)
- [ ] 43. previous_nitrogen — 정상
- [ ] 44. previous_spray — 정상
- [ ] 45. season_day — 1번 중복

### 23. 행동 공간 점검·정리 (2026-11-11) (3)

- [ ] 관수 — 0, 5, 10, 15, 20, 25 mm
- [ ] 시비 — 0, 10, 20, 27, 35, 40, 54, 60, 80 kg/ha
- [ ] 살포 — 0/1

## D. 측정·탐색 결과 기록 (148)

값이 아니라 실행 결과 행이다. 읽고 확인하는 용도.

### 6. 측정값 (규칙 정책, 검증 120시즌, 감축 없음) (8)

- [ ] 1 — 출아~유년기 끝
- [ ] 2 — ~화서 분화
- [ ] 3 — ~잎 생장 끝
- [ ] 4 — 개화기~등숙 시작
- [ ] 5 — 유효 등숙
- [ ] 6 — 성숙
- [ ] 시즌 길이(일) — 132.8
- [ ] 시즌 관수량(mm) — 151.8

### 9. 관수 값 점검 (2026-11-11, `MARS_reference` 기준) (10)

- [ ] 물 단가 `water_usd_mm_ha` — 1.1
- [ ] 물 예산 `budgets_usd_ha.water` — ~~220~~ 제거
- [ ] 관수 격자 `irrigation_grid_mm` — 0~25, 5 간격
- [ ] 관수 작업비 `irrigation_labor_usd_event_ha` — 3.0
- [ ] b0′ 보호 구간 — istage 4·5 (83일~)
- [ ] 감축 계약 `reduction_contract` — remaining_fraction
- [ ] 희소 초기 질량 `sparse_nonzero_mass.irrigation` — 0.13
- [ ] 평가 행동 방식 (D9) — 최대확률
- [ ] 관수 효율 — 100 %
- [ ] 입력 상한 — 50 mm

### 9. 관수 값 점검 (2026-11-11, `MARS_reference` 기준) > 공급량별 규칙 정책 구속 비율 (4)

- [ ] 264 (이전) — 0.0 %
- [ ] 200 (현재) — 3.3 %
- [ ] 160 — 20.0 %
- [ ] 132 — 43.3 %

### 10. 공급량별 물 반응 (규칙 정책 πB) (9)

- [ ] 0 — 0.0
- [ ] 20 — 20.0
- [ ] 40 — 40.0
- [ ] 60 — 60.0
- [ ] 80 — 79.5
- [ ] 100 — 96.5
- [ ] 120 — 110.5
- [ ] 160 — 126.0
- [ ] 200 — 130.6

### 11. 단계별 규칙 기준선 탐색 (채택) (4)

- [ ] 평균 순수익 — 840.1
- [ ] 하위 10% 평균 — 606.6
- [ ] 평균 곡실 kg/ha — 7547
- [ ] 평균 관수 mm — 134.4

### 11. 단계별 규칙 기준선 탐색 (채택) > 단계별 규칙 기준 재측정 (4)

- [ ] 80 — 5905
- [ ] 120 — 7220
- [ ] 160 — 7748
- [ ] 200 — 7890

### 14. 공급량 재평가 (본 연구) (1)

- [ ] `scenarios.evaluation_supply_mm` — [120, 160]

### 15. 시비 값 점검 (2026-11-11, 진행 중) > 질소량별 반응 (규칙 정책, 질소 예산 해제) (6)

- [ ] 없음 — 0
- [ ] 45:27, 65:20, 85:10 — 57
- [ ] 45:54, 65:35, 85:27 (현재) — 116
- [ ] 40:27, 45:35, 80:54 (이전) — 116
- [ ] 45:80, 65:54, 85:40 — 174
- [ ] 45:80, 65:80, 85:80 — 240

### 15. 시비 값 점검 (2026-11-11, 진행 중) > 문헌 대조 (6)

- [ ] 시비 총량 상한 (예산) — 116 kg (91.64 USD)
- [ ] 질소 단가 — 0.79 USD/kg
- [ ] 시비 시기 — 45·65·85일
- [ ] 시비 작업비 — 5 USD/회
- [ ] 희소 초기 질량 — 0.03
- [ ] 입력 상한 — 200 kg/일

### 15. 시비 값 점검 (2026-11-11, 진행 중) > 시비 일정 탐색 (채택) (5)

- [ ] 총량 kg N/ha — 116
- [ ] 평균 순수익 — 886.4
- [ ] 하위 10% 평균 — 695.1
- [ ] 평균 곡실 kg/ha — 7821
- [ ] 평균 관수 mm — 147.8

### 16. 방제 구현·타당성·값 점검 (2026-11-11) > 현재 설정에서의 측정 (규칙 정책, 검증 80시즌) (5)

- [ ] 해충 없음 — 1094.2
- [ ] 규칙 (임계 0.3) — 998.1
- [ ] 임계 0.1 — 996.2
- [ ] 임계 0.5 — 995.8
- [ ] 무방제 — 789.0

### 16. 방제 구현·타당성·값 점검 (2026-11-11) > 타당성 판단 (7)

- [ ] DSSAT 잎 피해 전달 — 기술적으로 타당
- [ ] 날짜·외생 대응 — 타당
- [ ] 해충 개체군 — 정성적 모형
- [ ] 피해 시기 — 한계
- [ ] 조사 정보 — 낙관적
- [ ] 물×해충 상호작용 — 없음
- [ ] 연구 사용 범위 — 실험용

### 16. 방제 구현·타당성·값 점검 (2026-11-11) > 값 점검 (12)

- [ ] 유입 확률·크기 — 0.03, 0.05
- [ ] 증식률 범위 — 0.05~0.15/일
- [ ] 온도 기준 — 10, 30 °C (코드 고정, 설정 null)
- [ ] 살포 효능·잔효 — 0.8, 5일
- [ ] 피해 계수 α — 0.03
- [ ] 조사 잡음 — 0.01 (코드 고정, 설정 null)
- [ ] 조사 주기·창 — 7일, 7일 (코드 기본값)
- [ ] 방제 임계 — 0.3
- [ ] 살포비 — 35+15 = 50 USD/회
- [ ] 살포 예산 — 150 USD (3회)
- [ ] 살포 간격·단계 — 7일, istage 5 미만
- [ ] 희소 초기 질량 (살포) — 0.03

### 17. 방제 개선 (2026-11-11, 진행 중) > 3. 초기 적엽 반응 (가중치 불필요) (5)

- [ ] V2 33 % — 0.999
- [ ] V2 66 % — 0.999
- [ ] V4 33 % — 1.001
- [ ] V4 66 % — 1.000
- [ ] V6 66 % — 1.004

### 17. 방제 개선 (2026-11-11, 진행 중) > 2. 피해 계수 α (8)

- [ ] 0.03 — 81 %
- [ ] 0.02 — 69 %
- [ ] 0.015 — 59 %
- [ ] 0.01 — 45 %
- [ ] 0.0075 — 37 %
- [ ] 0.005 — 27 %
- [ ] 0.005 — 1031.2
- [ ] 0.01 — 1024.7

### 17. 방제 개선 (2026-11-11, 진행 중) > b0′ 여유 비율 (사용자 결정: 기준에 여유 두기) (9)

- [ ] 9조건 평균 — 887.5
- [ ] 하위 10 % — 490.7
- [ ] 초기·중기 20 % — 974.6
- [ ] 초기·중기 40 % — 873.0
- [ ] 초기·중기 60 % — 661.4
- [ ] 후기 20 % — 994.3
- [ ] 후기 40 % — 971.5
- [ ] 후기 60 % — 925.0
- [ ] 9조건 평균 / 하위 10 % — 878.8 / 433.4

### 17. 방제 개선 (2026-11-11, 진행 중) > 살포 효능 0.8·잔효 5일: 가정으로 유지 (2026-11-11 사용자 결정) (4)

- [ ] 맞는 자료를 찾지 못함 — 잎 살포 포장 시험의 살포 후 일자별 방제가(대조구 포함)가 필요하다. 2026-11-11 조사에서 검색 1회는 도구 정책 필터로 거부됐고, 후보 논문 2편(Sisay et al. 2019, Insects 10(2):45; Florida Entomologist
- [ ] 찾은 자료는 방식이 다름 — 검색된 잔효 자료는 대부분 종자 처리(잎 생물검정 16~46일 보호)로, 침투 이행 방식이라 잎 살포의 잔효로 쓸 수 없다
- [ ] 모형 단위 문제 — 모형의 밀도는 0~1 지수이고 문헌은 유충 수·감염주율·방제가(Henderson–Tilton 등)로 보고하므로, 자료가 있어도 환산 가정이 필요하다
- [ ] 결과 민감도는 확인됨 — 이전 진단(PEST_SURVEY_EFFICACY_SENSITIVITY.md)에서 효능 0.8 → 0.6으로 낮춰도 방제 규칙 비교의 차이가 모두 95 % 구간에 0을 포함했다

### 17. 방제 개선 (2026-11-11, 진행 중) > 해충 적엽과 물 절약 경로 (2026-11-11) (3)

- [ ] 없음 — 11.4
- [ ] 초기 40 % — 1.3
- [ ] 초기 60 % — 0.0

### 17. 방제 개선 (2026-11-11, 진행 중) > 방제 임계 재조정 (채택) (2)

- [ ] 평균 순수익 — 1022.6
- [ ] 평균 살포 — 1.52

### 18. 학습 설정 점검 B (2026-11-11, 진행 중) > B1 희소 초기 질량 (3)

- [ ] 관수 — 0.13
- [ ] 시비 — 0.03
- [ ] 살포 — 0.03

### 18. 학습 설정 점검 B (2026-11-11, 진행 중) > 시험 학습·처리량·수확지수 (A1·A2·A4·B2·B3) (8)

- [ ] 5만 — 370.5 / 670.2
- [ ] 15만 — 932.6 / 924.6
- [ ] 31만 — 876.9 / 885.5
- [ ] 36만 — 802.6 / 794.9
- [ ] 46만 — 813.9 / 830.3
- [ ] 51만 — 960.0 / 953.7
- [ ] 로그를 프로젝트 폴더에 기록 — 141.3
- [ ] 로그를 컨테이너 내부에 기록 — 139.9

### 18. 학습 설정 점검 B (2026-11-11, 진행 중) > B3 학습 설정 시험 (진행 중) (11)

- [ ] 5만 — 370.5 / 670.2
- [ ] 10만 — 159.3 / 115.7
- [ ] 15만 — 932.6 / 924.6
- [ ] 20만 — 824.8 / 863.2
- [ ] 26만 — 683.8 / 681.6
- [ ] 31만 — 876.9 / 885.5
- [ ] 36만 — 802.6 / 794.9
- [ ] 41만 — 874.9 / 895.1
- [ ] 46만 — 813.9 / 830.3
- [ ] 51만 — 960.0 / 953.7
- [ ] 마지막 4개 평균(최대확률) — 862.9

### 21. DSSAT 시나리오 값의 원 실험 대조 (2026-11-11) (14)

- [ ] 파종일, 이랑, 품종 — 1982-02-26, 61 cm, McCurdy 84AA
- [ ] 재식밀도 — 71,000 주/ha (7.1 주/m²)
- [ ] 생리적 성숙 — 관측 7월 4일
- [ ] 토양 수분 한계·초기 수분 — 0–5 cm LL 0.026, DUL 0.096, 초기 0.086 등(표 1)
- [ ] **저질소 처리 시비** — 4월 7일 27, 4월 12일 35 kg N/ha, 합계 62
- [ ] 시즌 무기화 — DSSAT-CERES가 무관수 저질소에서 35 kg N/ha 모의
- [ ] 관측 곡실 수량 — 무관수 2,929(62 N)·3,130(275 N), 관수 6,850·11,881, 영양기 스트레스 6,375·9,344 kg/ha
- [ ] 1 무관수·저질소 — 2929
- [ ] 2 무관수·고질소 — 3130
- [ ] 3 관수·저질소 — 6850
- [ ] 4 관수·고질소 — 11881
- [ ] 5 영양기 스트레스·저질소 — 6375
- [ ] 6 영양기 스트레스·고질소 — 9344
- [ ] RMSE / 평균 편향 (kg/ha)

## E. 진입 조건·미기록 범위·한계 (36)

학습 전 해결 대상이 아니거나 한계로 분류된 항목.

### 8. 아직 기록하지 않은 범위 (5)

- [ ] `configs/*.json` 17개 — 현장 검증 등급, 공개 연구 자료, 수확·탄소 측정 계약 등
- [ ] `docker/` 패치 — DSSAT 소스 패치와 이미지별 차이
- [ ] 진단용 스크립트 내부 상수 — `scripts/`의 감사·검증 스크립트
- [ ] DSSAT 전역 계수 — `MZCER048.SPE`, `DSSATPRO` 등 원본 파일
- [ ] WGEN 기상 입력 — UFGA 기상 파일과 월별 통계

### 19. 연구 진입 조건과 미기록 범위 점검 C (2026-11-11) > C1 진입 조건 현황 (7)

- [ ] whole_elemental_carbon_and_crop_soil_n_balance — 작물 재고·종자·동화·호흡·수확·피해 반출의 원소 C 미확인
- [ ] native_qf_n_partition_conservation — 고사엽 N 중복 문제 미해결
- [ ] harvest_n_candidate_domain_expansion — 무투입 등 넓은 범위에서 실제 반출 수지 미통과
- [ ] independent_agronomic_recovery — 단 B 판정 실패(V8·V13 99 % 적엽 칸)
- [ ] validation_tuned_baselines — 관수·시비·방제 규칙을 검증 시즌 탐색 + 별도 확인 시즌으로 채택(11·15·17절). 판정 스크립트의 미충족 목록은 고정 문자열이라 갱신되지 않았다
- [ ] fixed_reduction_calendar_and_preregistered_contrasts — 감축일·감축률 승인(D6), 사전등록 초안 갱신. 학습량 미정이라 동결 전
- [ ] independent_parameter_lineage — 품종·모형 계수의 독립 계보 미입증

### 19. 연구 진입 조건과 미기록 범위 점검 C (2026-11-11) > C4 미기록 범위 (17)

- [ ] actual_harvest_candidate_domain.json — 실제 반출 수확 후보 이미지의 검증 범위 기록
- [ ] agronomic_input_priorities.json — 공개 연구별 입력 확보 상태와 작업 순서
- [ ] agronomic_protocols.json — 공개 연구 처리 번역과 차단 요인
- [ ] agronomic_sources.json — 공개 근거 목록(연구 10편)
- [ ] balance_observability.json — 수지 항목별 관측 가능 여부
- [ ] carbon_measurement_contract.json — 원소 C 측정 계약과 금지 추론
- [ ] damage_recovery_tier_b.json — 단 B 동결 기준
- [ ] evidence_qualifications.json — 실행별 근거 자격 기록
- [ ] faw_technical_sensitivity.json — 해충 계수 합성 민감도 설정
- [ ] field_calibration_candidate_screen.json — 현장 보정 후보 선별 결과
- [ ] field_validation_tiers.json — 현장 검증 3단 기준
- [ ] harvest_n_candidate_domain.json — 수확 N 후보 이미지의 검증 범위
- [ ] lirf_translation_contract.json — LIRF 입력 변환 계약
- [ ] oveysi2010_input_dossier.json — Oveysi 2010 재현 입력 명세
- [ ] oveysi2010_table4_grain.json — Oveysi 2010 표 4 곡실 수량
- [ ] rahman2022_marginal_grain.json — Rahman 2022 주변평균 곡실
- [ ] santos2018_table1_productivity.json — Santos 2018 표 1 생산성

### 20. 진입 조건 재분류 (2026-11-11 결정) > 재분류 전 제안 표 (7)

- [ ] 전체 원소 C와 작물–토양 N — 작물 C 항목 6개와 수확·휴경·재초기화까지 C/N 수지가 닫힘
- [ ] 네이티브 Q/F N 배분 — 다년 연속(Q/F) 모드에서 반출·고사물·잔사 N이 한 번씩 계상
- [ ] 수확 N 후보 적용 범위 — 후보 이미지에서 무투입·실패·다년 등의 실제 반출 검증
- [ ] 독립 피해·회복 (단 B) — 보정에 쓰지 않은 포장의 피해–수량 반응 재현
- [ ] 검증용 기준 정책 튜닝 — 관수·방제 임계, η, GAE λ 후보 비교
- [ ] 감축일 달력과 사전 대비의 확정 — 감축 설정·대비를 최종 시험 전 동결
- [ ] 독립 매개변수 계보 — 평가 관측이 계수 선정에 쓰이지 않았음을 입증

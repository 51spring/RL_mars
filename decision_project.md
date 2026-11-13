# MARS 프로젝트 변수·값 결정 기록

시작일 2026-11-11. 제안서 PDF가 아니라 **현재 코드·설정·실행 이미지의 실제 값**을 기록한다. 항목별로 확인하면서 `확인` 칸을 채우고, 결정이 바뀌면 값과 아래 변경 이력을 함께 고친다.

- **성격:** `설계`는 프로젝트 초기 설계값, `지시`는 2026-11-10 비교 실험 지시, `측정`은 규칙 정책 측정값, `가정`은 구현 가정, `미보정`은 근거 자료로 보정되지 않은 값, `원본`은 DSSAT·라이브러리 원본 값이다.
- **반영:** `읽음`은 학습·평가 경로가 설정값을 실제로 읽는다는 뜻이다. `미사용`은 설정에 적혀 있어도 그 값을 바꿔서는 동작이 바뀌지 않는다는 뜻이다.
- **확인:** `[ ]` 미확인, `[x]` 확인 완료, `[!]` 변경 필요. 확정된 값은 <mark>형광펜</mark>으로 표시한다.

## 0. 먼저 결정할 항목

| # | 항목 | 현재 상태 | 확인 |
|---|---|---|---|
| D1 | 해충 온도 하한·상한 | **해결(2026-11-11):** 설정 10·30 °C를 학습·평가가 읽는다(가정, 17절) | [x] |
| D2 | 조사 잡음 표준편차 | **해결(2026-11-11):** 설정 0.01을 읽는다(가정). 민감도 0.05 추가 | [x] |
| D3 | 해충 계수·조사 주기의 설정값 | **해결(2026-11-11):** 해충 계수는 설정에서 읽는다. 조사 주기·창은 7일이 아니면 실행을 거부한다 | [x] |
| D4 | 무투입 대조 | <mark>**결정(2026-11-11): 비교 실험 결과표에서 제외.** 정책 클래스(`NoInputPolicy`)는 코드에 그대로 둔다</mark> | [x] |
| D5 | 살포 횟수 상한 | **결정(2026-11-11): 막는다. 별도 횟수 상한 없이 살포 예산 150 USD(회당 50 USD)로 시즌 3회까지.** 예산 배율이 1.0 고정이라 예산과 횟수 상한이 같은 일을 한다. 7일 간격·istage 5 미만 조건도 그대로다. 규칙 정책은 시즌 평균 약 0.7회를 쓴다(검증 16·60시즌, 23절) | [x] |
| D6 | 학습 감축일 구간·평가 3시점 | **승인(2026-11-11): 학습 13~112일, 평가 13·37·83일.** 단계별 규칙 기준에서도 단계 진입일이 같았다 | [x] |
| D7 | GAE λ | **결정(2026-11-11): 0.95 유지.** 시험 학습에서 0.98은 무관수 붕괴가 여러 번 났다(18절) | [x] |
| D8 | 보상 계수 η | **결정(2026-11-11): 0.45 유지.** 측정 수확지수 0.514이지만 잠재함수 보정이라 최적 정책을 바꾸지 않는다(18절) | [x] |
| D9 | 평가·동결망 행동 방식 | **결정(2026-11-11): 최대확률 행동.** 평가와 동결망 모두 `deterministic_policy: true`. 256·256·10 시험 학습에서 최대확률이 확률 행동보다 꾸준히 높았고 무관수 붕괴가 없었다(18절 B3) | [x] |
| D10 | 정책 4의 학습 시즌·학습량 | 1,500만 단계에 약 11만 3천 시즌이 필요하고 고유 시즌은 89,998개라 약 20%를 재사용한다. **2026-11-11 임의 제안: 500만 × 10시드는 너무 길다. 100만 × 10시드와 200만 × 5시드를 비교 중**(18절 D10 비교). 두 안 모두 재사용이 없다 | [ ] |
| D11 | 규칙 함수 기본값 | **해결(2026-11-11):** `RulePolicy` 기본 시비를 새 일정 {45:80, 65:54, 95:27}로 바꿨다. 관수 단계 규칙·방제 임계 기본값은 아직 옛 값(0.3, 10 mm, 조사 0.3)이고 비교 실험은 설정값을 쓴다 | [x] |
| D12 | 시즌 물 공급량과 감축의 구속력 | <mark>**결정(2026-11-11): 공급량 200 mm.** 264 mm에서는 20% 감축이 규칙 정책 시즌의 0.8%에만 영향을 줬다. 9절</mark> | [x] |
| D13 | 검증 게이트 값 | **결정(2026-11-11): `dssat_state_read` false → true.** 제안서 11쪽 "상태 읽기"의 날짜·필수 변수·토양층 집계·최종 곡실량·기상 시점이 각각 다른 이름의 검사로 통과했다. `live_leaf_damage_write: false`는 연구용 잎 피해 쓰기 판정으로 유지한다. 코드는 이 키들을 읽지 않는다 | [x] |
| D14 | 평가 감축일 방식 | <mark>**결정(2026-11-11): 평가는 13·37·83일 고정 유지.** 학습은 13~112일 랜덤이다. πB는 13일과 37일 결과가 같지만 C2(초기 대 후기) 계산에는 영향이 없다</mark> | [x] |
| D15 | 예산 배율 | <mark>**결정(2026-11-11): 0.6·1.4 제거, 학습·평가 모두 1.0.** 예산 민감도를 보려면 다시 표집하거나 재학습해야 한다</mark> | [x] |
| D16 | 단계별 규칙의 공급 구속 | <mark>**결정(2026-11-11): 200 mm 유지.** 새 πB는 시즌 평균 151.8 mm를 써서 감축 없이도 시즌의 11.7%가 200 mm 한도에 닿지만, 공급 160 mm와 200 mm의 순수익 차이는 8.8 USD/ha다</mark> | [x] |

## 1. 시뮬레이터 (DSSAT 시나리오)

실제 입력은 이미지 안의 `gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2`다. 이미지 안의 `/opt/dssat_pdi/Maize/UFGA8201.MZX`와는 초기조건일·모의 시작일이 다르다(82056 대 82030).

| 변수 | 현재값 | 위치 | 성격 | 확인 |
|---|---|---|---|---|
| DSSAT 실행 모드 | `mode="all"` (관수·시비 외부 입력, 파종 고정) | `dssat_backend.py` `DssatBackend.reset` | 원본 | [x] |
| 시나리오 | UFGA8201, Gainesville FL, 필드 UFGA0002 | FileX | 원본 | [x] |
| 처리 번호 | 3 (IRRIGATED LOW NITROGEN 행. 관수·시비 일정은 외부 입력으로 대체) | `env_config.yml` | 원본 | [x] |
| 위도, 경도, 고도 | 29.6380, −82.3689, 40 m | FileX, `input_metadata.py` (원본의 경위도 칸 뒤바뀜 보정) | 가정 | [x] |
| 작물·품종 | 옥수수, IB0035 McCurdy 84aa | FileX | 원본 | [x] |
| 품종 계수 P1, P2, P5, G2, G3, PHINT | 265.0, 0.300, 920.0, 920.0, 8.00, 43.00 | `MZCER048.CUL` | 원본 | [x] |
| 생태형 | IB0001 GENERIC MIDWEST1 | `MZCER048.CUL` | 원본 | [x] |
| 생태형 TBASE, TOPT, ROPT, P20, DJTI, GDDE, DSGFT, RUE, KCAN | 8.0, 34.0, 34.0, 12.5, 4.0, 6.0, 170, 4.2, 0.85 | `MZCER048.ECO` | 원본 | [x] |
| 토양 | IBMZ910014 Millhopper Fine Sand, 깊이 180 cm | `SOIL.SOL` | 원본 | [x] |
| 토양 표층 SALB, SLU1, SLDR, SLRO, SLNF, SLPF | 0.18, 2.0, 0.65, 60.0, 1.00, 0.92 | `SOIL.SOL` | 원본 | [x] |
| 모의 시작일, 초기조건일 | 1982년 30일 | FileX | 원본 | [x] |
| 파종일 | 1982년 57일 (`planting_yrdoy` 1982057) | FileX, `dssat_backend.py` | 원본 | [x] |
| 재식밀도 | 7.2 주/m² | FileX | 원본 | [x] |
| 이랑 폭, 파종 깊이 | 61 cm, 7 cm | FileX | 원본 | [x] |
| 초기 잔사 ICRES, ICREN | 1000 kg/ha, 0.8 % | FileX | 원본 | [x] |
| 수확 | 성숙기 수확 (HARVS M), 수확 종료 한계 83057 | FileX | 원본 | [x] |
| 기상 | WTHER W, WGEN 확률 기상 (`random_weather=True` 코드 고정) | `dssat_backend.py` | 원본 | [x] |
| 시뮬레이터 입력 상한 | 관수 50 mm, 질소 200 kg/ha | `DssatBackend.step` | 원본 | [x] |
| 관수 효율 EFIR, IREFF | 1, 1 (넣은 물이 전량 토양에 도달) | FileX | 원본 | [x] |
| FileX 자동관수 계수 (mode all에서는 미사용) | IMDEP 30 cm, ITHRL 50 %, ITHRU 100 %, IRAMT 10 mm | FileX | 원본 | [x] |
| 생육 실패 판정 | WARNING.OUT의 실패 문구 3종이면 매출 0 | `classify_terminal` | 설계 | [x] |
| 곡실 수량 | Summary.OUT `HWAH` (kg/ha) | `classify_terminal` | 원본 | [x] |
| 실행 이미지 | `mars-dssat:ppo-cpu-metadata` (sha256:11e2650fed75…) | Docker | 설계 | [x] |
| 라이브러리 | sb3-contrib 2.7.1, stable-baselines3 2.7.1, torch 2.5.1+cpu, gymnasium 1.2.2 | 이미지 | 원본 | [x] |

### 토양층

| 깊이 cm | 하한 SLLL | 상한 SDUL | 포화 SSAT | 뿌리 SRGF | 용적밀도 SBDM | 유기탄소 SLOC | 초기 수분 SH2O | 초기 NH4 | 초기 NO3 | 확인 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 5 | 0.026 | 0.096 | 0.230 | 1.000 | 1.30 | 2.00 | .086 | .5 | .1 | [x] |
| 15 | 0.025 | 0.086 | 0.230 | 1.000 | 1.30 | 1.00 | .086 | .5 | .1 | [x] |
| 30 | 0.025 | 0.086 | 0.230 | 0.700 | 1.40 | 1.00 | .086 | .5 | .1 | [x] |
| 60 | 0.025 | 0.086 | 0.230 | 0.300 | 1.40 | 0.50 | .086 | .5 | .1 | [x] |
| 90 | 0.028 | 0.090 | 0.230 | 0.050 | 1.45 | 0.10 | .076 | .6 | .1 | [x] |
| 120 | 0.028 | 0.090 | 0.230 | 0.030 | 1.45 | 0.10 | .076 | .5 | .1 | [x] |
| 150 | 0.029 | 0.130 | 0.230 | 0.002 | 1.45 | 0.04 | .13 | .5 | .1 | [x] |
| 180 | 0.070 | 0.258 | 0.360 | 0.000 | 1.20 | 0.24 | .258 | .5 | .1 | [x] |

### 1절 점검 (2026-11-11)

**원본 대조.** 위 값을 실행 이미지 안의 파일과 하나씩 대조했고 모두 같다: `gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2`(FileX 템플릿), `/opt/dssat_pdi/Genotype/MZCER048.CUL` 98행, `MZCER048.ECO` 22행, `/opt/dssat_pdi/Soil/SOIL.SOL` 481~494행, `/opt/dssat_pdi/Weather/Climate/UFGA.CLI`. 원 실험 대조는 21절.

| 항목 | 점검 결과 | 판정 | 확인 |
|---|---|---|---|
| 위치 | 필드 29.638, −82.369, 40 m. 토양 파일 29.630, −82.370, 기후 파일 29.63, −82.37. Gainesville와 일치 | 유지 | [x] |
| 품종 IB0035 | CUL 머리 주석: UFGA8201 품종의 P1을 DSSAT v3 전환 때 **이 실험으로 다시 보정**했고(Bowen 1994), G2는 RUE 변경으로 1.1배 했다. 21절의 "UFGA8201은 보정에 쓰였을 수 있다"가 사실로 확인됐다. 독립 매개변수 계보 한계(20절)의 근거 | 유지, 한계 근거 추가 | [x] |
| 생태형 IB0001 | 일반 중서부 생태형. 플로리다 전용 값은 아니다. 성숙일은 관측과 2일 차이(21절) | 유지 | [x] |
| 토양 | Millhopper fine sand(Arenic Paleudult). 0~150 cm 모래(DUL 0.086~0.13), 150~180 cm 점토 집적층(DUL 0.258). SLPF 0.92는 토양 비옥도 계수(생장 8 % 감소)로 원본 값 | 유지 | [x] |
| 모의 시작일 | 82030, 파종 27일 전. 배포 MZX(82056)와 다르지만 초기 무기질소 차이는 수량 영향 없음(21절) | 유지 | [x] |
| 재식밀도 | 7.2 주/m², 논문 7.1 | 유지 (차이 1.4 %) | [x] |
| 기상 | WGEN 확률 기상. 월 통계는 `UFGA.CLI`(1958년부터 49년 일 자료로 계산). 학습·검증·시험 시즌마다 다른 WGEN 시드 | 유지 | [x] |
| CO₂ | 모의 옵션 CO2 = M(연도별 실측). 모의 연도가 1982년으로 고정이라 약 341 ppm이다(현재 약 420 ppm). 옥수수는 C4라 CO₂ 비료 효과가 작다(해석) | 유지, 한계로 명시 | [x] |
| 모형 선택 | 증발산 Priestley–Taylor(R), 침투 SCS(S), 광합성 RUE(R), 토양 유기물 Godwin(G) — 템플릿 원본 | 유지 | [x] |
| 입력 상한 50 mm·200 kg | 행동 격자 최대 25 mm·80 kg이라 구속하지 않는다 | 유지 | [x] |
| 관수 효율 1 | 9절에서 유지·한계로 결정 | 유지 | [x] |
| 수확 | 성숙기 수확(HARVS M), 수확 한계 83057 | 유지 | [x] |
| **곡실 수량 HWAH 단위** | DSSAT `DATA.CDE`: HWAH는 **건물 기준(kg [dm]/ha)**. 단가 0.158 USD/kg은 Tao 2023에서 가져온 값(`MARS_LITERATURE_CROSSWALK.md`)이다. 곡물 시장 가격은 보통 수분 15.5 % 기준이라, 건물 수량에 그대로 곱하면 매출이 시장 기준보다 약 15.5 % 낮다(같은 kg이면 건물 1 kg = 시장 기준 1.183 kg). 매출이 낮으면 관수·시비의 경제적 최적량이 낮아진다 | **결정(2026-11-12, 임의): 수분 15.5 % 기준으로 환산.** 매출 = HWAH / (1 − 0.155) × 0.158 = HWAH × 0.187 USD. 잠재함수 Φ도 같은 단가. 모든 단가 읽기를 `mars_env.economics.grain_price`로 모았다. 규칙 기준선(관수·시비·방제·b0′)과 질소 예산을 다시 탐색한다(24절) | [x] |
| 생육 실패 판정 | WARNING.OUT의 실패 문구 3종일 때만 매출 0. 단계 6만으로는 실패로 보지 않는다 | 유지 | [x] |
| 실행 이미지·라이브러리 | 학습·평가 모두 같은 이미지 | 유지 | [x] |

## 2. 환경 설정 (`configs/proposal_v2.yaml`)

| 변수 | 현재값 | 단위·설명 | 성격 | 반영 | 확인 |
|---|---|---|---|---|---|
| `source.proposal` | docs/proposal_revised.pdf | 기록용 | 설계 | 미사용 | [x] |
| `source.revised` | 2026-11-05 | 기록용 | 설계 | 미사용 | [x] |
| `source.status` | metadata_corrected_runtime_verified_harvest_boundary_mapped_agronomic_validation_pending | 기록용 | 설계 | 미사용 | [x] |
| `environment.backend` | dssat | 코드 고정 | 설계 | 미사용 | [x] |
| `environment.runtime_profile` | metadata_corrected | 이미지 환경변수가 결정 | 설계 | 미사용 | [x] |
| `environment.mode` | all | 코드 고정 | 설계 | 미사용 | [x] |
| `environment.scenario` | UFGA8201 | 코드 고정 | 설계 | 미사용 | [x] |
| `environment.random_weather` | true | 코드 고정 | 설계 | 미사용 | [x] |
| `environment.frame_size` | 28 | 하루 관측 변수 수 (이전 45, 22절) | 설계 | 미사용 | [x] |
| `environment.history_days` | 7 | 일 | 설계 | 미사용 | [x] |
| `environment.observation_size` | 196 | 28×7 (이전 315) | 설계 | 미사용 | [x] |
| `environment.action_nvec` | [6, 9, 2] | 관수·시비·방제 선택지 수 | 설계 | 일치 검사 | [x] |
| `environment.mask_size` | 17 | 6+9+2 | 설계 | 미사용 | [x] |
| `environment.irrigation_grid_mm` | [0, 5, 10, 15, 20, 25] | mm/일 | 설계 | 읽음 | [x] |
| `environment.nitrogen_grid_kg_ha` | [0, 10, 20, 27, 35, 40, 54, 60, 80] | kg N/ha/일 | 설계 | 읽음 | [x] |
| `environment.required_nitrogen_values` | [0, 27, 54, 80] | 새 πB 일정 재현용 값 (이전 [0, 10, 27, 35, 54]) | 측정 | 미사용 | [x] |
| `environment.pest_enabled` | true | 연구용 해충 실행은 코드가 거부, 실험용 클래스를 사용 | 설계 | 미사용 | [x] |
| `environment.require_live_leaf_damage_writer` | true | | 설계 | 미사용 | [x] |
| `environment.initial_water_mm` | <mark>200.0</mark> | 시즌 물 공급량 mm (이전 264.0) | 지시 | 읽음 | [x] |
| `economics.grain_usd_kg` | 0.158 | USD/kg, 시장 가격(수분 15.5 % 기준, Tao 2023) | 설계 | 읽음 | [x] |
| `economics.grain_moisture_fraction` | 0.155 | 시장 가격의 수분 기준. 건물 기준 단가 = 0.158 / 0.845 = 0.187 USD/kg (1절, 2026-11-12) | 결정 | 읽음 | [x] |
| `economics.water_usd_mm_ha` | <mark>1.17 (이전 1.1)</mark> | USD/mm/ha. Alabama 2026 예산서 $12/acre-inch (27절) | 측정 | 읽음 | [x] |
| `economics.nitrogen_usd_kg` | <mark>1.83 (이전 0.79)</mark> | USD/kg N. USDA AMS Alabama 질산암모늄 2025년 평균 (27절) | 측정 | 읽음 | [x] |
| `economics.spray_product_usd_ha` | <mark>24.7 (이전 35.0)</mark> | USD/ha. Alabama 2026 예산서 살충제 $10/acre (27절) | 측정 | 읽음 | [x] |
| `economics.spray_labor_usd_ha` | <mark>24.7 (이전 15.0)</mark> | USD/ha. 살포 1회 합계 49.4. Alabama 2026 예산서 항공 살포 $10/acre (27절) | 측정 | 읽음 | [x] |
| `economics.irrigation_labor_usd_event_ha` | <mark>2.04 (이전 3.0)</mark> | USD/회/ha. LSU 2025 고랑 관수 노동 (27절) | 측정 | 읽음 | [x] |
| `economics.nitrogen_labor_usd_event_ha` | <mark>34.8 (이전 5.0)</mark> | USD/회/ha. Iowa 2026 액비 곁거름 (27절) | 측정 | 읽음 | [x] |
| `economics.budgets_usd_ha.nitrogen` | <mark>441.03 (이전 190.39)</mark> | USD/ha, (161+80)×1.83 (27절) | 측정 | 읽음 | [x] |
| `economics.budgets_usd_ha.spray` | 150.0 | USD/ha, 3회분(1회 49.4, 4회째 197.6은 막힘) | 설계 | 읽음 | [x] |
| `economics.budget_multipliers` | <mark>[1.0]</mark> | 예산 배율 제거, 학습·평가 모두 1.0 (이전 [0.6, 1.0, 1.4]) | 지시 | 읽음 | [x] |
| `pest.arrival_probability` | 0.03 | 일별 유입 확률 | 미보정 | 읽음 | [ ] |
| `pest.arrival_amplitude` | 0.05 | 유입 시 밀도 증가 | 미보정 | 읽음 | [ ] |
| `pest.growth_low` | 0.05 | 일 증식률 하한 | 미보정 | 읽음 | [ ] |
| `pest.growth_high` | 0.15 | 일 증식률 상한 | 미보정 | 읽음 | [ ] |
| `pest.temperature_low_c` | 10 | Du Plessis 2020 발육 하한 12~13 °C보다 낮음. 코드 고정값을 옮김 | 가정 | 읽음 | [x] |
| `pest.temperature_high_c` | 30 | Du Plessis 2020 발육 최적 26~30 °C의 상한. 코드 고정값을 옮김 | 가정 | 읽음 | [x] |
| `pest.efficacy` | 0.8 | 살충 효과. 제안서 초기 가정, 근거 자료 없음 (17절) | 가정 | 읽음 | [x] |
| `pest.residual_days` | 5.0 | 잔효 시상수, 일. 제안서 초기 가정, 근거 자료 없음 (17절) | 가정 | 읽음 | [x] |
| `pest.alpha` | 0.01 | 밀도 1일 때 일 잎 손실 비율. 문헌 범위 맞춤 (17절, 이전 0.03) | 가정 | 읽음 | [x] |
| `pest.survey_noise_std` | 0.01 | 자료 없음. 코드 고정값을 옮김 | 가정 | 읽음 | [x] |
| `management.spray_interval_days` | 7 | 살포 최소 간격, 일 | 설계 | 읽음 | [x] |
| `management.spray_istage_exclusive_upper` | 5 | istage 5 미만에서만 살포 | 설계 | 읽음 | [x] |
| `management.input_closed_istage` | 6 | 생리적 성숙~수확에 관수·시비 마스크 (23절) | 설계 | 읽음 | [x] |
| `management.survey_interval_days` | 7 | 일. 7이 아니면 실행 거부(D3) | 설계 | 읽음 | [x] |
| `management.survey_window_days` | 7 | 일. 7이 아니면 실행 거부(D3) | 설계 | 읽음 | [x] |
| `management.baseline_nitrogen.45` | 80 | 파종 후 45일, kg N/ha (이전 54) | 측정 | 읽음 | [x] |
| `management.baseline_nitrogen.65` | 54 | 파종 후 65일, kg N/ha (이전 35) | 측정 | 읽음 | [x] |
| `management.baseline_nitrogen.95` | 27 | 파종 후 95일, kg N/ha (이전 85일 27) | 측정 | 읽음 | [x] |
| `baseline_policy.water_stress_threshold` | 0.3 | 스트레스 지수(1−SWFAC) 임계. 단계 3·4·5 밖(1·2단계)에만 적용되고 그 단계 관수는 시즌 평균 0.2 mm라 재탐색 대상이 아님(24절) | 지시 | 읽음 | [x] |
| `baseline_policy.irrigation_mm` | 10 | 요청 관수량 mm. 단계 3·4·5 밖(1·2단계)에만 적용되고 그 단계 관수는 시즌 평균 0.2 mm라 재탐색 대상이 아님(24절) | 지시 | 읽음 | [x] |
| `baseline_policy.survey_threshold` | 0.7 | 조사값 임계 (이전 0.3). 방제 임계 탐색 채택 (17절) | 측정 | 읽음 | [x] |
| `baseline_policy.stage_water` | [[3, 0.5, 20], [4, 0.05, 20], [5, 0.3, 15]] | (istage, 스트레스 임계, 관수 mm). 나머지 단계는 위 기본값. 2026-11-12 재탐색 채택(24절, 이전 [[3, 0.5, 15], [4, 0.1, 20], [5, 0.2, 15]]) | 측정 | 읽음 | [x] |
| `reduction_response_rule.reserve_mm` | 78.0 | b0′ 개화·등숙기 예비 mm (단계 4·5 평균 관수 32.3+45.7, 24절. 이전 83.5) | 측정 | 읽음 | [x] |
| `reduction_response_rule.flowering_day` | 83 | 파종 후 일수 (단계 4 평균 진입 82.6, 24절) | 측정 | 읽음 | [x] |
| `reduction_response_rule.maturity_day` | 130 | 파종 후 일수 (단계 6 평균 진입 130.4, 24절) | 측정 | 읽음 | [x] |
| `reduction_response_rule.event_interval_days` | 10.0 | 일 (47.8일 / 4.78회, 24절. 이전 9.4) | 측정 | 읽음 | [x] |
| `reduction_response_rule.remaining_demand_mm` | [[0, 171.5], [42, 171.3], [83, 78.0], [93, 45.7], [130, 0.0]] | (파종 후 일수, πB 남은 평균 수요 mm), 24절 재측정 | 측정 | 읽음 | [x] |
| `reduction_response_rule.demand_margin` | 0.4 | 남은 물이 (0.4 × 남은 수요) 미만일 때만 예비 적용. 검증 시즌 탐색 | 측정 | 읽음 | [x] |
| `reward_shaping.enabled` | true | 잠재함수 보조 보상 | 설계 | 읽음 | [x] |
| `reward_shaping.scale` | 1000.0 | 학습 보상 나눗수 | 설계 | 읽음 | [x] |
| `reward_shaping.gamma` | 1.0 | | 설계 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.1` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.2` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.3` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.4` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.5` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.6` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.7` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.8` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.9` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `reward_shaping.eta_by_stage.10` | 0.45 | D8 | 가정 | 읽음 | [x] |
| `training.algorithm` | MaskablePPO | 코드 고정 | 설계 | 미사용 | [x] |
| `training.gamma` | 1.0 | | 설계 | 읽음 | [x] |
| `training.gae_lambda` | 0.95 | D7 | 가정 | 읽음 | [x] |
| `training.gae_lambda_candidates` | [0.95, 0.98] | D7 | 설계 | 미사용 | [x] |
| `training.policy_layers` | [256, 256] | | 설계 | 읽음 | [x] |
| `training.value_layers` | [256, 256] | | 설계 | 읽음 | [x] |
| `training.n_envs` | 8 | 학습 병렬 환경 수. 18절 B3 결정(4 → 8) | 설계 | 읽음 | [x] |
| `training.checkpoint_selection.first_season` | 1200 | 체크포인트 선택용 검증 시즌 시작 (25절, 2026-11-13) | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.seasons` | 32 | 선택용 시즌 수 (1200~1231) | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.workers` | 4 | 선택 평가 프로세스 수 (학습 환경과 동시에 돌아 메모리 고려) | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.weights_a.none` | 1.0 | a 정책 선택 기준: 감축 없음 | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.weights_b.none` | 0.25 | b 정책 선택 기준 가중 | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.weights_b.early_40` | 0.25 | 〃 | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.weights_b.mid_40` | 0.25 | 〃 | 결정 | 읽음 | [ ] |
| `training.checkpoint_selection.weights_b.late_40` | 0.25 | 〃 (감축 확률 0.75를 세 시점에 나눔) | 결정 | 읽음 | [ ] |
| `training.checkpoint_steps` | 102400 | 적합 중간 저장 간격. 중단 시 마지막 저장 지점부터 재개 | 설계 | 읽음 | [x] |
| `training.n_steps` | 256 | 환경당 롤아웃 길이. 18절 B3 시험 학습 비교로 결정 | 시험 학습 | 읽음 | [x] |
| `training.batch_size` | 256 | 18절 B3 | 시험 학습 | 읽음 | [x] |
| `training.n_epochs` | 10 | 18절 B3 | 시험 학습 | 읽음 | [x] |
| `training.deterministic_policy` | true | D9 | 가정 | 읽음 | [x] |
| `training.timesteps_per_seed` | 5000000 | 정책 1·2·3 각각, 정책 4는 3배 | 설계 | 읽음 | [ ] |
| `training.seeds` | [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] | | 설계 | 읽음 | [ ] |
| `training.sparse_nonzero_mass.irrigation` | 0.13 | 초기 비영 행동 확률 | 설계 | 읽음 | [ ] |
| `training.sparse_nonzero_mass.nitrogen` | 0.03 | | 설계 | 읽음 | [ ] |
| `training.sparse_nonzero_mass.spray` | 0.03 | | 설계 | 읽음 | [ ] |
| `training.device` | cpu | 코드 고정 | 설계 | 미사용 | [x] |
| `scenarios.reduction_probability` | 0.75 | b 정책 학습. a 정책은 코드에서 0 | 지시 | 읽음 | [x] |
| `scenarios.timing` | calendar_day | stage_entry는 보조 분석 | 지시 | 읽음 | [x] |
| `scenarios.training_day_range_inclusive` | [13, 112] | 파종 후 일수, 승인 (D6) | 측정 | 읽음 | [x] |
| `scenarios.evaluation_days.early` | 13 | 승인 (D6) | 측정 | 읽음 | [x] |
| `scenarios.evaluation_days.mid` | 37 | 승인 (D6) | 측정 | 읽음 | [x] |
| `scenarios.evaluation_days.late` | 83 | 승인 (D6) | 측정 | 읽음 | [x] |
| `scenarios.evaluation_beta` | 1.0 | 평가 예산 배율 | 설계 | 읽음 | [x] |
| `scenarios.bootstrap_replicates` | 10000 | | 지시 | 읽음 | [x] |
| `scenarios.sensitivity_seasons_per_condition` | 300 | 민감도 재평가 시즌 수 (본 표 앞쪽 시즌). 5절 평가 시간 결정 | 결정 | 읽음 | [x] |
| `scenarios.sensitivity_rows` | [a, b_none, b_cut] | 민감도에서 평가하는 행. a-유 제외 | 결정 | 읽음 | [x] |
| `scenarios.evaluation_workers` | 8 | 평가 프로세스 수 (이전 코드 상수 4) | 결정 | 읽음 | [x] |
| `scenarios.announcement_istages` | [1, 2, 4] | stage_entry 전용 | 설계 | 보조 분석만 | [x] |
| `scenarios.delay_days_inclusive` | [0, 5] | stage_entry 전용, 일 | 설계 | 보조 분석만 | [x] |
| `scenarios.training_reduction_range` | [0.1, 0.7] | 균등 표집 | 지시 | 읽음 | [x] |
| `scenarios.evaluation_reductions` | [0.2, 0.4, 0.6] | 승인. 단계별 규칙 기준 감축 후 160·120·80 mm가 시즌의 37.5·80.8·97.5 %를 구속 | 지시 | 읽음 | [x] |
| `scenarios.evaluation_seasons_per_condition` | 1000 | 공통 시즌 수 | 지시 | 읽음 | [x] |
| `scenarios.evaluation_delay_days` | 3 | stage_entry 전용, 일 | 설계 | 보조 분석만 | [x] |
| `scenarios.reduction_contract` | remaining_fraction | 남은 물에 비례 감축 | 설계 | 읽음 | [x] |
| `reproducibility.weather_seed_version` | 1 | | 설계 | 읽음 | [x] |
| `reproducibility.split_seeds.train` | 11001 | | 설계 | 읽음 | [x] |
| `reproducibility.split_seeds.validation` | 22001 | | 설계 | 읽음 | [x] |
| `reproducibility.split_seeds.test` | 33001 | | 설계 | 읽음 | [x] |
| `reproducibility.streams` | [weather, pest_arrival, survey_noise, reduction, budget] | 실제 ID는 코드 | 설계 | 미사용 | [x] |
| `reproducibility.paired_external_seasons` | true | | 설계 | 미사용 | [x] |

### 2절 점검 (2026-11-12)

- **값 대조:** 설정 파일 잎 151개와 이 표가 모두 같다(형광펜 표시는 서식 차이).
- **코드 사용 대조:** 키마다 `src/mars_env`와 비교 실험 스크립트 8개에서 읽는 곳을 찾았다. `baseline_policy`·`reduction_response_rule`·`pest`는 묶음으로 넘겨 읽고(`**config[...]`, `from_config`), `evaluation_days`는 시점 사전으로 읽는다. `management.survey_interval_days/window_days`는 "미사용"으로 적혀 있었으나 실제로는 읽고 7이 아니면 실행을 거부해 고쳤다. "미사용" 행(`source.*`, `environment.backend/mode/scenario/random_weather/frame_size/history_days/observation_size/mask_size/pest_enabled/require_live_leaf_damage_writer`, `training.algorithm/device/gae_lambda_candidates`, `reproducibility.streams/paired_external_seasons`)은 실제로 읽지 않는 기록용이다.
- **표시:** `[x]` 확인, `[!]` 15.5 % 가격 환산 뒤 **재탐색 중**(관수 단계 규칙·시비 일정·질소 예산·방제 임계·b0′ 값, 24절), `[ ]` 미결:
  - ~~살포 자재비·작업비 35·15 USD, 관수·시비 작업비 3·5 USD: 값의 출처가 기록에 없다.~~ 2026-11-13 출처 있는 값으로 교체(27절).
  - 해충 유입 확률·크기, 증식률 범위: 가정이며 결정이 아직 없다.
  - `training.timesteps_per_seed`, `training.seeds`: D10 결정 대기.
  - 희소 초기 확률 3개: 18절 B1, 시험 학습 결과 뒤 결정.

## 3. 코드에 고정된 값

| 변수 | 현재값 | 위치 | 성격 | 확인 |
|---|---|---|---|---|
| 해충 온도 하한·상한 | ~~코드 고정~~ → 설정 `pest.temperature_low_c/high_c` (10, 30 °C)에서 읽음 (D1, 2026-11-11) | `pests.py` `pest_settings` | 미보정 | [x] |
| 조사 잡음 표준편차 | ~~코드 고정~~ → 설정 `pest.survey_noise_std` (0.01)에서 읽음 (D2) | `pests.py` `pest_settings` | 미보정 | [x] |
| 조사 주기·창 | 7일, 7일. 설정값이 7이 아니면 실행 거부 (D3) | `pests.py` | 미보정 | [x] |
| 증식률 g(T) | growth_low + (growth_high − growth_low)×(T−T하한)/(T상한−T하한), 구간 밖은 끝값 고정. 현재 0.05 + 0.10×(T−10)/20 | `pests.py` `growth` | 미보정 | [x] |
| 살포 효과 | 효능×exp(−경과일/잔효일). 현재 0.8×exp(−경과일/5), 마지막 살포 기준, 누적 없음 | `pests.py` `advance` | 미보정 | [x] |
| 밀도 갱신 | (1−효과)×[밀도 + g×밀도×(1−밀도) + 유입], 0~1로 제한 | `pests.py` `advance` | 미보정 | [x] |
| 일 잎 손실 | α×밀도. 현재 α = 0.01 (이전 0.03, 17절) | `pests.py` `advance` | 미보정 | [x] |
| 조사값 | 7일 평균 손실/α + 잡음 표준편차×표준정규, 0~1로 제한, 7의 배수 일 아침 | `pests.py` `morning` | 미보정 | [x] |
| 온도 입력 | (Tmin+Tmax)/2 | `online_pests.py` | 가정 | [x] |
| 시즌 최대 일수 | 240일 | `environment.py` `max_days` | 가정 | [x] |
| 평가 최대 단계 | 240 | `baseline_evaluation.py` | 가정 | [x] |
| 외생 배열 길이 | 400일 | `exogenous.py` `horizon` | 가정 | [x] |
| 난수 흐름 ID | weather 11, pest_arrival 23, survey_noise 37, reduction 53, budget 71 | `exogenous.py` | 가정 | [x] |
| 난수 흐름 버전 | 1 | `exogenous.py` | 가정 | [x] |
| WGEN 시드 구간 | train 10001–99998 (89,998개), validation 1–4999, test 5000–9999 | `exogenous.py` | 설계 | [x] |
| 학습 시즌 소진 시 | 순서대로 반복 (D10) | `training_env.py` `SeasonCycler.reset` | 가정 | [x] |
| a 정책 학습 감축 확률 | 0.0 | `comparison.py` `training_plan` | 지시 | [x] |
| 물 감축 시 원장 | 남은 물×(1−감축률), 시즌 1회 | `resources.py` `open_day` | 지시 | [x] |
| 예산 차감 | 자재비만(질소·살포). 관수·시비 작업비는 예산 제외, 비용에는 포함. 물은 예산 없이 공급량만 차감(23절) | `resources.py` `commit` | 설계 | [x] |
| 성숙 뒤 투입 차단 | istage 6에서 관수·시비 0만 허용 (설정 `management.input_closed_istage`) | `resources.py` `action_masks` | 설계 | [x] |
| 원장 허용 오차 | 1e-8 | `resources.py` `EPS` | 가정 | [x] |
| 보상 | 수확 매출 − 당일 비용. 실패 시 매출 0 | `environment.py` | 설계 | [x] |
| 잠재함수 Φ | 곡실 단가×η(단계)×`topwt`. 단가는 환경 상수(관측에서 제거, 22절) | `rewards.py` | 설계 | [x] |
| 학습 보상 | (원보상 + Φ다음 − Φ현재)/1000 | `rewards.py` | 설계 | [x] |
| b0′ 보호 단계 | istage 4, 5 | `policies.py` `ReductionResponseRule` | 지시 | [x] |
| b0′ 배분 | 풀/남은 예상 관수 횟수, 최소 5 mm 단위 허용 | `policies.py` | 가정 | [x] |
| 평가 시작 시즌 | validation 2000번부터 | `run_comparison.py` `--first-season` | 가정 | [x] |
| 측정 시작 시즌 | validation 1000번부터 120개 | `measure_stage_entry.py` | 가정 | [x] |
| 최종 시험 구간 접근 | 코드에서 차단 | `baseline_evaluation.py`, `training_env.py` | 설계 | [x] |
| 진입 조건 판정 | `research_ready=false`, `main_training_allowed=false` | `build_readiness_report.py` | 설계 | [x] |

### PPO에서 지정하지 않아 라이브러리 기본값을 쓰는 항목

| 변수 | 현재값 | 확인 |
|---|---|---|
| learning_rate | 0.0003 | [x] |
| clip_range | 0.2 | [x] |
| clip_range_vf | None | [x] |
| normalize_advantage | True | [x] |
| ent_coef | 0.0 | [x] |
| vf_coef | 0.5 | [x] |
| max_grad_norm | 0.5 | [x] |
| target_kl | None | [x] |
| activation_fn | Tanh | [x] |
| ortho_init | True | [x] |
| optimizer | Adam | [x] |
| share_features_extractor | True | [x] |

### 3절 점검 (2026-11-11)

**PPO 기본값 12개.** 근거: `MARS_reference`의 PPO 원 논문(Schulman 2017)과 작물 RL 논문들에서 하이퍼파라미터 부분을 추출해 대조했다.

| 변수 | 현재값 | 이 문제에서의 의미 | 문헌 | 판정 | 확인 |
|---|---|---|---|---|---|
| learning_rate | 3e-4 고정 | Adam 보폭. 감쇠 없음 | PPO 원 논문 MuJoCo 표 3e-4. Balderas 2025·Kallenberg 2023(질소 관리 PPO)은 SB3 기본값. 다른 알고리즘(DQN) 논문은 1e-5~5e-5 | 유지. 시험 학습에서 발산·붕괴 없음 | [x] |
| clip_range | 0.2 | 한 번의 갱신에서 정책 확률비 변화 한도 | PPO 원 논문 비교에서 0.2가 가장 좋음(0.1·0.3보다) | 유지 | [x] |
| clip_range_vf | None | 가치함수 갱신 한도 없음 | SB3 기본, 원 논문 MuJoCo도 없음 | 유지 | [x] |
| normalize_advantage | True | 미니배치마다 이점 표준화 | SB3 기본 | 유지 | [x] |
| ent_coef | 0.0 | 탐색 보너스 없음 | 원 논문 MuJoCo 0, Atari 0.01. 작물 PPO 논문들은 기본값(0) | 유지. 탐색은 희소 초기 확률(18절 B1)로 확보하고, 시험 학습에서 무투입 수렴이 없었다. 학습량을 늘렸는데 탐색 부족이 보이면 재검토 | [x] |
| vf_coef | 0.5 | 가치 손실 가중 | 정책·가치망이 분리돼(아래) 영향이 작다 | 유지 | [x] |
| max_grad_norm | 0.5 | 경사 크기 상한 | SB3 기본 | 유지 | [x] |
| target_kl | None | KL 조기 중단 없음 | 원 논문은 클리핑이 KL 벌점보다 좋다고 보고 | 유지 | [x] |
| activation_fn | Tanh | 은닉층 활성함수 | 원 논문 MuJoCo, Kallenberg 2023 모두 tanh | 유지 | [x] |
| ortho_init | True | 직교 초기화. 단, 행동 출력층은 희소 초기 확률로 덮어쓴다 | SB3 기본 | 유지 | [x] |
| optimizer | Adam | | 원 논문 | 유지 | [x] |
| share_features_extractor | True | 공유되는 것은 평탄화뿐이고, 정책망·가치망은 각각 [256, 256]으로 분리(`net_arch` pi/vf) | 원 논문 MuJoCo도 분리 | 유지 | [x] |

참고: 보상은 1/1,000 척도라 시즌 합이 약 1 수준이고 관측도 대부분 0~1이라, 기본값이 가정하는 크기와 맞는다. Kallenberg 2023은 VecNormalize를 썼지만 이 연구는 고정 척도만 쓴다(22절).

**코드 고정값 30개.** 코드와 대조했고 기록과 같다. 해충 관련 8행은 설정에서 읽도록 바뀐 상태로 고쳤다(위 표). 판단이 필요한 것만 적는다.

| 항목 | 점검 결과 | 판정 | 확인 |
|---|---|---|---|
| 시즌 최대 240일, 평가 최대 240단계 | 실제 시즌 약 133일(최대 138). 시험 학습에서 잘림 0건(검사로 확인) | 유지 | [x] |
| 외생 배열 400일 | 240일 + 마지막 아침보다 길다 | 유지 | [x] |
| 난수 흐름 `budget`(71) | 예산 배율 제거로 쓰이지 않는다. 지우면 흐름 번호 체계만 바뀌므로 그대로 둔다 | 유지 | [x] |
| WGEN 시드 구간 | 학습 89,998 / 검증 4,999 / 시험 5,000. 적합당 200만 단계면 정책 4는 600만 단계, 약 4만 5천 시즌이라 재사용 없음 | 유지 | [x] |
| **학습 시즌 순서** | `season_id = rank + count × n_envs`로 시드와 무관하다. 모든 적합·시드가 같은 학습 시즌을 같은 순서로 본다. 그래서 시드 간 차이는 초기화·행동 표본 차이만 반영하고 학습 날씨의 차이는 반영하지 않는다 | 유지(공통 난수 설계). 시드 수 결정(D10) 때 고려 | [x] |
| 시즌 번호 사용처 | 측정 1000~1119, b0′ 여유 탐색 3100~3239, 기준선 탐색 4000~4479, 시험 학습 4500~4519, **비교 평가 2000~2999**(조건당 1,000). 평가 구간이 튜닝 구간과 겹치지 않는다 | 유지 | [x] |
| 최종 시험 구간 | `baseline_evaluation.py`, `training_env.py`가 시험 구간을 거부한다 | 유지 | [x] |
| b0′ 배분 | 풀 ÷ 남은 예상 관수 횟수, 풀이 있으면 최소 5 mm | 유지 | [x] |
| 보상·잠재함수 | 단가는 환경 상수(22절). 15.5 % 환산 후에는 건물 기준 단가가 들어간다(1절) | 유지 | [x] |

## 4. 관측 변수 (하루 28개 × 7일 = 196)

값은 고정 척도로 나눠 입력한다(`observations.py` `FIELDS`). 2026-11-11에 45개(315)에서 정리했다(22절).

| 변수 | 척도 | 변수 | 척도 | 변수 | 척도 |
|---|---:|---|---:|---|---:|
| dap | 200 | istage | 10 | vstage | 30 |
| xlai | 10 | topwt | 20000 | grnwt | 15000 |
| rtdep | 300 | swfac | 1 | nstres | 1 |
| sw (뿌리 영역 평균) | 0.15 | ep | 20 | rain | 100 |
| tmax | 50 | srad | 40 | dtt | 50 |
| water_used | 200 | nitrogen_used | 241 | sprays | 4 |
| water_left | 200 | announced | 1 | reduction_fraction | 1 |
| days_since_announcement | 200 | survey_value | 1 | survey_age | 7 |
| days_since_spray | 200 | previous_water | 25 | previous_nitrogen | 80 |
| previous_spray | 1 | | | | |

확인: [x]

변수별 의미, 실제 범위, 점검 결과, 정리 결정은 22절에 있다.

## 5. 정책과 실험 구성

| 정책 | 관수 | 시비 | 방제 | 학습 환경 | 학습 단계 | 확인 |
|---|---|---|---|---|---:|---|
| 0 (πB) | 규칙 | 규칙 | 규칙 | 없음, a·b 공통 | 0 | [x] |
| a1 / b1 | PPO | 규칙 | 규칙 | a 감축 0 / b 감축 0.75 | 5,000,000 | [ ] |
| a2 / b2 | 정책 1 동결 | PPO | 규칙 | 〃 | 5,000,000 | [ ] |
| a3 / b3 | 정책 1 동결 | 정책 2 동결 | PPO | 〃 | 5,000,000 | [ ] |
| a4 / b4 | PPO | PPO | PPO | 〃 | 15,000,000 | [ ] |
| b0′ | 감축 전 규칙, 감축 후 예비 배분 | 규칙 | 규칙 | 없음, b-유 행만 평가 | 0 | [x] |

- 동결 사슬은 벌과 시드 번호 안에서만 잇는다.
- 무투입 대조(관수·시비·방제 모두 0)는 비교 실험에서 제외한다(D4).

| 평가 행 | 정책 | 감축 조건 | 확인 |
|---|---|---|---|
| a | 0, a1~a4 | 없음 | [x] |
| b-무 | 0, b1~b4 | 없음 | [x] |
| a-유 | a1~a4 (정책망 고정, 당일 관측에 반응) | b-유와 같은 9조건 평균 | [x] |
| b-유 | 0, b1~b4, b0′ | 13·37·83일 × 20·40·60%의 9조건 평균 | [x] |

| 통계 항목 | 현재값 | 확인 |
|---|---|---|
| 각 칸 지표 | 평균 순수익, 하위 10% 평균(USD/ha) | [x] |
| 하위 10% 계산 | 시드별로 하위 ceil(10%) 시즌 평균 후 시드 평균, b-유는 9조건 평균 | [x] |
| 부트스트랩 | 시드·시즌 교차 복원추출 10,000회, 95% 백분위 구간, 난수 시드 0 | [x] |
| p값 | 귀무 중심화 부트스트랩. C1·C2 단측, 나머지 양측 | [x] |
| Holm 검정군 | 가설 2개, 조건별 9개, 대비 비용 4개, 대비 이득 4개, 감축 손실 5개, 효과 5개 | [x] |
| 대비 비용 | a − (b-무), 정책 1~4 (정책 0은 항상 0이라 제외) | [x] |
| 대비 이득 | (b-유) − (a-유), 정책 1~4 | [x] |
| C1, C2 | b4−b1 기준, 초기 대 후기 시점 | [x] |

### 가설 (2026-11-11 새 비교구조)

| 가설 | 내용 | 대비 | 판정 | 확인 |
|---|---|---|---|---|
| H1 감축 강도 | 감축률이 커질수록 b4의 b1 대비 추가 가치가 커진다 | C1 | > 0, 단측 | [x] |
| H2 감축 시점 | 초기 감축에서 후기 감축보다 b4의 b1 대비 추가 가치가 크다 | C2 | > 0, 단측 | [x] |
| H3 방제 가치 | 감축은 시비까지 학습한 정책에 방제 학습을 더한 가치를 바꾼다. 해충·회복 검증 전에는 탐색 분석 | (b3−b2)의 b-유 − b-무 | ≠ 0, 양측 | [x] |
| H4 대비 비용과 이득 | 감축에 대비해 학습하면 무감축 때 수익이 낮아지고 감축 때 수익이 높아진다 | a − (b-무), (b-유) − (a-유) | 정책별 > 0 예상. 검정은 양측(사전등록 초안·코드 일치) | [x] |
| H5 관수 학습의 감축 대응 | 관수 학습의 규칙 대비 이득은 감축 때 더 크고, b0′보다 수익이 높다 | (b1−b0)의 b-유 − b-무, b-유의 b1−b0′ | > 0 예상. 검정은 양측(사전등록 초안·코드 일치) | [x] |
| H6 학습 구조 | 순차 추가와 동시 학습의 효과는 감축 유무에 따라 달라진다 | (b3−b1), (b4−b3)의 b-유 − b-무 | ≠ 0, 양측 | [x] |

### 5절 점검 (2026-11-12)

**코드 대조.** 위 표를 `src/mars_env/comparison.py`(`training_plan`, `table_cells`, `results_table`, `contrasts`, `cross_bootstrap`, `holm`, `inference`)와 `scripts/run_comparison.py`(평가·조립·검사)와 대조했다. 정책 구성, 평가 행, 칸 지표, 하위 10 % 계산, 부트스트랩, p값, Holm 검정군 6개(2·9·4·4·5·5개), 대비 정의, 가설 H1~H6의 대비가 모두 기록과 같다. 다른 점은 하나다: 위 정책 표의 **학습 단계 500만·1,500만은 D10 결정 전 값**이다(100만×10 또는 200만×5 검토 중).

| 항목 | 점검 결과 | 판정 | 확인 |
|---|---|---|---|
| 정책 구성·동결 사슬 | `training_plan`이 벌(a·b)과 시드 번호 안에서만 정책 1→2→3을 잇고, 정책 4는 3배 단계 | 유지 | [x] |
| 공통 시즌 | 모든 정책·시드가 같은 평가 시즌(검증 2000~2999)을 쓰고, 감축일이 정책 간 같음을 검사(`reduction_day_shared_across_policies`) | 유지 | [x] |
| 정책 0 | a행과 b-무행의 정책 0이 같은 값인지 검사(`a0_equals_b_none_b0`). 규칙 정책은 시드마다 다시 돌리지 않고 복사 | 유지 | [x] |
| 하위 10 % | 칸 표에만 쓰고 검정하지 않는다 | 유지 | [x] |
| 교차 부트스트랩 | 시드 행과 시즌 열을 독립으로 다시 뽑는다(모든 대비를 같은 표본으로). Agarwal et al. 2021(`MARS_reference`)은 3~10회 실행이 흔한 상황에서 점추정 대신 부트스트랩 구간을 보고하라고 권한다. 이 연구는 시즌 1,000개를 함께 다시 뽑아 시즌 변동도 구간에 들어간다 | 유지 | [x] |
| 시드 변동의 범위 | 3절 점검: 학습 시즌 순서가 시드와 무관해 시드 간 차이는 초기화·행동 표본 차이만 반영한다. 시드가 5개면 시드 행 재표집의 조합이 적다 | 한계로 명시. D10에서 고려 | [x] |
| C1·C2 정의 | C1은 감축률 20 %와 60 %의 기울기(40 %는 쓰지 않음), C2는 13일과 83일의 차이(37일은 쓰지 않음)를 세 시점·세 감축률에 대해 평균. 사전등록대로 | 유지 | [x] |
| p값 | 귀무 중심화 부트스트랩, (1 + 초과 수)/(반복 + 1). C1·C2만 단측 | 유지 | [x] |
| **평가 계산량** | 시즌 하나에 칸 100개: 규칙 정책 20회 + 학습 정책 80회 × 시드 수. 시즌 1,000개 × (본 표 + 공급 120·160 mm + 조사 잡음 0.05의 4벌)이라 **5시드 약 168만, 10시드 약 328만 회**다. 평가 프로세스가 4개(`WORKERS = 4`)이고 회당 약 1.9초(시험 학습 평가 기준)라 **5시드 약 9일, 10시드 약 18일**이 학습과 별도로 든다 | **결정 필요** (D10과 함께) | [x] |

**결정 (2026-11-12, 임의): ①+③ 적용.** 본 표는 시즌 1,000개·칸 100개 그대로. 민감도 3벌(공급 120·160 mm, 조사 잡음 0.05)은 본 표의 앞쪽 300시즌만, a-유 행 없이 평가한다(`scenarios.sensitivity_seasons_per_condition: 300`, `sensitivity_rows: [a, b_none, b_cut]`). 평가 프로세스는 코드 상수 4에서 설정값 8로(`scenarios.evaluation_workers`). 민감도 결과에는 대비 이득(`preparedness_gain`)이 없다. 예상 평가 시간: 5시드 약 2.8일, 10시드 약 5.4일(8프로세스 효과는 미측정). 코드: `comparison.table_cells(rows=...)`, `contrasts`가 a-유 행이 없으면 대비 이득을 건너뜀, `run_comparison.py`. 테스트 2개 추가. 소형 전체 실행 확인(`outputs/runs/20261111T151855Z_policy_comparison_c92bec7c`, 시드 1개·시즌 2개·적합당 2,048단계): 본 표 200회(칸 20개, 모든 검사 통과, 자원 위반 0), 민감도 벌마다 128회(a·b-무·b-유 행만, 대비 이득 없음)로 계산과 일치.

**평가 시간 단축 방안 (2026-11-12).** 회당 1.9초, 평가 프로세스 4개 기준. 민감도 3벌(공급 120·160 mm, 조사 잡음 0.05)이 전체 평가의 75 %다.

| 방안 | 내용 | 5시드 | 10시드 | 잃는 것 |
|---|---|---:|---:|---|
| 현재 | 4벌 모두 시즌 1,000개, 칸 100개 | 9.2일 | 18.0일 | — |
| ① 민감도 축소 | 본 표는 그대로. 민감도 3벌은 시즌 300개, a-유 행(감축 아래 a 정책, 학습 정책 칸의 45 %) 제외 | 3.5일 | 6.8일 | 민감도에서 대비 이득(H4 일부)을 계산할 수 없고, 민감도 구간이 넓어진다 |
| ①′ 민감도 시즌 500개 | ①과 같고 민감도 시즌만 500개 | 4.3일 | 8.3일 | ①보다 덜 잃음 |
| ② 본 표도 축소 | ①에 더해 본 표 시즌 500개 | 2.3일 | 4.5일 | 주 가설 구간이 넓어진다(시즌 성분 표준오차 약 1.4배) |
| ③ 평가 프로세스 4 → 8 | 코드 상수 `WORKERS`를 설정값으로. CPU 6코어라 학습 처리량 측정상 이득은 약 20~30 %로 예상(미측정) | ①과 함께 2.8일 | ①과 함께 5.4일 | 없음. 효과는 측정 필요 |

해석: 시즌 간 짝지은 차이의 표준편차를 약 50~100 USD/ha로 보면(11절 확인 80시즌의 +54.9 구간 폭에서 역산한 약 53), 시즌 성분 표준오차는 1,000시즌 약 1.7~3.2, 500시즌 약 2.2~4.5, 300시즌 약 2.9~5.8 USD/ha다. 주 가설은 본 표 1,000시즌으로 두고, 민감도는 방향 확인용이라 300~500시즌으로 줄여도 판단에 쓸 수 있다고 본다.

## 6. 측정값 (규칙 정책, 검증 120시즌, 감축 없음)

근거: `outputs/runs/20261110T172016Z_stage_entry_rule_policy_39458a4b/verification.json` (공급 200 mm, 단계별 규칙). 시비 일정은 45·65·85일, 생육 실패 0건이다.

| istage | 의미 | 평균 진입일 | 표준편차 | 최소 | 최대 | 평균 관수 mm | 평균 관수 횟수 | 확인 |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 출아~유년기 끝 | 13.0 | 3.27 | 8 | 22 | 0.0 | 0.00 | [ ] |
| 2 | ~화서 분화 | 36.8 | 4.85 | 28 | 51 | 0.17 | 0.02 | [ ] |
| 3 | ~잎 생장 끝 | 41.8 | 4.85 | 33 | 56 | 77.3 | 5.15 | [ ] |
| 4 | 개화기~등숙 시작 | 82.6 | 4.72 | 72 | 96 | 30.8 | 1.54 | [ ] |
| 5 | 유효 등숙 | 92.8 | 4.50 | 83 | 105 | 43.4 | 2.94 | [ ] |
| 6 | 성숙 | 130.4 | 4.22 | 121 | 141 | | | [ ] |

| 지표 | 평균 | 표준편차 | 최소 | 최대 | 확인 |
|---|---:|---:|---:|---:|---|
| 시즌 길이(일) | 132.8 | 4.31 | 123 | 144 | [ ] |
| 시즌 관수량(mm) | 151.8 | 34.7 | 30 | 200 | [ ] |

## 7. 검증 게이트 값 (`validation_gates`, 코드 미사용)

| 변수 | 현재값 | 확인 |
|---|---|---|
| `validation_gates.metadata_read_store_and_coordinates` | true | [x] |
| `validation_gates.corrected_profile_short_ppo` | true | [x] |
| `validation_gates.harvest_boundary_observed` | true | [x] |
| `validation_gates.experimental_qf_native_residue_handoff` | true | [x] |
| `validation_gates.experimental_maize_harvest_unit_adapter` | false | [x] |
| `validation_gates.experimental_c_terminal_allocation` | true | [x] |
| `validation_gates.native_qf_n_partition_conservation` | false | [x] |
| `validation_gates.experimental_harvest_n_candidate` | true | [x] |
| `validation_gates.experimental_harvest_scope_audit` | true | [x] |
| `validation_gates.harvest_n_candidate_broad_scope` | false | [x] |
| `validation_gates.experimental_direct_ear_organ_audit` | true | [x] |
| `validation_gates.experimental_actual_harvest_contract_v2` | true | [x] |
| `validation_gates.experimental_integrated_crop_soil_n_v2` | true | [x] |
| `validation_gates.public_agronomic_scenario_registry` | true | [x] |
| `validation_gates.post_harvest_ecosystem_balance` | false | [x] |
| `validation_gates.experimental_weather_calendar_action_audit` | true | [x] |
| `validation_gates.experimental_soil_output_arithmetic` | true | [x] |
| `validation_gates.experimental_maturity_preharvest_n` | true | [x] |
| `validation_gates.real_cuda_long_stability` | true | [x] |
| `validation_gates.real_cpu_long_stability` | true | [x] |
| `validation_gates.controlled_long_cpu_gpu_comparison` | true | [x] |
| `validation_gates.baseline_policy_interfaces` | true | [x] |
| `validation_gates.potential_reward_telescope` | true | [x] |
| `validation_gates.real_cpu_maskableppo_smoke` | true | [x] |
| `validation_gates.experimental_plant_n_inventory_balance` | true | [x] |
| `validation_gates.experimental_online_pest_survey` | true | [x] |
| `validation_gates.experimental_native_leaf_write` | true | [x] |
| `validation_gates.whole_season_carbon_nitrogen_balance` | false | [x] |
| `validation_gates.deep_planting_failure_handling` | true | [x] |
| `validation_gates.paired_external_seasons` | true | [x] |
| `validation_gates.dssat_state_read` | true | [x] |
| `validation_gates.live_leaf_damage_write` | false | [x] |
| `validation_gates.irrigation_10mm_regression` | true | [x] |
| `validation_gates.no_pest_regression` | true | [x] |
| `validation_gates.crop_recovery` | false | [x] |
| `validation_gates.water_nitrogen_damage_interaction` | false | [x] |

### 7절 점검 (2026-11-12)

게이트 값은 코드가 읽지 않는 기록용이다. 각 값의 근거는 설정 파일의 행 주석에 있다. 35개를 비교 실험과의 관련으로 나눴다.

**① 비교 실험 경로 — 현재 코드로 재검증.** 근거 파일이 2026-11-05 것이라 관측 28개, 물 예산 제거, 성숙 뒤 마스크, 15.5 % 가격 환산보다 오래됐다. 현재 실행 이미지(`mars-dssat:ppo-cpu-metadata`)에서 `scripts/recheck_gates.sh`로 다시 돌렸다. 이전 근거는 `outputs/gate_evidence_before_2026-11-12/`에 백업했다.

| 게이트 | 값 | 검증 스크립트 | 2026-11-12 결과 | 확인 |
|---|---|---|---|---|
| no_pest_regression | true | `verify_gym_integration.py` | 통과 | [x] |
| paired_external_seasons | true | `verify_paired_seasons.py` | 처음엔 실패: Windows 쪽 시즌 목록(`outputs/exogenous_manifest.json`)이 11월 5일 설정으로 만든 것이었다. 현재 설정으로 다시 만든 뒤 통과(Windows·Linux 외생 흐름 일치) | [x] |
| potential_reward_telescope | true | `verify_real_rewards.py` | 통과(수확·생육 실패·행정 잘림) | [x] |
| experimental_online_pest_survey | true | `verify_experimental_env.py` | 통과 | [x] |
| experimental_native_leaf_write | true | `verify_native_leaf.py` | 통과 | [x] |
| deep_planting_failure_handling | true | `verify_crop_failure.py` | 통과 | [x] |
| irrigation_10mm_regression | true | `probe_dssat_contract.py` | 통과 | [x] |
| baseline_policy_interfaces | true | `verify_policy_interfaces.py` | 통과 | [x] |
| dssat_state_read | true | 위 검사들의 조합(D13) | 구성 검사가 모두 통과 | [x] |
| corrected_profile_short_ppo, real_cpu_maskableppo_smoke, real_cpu_long_stability | true | 1,024·102,400단계 진단 | 2026-11-11 시험 학습 51만 단계(현재 설정)와 200만 단계 연장이 더 강한 근거. 잘림 0건·파라미터 유한성 검사 통과 | [x] |
| live_leaf_damage_write | false | — | 연구용 잎 피해 쓰기 판정. 실험용 경로만 통과했고 비교 실험은 실험용 해충 환경을 쓴다(결과는 실험용으로만 해석) | [x] |

**② 하드웨어 — 비교 실험과 무관.** real_cuda_long_stability, controlled_long_cpu_gpu_comparison(true). 비교 실험은 CPU만 쓴다.

**③ 다년·수확·C/N 회계 — 비교 실험 미사용.** metadata_read_store_and_coordinates, harvest_boundary_observed, experimental_qf_native_residue_handoff, experimental_maize_harvest_unit_adapter(false, 철회), experimental_c_terminal_allocation, native_qf_n_partition_conservation(false), experimental_harvest_n_candidate, experimental_harvest_scope_audit, harvest_n_candidate_broad_scope(false), experimental_direct_ear_organ_audit, experimental_actual_harvest_contract_v2, experimental_integrated_crop_soil_n_v2, post_harvest_ecosystem_balance(false), experimental_weather_calendar_action_audit, experimental_soil_output_arithmetic, experimental_maturity_preharvest_n, experimental_plant_n_inventory_balance, whole_season_carbon_nitrogen_balance(false). 비교 실험은 단일 시즌 `mode="all"`이고 수확은 Summary.OUT HWAH만 쓴다. false 항목은 20절에서 한계로 분류했다. 다시 돌리지 않았다.

**④ 농학 검증.** public_agronomic_scenario_registry(true, 기록용 목록), crop_recovery(false), water_nitrogen_damage_interaction(false). 둘 다 20절·19절에서 한계로 기록돼 있다.

판정: ①의 값은 현재 코드에서도 맞다. ②~④는 비교 실험 결과에 영향이 없어 값을 그대로 둔다.

## 8. 아직 기록하지 않은 범위

| 대상 | 내용 | 확인 |
|---|---|---|
| `configs/*.json` 17개 | 현장 검증 등급, 공개 연구 자료, 수확·탄소 측정 계약 등 | [ ] |
| `docker/` 패치 | DSSAT 소스 패치와 이미지별 차이 | [ ] |
| 진단용 스크립트 내부 상수 | `scripts/`의 감사·검증 스크립트 | [ ] |
| DSSAT 전역 계수 | `MZCER048.SPE`, `DSSATPRO` 등 원본 파일 | [ ] |
| WGEN 기상 입력 | UFGA 기상 파일과 월별 통계 | [ ] |

## 9. 관수 값 점검 (2026-11-11, `MARS_reference` 기준)

점검만 했고 설정값은 바꾸지 않았다. **판정**은 `근거 있음`(문헌과 일치), `부분 근거`(유사 조건만 있음), `근거 없음`(자료에 수치 없음)으로 적는다.

| 변수 | 현재값 | 문헌 내용 | 판정 | 제안 | 확인 |
|---|---|---|---|---|---|
| 시즌 물 공급 `initial_water_mm` | <mark>200 mm (이전 264)</mark> | Gautron 2022 표 6·9의 UFGA8201 #3 전문가 일정 16회 합계가 264 mm다. 같은 시나리오의 학습 정책 사용량은 PPO 133.8 mm(Gautron), DQN 120 mm(Tao 2023 플로리다 RF1)이고 πB는 132 mm다 | 264는 근거 있음, 200은 구속 비율로 결정 | 200 mm로 변경 완료 | [x] |
| 감축률 `evaluation_reductions` | 20·40·60 % | Kelly 2024는 물 상한 75·100·125 mm에서 DRL 이득이 +12.2·+7.1·+4.3 USD/ha, 상한 없을 때 −1.3 USD/ha였다. 200 mm 기준 감축 후 160·120·80 mm가 이 구간에 걸친다. 세 수준의 선택 이유는 문서와 문헌에 없고 제안서 설정에서 이어졌다 | 근거 없음, 구속 비율로 판단 | 유지 승인 | [x] |
| 물 단가 `water_usd_mm_ha` | 1.1 | Tao 2023 표 1 RF1이 1.1이다. Kelly 2024는 1 USD/ha-mm, Saikai 2023은 저비용 시나리오 0.6 AUD/mm | 근거 있음 | 유지 | [ ] |
| 물 예산 `budgets_usd_ha.water` | ~~220~~ 제거 | 200×1.1로 문헌 값은 아니다. 물리 한도 200 mm와 같아 별도로 구속하지 않는다(예산 배율 제거) | 근거 없음 | 2026-11-11 제거 (23절) | [ ] |
| 관수 격자 `irrigation_grid_mm` | 0~25, 5 간격 | Kelly 2024 최적 행동이 0~25 mm 2.5 간격이다. Tao·Balderas는 0~24 mm 6 간격, Saikai는 0~40 mm 10 간격이고 전문가 일정 최대는 25 mm다 | 근거 있음 | 유지 | [ ] |
| 결정 주기 | <mark>매일</mark> | Kelly 2024는 3일 주기 수익이 가장 높고 행동 집합보다 주기의 영향이 컸다 | 부분 근거 | 후속 연구로만 둔다 (2026-11-11 결정) | [x] |
| 관수 작업비 `irrigation_labor_usd_event_ha` | <mark>2.04 (이전 3.0)</mark> | LSU AgCenter 2025 예산서 부록 표 2: 고랑(이동식 관) 관수 노동 0.223 h/acre × $14.83, 4회. 원 실험 고랑 관수(IR001)와 방식 같음 | 근거 있음 | 2026-11-13 교체 (27절) | [x] |
| 규칙 관수 임계·양 | <mark>1−SWFAC ≥ 0.30, 10 mm</mark> | Saseendran 2014: SWFAC는 공급이 수요보다 적을 때 작동하고 잎 신장 스트레스(TURFAC)는 더 일찍 시작한다. Kelly 2024의 기준선은 생육단계별 토양수분 임계 4개를 최적화했다. Gautron 2022는 DSSAT 자동관수 기준선을 제안했다. FileX 자동관수량은 10 mm다 | 부분 근거 | 단계별 규칙 채택 (11절) | [x] |
| b0′ 보호 구간 | istage 4·5 (83일~) | Fereres 2007: 개화 후 스트레스는 피해야 하고 개화 전 부족은 수확지수를 높일 수 있다. Santos 2018 인용: 민감기는 추대~등숙 시작이다. Gautron·Balderas의 PPO 관수는 모의 80~120일(파종 후 약 53~93일)에 집중됐다 | 부분 근거 | 보호 시작일을 83일보다 앞당기는 후보 비교 | [ ] |
| 감축 계약 `reduction_contract` | remaining_fraction | Kelly 2024는 시즌 총량 상한이다 | 부분 근거 | 주 분석 유지, 총량 상한을 민감도로 | [ ] |
| 희소 초기 질량 `sparse_nonzero_mass.irrigation` | 0.13 | 전문가 16회, πB 13.2회/132.8일(0.10)과 같은 규모다. Tao는 부분관측 RL이 무투입으로 수렴했고, Balderas는 혼합 과제 PPO가 물을 전혀 안 줬다 | 부분 근거 | 유지, 정책 4의 무관수 수렴 감시 | [ ] |
| 평가 행동 방식 (D9) | 최대확률 | Balderas 2025는 단일 관수 과제에 확률 행동, 혼합 과제에 최대확률 행동을 썼다 | 부분 근거 | 두 방식 모두 검증 구간에서 비교 | [ ] |
| 관수 효율 | 100 % | Santos 2018은 점적 효율로 관수량을 보정했다(CUC 96.2 %). 스프링클러 수치는 자료에 없다 | 근거 없음 | 유지, 한계로 명시 | [ ] |
| 입력 상한 | 50 mm | Gautron 2022 관수 범위 [0, 50] | 근거 있음 | 유지 | [ ] |

### 공급량별 규칙 정책 구속 비율

감축일 0일에 감축된다고 보고, 검증 120시즌의 πB 시즌 관수량이 감축 후 물을 넘는 비율이다. πB 시즌 관수량 분위수는 5% 80, 중앙 130, 95% 200 mm다.

| 공급 mm | 감축 없음 | 20 % | 40 % | 60 % | 감축 후 물 mm (20·40·60 %) | 확인 |
|---:|---:|---:|---:|---:|---|---|
| 264 (이전) | 0.0 % | 0.8 % | 29.2 % | 74.2 % | 211.2, 158.4, 105.6 | [ ] |
| 200 (현재) | 3.3 % | 20.0 % | 52.5 % | 88.3 % | 160, 120, 80 | [ ] |
| 160 | 20.0 % | 52.5 % | 85.8 % | 98.3 % | 128, 96, 64 | [ ] |
| 132 | 43.3 % | 74.2 % | 95.8 % | 99.2 % | 105.6, 79.2, 52.8 | [ ] |

- 200 mm는 πB 사용량의 95% 분위수라 무감축 행이 거의 제약받지 않고, 감축 후 물이 Kelly 2024의 상한 구간에 걸친다.
- 200 mm로 바꾸면서 물 예산(공급×1.1), 코드 기본값, 관측 척도(`water_used`, `water_left`, `initial_water`, `initial_water_budget`), b0′ 값을 함께 고쳐야 한다.
- Santos 2018의 관수량 105.7·158.5·211.5·264.2 mm는 264 mm의 감축 후 물과 수치가 거의 같지만 단옥수수·다른 지역의 50·75·100·125 % ETc라 근거로 쓰지 않는다.
- Gautron 2022 표 10의 단계 설명은 해당 단계가 끝나는 사건 기준으로 읽어야 한다. 시작 사건으로 읽으면 파종 후 2일 출아, 42일 출사가 되어 맞지 않는다. Summary.OUT의 개화일과 직접 대조하지는 않았다.

## 10. 공급량별 물 반응 (규칙 정책 πB)

근거: `outputs/runs/20261110T161703Z_water_response_rule_policy_e4893747/verification.json`. 검증 80시즌을 공급량마다 같게 썼고 감축은 없으며 시비는 116 kg N/ha, 예산 배율은 1.0이다. 시즌 강수는 평균 488 mm, 5% 분위 260 mm다. 작물 실패는 모든 공급량에서 0건이었다.

| 공급 mm | 실제 관수 mm | 평균 곡실 kg/ha | 최대 대비 | 5% 분위 곡실 | 최저 곡실 | 평균 순수익 | 하위 10% 순수익 | 증산량 mm | 확인 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 0.0 | 3645 | 48 % | 930 | 800 | 407.4 | −9.5 | 172.7 | [ ] |
| 20 | 20.0 | 3937 | 52 % | 1124 | 823 | 425.5 | −19.4 | 199.1 | [ ] |
| 40 | 40.0 | 4431 | 59 % | 1379 | 860 | 475.6 | −11.7 | 226.6 | [ ] |
| 60 | 60.0 | 5104 | 68 % | 2108 | 872 | 553.9 | 26.7 | 250.1 | [ ] |
| 80 | 79.5 | 5919 | 79 % | 2727 | 1290 | 655.3 | 115.3 | 269.6 | [ ] |
| 100 | 96.5 | 6639 | 88 % | 3960 | 1713 | 745.3 | 272.4 | 283.8 | [ ] |
| 120 | 110.5 | 7097 | 94 % | 5081 | 4116 | 798.2 | 436.8 | 293.7 | [ ] |
| 160 | 126.0 | 7465 | 99 % | 6172 | 5714 | 834.6 | 588.5 | 303.1 | [ ] |
| 200 | 130.6 | 7525 | 100 % | 6420 | 5714 | 837.6 | 618.6 | 304.8 | [ ] |

- 규칙 정책 기준값이며, 물을 더 잘 나눠 쓰는 정책은 같은 수량을 더 적은 물로 낼 수 있다.
- 평균 수량 90 %는 약 106 mm, 95 %는 약 126 mm 공급에서 도달한다(표의 값 사이를 선형 보간).

### b0′ 조건별 평균 순수익 (공급 200 mm, 8시즌, `20261110T161247Z_policy_comparison_7f643a97`)

| 조건 | 20 % | 40 % | 60 % |
|---|---|---|---|
| 초기·중기 (πB / b0′) | 812.1 / 783.7 | 745.4 / 715.7 | 551.8 / 625.7 |
| 후기 (πB / b0′) | 812.9 / 810.6 | 809.3 / 793.8 | 775.7 / 761.3 |

### 부족 시에만 예비를 쓰는 b0′ (공급 200 mm, 검증 40시즌, `20261110T162631Z_reduction_rule_comparison_c7a1f491`)

평균 순수익 / 하위 10% 평균(USD/ha). 위 8시즌 표와 시즌이 달라 직접 비교할 수 없다.

| 조건 | πB | b0′ |
|---|---|---|
| 초기·중기 20 % | 866.1 / 582.1 | 856.0 / 500.3 |
| 초기·중기 40 % | 828.9 / 353.3 | 792.0 / 381.7 |
| 초기·중기 60 % | 677.6 / −13.5 | 699.6 / 280.9 |
| 후기 20 % | 867.1 / 597.9 | 864.4 / 574.2 |
| 후기 40 % | 864.8 / 584.8 | 857.6 / 539.9 |
| 후기 60 % | 856.5 / 526.6 | 819.6 / 457.7 |
| 9조건 평균 | 814.9 / 394.8 | 804.1 / 433.1 |

## 11. 단계별 규칙 기준선 탐색 (채택)

근거: `outputs/runs/20261110T165939Z_rule_baseline_search_33d3c832/verification.json`. istage 3·4·5의 임계 {0.1~0.5}와 관수량 {5, 10, 15, 20} mm를 감축 없는 검증 40시즌(4000~4039)에서 좌표 탐색했다(2회, 46개 설정). 채택 기준은 겹치지 않는 80시즌(4100~4179)에서 평균 순수익 차이의 95% 구간이 0보다 위인 것이었다.

| 항목 | 현재 πB | 단계별 규칙 | 차이 (95% 구간) | 확인 |
|---|---:|---:|---|---|
| 평균 순수익 | 840.1 | 895.1 | +54.9 (43.5~66.7) | [ ] |
| 하위 10% 평균 | 606.6 | 685.8 | | [ ] |
| 평균 곡실 kg/ha | 7547 | 7964 | | [ ] |
| 평균 관수 mm | 134.4 | 154.1 | | [ ] |

감축 조건(결과 보고만, 40시즌)의 평균 순수익 차이는 20 %에서 +52.1~+56.3, 40 %에서 +41.7~+55.0, 후기 60 %에서 +49.7이고, 초기·중기 60 %는 +16.0(−6.4~39.4)이었다. istage 3 임계 0.5와 istage 4 임계 0.1은 탐색 범위의 끝값이었다.

### 범위 확장 탐색 (현재 값 유지)

근거: `outputs/runs/20261110T222729Z_rule_baseline_search_1f4c80da/verification.json`. 채택값에서 출발해 임계 0.05~0.7(8개), 관수량 5~25 mm(5개)로 넓혀 같은 40시즌에서 다시 탐색했다. 최선은 istage 4 임계만 0.1 → 0.05로 바꾼 값이었다(튜닝 907.2 대 904.6). 새 확인 80시즌(4200~4279)에서 차이는 +0.8 USD/ha(−0.6~2.5)로 채택 기준을 통과하지 못해 현재 값을 유지한다.

- istage 3 임계는 0.05~0.7 전체에서 895.7~904.6으로 거의 평탄했다. 끝값 0.5가 범위 제약 때문에 고른 값은 아니다.
- istage 4 임계를 0.4 이상으로 올리면 887.2 → 774.1로 크게 떨어진다. 개화기는 일찍 관수할수록 유리하다.
- 관수량 25 mm는 istage 3·4·5 모두 15~20 mm보다 낮았다.

### 단계별 규칙 기준 재측정

| 공급 mm | 평균 곡실 | 최대 대비 | 평균 순수익 | 하위 10% 순수익 | 확인 |
|---:|---:|---:|---:|---:|---|
| 80 | 5905 | 75 % | 659.7 | 137.1 | [ ] |
| 120 | 7220 | 92 % | 821.6 | 441.9 | [ ] |
| 160 | 7748 | 98 % | 873.0 | 649.9 | [ ] |
| 200 | 7890 | 100 % | 881.8 | 679.1 | [ ] |

근거: `20261110T172123Z_water_response_rule_policy_c7f8b4ba`(80시즌). 감축 없을 때 시즌 관수량 분위수는 5 % 99.5, 중앙 157.5, 95 % 200 mm이고, 감축 후 물 160·120·80 mm를 넘는 시즌 비율은 37.5·80.8·97.5 %다.

| 조건 (검증 40시즌, `20261110T172749Z_reduction_rule_comparison_960faaf9`) | πB | b0′ |
|---|---|---|
| 초기·중기 20 % | 898.4 / 628.5 | 884.5 / 545.7 |
| 초기·중기 40 % | 840.1 / 380.4 | 828.7 / 429.9 |
| 초기·중기 60 % | 650.3 / −0.1 | 715.9 / 270.5 |
| 후기 20 % | 902.8 / 681.8 | 900.1 / 646.8 |
| 후기 40 % | 896.2 / 620.0 | 887.5 / 569.9 |
| 후기 60 % | 876.8 / 521.6 | 856.8 / 499.7 |
| 9조건 평균 | 828.1 / 426.8 | 833.6 / 467.6 |

## 12. 기준선 강화와 후속 연구 (2026-11-11 정리)

### 규칙 기준선 강화

| 순서 | 방안 | 결과 | 확인 |
|---:|---|---|---|
| 1 | 단계별 스트레스 임계 | 채택. istage 3·4·5 임계 0.5·0.1·0.2 (단계별 규칙 기준선 탐색 절) | [x] |
| 2 | 단계별 관수량 | 채택. 15·20·15 mm | [x] |
| 3 | 토양수분 기준 규칙 | 채택 안 함. 관측 `sw`가 180 cm 전체 평균이라 뿌리 영역 상태를 나타내지 못한다 | [x] |

### 후속 연구 (본 연구에서는 수행하지 않을 가능성이 높음)

| 항목 | 주 분석 | 후속 값 | 근거 |
|---|---|---|---|
| 관수 작업비 USD/회 | 3 | 0, 6 | 자료 없음 |
| 관수 효율 | 1.0 | 0.9, 0.75 | 자료 없음, 코드 구현 필요 |
| 물 단가 USD/mm/ha | 1.1 | 0, 1.0, 2.2 | Tao 2023, Kelly 2024 |
| 곡실 단가 USD/kg | 0.158 | 0.18 | Kelly 2024 |
| 시즌 물 공급 mm | 200 | 264 | Gautron 2022. 120·160 mm 재평가는 `evaluation_supply_mm`으로 본 분석에 포함 |
| 감축 계약 | 남은 물 비례 | 시즌 총량 기준 | Kelly 2024 |
| 평가 행동 | 최대확률 | 확률 표집 | Balderas 2025. 주 분석 방식은 D9에서 결정 |
| 결정 주기 | 매일 | 3일 | Kelly 2024 |

## 13. 팀원용 설계 설명 (왜 이렇게 정했나)

### 평가 감축일

평가 감축일은 학습이 끝난 정책의 성적을 잴 때 시험 조건으로 정해 둔 "물이 줄어드는 날짜"다. 현재 파종 후 13일(초기), 37일(중기), 83일(후기)이고, 규칙 정책이 생육 단계 1·2·4에 들어가는 평균 날짜(13.0·36.8·82.6일)에서 정했다.

| 구분 | 학습 | 평가 |
|---|---|---|
| 목적 | 정책이 여러 상황을 겪으며 배운다 | 완성된 정책들의 성적을 비교한다 |
| 감축 발생 | 75 % 확률 (a 정책은 0 %) | 조건마다 정해져 있다 (무감축 또는 감축) |
| 감축일 | 13~112일 중 랜덤 | 13·37·83일 고정 |
| 감축률 | 10~70 % 중 랜덤 | 20·40·60 % |

정책은 학습과 평가 모두 감축을 미리 알 수 없고 감축 당일에야 관측으로 안다. 날짜를 고정하는 쪽은 정책이 아니라 채점 조건이다.

날짜를 고정하는 이유는 세 가지다.

1. **공정한 비교.** 모든 정책이 같은 날씨·날짜·감축률을 겪어야 수익 차이를 정책 차이로 볼 수 있다.
2. **가설 검정.** H2는 이른 감축에서 공동 관리의 가치가 더 큰지 묻는다. 초기와 후기 조건이 나뉘어 있어야 C2(초기 − 후기)를 계산할 수 있다.
3. **조건별 해석.** 3시점 × 3감축률의 9조건으로 나누면 어떤 때 어떤 정책이 강한지 보인다. 랜덤 감축의 평균 하나로는 이 정보가 사라진다.

날짜의 랜덤성은 학습에서 이미 다루므로 평가는 고정한다(D14). 규칙 정책은 42일 전에 물을 거의 쓰지 않아 13일과 37일 감축 결과가 같지만, C2는 초기와 후기를 비교하므로 계산에 지장이 없다.

### 시즌 물 공급량 200 mm

이전 값 264 mm는 UFGA8201 전문가 일정의 합계였지만 규칙 정책 사용량(약 132 mm)의 두 배라 감축이 거의 제약이 되지 않았다. 200 mm는 규칙 정책 사용량의 95 % 분위수라 무감축에서는 거의 제약이 없고, 감축 후 물은 160·120·80 mm가 된다(9절 표).

### 감축률 20·40·60 %

제안서 설정에서 이어진 값이고, 선택 이유는 문서와 참고문헌에 없다. 학습 구간(10~70 %) 안에 있고 간격이 같아 감축률 추세(C1)를 계산하기 좋다는 것은 설계에서 추정한 이유다. 200 mm 기준으로 20 %는 평균 수익 손실이 작아 "거의 무손실" 조건에 가깝다.

### 작물에 필요한 최소 물

관수가 0이어도 검증 80시즌에서 작물 실패는 없었다(평균 곡실 3,645 kg/ha). 규칙 정책 기준으로 평균 수량 90 %에 약 106 mm, 95 %에 약 126 mm의 공급이 필요하고, 최저 수량까지 안정되려면 약 160 mm 공급이 필요하다(10절). 강수가 평균 488 mm여도 모래 토양이라 작물이 다 쓰지 못한다는 것은 해석이다.

### b0′의 예비 물

감축은 예고 없이 오므로 미리 대비해 물을 남기는 것은 불가능하고, b0′도 감축 전에는 규칙 정책과 똑같이 행동한다. 예비는 감축을 안 뒤의 배분 규칙이다. 남은 물이 규칙 정책의 남은 평균 수요보다 적을 때만 개화·등숙기 몫 58.6 mm를 떼어 둔다. 검증 40시즌에서 평균은 규칙 정책보다 낮고(804.1 대 814.9) 하위 10 % 평균은 높았다(433.1 대 394.8). 이득은 초기·중기 60 % 감축에 집중됐다.

### 예산 배율 제거

배율 0.6에서는 물 예산이 공급을 120 mm어치로 줄여 감축 없이도 규칙 정책 시즌의 절반 이상을 제약했고, 평가는 1.0만 쓰므로 학습과 평가 조건이 어긋났다. 그래서 학습·평가 모두 1.0으로 고정했다. 예산 변화에 대한 분석이 필요하면 다시 표집해 재학습해야 한다.

## 14. 공급량 재평가 (본 연구)

200 mm라는 공급량 가정에 결론이 얼마나 의존하는지 해석하기 위해 본 연구에 포함한다. `scripts/run_comparison.py`가 본 평가에 이어 실행하고 결과를 `water_supply_<mm>.json`에 저장한다.

| 변수 | 현재값 | 방식 | 근거 | 확인 |
|---|---|---|---|---|
| `scenarios.evaluation_survey_noise_std` | [0.05] | 민감도. 학습된 정책을 재학습 없이 조사 잡음만 키워 재평가 (주 분석 0.01) | 지시 | 읽음 | [x] |
| `scenarios.evaluation_supply_mm` | [120, 160] | 학습된 정책 재평가(앞쪽 300시즌, a-유 제외), 대비 계산, 물은 공급량만 제한 | 10절 측정, Kelly 2024 상한 실험 | [ ] |

재평가는 새 공급량에 맞춰 다시 학습한 결과가 아니다. 물 단가 0 재학습은 채택하지 않았다. 물 단가 기본값은 1.1 USD/mm/ha다.

## 15. 시비 값 점검 (2026-11-11, 진행 중)

### 질소량별 반응 (규칙 정책, 질소 예산 해제)

근거: `outputs/runs/20261110T230138Z_nitrogen_response_rule_policy_9e418a8e/verification.json`. 검증 80시즌(1000~1079), 공급 200 mm, 단계별 관수 규칙, 감축 없음. 질소 예산만 풀어 모든 일정을 다 줄 수 있게 했다.

| 일정 (파종 후 일: kg N/ha) | 총량 | 평균 곡실 | 평균 순수익 | 하위 10% | 관수 mm | 평균 N 스트레스 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---|
| 없음 | 0 | 1205 | 47.4 | −50.9 | 62.9 | 0.243 | [ ] |
| 45:27, 65:20, 85:10 | 57 | 4971 | 509.8 | 334.9 | 119.3 | 0.155 | [ ] |
| 45:54, 65:35, 85:27 (현재) | 116 | 7890 | 881.8 | 679.1 | 152.0 | 0.104 | [ ] |
| 40:27, 45:35, 80:54 (이전) | 116 | 7558 | 831.0 | 639.1 | 150.9 | 0.102 | [ ] |
| 45:80, 65:54, 85:40 | 174 | 9028 | 1002.5 | 753.1 | 162.3 | 0.056 | [ ] |
| 45:80, 65:80, 85:80 | 240 | 9114 | 962.0 | 696.9 | 163.8 | 0.031 | [ ] |

- 174 kg은 현재 116 kg보다 평균 순수익이 120.6 USD/ha 높고, 240 kg은 174 kg보다 낮다. 경제적 최적 총량은 이 두 값 사이일 가능성이 높다.
- 현재 질소 예산 91.64 USD는 116 kg어치라 규칙 정책과 학습 정책 모두 116 kg을 넘을 수 없다.
- 같은 116 kg에서 45·65·85일 일정이 40·45·80일보다 50.9 USD/ha 높다.

### 문헌 대조

| 변수 | 현재값 | 문헌 내용 | 판정 | 확인 |
|---|---|---|---|---|
| 시비 총량 상한 (예산) | 116 kg (91.64 USD) | Gautron 2022 전문가 일정과 UFGA8201 저질소 처리가 27+35+54=116 kg이다. Tao 2023 플로리다 학습 정책은 200 kg, 지침 기준선은 360 kg이었다 | 출처는 있으나 수익 최적보다 낮음 | [ ] |
| 질소 단가 | <mark>1.83 USD/kg (이전 0.79)</mark> | USDA AMS Alabama 주간 생산비 보고서 질산암모늄 2025년 48주 평균 565.2 USD/톤(27절). 이전 값은 Tao 2023 RF1 | 근거 있음 | [x] |
| 1회 시비 격자 | 0~80 kg, 9단계 | **결정(2026-11-11): 9단계 유지.** 제안서 근거는 옛 πB 27·35·54 kg 재현뿐이다. 문헌은 3~21단계로 다양하다(Kallenberg 0·20·40, Tao·Wu 0~160 40 간격, Baja 0~80 10 간격, Wang 0~200 10 간격). 탐색에서 최적 근처의 세밀한 단계 차이는 3 USD/ha 이내라 [0, 27, 54, 80]으로도 πB는 재현되지만, 학습 정책의 시즌별 양 조절 여지와 코드 수정 비용을 고려해 유지한다 | 부분 근거 | [x] |
| 시비 시기 | 45·65·85일 | Gautron 2022의 PPO는 화서 분화 시작(istage 2, 평균 37일) 무렵에 시비를 집중했다. Wu 2022 기준선은 V5 1회 | 부분 근거 | [ ] |
| 시비 작업비 | <mark>34.8 USD/회 (이전 5)</mark> | Iowa State 2026 위탁작업 조사 액비 곁거름 $14.10/acre. 생육 중(45·65·95일) 지상 시비 가정(27절) | 근거 있음 | [x] |
| 희소 초기 질량 | 0.03 | 시즌 3회 / 약 133일(0.023)과 같은 규모 | 부분 근거 | [ ] |
| 입력 상한 | 200 kg/일 | gym-DSSAT 범위 [0, 200] | 근거 있음 | [ ] |

### 시비 일정 탐색 (채택)

근거: `outputs/runs/20261110T230932Z_nitrogen_schedule_search_bc6b0f65/verification.json`. 3회 시비의 시기(1회차 35~55일, 2회차 55~75일, 3회차 75~95일)와 양(격자 9단계)을 질소 예산을 푼 상태로 검증 40시즌에서 좌표 탐색했다. 새 확인 80시즌(4300~4379)에서 판단했다.

| 항목 | 이전 (45:54, 65:35, 85:27) | 채택 (45:80, 65:54, 95:27) | 확인 |
|---|---:|---:|---|
| 총량 kg N/ha | 116 | 161 | [ ] |
| 평균 순수익 | 886.4 | 999.2 (+112.8, 95.9~129.4) | [ ] |
| 하위 10% 평균 | 695.1 | 712.0 | [ ] |
| 평균 곡실 kg/ha | 7821 | 8867 | [ ] |
| 평균 관수 mm | 147.8 | 160.8 | [ ] |

감축 조건 차이(결과 보고만, 40시즌)는 +59.5~+107.2였고 초기·중기 60 %만 −8.4(−38.2~22.3)였다. 1회차 80 kg은 격자 최대값, 3회차 95일은 시기 범위의 끝이다(90일과 1.5 USD/ha 차이).

### 새 시비 일정 기준 연쇄 재측정

- 단계 진입일은 변하지 않았다(`20261110T233443Z_stage_entry_rule_policy_6c9d5374`). 감축일 근거는 그대로다.
- 감축 없을 때 πB 시즌 관수량은 평균 161.7 mm(중앙 165, 95 % 200)이고 시즌의 19.2 %가 200 mm 한도에 닿는다. 감축 후 160·120·80 mm를 넘는 시즌은 52.5·86.7·98.3 %다.
- 공급량별 평균 순수익(`20261110T233531Z_water_response_rule_policy_d7c0be90`): 120 mm 900.4, 160 mm 977.3, 200 mm 998.1.

| 조건 (검증 40시즌, `20261110T234153Z_reduction_rule_comparison_0b51ad32`) | πB | b0′ |
|---|---|---|
| 초기·중기 20 % | 1009.3 / 635.2 | 961.9 / 526.5 |
| 초기·중기 40 % | 913.6 / 257.1 | 840.5 / 414.0 |
| 초기·중기 60 % | 678.2 / −59.9 | 687.0 / 203.6 |
| 후기 20 % | 1019.8 / 711.3 | 1012.6 / 664.8 |
| 후기 40 % | 1011.4 / 667.7 | 996.8 / 626.1 |
| 후기 60 % | 982.3 / 568.2 | 950.6 / 552.1 |
| 9조건 평균 | 912.9 / 401.3 | 882.1 / 459.0 |

초기 20 % 감축 뒤 남는 160 mm가 남은 평균 수요 161.0 mm보다 1 mm 적어, b0′가 20 % 감축에서도 예비를 적용한다.

## 16. 방제 구현·타당성·값 점검 (2026-11-11)

### 구현 요약

| 단계 | 구현 | 위치 |
|---|---|---|
| 유입 | 시즌 시작 전에 날짜별 유입 배열을 생성(확률 0.03, 크기 0.05). 살포와 무관하게 고정 | `exogenous.py` |
| 밀도 | 하루 말에 (1−살포효과)×[밀도 + g(T)×밀도×(1−밀도) + 유입], 0~1로 제한. T = (Tmin+Tmax)/2 | `pests.py` `PestState.advance` |
| 증식률 | g(T) = 0.05 + 0.10×(T−10)/20, 10 °C 이하 0.05, 30 °C 이상 0.15 | `pests.py` `growth` |
| 살포 효과 | 0.8×exp(−경과일/5), 마지막 살포 기준, 누적 없음 | `pests.py` |
| 잎 피해 | 하루 손실 비율 = 0.03×밀도. DSSAT의 잎 건물중·녹색 엽면적에서 같은 비율을 실제로 제거하고 반출 질소·건물중을 회계. 생육 단계 제한 없음 | `online_pests.py`, `leaf_diagnostics.py` |
| 조사 | 파종 후 7의 배수 일 아침, 최근 7일 평균 손실/0.03(= 평균 밀도) + 0.01×표준정규, 0~1로 제한 | `pests.py` `DamageSurvey` |
| 살포 제한 | istage 5 미만, 직전 살포 후 7일 이상, 예산 150 USD(회당 50 USD, 시즌 3회) | `resources.py` |
| 규칙 방제 | 조사값이 있고 0.30 이상이며 마스크가 허용하면 살포 | `policies.py` `RulePolicy` |

### 현재 설정에서의 측정 (규칙 정책, 검증 80시즌)

근거: `outputs/runs/20261111T002546Z_pest_control_rule_policy_503ef94e/verification.json`. 공급 200 mm, 단계별 관수, 161 kg 시비, 감축 없음.

| 변형 | 평균 순수익 | 하위 10% | 평균 곡실 | 평균 살포 | 평균 밀도 | 최고 밀도 평균 | 일 잎 손실 합 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 해충 없음 | 1094.2 | 844.9 | 9176 | 0 | 0 | 0 | 0 | [ ] |
| 규칙 (임계 0.3) | 998.1 | 753.2 | 8920 | 1.24 | 0.19 | 0.80 | 0.67 | [ ] |
| 임계 0.1 | 996.2 | 745.3 | 9096 | 1.74 | 0.12 | 0.74 | 0.42 | [ ] |
| 임계 0.5 | 995.8 | 770.4 | 8804 | 0.96 | 0.25 | 0.88 | 0.93 | [ ] |
| 무방제 | 789.0 | 590.1 | 6981 | 0 | 0.57 | 0.96 | 2.18 | [ ] |

- 방제의 가치는 무방제 대비 +209.1 USD/ha이고, 방제 후에도 해충 없음보다 96.1 USD/ha 낮다.
- 임계 0.1~0.5의 평균 차이는 2.3 USD/ha 이내로 평탄하다. 0.3 유지에 문제가 없다.
- 규칙(0.3)의 살포는 시즌 0회 12, 1회 37, 2회 31이고 3회는 없었다. 살포일 분위수는 5 % 28일, 중앙 49일, 95 % 91일이다.
- 최고 밀도의 95 % 분위수가 1.0이라 대부분의 시즌에서 해충이 상한까지 증식한다. 무방제 시즌의 일 손실 합 2.18은 재생장을 빼면 잎의 약 89 %를 제거하는 크기다.

### 타당성 판단

| 항목 | 판단 | 근거 | 확인 |
|---|---|---|---|
| DSSAT 잎 피해 전달 | 기술적으로 타당 | 잎 건물중·녹색 엽면적 감소와 반출 회계를 실제 Fortran 상태에서 검산(`verify_leaf_accounting`) | [ ] |
| 날짜·외생 대응 | 타당 | 유입·조사 난수를 미리 생성해 살포 여부와 무관, 정책 간 같은 시즌 공유 | [ ] |
| 해충 개체군 | 정성적 모형 | 자연 사망·이출이 없고 밀도 상한 1에서 포화한다. 보정 자료 없음(FAW_PARAMETER_SENSITIVITY.md) | [ ] |
| 피해 시기 | 한계 | 모든 생육 단계에서 잎을 제거한다. Blanco 2022·2023은 V7 이전 적엽(66 %, 반복)에서 수량 감소가 없었고, Abang 2024는 약 50 % 적엽부터 건기에만 유의한 손실을 보고했다 | [ ] |
| 조사 정보 | 낙관적 | 잡음 0.01이라 사실상 7일 지연된 평균 밀도를 그대로 본다. 공개 자료에서 반복 판독 오차를 확보하지 못했다 | [ ] |
| 물×해충 상호작용 | 없음 | 살포 효과가 수분 상태와 무관하다. Real-Santillán 2024는 수분 스트레스가 바이러스 방제 효능을 낮췄다고 보고했으나 화학 약제에 그대로 적용할 근거는 없다 | [ ] |
| 연구 사용 범위 | 실험용 | `research_ready=false`, H3는 피해·회복 검증 통과 범위에서만 해석 | [ ] |

### 값 점검

| 변수 | 현재값 | 문헌·측정 | 판정 | 확인 |
|---|---|---|---|---|
| 유입 확률·크기 | 0.03, 0.05 | 보정 자료 없음. 이전 민감도(1.5·6 %)에서 방제 순위는 유지 | 미보정 | [ ] |
| 증식률 범위 | 0.05~0.15/일 | 보정 자료 없음. 측정상 대부분 시즌에서 밀도 상한 도달 | 미보정 | [ ] |
| 온도 기준 | 10, 30 °C (코드 고정, 설정 null) | Du Plessis 2020: 발육 하한 알 13.0, 유충 12.1, 알~성충 13.1 °C, 최적 26~30 °C. 발육률이며 개체군 증가율이 아니다 | 상한은 일치, 하한은 2~3 °C 낮음 | [ ] |
| 살포 효능·잔효 | 0.8, 5일 | 포장 자료 없음 | 미보정 | [ ] |
| 피해 계수 α | 0.03 | 실제 신규 손실 측정 자료 없음 | 미보정 | [ ] |
| 조사 잡음 | 0.01 (코드 고정, 설정 null) | 자료 없음. 이전 민감도 0.05에서 하위 10 % 수익 감소 | 낙관적 가정 | [ ] |
| 조사 주기·창 | 7일, 7일 (코드 기본값) | 제안서 설계 | 설계 | [ ] |
| 방제 임계 | 0.3 | 측정상 0.1~0.5 평탄. Overton 2021: 경제적 임계는 문헌에 없고 행동 임계는 감염주율(예: 15 %)로 보고돼 척도가 다르다 | 유지 | [ ] |
| 살포비 | <mark>24.7+24.7 = 49.4 USD/회 (이전 35+15)</mark> | Alabama 2026 예산서 살충제·항공 살포 각 $10/acre(27절). 곡실(건물) 264 kg/ha와 같은 값 | 근거 있음 | [x] |
| 살포 예산 | 150 USD (3회) | 규칙 정책 최대 사용 2회 | 구속하지 않음 | [ ] |
| 살포 간격·단계 | 7일, istage 5 미만 | 설계 | 설계 | [ ] |
| 희소 초기 질량 (살포) | 0.03 | 규칙 1.24회/133일(0.009)보다 크다 | 부분 근거 | [ ] |

## 17. 방제 개선 (2026-11-11, 진행 중)

### 1. 해충 계수 출처 일원화 (완료)

학습·평가·측정 스크립트 9곳의 고정값 `PestParameters(10, 30)`, 잡음 0.01을 `pest_settings(config)`로 바꿨다. 설정의 온도 기준 10·30 °C와 조사 잡음 0.01을 null에서 같은 값으로 채웠다. 조사 주기·창은 온라인 제어기에 연결되지 않아 설정값이 7일이 아니면 실행을 거부한다. 동작은 바뀌지 않았고 테스트로 확인했다.

### 3. 초기 적엽 반응 (가중치 불필요)

근거: `outputs/runs/20261111T005434Z_early_defoliation_check_37db0257/verification.json`. Blanco 2022는 V1-V2·V3-V4에서 33·66 % 적엽해도 수량이 줄지 않았다. 사전 기준은 DSSAT 수량비 1.0 ± 0.10(단 B 허용폭)이다. 단 B와 같은 16시즌·관리를 썼다.

| 시점·적엽률 | 평균 수량비 | 범위 | 판정 | 확인 |
|---|---:|---|---|---|
| V2 33 % | 0.999 | 0.985~1.002 | 통과 | [ ] |
| V2 66 % | 0.999 | 0.986~1.002 | 통과 | [ ] |
| V4 33 % | 1.001 | 0.997~1.006 | 통과 | [ ] |
| V4 66 % | 1.000 | 0.990~1.011 | 통과 | [ ] |
| V6 66 % | 1.004 | 0.989~1.023 | 통과 | [ ] |

DSSAT가 초기 적엽의 무손실을 이미 재현하므로 단계별 피해 가중치를 넣지 않는다. CERES vstage는 잎 끝 기준이라 현장 단계보다 약 두 잎 이르다.

### 2. 피해 계수 α

근거: `outputs/runs/20261111T005522Z_pest_severity_alpha_5451bc0c/verification.json`. 무방제 적엽 강도 = 1 − LAI/해충 없는 쌍둥이 시즌 LAI. 사전 규칙: 시즌 최대 강도 중앙값이 25 %에 가장 가깝고 50 % 초과 시즌이 10 % 이하인 α(Hruska 2019, Abang 2024 인용: "50 %를 넘는 경우가 드물고 보통 25 % 정도").

| α | 최대 강도 중앙값 | 50 % 초과 | 평균 강도 중앙값 | 수량 손실 중앙값 | 상위 10 % | 확인 |
|---:|---:|---:|---:|---:|---:|---|
| 0.03 | 81 % | 88 % | 45 % | 27.1 % | 34.4 % | [ ] |
| 0.02 | 69 % | 85 % | 36 % | 14.5 % | 22.2 % | [ ] |
| 0.015 | 59 % | 83 % | 29 % | 8.2 % | 15.4 % | [ ] |
| 0.01 | 45 % | 13 % | 21 % | 4.9 % | 11.9 % | [ ] |
| 0.0075 | 37 % | 0 % | 16 % | 3.3 % | 8.9 % | [ ] |
| 0.005 | 27 % | 0 % | 11 % | 2.3 % | 8.3 % | [ ] |

사전 규칙은 0.005를 고른다. 비교 문헌: Abang 2024 우기 수량 손실 4.5~11.7 %, 건기 5.9~53.8 %, 현장 시험 대부분 20 % 미만.

| α (`measure_pest_control`, 80시즌) | 규칙 0.3 | 무방제 | 임계 0.5 | 해충 없음 | 살포가 이득인 시즌 | 확인 |
|---|---:|---:|---:|---:|---:|---|
| 0.005 | 1031.2 | 1063.6 | 1043.0 | 1094.2 | 12.5 % | [ ] |
| 0.01 | 1024.7 | 1026.8 | 1035.3 | 1094.2 | 36.2 % | [ ] |

근거: `20261111T011817Z_pest_control_rule_policy_b0c12383`(0.005), `20261111T012048Z_pest_control_rule_policy_6d9c6c84`(0.01).

**결정(2026-11-11): α = 0.01 (임의 결정).** 결과를 보기 전에 정한 규칙은 0.005를 골랐으나, 결과를 본 뒤 아래 이유로 0.01을 택했다. 사전 규칙에서 벗어난 결정이다.

| 이유 | 근거 문헌·측정 |
|---|---|
| "보통 25 % 정도"를 시즌 최대값이 아니라 평균 적엽으로 읽으면 0.01(평균 21 %)이 가깝고, 50 % 초과 시즌 13 %는 "드물다"에 해당한다 | Abang et al. 2024, J. Econ. Entomol. 117(6), Hruska 2019 인용: FAW 적엽은 50 %를 넘는 경우가 드물고 보통 25 % 정도 |
| 수량 손실 중앙값 4.9 %, 상위 10 % 11.9 %가 우기 손실 범위와 일치한다(0.005는 2.3 %로 낮다) | Abang et al. 2024 표 2: 우기 손실 4.5~11.7 %, 건기 5.9~53.8 %. 같은 논문 서론: 현장 시험 대부분 20 % 미만 |
| 살포가 이득인 시즌 36 %, 평균 손익분기로 방제 결정이 비자명하다(0.005는 13 %, 무방제가 평균 32.4 USD/ha 우위) | 제안서 11쪽 검증 기준 "가격·피해 범위에서 살포 순이익이 양·음인 조건의 존재 확인" |
| 피해 정도가 단 B에서 허용 범위로 확인된 적엽 33~66 % 안에 대부분 머문다(최대 강도 상위 10 % 50.8 %) | `20261109T232350Z_damage_recovery_tier_b_643c4968`: 99 % 적엽만 허용 범위 밖 |

남는 한계: α는 여전히 보정값이 아니라 문헌 범위에 맞춘 가정이다. 같은 α에서 방제 임계 0.5(1035.3)가 0.3(1024.7)보다 높았으나 확인 시즌에서 검증하지 않아 0.3을 유지한다.

### 4. 검증 범위 확인과 연쇄 재측정

- 단 B는 DSSAT의 적엽 반응을 시험하므로 해충 계수를 바꿔도 판정이 달라지지 않아 다시 판정하지 않았다. 대신 해충 피해가 단 B 허용 범위(적엽 33~66 %) 안에 머무는지 확인했다. α 0.01에서 무방제 최대 적엽 강도 중앙값 45 %, 상위 10 % 50.8 %로 99 % 적엽(허용 범위 밖) 영역에 들어가지 않는다.
- 단계 진입일은 변하지 않았다(`20261111T013338Z_stage_entry_rule_policy_e13f0fee`). 감축 없을 때 πB 시즌 관수량 평균 165.8 mm, 시즌의 23.3 %가 200 mm 한도에 닿는다. 감축 후 160·120·80 mm를 넘는 시즌은 60.8·88.3·97.5 %다.
- b0′ 값: 예비 84.0 mm, 관수 간격 9.3일, 남은 수요 시작값 165.2 mm.

### b0′ 여유 비율 (임의 결정: 기준에 여유 두기)

여유 비율 m: 남은 물이 m × 남은 평균 수요보다 적을 때만 예비를 쓴다. 목표는 감축 9조건 평균 순수익. 탐색 40시즌(3100~3139).

| m | 1.0 | 0.9 | 0.8 | 0.7 | 0.6 | 0.5 | **0.4** | 0.3 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 9조건 평균 | 887.5 | 900.8 | 919.0 | 925.4 | 929.5 | 946.9 | **949.6** | 944.5 | [ ] |
| 하위 10 % | 490.7 | 502.4 | 528.5 | 516.7 | 524.5 | 532.6 | 531.2 | 521.8 | [ ] |

0.6이 범위 끝이어서 0.3~0.5를 추가했다(`20261111T013531Z_reduction_margin_tuning_e3ebf3ec`, `20261111T015158Z_reduction_margin_tuning_4edce9d5`). 새 확인 40시즌(3300~3339)에서 m = 0.4의 결과:

| 조건 | πB | b0′ | 확인 |
|---|---:|---:|---|
| 초기·중기 20 % | 974.6 | 979.9 | [ ] |
| 초기·중기 40 % | 873.0 | 856.7 | [ ] |
| 초기·중기 60 % | 661.4 | 744.0 | [ ] |
| 후기 20 % | 994.3 | 995.2 | [ ] |
| 후기 40 % | 971.5 | 974.4 | [ ] |
| 후기 60 % | 925.0 | 921.5 | [ ] |
| 9조건 평균 / 하위 10 % | 878.8 / 433.4 | 894.7 / 494.9 | [ ] |

### 살포 효능 0.8·잔효 5일: 가정으로 유지 (2026-11-11 임의 결정)

**값의 출처.** 제안서 8쪽 해충 매개변수 표의 초기 가정값이다("e, τ₀ 0.8, 5일 — 검증 방향: 선택한 화학 약제의 살충·잔효 자료"). 제안서에 인용 문헌은 없다.

**가정으로 두는 이유.**

| 이유 | 내용 | 확인 |
|---|---|---|
| 맞는 자료를 찾지 못함 | 잎 살포 포장 시험의 살포 후 일자별 방제가(대조구 포함)가 필요하다. 2026-11-11 조사에서 검색 1회는 도구 정책 필터로 거부됐고, 후보 논문 2편(Sisay et al. 2019, Insects 10(2):45; Florida Entomologist 103(2) 인도 포장 시험)은 원문을 읽지 못했다. 이전 조사(FAW_PARAMETER_SENSITIVITY.md)에서도 Masii는 처리 배정만, Varella는 무살충 시험이었다 | [ ] |
| 찾은 자료는 방식이 다름 | 검색된 잔효 자료는 대부분 종자 처리(잎 생물검정 16~46일 보호)로, 침투 이행 방식이라 잎 살포의 잔효로 쓸 수 없다 | [ ] |
| 모형 단위 문제 | 모형의 밀도는 0~1 지수이고 문헌은 유충 수·감염주율·방제가(Henderson–Tilton 등)로 보고하므로, 자료가 있어도 환산 가정이 필요하다 | [ ] |
| 결과 민감도는 확인됨 | 이전 진단(PEST_SURVEY_EFFICACY_SENSITIVITY.md)에서 효능 0.8 → 0.6으로 낮춰도 방제 규칙 비교의 차이가 모두 95 % 구간에 0을 포함했다 | [ ] |

**이 가정이 뜻하는 것.** 살포한 날 밀도의 80 %를 줄이고, 이후 k일째에도 0.8·exp(−k/5)만큼(1일 65.5 %, 3일 43.9 %, 7일 19.7 %, 14일 4.9 %) 매일 추가로 줄인다. 해충 증식을 빼고 계산하면 살포 후 3일까지 밀도가 처리 전의 약 2 %로 떨어지는 강한 방제다. 이후 재유입으로 다시 늘어난다. 여러 번 살포해도 효과는 누적되지 않는다(제안서 8쪽).

**보완.** 효능·잔효는 민감도 조건으로 다룬다(예: 효능 0.6, 잔효 2.5·10일). 원문(PDF)이 `MARS_reference`에 추가되면 일자별 방제가를 추출해 위 식과 대조한다.

### 해충 적엽과 물 절약 경로 (2026-11-11)

**질문.** 초기 적엽은 수량을 줄이지 않고(위 3번) 엽면적이 줄면 증산이 줄어드니, PPO가 살포를 미뤄 해충으로 물을 아끼는 전략을 학습할 수 있는가.

**기록 항목 추가(본학습 해석용).** `run_comparison.py`의 평가 기록에 칸·조건별 생육단계별 살포 횟수, V7 이전 살포 횟수, 감축 전 살포 횟수, 시즌 증산량(ep 합)을 추가했다(`baseline_evaluation.py`의 결정 기록에 vstage·ep 추가). 짧은 전 과정 실행(`20261111T063140Z_policy_comparison_b87a7f6b`)에서 기록 생성과 기존 검산 통과를 확인했다.

**DSSAT 확인.** 근거: `outputs/runs/20261111T062911Z_damage_water_path_a58e1f21/verification.json`. 검증 40시즌(1200~1239), 규칙 정책, α 0.01. 해충 없음 대비 차이다.

| 감축 조건 | 무방제 물 절약 mm | 무방제 수량 손실 | 무방제 증산 변화 mm | 무방제 토양 증발 변화 mm | 무방제가 해충 없음보다 순수익이 높은 시즌 | 확인 |
|---|---:|---:|---:|---:|---:|---|
| 없음 | 11.4 | 5.0 % | −26.8 | +18.2 | 10 % | [ ] |
| 초기 40 % | 1.3 | 2.4 % | −18.7 | +14.9 | 28 % | [ ] |
| 초기 60 % | 0.0 | 1.5 % | −17.2 | +13.7 | 45 % | [ ] |

- **초기 적엽 경로는 작다.** V7 이전 누적 잎 손실은 0.019로, 해충은 대부분 V7 이후에 피해를 준다(무방제 0.732). "초기에만 먹게 두기" 변형은 V7에 살포해도 이후 0.218의 손실이 남아 초기 효과만 분리되지 않았다.
- **물 감축 시 절약은 사라진다.** 감축된 물을 결국 다 쓰기 때문에 관수 절약이 0~1.3 mm다. 대신 같은 물에서 증산이 줄고 토양 증발이 늘어, Fereres 2007의 지적(엽면적 감소가 증발 비중을 키워 절약을 상쇄)과 같은 방향이다.
- **피해 영향은 물이 부족할수록 작다.** 수량 손실이 5.0 → 2.4 → 1.5 %로 줄었다. Oveysi 2010의 V8 적엽 손실(완전 관수 19.2 %, 물 부족 14.8 %)과 같은 방향이다.
- **주의.** 초기 60 % 감축에서는 무방제가 해충 없음보다 순수익이 높은 시즌이 45 %였다(평균은 −23.4 USD/ha). 엽면적 감소가 토양 물을 아껴 후반에 쓰게 하는 효과로 보인다. 문헌은 물 부족에서도 적엽이 수량을 줄인다고 보고하므로(Oveysi 2010 14.8 %, Santos 2018), 이 이득은 모형이 과장할 수 있다. PPO가 극심한 감축에서 살포를 줄이는 행동을 보이면 이 경로의 기여를 위 기록 항목으로 분리해 해석한다.

### 방제 임계 재조정 (채택)

근거: `outputs/runs/20261111T070152Z_spray_threshold_search_1b660962/verification.json`. α 0.01 기준. 감축 없는 검증 40시즌(4000~4039)에서 임계 0.1~0.8을 비교하고, 겹치지 않는 80시즌(4400~4479)에서 사전 기준(평균 차이 95 % 구간 > 0)으로 판단했다.

| 임계 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | **0.7** | 0.8 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 평균 순수익 | 1022.6 | 1040.3 | 1040.6 | 1050.2 | 1060.1 | 1062.1 | **1067.1** | 1063.7 | [ ] |
| 평균 살포 | 1.52 | 1.20 | 1.07 | 0.90 | 0.72 | 0.70 | 0.68 | 0.68 | [ ] |

확인 80시즌: 0.3 998.1 → 0.7 1008.6, 차이 +10.5 USD/ha(2.0~20.2), 하위 10 % 751.1 → 766.9, 살포 1.30 → 0.89회. 감축 9조건(결과 보고만, 40시즌)에서도 +8.4~+15.2 USD/ha였다. 해충 피해를 문헌 범위로 낮춘 뒤라 해충이 많을 때만 살포하는 편이 낫다. b0′도 같은 방제 규칙을 쓴다.

연쇄 재측정(`20261111T071023Z_stage_entry_rule_policy_454db302`): 단계 진입일 불변, πB 시즌 관수량 164.3 mm, 200 mm 한도 도달 21.7 %, b0′ 예비 83.5 mm·간격 9.4일·남은 수요 163.6 mm. 여유 비율 0.4는 재탐색하지 않았다(값 변화 1 mm 내외).

### 조사 잡음 민감도 (임의 결정)

`scenarios.evaluation_survey_noise_std: [0.05]`. 공급량 민감도와 같이 학습된 정책을 재학습 없이 조사 잡음만 0.05로 키워 다시 평가하고 `survey_noise_0.05.json`에 결과표·보조 기록·대비를 남긴다. 다른 민감도 후보(살포비, 효능·잔효)는 넣지 않았다.

## 18. 학습 설정 점검 B (2026-11-11, 진행 중)

### B1 희소 초기 질량

| 행동 | 현재 초기 비영 확률 | 정책 0의 실제 비영 행동 빈도 | 근거 | 확인 |
|---|---:|---:|---|---|
| 관수 | 0.13 | 0.079 (시즌 10.5회 / 132.8일) | `20261111T071023Z_stage_entry_rule_policy_454db302` | [ ] |
| 시비 | 0.03 | 0.023 (3회 / 132.8일) | 규칙 일정 | [ ] |
| 살포 | 0.03 | 0.0067 (0.89회 / 132.8일) | `20261111T070152Z_spray_threshold_search_1b660962` 확인 시즌 | [ ] |

관수는 규칙보다 1.6배, 살포는 4.5배 높다. 초기 확률은 탐색량만 정하고 최적 정책을 바꾸지 않는다. Tao 2023(부분관측 RL의 무투입 수렴)과 Balderas 2025(혼합 과제 PPO의 무관수)를 고려해 탐색 여유를 둔 값으로 보고, 시험 학습에서 무투입 수렴이 생기는지 본 뒤 정한다. 수렴 문제가 생기면 제안서 10쪽의 대안(규칙 궤적 행동 복제 후 PPO 미세조정)을 검토한다.

### B2 보상 계수 η

- 잠재함수 Φ = 곡실 단가 × η × 지상부 건물중이고 γ = 1이라, Ng 1999(MARS_reference)에 따라 η는 최적 정책을 바꾸지 않고 학습 신호의 모양만 바꾼다. 이전 확인(REWARD_ETA_SENSITIVITY.md)에서 η 0~0.9 모두 수확까지 학습 보상 합이 원수익/1,000과 일치했고, η 0.45의 일별 보정 크기는 4.5~6.3 USD/ha였다.
- η 0.45는 옥수수 수확지수 수준의 구현 가정이다. 같은 의미를 유지하려면 현재 환경의 실제 수확지수(성숙 시 건조 곡실 / 지상부 건물중)로 맞추는 것이 근거가 더 분명하다. 시험 학습이 끝난 뒤 검증 시즌에서 측정한다.

### 시험 학습·처리량·수확지수 (A1·A2·A4·B2·B3)

**시험 학습** (정책 b1, 시드 0, 병렬 환경 8, n_steps 64·배치 64·에폭 2, 검증 16시즌, 순수익 USD/ha, 최대확률 / 확률 행동):

| 단계 | λ 0.95 감축 없음 | λ 0.95 초기 40 % | λ 0.98 감축 없음 | λ 0.98 초기 40 % | 확인 |
|---:|---|---|---|---|---|
| 5만 | 370.5 / 670.2 | 370.5 / 416.3 | 370.5 / 370.5 | 370.5 / 370.5 | [ ] |
| 15만 | 932.6 / 924.6 | 780.9 / 809.8 | 370.5 / 775.0 | 370.5 / 480.1 | [ ] |
| 31만 | 876.9 / 885.5 | 765.9 / 776.4 | 1048.7 / 933.2 | 903.5 / 716.0 | [ ] |
| 36만 | 802.6 / 794.9 | 715.1 / 709.1 | 370.5 / 913.8 | 370.5 / 779.0 | [ ] |
| 46만 | 813.9 / 830.3 | 801.6 / 823.3 | 928.4 / 1010.7 | 818.6 / 873.2 | [ ] |
| 51만 | 960.0 / 953.7 | 819.9 / 822.2 | 1001.7 / 1012.4 | 817.5 / 648.5 | [ ] |

정책 0: 1028.0 / 838.8. 근거: `20261111T091615Z_pilot_b1_s0_377b7d3c`(λ 0.95), `20261111T102954Z_pilot_b1_s0_5351fb9b`(λ 0.98). 370.5는 관수를 전혀 하지 않는 행동이다.

- PPO는 배우지만 51만 단계에서 수렴하지 않았고 점검마다 크게 흔들린다. 감축 없음에서는 정책 0에 못 미치고, 초기 40 %에서는 비슷한 수준까지 온다.
- λ 0.98은 최대확률 행동이 여러 번 무관수(370.5)로 무너졌다. λ 0.95는 그런 붕괴가 15만 단계 이후 없었다. 시드 하나라 근거는 약하다.
- 최대확률과 확률 행동은 λ 0.95에서 거의 같았고, λ 0.98에서는 최대확률이 무너질 때 확률 행동이 더 안정적이었다.

**처리량** (`20261111T102110Z_throughput_35218504`, 초당 단계, 12,288단계 측정):

| 병렬 환경 | 4 | 8 | 12 | 확인 |
|---|---:|---:|---:|---|
| 로그를 프로젝트 폴더에 기록 | 141.3 | 162.3 | 164.9 | [ ] |
| 로그를 컨테이너 내부에 기록 | 139.9 | 165.9 | 178.2 | [ ] |

로그 위치의 영향은 12환경에서 8 % 정도로 작다. 환경을 늘려도 처리량이 거의 오르지 않아, CPU(6코어 12스레드)가 한계로 보인다(해석). 최대 약 178단계/초면 현재 계획 6억 단계는 약 39일이다.

**수확지수** (`20261111T102933Z_harvest_index_5699ad20`, 규칙 정책, 검증 40시즌): 성숙 시 곡실/지상부 건물중 평균 0.514 (5 % 0.463, 95 % 0.562). 현재 η 0.45보다 높다.

**결정 (2026-11-11, 임의): η 0.45 유지, GAE λ 0.95 유지.**
- η: 측정 수확지수 0.514는 0.51로 바꿀 근거가 되지만, 잠재함수 보상 보정(Ng 1999, γ = 1)이라 η는 최적 정책과 시즌 보상 합을 바꾸지 않는다. 그래서 이미 쓴 시험 학습과 설정 해시를 유지하는 쪽을 택했다. 0.45와 0.51의 차이는 일별 보정 크기에만 약 13 % 영향을 준다(해석).
- λ: 시험 학습에서 λ 0.98은 최대확률 행동이 무관수(370.5)로 여러 번 무너졌고, λ 0.95는 15만 단계 이후 그런 붕괴가 없었다(시드 1개).

### B3 학습 설정 시험 (진행 중)

λ 0.95에서 n_steps 64→256, 배치 64→256, 에폭 2→10으로 바꿔 같은 51만 단계·같은 검증 시즌으로 비교한다. 업데이트당 자료가 4배로 늘고 같은 자료를 더 여러 번 학습해, 점검마다 흔들리는 문제가 줄어드는지 본다. `scripts/pilot_learning_curve.py`에 `--n-steps`, `--batch-size`, `--n-epochs` 옵션을 추가했다(기본값은 설정 파일).

근거: `20261111T115521Z_pilot_b1_s0_da85f87f`. 정책 b1, 시드 0, 병렬 환경 8, λ 0.95, 검증 16시즌, 순수익 USD/ha, 최대확률 / 확률 행동.

| 단계 | 기존(64·64·2) 감축 없음 | 기존 초기 40 % | 변경(256·256·10) 감축 없음 | 변경 초기 40 % | 확인 |
|---:|---|---|---|---|---|
| 5만 | 370.5 / 670.2 | 370.5 / 416.3 | 927.8 / 835.0 | 432.8 / 298.7 | [ ] |
| 10만 | 159.3 / 115.7 | 175.3 / 169.9 | 840.1 / 787.0 | 764.8 / 496.5 | [ ] |
| 15만 | 932.6 / 924.6 | 780.9 / 809.8 | 1002.3 / 716.7 | 553.1 / 396.5 | [ ] |
| 20만 | 824.8 / 863.2 | 414.8 / 343.1 | 996.9 / 764.0 | 693.1 / 417.2 | [ ] |
| 26만 | 683.8 / 681.6 | 701.2 / 726.8 | 964.5 / 747.3 | 641.4 / 439.7 | [ ] |
| 31만 | 876.9 / 885.5 | 765.9 / 776.4 | 944.6 / 868.9 | 762.7 / 562.3 | [ ] |
| 36만 | 802.6 / 794.9 | 715.1 / 709.1 | 1013.1 / 858.6 | 618.5 / 400.2 | [ ] |
| 41만 | 874.9 / 895.1 | 848.8 / 857.8 | 958.7 / 849.6 | 796.0 / 626.7 | [ ] |
| 46만 | 813.9 / 830.3 | 801.6 / 823.3 | 994.7 / 887.6 | 840.8 / 766.1 | [ ] |
| 51만 | 960.0 / 953.7 | 819.9 / 822.2 | 1037.7 / 898.8 | 796.4 / 551.8 | [ ] |
| 마지막 4개 평균(최대확률) | 862.9 | 796.4 | 1001.1 | 762.9 | [ ] |

정책 0: 1028.0 / 838.8. 처리량: 기존 139~150, 변경 138~144단계/초로 비슷하다.

- 감축 없음: 변경 설정은 무관수 붕괴가 한 번도 없었다. 15만 단계 이후 최대확률 945~1038로 좁게 움직였고, 51만에서 정책 0(1028.0)과 비슷한 수준이다. 기존보다 분명히 안정적이다.
- 초기 40 %: 553~841로 여전히 흔들린다. 마지막 4개 평균은 기존과 비슷하거나 조금 낮고(762.9 vs 796.4), 정책 0(838.8)에 못 미친다. 감축 대응은 51만 단계로는 아직 덜 배웠다(해석).
- 변경 설정에서는 확률 행동이 최대확률보다 꾸준히 낮다. 정책이 덜 뾰족해 탐색이 남아 있다는 뜻으로 보인다(해석). 평가 방식이 최대확률(`deterministic_policy: true`)이라 비교에는 영향이 없다.
- 시드 1개, 검증 16시즌이라 근거는 약하다.

**결정 (2026-11-11, 임의): n_steps 256 · batch_size 256 · n_epochs 10, 병렬 환경 8로 변경.**

세 값의 뜻과 두 설정의 차이 (병렬 환경 8 기준):

| 항목 | 64·64·2 (기존) | 256·256·10 (채택) |
|---|---:|---:|
| n_steps: 환경 하나가 정책을 고치기 전까지 진행하는 날 수 | 64일 (시즌 절반쯤) | 256일 (시즌 약 2개) |
| batch_size: 경사 계산 한 번에 쓰는 자료 수 | 64 | 256 |
| n_epochs: 모은 자료를 반복 학습하는 횟수 | 2 | 10 |
| 업데이트 한 번에 모으는 자료 | 512일 (시즌 약 4개) | 2,048일 (시즌 약 15개) |
| 업데이트 한 번의 경사 계산 횟수 | 16 | 80 |
| 51만 단계 동안 업데이트 횟수 | 1,000 | 250 |

시험 학습 비교 요약 (최대확률 행동, 순수익 USD/ha, 위 단계별 표에서 계산):

| 지표 | 64·64·2 | 256·256·10 | 정책 0 |
|---|---:|---:|---:|
| 감축 없음, 마지막 4개 점검 평균 | 862.9 | 1001.1 | 1028.0 |
| 감축 없음, 51만 단계 | 960.0 | 1037.7 | 1028.0 |
| 감축 없음, 15만 단계 이후 범위 | 683.8~960.0 | 944.6~1037.7 | – |
| 초기 40 %, 마지막 4개 점검 평균 | 796.4 | 762.9 | 838.8 |
| 감축 없음 최대확률 붕괴 (400 미만) 횟수 | 2 (5만 370.5 무관수, 10만 159.3) | 0 | – |
| 처리량 (단계/초) | 139~150 | 138~144 | – |

이유:
1. **안정성:** 256·256·10은 무관수 붕괴가 한 번도 없었다. 감축 없음에서 15만 단계 이후 변동 폭이 약 93 USD/ha로, 기존(약 276)의 3분의 1이다. 본 비교는 적합마다 최종 체크포인트 하나를 평가하므로, 점검마다 크게 흔들리면 결과가 끝난 시점의 운에 좌우된다.
2. **수준:** 감축 없음의 마지막 4개 평균이 138 USD/ha 높고, 51만 단계에서 정책 0과 같은 수준에 도달했다.
3. **비용 없음:** 처리량이 거의 같다. 에폭 10의 추가 계산은 DSSAT 시뮬레이션 시간에 비해 작다.
4. **문제 구조와의 정합(해석):** 수익의 대부분이 수확 때 확정된다. 64일 롤아웃은 시즌 중간에서 끊긴 조각이 많아 가치 추정에 더 의존하고, 업데이트 하나가 시즌 4개라 날씨·감축의 우연에 크게 흔들린다. 256일 × 8환경은 업데이트당 시즌 약 15개를 평균한다. 참고로 SB3 기본값은 2048·64·10이다.
5. **병렬 환경 8:** 시험 학습과 같은 조건(업데이트당 2,048일)을 유지한다. 처리량 측정상 4개(141)보다 약 15 % 빠르고, 12개(165~178)와는 거의 차이가 없어 CPU 한계 근처다. 7 GB 메모리 제한 안에서 문제없이 돌았다. `checkpoint_steps` 102,400은 2,048의 50배라 그대로 맞는다.

남은 한계:
- 초기 40 %는 나아지지 않았다(762.9 vs 796.4, 정책 0 838.8). 감축 대응 학습은 학습량 결정(A1)에서 더 긴 학습으로 확인해야 한다.
- 256·256·10에서는 확률 행동이 최대확률보다 꾸준히 낮다. 본 평가는 최대확률(`deterministic_policy: true`)이라 비교에는 영향이 없다.
- 시드 1개, 검증 16시즌의 비교라 근거는 약하다.
- 설정 해시가 바뀌어, 이전 시험 학습은 현재 설정으로 재개할 수 없다. 환경 수가 달라지면 같은 시드라도 시즌 배정 순서가 달라진다.

### D10 학습량 비교 (2026-11-11, 결정 대기)

시드 하나의 학습량은 정책 1·2·3 각 S단계, 정책 4는 3S단계이고 a·b 두 벌이라 12S다. 처리량 약 165단계/초(병렬 환경 8) 기준이며 평가 시간은 뺐다.

| 안 | 적합당 S | 시드 | 전체 단계 | 예상 시간 | 정책 4 | 시즌 재사용 |
|---|---:|---:|---:|---:|---:|---|
| 현재 설정 | 500만 | 10 | 6억 | 약 42일 | 1,500만 | 약 20 % |
| 1안 | 100만 | 10 | 1.2억 | 약 8.4일 | 300만 | 없음 |
| 2안 | 200만 | 5 | 1.2억 | 약 8.4일 | 600만 | 없음 |
| 참고 | 200만 | 10 | 2.4억 | 약 17일 | 600만 | 없음 |

판단 기준:
- **학습 부족은 편향이다.** 덜 배운 PPO는 규칙 정책보다 낮게 나와, 대비가 "정책 구조의 차이"가 아니라 "학습이 덜 된 정도"를 재게 된다. 시드를 늘려도 이 편향은 줄지 않는다.
- **시드가 적으면 구간이 넓어지고 덜 믿을 만해진다.** 교차 부트스트랩이 시드 행을 다시 뽑는데, 5개면 서로 다른 조합이 적어 시드 간 차이를 거칠게 반영한다. 시험 학습에서 점검마다 수익이 크게 흔들렸으므로 시드 간 차이도 클 수 있다.
- 현재 근거: 관수만 배우는 b1이 51만 단계에서 감축 없음은 규칙 수준에 왔지만 초기 40 %는 아직 덜 배웠다. 시비(시즌 3회)·살포(약 0.7회)는 결정이 드물어 관수보다 더 오래 걸릴 가능성이 높다(해석).

**200만 단계 시험 학습 (2026-11-12).** 근거: `outputs/runs/20261111T135941Z_pilot_b1_s0_b7c6f055/pilot_state.json`. 정책 b1, 시드 0, 관측 28개·성숙 뒤 마스크, 256·256·10, 병렬 환경 8, 검증 16시즌(4500~4515). **이전 단가(0.158)·이전 관수 규칙으로 시작했다**(수익 수준은 이전 기준, 정책 0 = 1028.9 / 838.8). 최대확률 행동, 순수익 USD/ha:

| 구간 (점검 수) | 감축 없음 평균 | 초기 40 % 평균 | 초기 40 % 범위 | 확인 |
|---|---:|---:|---|---|
| 5만~20만 (4) | 1036.2 | 860.3 | 774~916 | [ ] |
| 26만~51만 (6) | 892.8 | 577.4 | 409~816 | [ ] |
| 56만~97만 (9) | 876.3 | 521.9 | 373~739 | [ ] |
| 100만~148만 (10) | 898.8 | 541.2 | 224~825 | [ ] |
| 154만~205만 (11) | 922.2 | 625.3 | 270~778 | [ ] |
| 정책 0 | 1028.9 | 838.8 | | [ ] |

해석:
- **가장 좋은 정책은 10만~15만 단계에서 나왔고**(감축 없음 1040 안팎, 초기 40 % 912~916으로 정책 0보다 높음), 그 뒤 성능이 떨어져 200만 단계까지 그 수준으로 돌아오지 않았다. 마지막 점검(204.8만)은 895.0 / 717.5로 정책 0보다 낮다.
- 100만→200만 사이 평균은 조금 올랐지만(898.8 → 922.2, 541.2 → 625.3) 점검마다 초기 40 %가 224~825로 크게 흔들린다.
- 즉 **학습량 부족이 아니라 학습 후반의 불안정·성능 저하가 문제**다(해석). 본 비교는 적합마다 마지막 체크포인트를 평가하므로, 이대로면 학습 정책이 끝난 시점의 운에 따라 정책 0보다 낮게 나올 수 있다.
- 이 실행은 기준선 재탐색과 같이 돌아 처리량이 70~110단계/초로 떨어진 구간이 있었으나, 학습 결과 자체에는 영향이 없다(시즌 순서·난수는 같음).

**D10 판단에 주는 의미.** 200만 단계가 100만 단계보다 낫다는 근거가 없다. 학습량을 늘리기보다 (a) 학습률 감쇠 등으로 후반을 안정시키거나 (b) 별도 검증 시즌으로 체크포인트를 고르는 방식이 먼저 필요하다. 결정 대기.

## 19. 연구 진입 조건과 미기록 범위 점검 C (2026-11-11)

### C1 진입 조건 현황

근거: `outputs/runs/20261111T092352Z_readiness_f3ca4e5c` (`scripts/build_readiness_report.py` 재실행). `research_ready=false`, `main_training_allowed=false`.

| 미충족 항목 | 현재 상태 | 확인 |
|---|---|---|
| whole_elemental_carbon_and_crop_soil_n_balance | 작물 재고·종자·동화·호흡·수확·피해 반출의 원소 C 미확인 | [ ] |
| native_qf_n_partition_conservation | 고사엽 N 중복 문제 미해결 | [ ] |
| harvest_n_candidate_domain_expansion | 무투입 등 넓은 범위에서 실제 반출 수지 미통과 | [ ] |
| independent_agronomic_recovery | 단 B 판정 실패(V8·V13 99 % 적엽 칸) | [ ] |
| validation_tuned_baselines | 관수·시비·방제 규칙을 검증 시즌 탐색 + 별도 확인 시즌으로 채택(11·15·17절). 판정 스크립트의 미충족 목록은 고정 문자열이라 갱신되지 않았다 | [ ] |
| fixed_reduction_calendar_and_preregistered_contrasts | 감축일·감축률 승인(D6), 사전등록 초안 갱신. 학습량 미정이라 동결 전 | [ ] |
| independent_parameter_lineage | 품종·모형 계수의 독립 계보 미입증 | [ ] |

충족: independent_year_water_response(단 A, SIAZ 1995). 한계로 기록: calibrated_new_damage_survey, water_nitrogen_damage_interaction.

### C2 피해·회복 단 B

판정 실패 상태(`20261109T232350Z_damage_recovery_tier_b_643c4968`)는 그대로다. 해충 피해 범위는 허용 칸(적엽 33~66 %) 안으로 맞췄지만(17절), 동결 기준상 판정 자체는 바뀌지 않는다.

### C3 검증 게이트 값

`validation_gates`는 코드가 읽지 않는 기록용이다. `live_leaf_damage_write: false`는 연구용 경로 판정이고 실험용 경로(`experimental_native_leaf_write: true`)와 모순되지 않는다. `dssat_state_read: false`는 제안서 11쪽 "상태 읽기" 필수 확인의 연구용 판정으로 보이며, 관련 실험용 검사는 통과했다. 갱신 여부는 미결정이다. 두 키에 설정 주석을 달았다.

### C4 미기록 범위

**JSON 설정 17개** (코드가 읽는 곳 기준)

| 파일 | 내용 | 읽는 코드 | 확인 |
|---|---|---|---|
| actual_harvest_candidate_domain.json | 실제 반출 수확 후보 이미지의 검증 범위 기록 | 없음(기록용) | [ ] |
| agronomic_input_priorities.json | 공개 연구별 입력 확보 상태와 작업 순서 | 진입 판정, 각종 자격 스크립트 | [ ] |
| agronomic_protocols.json | 공개 연구 처리 번역과 차단 요인 | agronomic_scenarios.py 등 | [ ] |
| agronomic_sources.json | 공개 근거 목록(연구 10편) | 진입 판정, 자격 스크립트 다수 | [ ] |
| balance_observability.json | 수지 항목별 관측 가능 여부 | audit_balance_observability.py | [ ] |
| carbon_measurement_contract.json | 원소 C 측정 계약과 금지 추론 | audit_carbon_measurement.py | [ ] |
| damage_recovery_tier_b.json | 단 B 동결 기준 | judge_damage_recovery_tier_b.py | [ ] |
| evidence_qualifications.json | 실행별 근거 자격 기록 | 진입 판정 | [ ] |
| faw_technical_sensitivity.json | 해충 계수 합성 민감도 설정 | 해충 진단 스크립트 3개 | [ ] |
| field_calibration_candidate_screen.json | 현장 보정 후보 선별 결과 | 자격·검증 스크립트 | [ ] |
| field_validation_tiers.json | 현장 검증 3단 기준 | 진입 판정, 단 A·B 판정 | [ ] |
| harvest_n_candidate_domain.json | 수확 N 후보 이미지의 검증 범위 | 없음(기록용) | [ ] |
| lirf_translation_contract.json | LIRF 입력 변환 계약 | LIRF 자격 스크립트 | [ ] |
| oveysi2010_input_dossier.json | Oveysi 2010 재현 입력 명세 | Oveysi 스크립트 | [ ] |
| oveysi2010_table4_grain.json | Oveysi 2010 표 4 곡실 수량 | agronomic_scenarios.py 등 | [ ] |
| rahman2022_marginal_grain.json | Rahman 2022 주변평균 곡실 | agronomic_marginals.py | [ ] |
| santos2018_table1_productivity.json | Santos 2018 표 1 생산성 | agronomic_scenarios.py | [ ] |

비교 실험의 학습·평가 경로는 이 JSON 파일들을 읽지 않는다(`proposal_v2.yaml`만 읽음).

**Docker 이미지와 패치.** 비교 실험은 `mars-dssat:ppo-cpu-metadata`(sha256:11e2650fed75…)를 쓴다. 이 이미지는 `ppo-cpu`(← `leaf-experimental` ← `integration` ← `gym-dssat:debian-bookworm`) 위에 `metadata-audit`의 보정 DSSAT 실행 파일을 복사한다. 패치는 모두 컨테이너 복사본에만 적용되고 vendor 원본은 바꾸지 않는다: `patch_leaf_source.py`·`leaf_integration.for`(실험용 잎 피해 쓰기), `patch_metadata_source.py`(진단 메타데이터 보정, 작물식 불변), 그 밖의 패치는 수확·순서·광 진단용 읽기 전용이다. `patch_sequence_units.py`는 철회된 후보다.

**WGEN 기상 (2026-11-11 대조).** 모의 시즌(파종 2월 26일~성숙 약 7월 6일) 강수 평균 488 mm(5 % 분위 260 mm, 10절)를 공개 월평년값으로 같은 기간을 합산해 비교했다. Gainesville 1.7 SE 관측소(climate-charts, 1991–2020 표기이나 2006–2020 자료로 표시) 2월 2.9·3월 2.6·4월 3.0·5월 4.5·6월 8.2·7월 7.3 in에서 약 509 mm, Gainesville 3.8 W 관측소 미터 값에서 약 496 mm다. 모의 평균은 이보다 2~4 % 낮아 평균 수준은 맞는다. 한계: 두 관측소 모두 기록이 짧고 값을 2차 사이트에서 가져왔으며, 시즌 강수의 해마다 분포(변동폭)는 비교하지 못했다. 공식 값은 NOAA NCEI의 Gainesville Regional Airport(USW00012816) 1991–2020 평년값으로 확인할 수 있다. 출처: https://climate-charts.com/USA-Stations/FL/US1FLAL0026.html, https://climate-charts.com/USA-Stations/FL/US1FLAL0010.html

### C5 제안서·방향서

미갱신. 오늘 바뀐 설계(정책 0~4 구조, 달력일 감축, 공급 200 mm, 규칙 기준선, α 0.01 등)가 반영되지 않았다.

## 20. 진입 조건 재분류 (2026-11-11 결정)

**결정.** 아래 표의 "분리" 3개를 포함해 5개 항목을 한계로 옮기고, 기준 정책 튜닝과 사전 대비 확정 2개를 진입 조건으로 유지한다(임의 결정: 분리 항목 전부 한계로, 입증이 어려운 이유를 함께 기록). `build_readiness_report.py`(`RECLASSIFIED_LIMITATIONS`)와 PRETRAINING_READINESS.md 표에 반영했다. 재판정(`20261111T093723Z_readiness_3f70e201`) 결과 미충족은 `validation_tuned_baselines`, `fixed_reduction_calendar_and_preregistered_contrasts` 2개이고 `research_ready=false`다.

| 한계 항목 | 입증이 어려운 이유 | 결과 보고 때 적을 범위 | 확인 |
|---|---|---|---|
| 전체 원소 C와 작물–토양 N | CERES-Maize가 작물 재고·종자·총동화·호흡·수확·피해 반출의 C를 출력하지 않는다. 수지를 닫으려면 Fortran 내부 계측과 건물중→C 환산 가정이 필요하고, 오차 허용폭을 정할 현장 C 시계열이 공개 자료에 없다 | 수익·수량 비교만 주장하고 C 수지는 주장하지 않는다 | [x] |
| 네이티브 Q/F N 배분 | 다년 연속 모드에서 부산물이 남을 때 고사엽 N이 이중 계상되는 DSSAT 내부 회계 문제다. 고치려면 원본 작물 모형 코드를 바꿔야 해 기존 검증이 무효가 되고, 출력 반올림이 차이를 가린다 | 단일 시즌만 사용, Q/F 모드 미사용 | [x] |
| 수확 N 후보 적용 범위 | 별도 후보 이미지의 실제 반출 수확 회계가 무투입 32개 사례에서 수지를 닫지 못했다. 넓히려면 수확 반출 처리를 다시 설계해야 하고 잔사 N 전달을 검증할 현장 자료가 없다 | 수량은 네이티브 HWAH, 후보 이미지 미사용 | [x] |
| 독립 피해·회복 (단 B) | 동결 기준 판정에서 V8·V13 99 % 적엽 칸이 허용 범위를 벗어났다. 회복을 고치려면 작물 모형 수정과 보정에 쓰지 않은 별도 피해 시험이 필요하다 | 해충 피해는 적엽 33~66 %에서 해석, H3는 탐색 분석 | [x] |
| 독립 매개변수 계보 | 품종 IB0035 계수의 보정 자료·연도·시험구 기록이 공개돼 있지 않아, 평가 관측이 보정에 쓰이지 않았음을 고정 자료로 입증할 수 없다 | 결과는 현 품종 계수 전제, 단 A 통과를 부분 근거로 명시 | [x] |

### 재분류 전 제안 표

분류: **유지** = 이 실험의 주장에 필요하고 검증 가능, **한계** = 필요하지만 자료가 없어 검증 불가(2026-11-10 물×질소×피해·신규 피해 조사 선례), **분리** = 단일 시즌 경제 비교와 관련이 적어 별도 과제.

| 진입 조건 | 합격 기준 요지 | 이 실험과의 관계 | 막힌 이유 | 제안 | 결정 | 확인 |
|---|---|---|---|---|---|---|
| 전체 원소 C와 작물–토양 N | 작물 C 항목 6개와 수확·휴경·재초기화까지 C/N 수지가 닫힘 | 수익·보상은 C를 쓰지 않음. 잎 피해 반출의 건물중·N 회계는 별도로 검산됨(`verify_leaf_accounting`) | DSSAT가 작물 C 항목을 출력하지 않아 모형 계측이 필요 | 분리 | | [ ] |
| 네이티브 Q/F N 배분 | 다년 연속(Q/F) 모드에서 반출·고사물·잔사 N이 한 번씩 계상 | 비교 실험은 단일 시즌 모드라 Q/F 경로를 쓰지 않음 | 모형의 고사엽 N 중복 | 분리 | | [ ] |
| 수확 N 후보 적용 범위 | 후보 이미지에서 무투입·실패·다년 등의 실제 반출 검증 | 비교 실험 이미지(`ppo-cpu-metadata`)는 이 후보를 쓰지 않고 수량은 HWAH | 넓은 범위에서 수지 미통과 | 분리 | | [ ] |
| 독립 피해·회복 (단 B) | 보정에 쓰지 않은 포장의 피해–수량 반응 재현 | 해충 피해의 수익 영향, H3 | 판정 실패. 99 % 적엽 칸만 허용 범위 밖이고 33~66 %는 범위 안 | 한계 (해석 범위를 적엽 66 % 이하로 한정, H3는 탐색 분석 유지) | | [ ] |
| 검증용 기준 정책 튜닝 | 관수·방제 임계, η, GAE λ 후보 비교 | 정책 0과 학습 설정 | "농학 검증 환경"이 다른 조건에 묶임 | 유지. 환경을 "본학습용으로 동결한 환경"으로 해석. 남은 일: η, GAE λ | | [ ] |
| 감축일 달력과 사전 대비의 확정 | 감축 설정·대비를 최종 시험 전 동결 | 실험 설계 자체 | 학습량 미정 | 유지. 남은 일: 학습량 결정 후 동결 | | [ ] |
| 독립 매개변수 계보 | 평가 관측이 계수 선정에 쓰이지 않았음을 입증 | 모형 신뢰도 | 품종 IB0035 계수의 보정 자료 계보가 공개돼 있지 않음 | 한계 (결과는 현 품종 계수를 조건으로 함. 독립 연도 물 반응 단 A 통과를 부분 근거로 명시) | | [ ] |

이 안대로 정하면 본학습 전 남는 진입 조건은 "기준 정책 튜닝"(η, GAE λ)과 "사전 대비 확정"(학습량 결정 후 동결) 두 가지다. 적용하려면 `build_readiness_report.py`의 고정 미충족 목록과 PRETRAINING_READINESS.md의 표를 함께 고쳐야 한다.

## 21. DSSAT 시나리오 값의 원 실험 대조 (2026-11-11)

출처: Ma et al. 2006, Agricultural Systems 87:274–295, "Evaluation of the RZWQM-CERES-Maize hybrid model for maize production"(UFGA8201을 DSSAT v3.5 입력으로 평가, https://www.ars.usda.gov/ARSUserFiles/3495/77.%20Agric%20System%202006.pdf). 원 실험: Bennett, Jones, Zur, Hammond 1986, Agronomy Journal 78:273–280.

| 항목 | 원 실험·논문 | 현재 MARS 입력 (gym-DSSAT 템플릿) | 판정 | 확인 |
|---|---|---|---|---|
| 파종일, 이랑, 품종 | 1982-02-26, 61 cm, McCurdy 84AA | 같음 | 일치 | [ ] |
| 재식밀도 | 71,000 주/ha (7.1 주/m²) | 7.2 주/m² | 거의 일치 | [ ] |
| 생리적 성숙 | 관측 7월 4일 | 모의 평균 파종 후 130.4일(7월 6일경) | 일치 | [ ] |
| 토양 수분 한계·초기 수분 | 0–5 cm LL 0.026, DUL 0.096, 초기 0.086 등(표 1) | 같은 값 | 일치 | [ ] |
| **초기 무기질소** | NO3 0.6, NH4 1.5 µg/g(0–60 cm), 깊은 층 NH4 0.5~0.6(표 3, DSSAT v3.5 값) | NO3 0.1, NH4 0.5 µg/g. FileX 주석에 "DSSAT35 values"로 1.5·0.6이 남아 있다 | 불일치(약 36 대 15 kg N/ha, 제 환산). **수량 영향 없음으로 확인, 현재 값 유지** (아래 검증) | [x] |
| **저질소 처리 시비** | 4월 7일 27, 4월 12일 35 kg N/ha, 합계 62 | 27·35에 5월 17일 54가 더 있어 116 | **불일치.** 고질소도 논문 275(5회) 대비 FileX는 5월 17일 126이 더해져 401 | [ ] |
| 시즌 무기화 | DSSAT-CERES가 무관수 저질소에서 35 kg N/ha 모의 | 미측정 | — | [ ] |
| 관측 곡실 수량 | 무관수 2,929(62 N)·3,130(275 N), 관수 6,850·11,881, 영양기 스트레스 6,375·9,344 kg/ha | 규칙 정책(161 kg N, 관수 약 165 mm) 약 8,900~9,200, 무관수 3,645 kg/ha | 같은 범위 | [ ] |

**초기 무기질소 영향 검증 (2026-11-11).** 근거: `outputs/runs/20261111T100622Z_initial_nitrogen_check_d56808ec/verification.json` (`scripts/check_initial_nitrogen.py`). 원 실험 6처리를 실제 1982년 기상(UFGA8201.WTH), FileX의 관수·시비 일정으로 돌려 관측 건조 곡실(UFGA8201.MZA)과 비교했다.

| 처리 | 관측 | 현재 초기 N, FileX 일정 | 원 실험 초기 N, FileX 일정 | 현재 초기 N, 논문 일정 | 원 실험 초기 N, 논문 일정 | 확인 |
|---|---:|---:|---:|---:|---:|---|
| 1 무관수·저질소 | 2929 | 1977 | 1966 | 1977 | 1967 | [ ] |
| 2 무관수·고질소 | 3130 | 2711 | 2715 | 2711 | 2715 | [ ] |
| 3 관수·저질소 | 6850 | 8653 | 8677 | 5634 | 5653 | [ ] |
| 4 관수·고질소 | 11881 | 11298 | 11298 | 11125 | 11125 | [ ] |
| 5 영양기 스트레스·저질소 | 6375 | 7879 | 7898 | 5587 | 5595 | [ ] |
| 6 영양기 스트레스·고질소 | 9344 | 9807 | 9808 | 9807 | 9808 | [ ] |
| RMSE / 평균 편향 (kg/ha) | | 1092 / +303 | 1104 / +309 | 813 / −611 | 809 / −608 | [ ] |

**판정: 현재 초기 N 값을 유지해도 문제없다.** 초기 무기질소를 바꿔도 처리별 수량 차이가 25 kg/ha 이내이고 RMSE 차이는 12 kg/ha 이하다. 모의가 파종 27일 전(82030)에 시작하고 토양이 모래라, 초기 무기질소 약 20 kg N/ha 차이가 작물에 거의 닿지 않는 것으로 보인다(해석). 수량을 크게 바꾸는 것은 시비 일정(저질소 처리의 5월 17일 54 kg 유무)이다. 한계: UFGA8201은 품종 IB0035 보정에 쓰였을 수 있어 독립 검증이 아니라 일관성 확인이다.

**의미.**
- 초기 무기질소가 원 실험 입력보다 약 20 kg N/ha 낮지만, 위 검증에서 수량 영향이 없어 시비 최적량(161 kg) 판단에도 영향이 작다. DSSAT 4.x 배포 예제에서 값을 낮춘 이유는 문서에서 찾지 못했다.
- 이전 규칙 시비 116 kg(gym-DSSAT 전문가 일정, 이전 질소 예산 91.64 USD의 근거)은 논문에 없는 5월 17일 54 kg이 포함된 값이다. 현재 시비 일정은 별도 탐색으로 정했으므로 직접 영향은 없다.

## 22. 관측 변수 45개 점검 (2026-11-11)

근거: `outputs/runs/20261111T133359Z_observation_ranges_1a7731db/verification.json` (`scripts/audit_observation_ranges.py`). 검증 20시즌(4500~4519) × {규칙 정책: 감축 없음·초기 40 %·후기 60 %, 무투입: 감축 없음}, 실험용 해충 환경, 매일 아침 관측 약 11,000개. 범위는 척도로 나누기 전의 원래 값이다. 정책 입력은 하루 45개 × 최근 7일 = 315개이고, 학습 중 정규화(VecNormalize)는 쓰지 않는다.

| # | 변수 | 의미 | 척도 | 실제 범위 (최소~최대) | 점검 | 확인 |
|---:|---|---|---:|---|---|---|
| 1 | dap | 파종 후 일수 (DSSAT) | 200 | 0~137 | 45번 season_day와 99.3 % 같음 (중복) | [x] |
| 2 | istage | CERES 생육 단계 | 10 | 1~10 | 10은 수확 뒤 마지막 관측에만 나온다 | [x] |
| 3 | vstage | 엽수 단계 | 30 | 0~22 | 정상 | [x] |
| 4 | xlai | 엽면적지수 | 10 | 0~4.22 | 정상 | [x] |
| 5 | topwt | 지상부 건물중 kg/ha | 20000 | 0~18,440 | 정상 | [x] |
| 6 | grnwt | 곡실 건물중 kg/ha | 15000 | 0~10,280 | 정상 | [x] |
| 7 | rtdep | 뿌리 깊이 cm | 300 | 0~113 | 척도 대비 0~0.38만 사용 | [x] |
| 8 | swfac | 수분 스트레스 (1 − DSSAT SWFAC, 0 = 없음) | 1 | 0~1 | 정상 | [x] |
| 9 | nstres | 질소 스트레스 (0 = 없음) | 1 | 0~0.59 | 정상 | [x] |
| 10 | sw | 토양 체적수분, 180 cm 전체 층 두께 가중 평균 | 1 | 0.089~0.168 | **척도 대비 폭 0.08로 매우 좁다.** 뿌리 영역이 아닌 전체 평균이라 정보도 약하다(12절 3번에서 같은 이유로 규칙 기준에서 제외) | [x] |
| 11 | wtdep | 지하수위 깊이 cm | 300 | 169.8~180 | **사실상 상수** (척도 대비 폭 0.03). 이 토양에 지하수위가 없다 | [x] |
| 12 | ep | 실제 증산 mm/일 | 20 | 0~5.94 | 정상 | [x] |
| 13 | rain | 강수 mm/일 | 100 | 0~232 | 0.4 %가 1을 넘음(최대 2.3). 드물어 문제 작음 | [x] |
| 14 | tmax | 최고기온 °C | 50 | 13.2~38.4 | 정상 | [x] |
| 15 | srad | 일사 MJ/m² | 40 | 8.2~25.7 | 정상 | [x] |
| 16 | dtt | 일 적산온도 °C·일 | 50 | 0~23.4 | 정상 | [x] |
| 17 | water_used | 누적 관수 mm | 200 | 0~200 | 20번과 완전 선형 (중복) | [x] |
| 18 | nitrogen_used | 누적 시비 kg/ha | 241 | 0~161 | 21번과 완전 선형 (중복) | [x] |
| 19 | sprays | 누적 살포 횟수 | 4 | 0~1 | 22·40번과 완전 상관 (이 정책들은 최대 1회) | [x] |
| 20 | water_budget_ratio | 물 예산 잔여 비율 | 1 | 0~1 | 17번 중복 | [x] |
| 21 | nitrogen_budget_ratio | 질소 예산 잔여 비율 | 1 | 0.33~1 | 18번 중복 | [x] |
| 22 | spray_budget_ratio | 살포 예산 잔여 비율 | 1 | 0.67~1 | 19번 중복 | [x] |
| 23 | water_left | 남은 공급량 mm (감축 반영) | 200 | 0~200 | 정상. 감축량은 이 값의 급감으로 드러남 | [x] |
| 24 | initial_water | 초기 공급량 mm | 200 | 200 | **상수** | [x] |
| 25 | initial_water_budget | 초기 물 예산 USD/ha | 220 | 220 | **상수** (예산 배율 제거 이후) | [x] |
| 26 | initial_nitrogen_budget | 초기 질소 예산 USD/ha | 190.39 | 190.39 | **상수** | [x] |
| 27 | initial_spray_budget | 초기 살포 예산 USD/ha | 150 | 150 | **상수** | [x] |
| 28 | grain_price | 곡실 단가 USD/kg | 0.158 | 0.158 | **상수** | [x] |
| 29 | water_price | 물 단가 USD/mm | 1.1 | 1.1 | **상수** | [x] |
| 30 | nitrogen_price | 질소 단가 USD/kg | 0.79 | 0.79 | **상수** | [x] |
| 31 | spray_price | 살포 단가 USD/회 | 50 | 50 | **상수** | [x] |
| 32 | irrigation_labor | 관수 노동비 USD/회 | 3 | 3 | **상수** | [x] |
| 33 | nitrogen_labor | 시비 노동비 USD/회 | 5 | 5 | **상수** | [x] |
| 34 | announced | 감축 발생 여부 | 1 | 0/1 | 정상. 감축 당일부터 1 | [x] |
| 35 | reduction_fraction | 감축률 | 1 | 0, 0.4, 0.6 | 정상. 감축 전 0 | [x] |
| 36 | days_since_announcement | 감축 후 경과일 | 200 | 0~124 | 정상 | [x] |
| 37 | survey_value | 최근 주간 조사 해충 밀도 (잡음 포함) | 1 | 0~1 | 정상 | [x] |
| 38 | survey_age | 조사 후 경과일 | 7 | 0~6 | 정상 | [x] |
| 39 | survey_available | 조사값 유무 | 1 | 1 | **상수** (해충 환경에서는 항상 1) | [x] |
| 40 | has_sprayed | 살포 이력 여부 | 1 | 0/1 | 19번 중복 | [x] |
| 41 | days_since_spray | 마지막 살포 후 경과일 | 200 | 0~85 | 정상. 미살포 시 0이고 40번으로 구분 | [x] |
| 42 | previous_water | 전날 관수 mm | 25 | 0~20 | 정상 (격자 최대 25) | [x] |
| 43 | previous_nitrogen | 전날 시비 kg/ha | 80 | 0~80 | 정상 | [x] |
| 44 | previous_spray | 전날 살포 | 1 | 0/1 | 정상 | [x] |
| 45 | season_day | 환경의 결정 일 수 | 200 | 0~138 | 1번 중복 | [x] |

**정보 누설 점검 (코드 확인):**
- 감축: `ResourceLedger.announcement()`만 관측에 들어가고, 감축이 일어나기 전에는 announced 0, fraction 0, 경과일 0이다. 감축 날짜·크기(`shock`)와 시즌 테이프(`exogenous`)는 관측에 없다. 누설 없음.
- 해충: 실제 밀도는 들어가지 않고, 잡음이 섞인 주간 조사값(`mars_pest_public`)만 들어간다. `frame()`이 이 세 키 외의 값을 거부한다. 누설 없음.
- 날씨: 당일 값만 들어가고 예보는 없다.

**발견 사항:**
1. **상수 11개 (24~33번, 39번):** 예산 배율을 없앤 뒤로 시즌마다 바뀌지 않는다. 신경망에서는 고정 편향과 같아 학습을 해치지는 않지만 정보도 없다. 7일 이력이라 입력 315개 중 77개가 상수다.
2. **중복 (1↔45, 17↔20, 18↔21, 19↔22↔40):** 단가가 고정이라 사용량과 잔여 비율이 정확히 같은 정보다. 해롭지는 않다.
3. **척도 문제 (10 sw, 11 wtdep):** 정규화 없이 고정 척도로만 나누므로, sw는 0.09~0.17, wtdep는 0.57~0.60 안에서만 움직인다. wtdep는 정보가 없고, sw는 변화가 작아 신경망이 쓰기 어렵다. 같은 토양 수분 정보는 swfac(수분 스트레스)가 0~1 전체로 전달한다.
4. **작물 상태 완전 관측 (가정):** topwt·grnwt·xlai·nstres·swfac는 실제 농가가 매일 정확히 알 수 없는 모형 내부 값이다. 정책 0과 PPO가 같은 정보를 쓰므로 비교는 공정하지만, 결과는 "작물 상태를 안다"는 조건에서의 성능이다.
5. 결정 기록 4절의 척도 두 개가 코드와 달라 고쳤다.

**결정 (2026-11-11, 임의): C안 적용. 관측을 하루 45개 → 28개(입력 315 → 196)로 정리.**

| 처리 | 변수 | 이유 |
|---|---|---|
| 제거 (상수 11개) | initial_water, initial_water_budget, initial_nitrogen_budget, initial_spray_budget, grain_price, water_price, nitrogen_price, spray_price, irrigation_labor, nitrogen_labor, survey_available | 시즌마다 같은 값이라 정보가 없다 |
| 제거 (중복 5개) | season_day, water_budget_ratio, nitrogen_budget_ratio, spray_budget_ratio, has_sprayed | 남긴 dap, water_used, nitrogen_used, sprays와 정확히 같은 정보 (단가·배율 고정) |
| 제거 | wtdep | 사실상 상수 (지하수위 없음) |
| 정의 변경 | sw | 180 cm 전체 평균 → **뿌리 깊이까지의 층 두께 가중 평균** (뿌리 내리기 전에는 표층). 척도 1 → 0.15 |
| 유지 | 나머지 28개 | |

딸린 변경:
- 잠재함수 보상 Φ의 곡실 단가를 관측 대신 환경 상수(`env.grain_price`, 0.158)에서 읽는다. 값과 Φ는 같다.
- 규칙 정책의 살포 조건 `survey_available > 0.5`를 뺐다. 조사값이 없으면 survey_value가 0이고 임계(0.7)가 양수라 결과가 같다.
- 크기 315/45를 코드 곳곳에 직접 쓰던 것을 `FRAME_SIZE`, `OBSERVATION_SIZE`로 바꿨다.

새 관측 범위 (`outputs/runs/20261111T135853Z_observation_ranges_922c7e78`, 같은 20시즌·4조건): 뿌리 영역 sw는 0.018~0.146(평균 0.070)으로, 전체 평균(0.089~0.168)보다 폭이 1.6배 넓고 더 건조하다. 척도 0.15로 0.12~0.97 범위가 된다. 상관 0.98을 넘는 변수 쌍은 0개다(이전 12쌍).

한계: 예산 배율 β는 이제 관측에 드러나지 않는다. 현재 설계는 β = 1.0 고정이라 문제없지만, β를 다시 바꾸면 관측에 넣어야 한다.

## 23. 행동 공간 점검·정리 (2026-11-11)

근거: `outputs/runs/20261111T134127Z_action_usage_87902f12/verification.json` (`scripts/measure_action_usage.py`). 검증 20시즌 × {감축 없음, 초기 40 %, 후기 60 %}, 규칙 정책과 시험 학습 PPO(b1, 256·256·10, 51만 단계 체크포인트), 결정일 약 8,000일.

| 행동 | 선택지 | 마스크 (정리 전) | 확인 |
|---|---|---|---|
| 관수 | 0, 5, 10, 15, 20, 25 mm | 남은 공급량 초과, 물 예산 초과 | [x] |
| 시비 | 0, 10, 20, 27, 35, 40, 54, 60, 80 kg/ha | 질소 예산 초과 | [x] |
| 살포 | 0/1 | 살포 예산 초과, istage 5 이상, 마지막 살포 후 7일 미만 | [x] |

| 측정 | 규칙 정책 | PPO b1 |
|---|---|---|
| 관수 선택 | 15 mm 433, 20 mm 81, 10 mm 19, 5 mm 8 | 10 mm 758, 5 mm 237, 15 mm 16 |
| 25 mm 사용 | 0 | 0 |
| 물 예산이 공급량보다 먼저 제한한 날 | 0일 | 0일 |
| 성숙 뒤(istage 6) 결정일 | 시즌당 약 2.2일 | 같음 |
| 성숙 뒤 관수 | 60시즌 중 1회 10 mm | 0 |
| 살포 가능일 비율 | 58 % | 58 % |
| 순수익: 감축 없음 / 초기 40 % / 후기 60 % | 1031.2 / 861.9 / 915.8 | 1034.5 / 806.4 / 909.7 |

**결정 (2026-11-11, 임의): 1·2 모두 적용.**
1. **물 예산 제거:** 예산 220 USD가 공급량 200 mm × 1.1 USD와 정확히 같아 한 번도 먼저 제한하지 않았다(감축 뒤에도 공급량이 먼저 준다). 관수 마스크는 남은 공급량만 본다. 물 비용 계산은 그대로다. `economics.budgets_usd_ha.water` 키를 지웠고, 이 키가 다시 들어오면 설정 로드가 실패하게 했다. 공급량 민감도(120·160 mm)도 공급량만 바꾼다.
2. **성숙 뒤 관수·시비 마스크:** istage 6(생리적 성숙~수확)에는 물과 질소가 수량에 영향을 주지 못한다. 이 단계에서 관수·시비는 0만 고를 수 있다(`management.input_closed_istage: 6`). 시즌당 약 2일이라 효과는 작고, PPO가 쓸모없는 행동을 탐색하지 않게 한다. 규칙 정책은 60시즌 중 1번 이 기간에 관수했으므로 그만큼 결과가 바뀐다.

유지: 관수 격자 6단계(25 mm는 안 쓰였지만 5 mm를 PPO가 237회 사용), 시비 9단계(D 결정, 15절), 살포 규칙과 질소·살포 예산(실제로 제한함).

## 24. 15.5 % 가격 환산 후 규칙 기준선 재탐색 (2026-11-12, 완료)

1절 결정으로 매출 단가가 0.158에서 0.187 USD/kg(건물 기준)으로 올랐다. 이전과 같은 절차로 다시 맞춘다: 현재 값에서 출발한 좌표 탐색(검증 4000~4039, 감축 없음), 겹치지 않는 확인 시즌에서 짝지은 95 % 구간이 0보다 위이면 채택. 감축 조건은 보고만 한다.

### 관수 단계 규칙 (채택)

근거: `outputs/runs/20261111T151115Z_rule_baseline_search_4050fc39/verification.json`. 임계 0.05~0.7(8개), 관수량 5~25 mm(5개), 확인 80시즌 4600~4679.

| istage | 이전 (임계, mm) | 채택 (임계, mm) | 확인 |
|---:|---|---|---|
| 3 | 0.5, 15 | 0.5, **20** | [ ] |
| 4 | 0.1, 20 | **0.05**, 20 | [ ] |
| 5 | 0.2, 15 | **0.3**, 15 | [ ] |

| 항목 (확인 80시즌, 감축 없음) | 이전 규칙 | 채택 규칙 | 차이 (95 % 구간) | 확인 |
|---|---:|---:|---|---|
| 평균 순수익 USD/ha | 1273.3 | 1293.4 | **+20.1 (0.8~40.8)** | [ ] |
| 하위 10 % 평균 | 1004.4 | 1012.2 | | [ ] |
| 평균 관수 mm | 167.0 | 172.7 | | [ ] |
| 평균 곡실 kg/ha | 8934 | 9057 | | [ ] |

감축 조건(보고만, 40시즌) 평균 순수익 차이: 후기 20·40·60 % +17.5·+15.9·+27.5(구간이 0 포함), 초기·중기 20 % +8.9, **초기·중기 40 % −36.4(−73.7~−0.6), 60 % −56.0~−57.2(구간이 0 아래)**. 새 규칙은 3단계에 물을 더 일찍 써서, 이른 감축에서는 남은 물이 적어 불리하다. 채택 기준은 감축 없음만 보므로 채택했다. 정책 0이 b-유 행에서 약해지는 방향이라 b4·b0′와의 대비 해석 때 이 점을 함께 적는다.

순수익 수준이 이전(약 1028)보다 높은 것은 단가 상승(×1.183) 때문이다.

### 시비 일정 (현재 값 유지)

근거: `outputs/runs/20261111T153914Z_nitrogen_schedule_search_cc55e693/verification.json`. 현재 일정 {45: 80, 65: 54, 95: 27}(161 kg)에서 출발, 새 관수 규칙 적용, 질소 예산 해제, 확인 80시즌 4700~4779.

| 항목 (확인 80시즌, 감축 없음) | 현재 161 kg | 탐색 최선 {45: 80, 60: 60, 95: 35} 175 kg | 차이 (95 % 구간) | 확인 |
|---|---:|---:|---|---|
| 평균 순수익 USD/ha | 1290.7 | 1301.0 | +10.2 (−3.2~23.3) | [ ] |
| 하위 10 % 평균 | 896.5 | 874.5 | | [ ] |
| 평균 곡실 kg/ha | 9018 | 9119 | | [ ] |

구간이 0을 포함해 **채택 기준 미달, 현재 일정 유지.** 감축 조건(보고만)은 +3.7~+15.9로 모두 같은 방향이고 후기 60 %만 구간이 0 위(+15.9, 1.7~30.9). 단가가 올라 질소를 14 kg 더 주는 쪽이 약간 낫지만 확인 시즌에서 입증되지 않았다. 일정이 그대로라 **질소 예산 190.39 USD((161 + 80) × 0.79)도 유지**한다.

### 방제 임계 (현재 값 유지)

근거: `outputs/runs/20261111T160531Z_spray_threshold_search_aab988ee/verification.json`. 후보 0.1~0.8, 튜닝 40시즌(4000~4039, 감축 없음).

| 임계 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | **0.7** | 0.8 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 평균 순수익 | 1308.5 | 1324.1 | 1323.2 | 1332.5 | 1344.1 | 1342.0 | **1345.9** | 1340.0 | [ ] |
| 평균 살포 횟수 | 1.52 | 1.20 | 1.07 | 0.90 | 0.72 | 0.70 | 0.68 | 0.68 | [ ] |

튜닝 최선이 현재 값 0.7이라 확인 단계 없이 **유지**. 0.5~0.8은 6 USD/ha 안에서 평탄하다.

### b0′ 값 (재측정 반영, 여유 비율 유지)

**재측정.** 근거: `outputs/runs/20261111T160808Z_stage_entry_rule_policy_71c481f4/verification.json`(새 관수 규칙, 검증 1000~1119, 생육 실패 0). 단계 진입일은 그대로(2·13·36.8·41.8·82.6·92.8·130.4일)이고 관수 배분이 바뀌었다.

| 값 | 이전 | 새 값 | 근거 | 확인 |
|---|---:|---:|---|---|
| 단계별 평균 관수 (3·4·5단계) | — | 93.3·32.3·45.7 mm | 시즌 171.5 mm | [ ] |
| 예비량 `reserve_mm` | 83.5 | **78.0** | 단계 4 + 5 | [ ] |
| 개화일·성숙일 | 83·130 | 83·130 | 단계 4·6 평균 진입 | [ ] |
| 관수 간격 `event_interval_days` | 9.4 | **10.0** | (130.4 − 82.6)일 / 4.78회 | [ ] |
| 남은 수요 | [[0,163.6],[42,163.6],[83,83.5],[93,49.5],[130,0]] | **[[0,171.5],[42,171.3],[83,78.0],[93,45.7],[130,0]]** | 단계별 누적 | [ ] |

**여유 비율.** 근거: `outputs/runs/20261111T160928Z_reduction_margin_tuning_439d0da0/verification.json`. 9조건 평균, 튜닝 40시즌(3100~3139), 확인 40시즌(3200~3239).

| 여유 비율 | 0.2 | 0.3 | **0.4** | 0.5 | 0.6 | 0.8 | 1.0 | 확인 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 튜닝 평균 순수익 | 1164.4 | 1180.2 | **1190.1** | 1174.3 | 1177.4 | 1167.9 | 1133.0 | [ ] |

최선이 현재 값 0.4라 **유지**. 확인 시즌에서 b0′ 1114.3 대 πB 1059.7(하위 10 % 577.7 대 501.0)로 b0′가 높다. 조건별로는 초기·중기 60 %에서 +228.3(852.6 대 624.3), 40 %에서 +21.8이고 20 %·후기 감축에서는 ±4 이내다. 새 관수 규칙이 이른 감축에 약해진 만큼(위 관수 절) b0′의 이득이 커졌다.

**재탐색 정리 (2026-11-12).** 15.5 % 환산 뒤 바뀐 값은 관수 단계 규칙과 b0′의 재측정 값뿐이다. 시비 일정, 질소 예산, 방제 임계, 여유 비율은 유지됐다. 200만 단계 시험 학습은 이전 관수 규칙·이전 단가로 시작했으나 b1은 관수를 PPO가 정하고 시비·방제 규칙은 바뀌지 않아, 학습 곡선 모양을 D10 판단에 쓰는 데 지장이 없다(수익 수준은 이전 단가 기준).

## 25. 시험 학습 결과의 인과 분석 (2026-11-12)

### 세 시험 학습에서 바뀐 것

| | P1 `…091615Z_…377b7d3c` | P2 `…115521Z_…da85f87f` | P3 `…135941Z_…b7c6f055` |
|---|---|---|---|
| n_steps·batch·epochs | 64·64·2 | **256·256·10** | 256·256·10 |
| 관측 | 45개 | 45개 | **28개, sw 뿌리 영역** |
| 물 예산·성숙 뒤 마스크 | 있음·없음 | 있음·없음 | **제거·추가** |
| 학습 단계 | 51만 | 51만 | 205만 |
| 시드 | 0 | 0 | 0 (입력 크기가 달라 초기 가중치 다름) |
| 학습 시즌 평균 수익 추이 | 642 → 905 꾸준히 상승 | 733 → 851 상승 중 | 734 → **925(20만)** → 605(46만) → 546(143만) → 801(205만) |

학습 시즌은 모두 새 시즌이라(205만 단계 ≈ 1만 5천 시즌 < 89,998), P3의 하락은 특정 시즌 과적합이 아니라 **정책 자체의 악화**다.

### 메커니즘 진단

근거: `outputs/runs/20261111T224941Z_pilot_checkpoint_diagnostics_13704d7c/verification.json` (`scripts/analyze_pilot_checkpoints.py`). 규칙 정책 궤적에서 뽑은 고정 상태(검증 4500~4507 × 감축 없음·초기 40 %, 약 2,100개)에서 체크포인트 41개의 관수 행동 분포를 비교하고, 5개 체크포인트를 검증 16시즌에서 다시 돌렸다(현재 단가·현재 설정 기준이라 수익 수준은 18절 표와 다르다).

**1. PPO는 거의 언제나 물을 다 쓴다**(감축 없음 200 mm, 초기 40 % 120 mm). 성능 차이는 양이 아니라 **시기**에서 난다.

**2. 성능이 나쁜 시기 = 생육 초기(1·2단계)에 관수하는 시기.** 고정 상태에서 1·2단계 기대 관수량(mm/일):

| 단계 | 10만~25만 | 30만~150만 | 160만~205만 |
|---|---:|---:|---:|
| 1단계 | 0.0 | 0.4~5.1 | 0.1~0.9 |
| 2단계 | 0.0~0.4 | 3.4~13.6 | 0.8~3.6 |
| 검증 초기 40 % (18절) | 840~916 | 224~825 | 492~778 |

**3. 검증 시즌 단계별 관수(mm)와 순수익.**

| 체크포인트 | 조건 | 1단계 | 2단계 | 3단계 | 4단계 | 5단계 | 순수익 | 확인 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 15.4만 (최고) | 감축 없음 | 0 | 0 | 90.9 | 36.2 | **72.8** | **1318.5** | [ ] |
| | 초기 40 % | 0 | 0 | 81.9 | 22.5 | 15.6 | **1146.0** | [ ] |
| 46.1만 | 감축 없음 | **38.1** | 10.0 | 112.8 | 22.5 | 11.6 | 1056.4 | [ ] |
| | 초기 40 % | 11.2 | 7.5 | 95.6 | **0.6** | **0** | 635.3 | [ ] |
| 117.8만 | 감축 없음 | 3.1 | 11.6 | **142.2** | 24.7 | 18.4 | 1147.1 | [ ] |
| | 초기 40 % | 0 | 1.6 | 91.2 | 18.4 | 8.8 | 1039.8 | [ ] |
| 143.4만 (최저) | 감축 없음 | 30.9 | 14.4 | 125.9 | 20.3 | 5.6 | 1020.5 | [ ] |
| | 초기 40 % | **67.2** | 19.1 | 30.9 | **0** | **0** | **334.6** | [ ] |
| 204.8만 (마지막) | 감축 없음 | 5.9 | 3.1 | 127.8 | 40.6 | 22.5 | 1147.2 | [ ] |
| | 초기 40 % | 1.9 | 3.8 | 106.2 | 7.8 | 0.3 | 917.5 | [ ] |
| 규칙 정책 | 감축 없음 | 0 | 0 | 93.8 | 36.2 | 46.6 | 1270.1 | [ ] |
| | 초기 40 % | 0 | 0 | 88.8 | 22.5 | 7.5 | 1031.8 | [ ] |

최고 체크포인트는 1·2단계에 물을 주지 않고 개화·등숙기(4·5단계)에 남겨 규칙 정책보다 높다. 나쁜 체크포인트는 초기나 3단계에 물을 몰아 쓰고 개화·등숙기에 물이 없다. 모래 토양이라 뿌리가 얕은 초기에 준 물은 대부분 빠져나간다(해석).

**4. 정책은 굳지 않고 계속 크게 흔들린다.** 관수 행동 엔트로피는 0.32~0.65로 0에 가깝게 붕괴하지 않았다. 대신 51,200단계마다 이전 체크포인트와의 KL이 0.10~0.53, 고정 상태에서 최대확률 행동이 바뀌는 비율이 11~34 %다. 정책이 한 전략에 수렴하지 못하고 "초기 관수"와 "개화기 보존" 사이를 오간다.

### 원인 가설과 근거

| 가설 | 근거 (찬성) | 근거 (반대·한계) | 판정 |
|---|---|---|---|
| **A. 업데이트가 너무 강함** (256·256·10 = 업데이트당 경사 80회, 학습률 3e-4 고정, 엔트로피 0) | 체크포인트 간 정책 변화가 매번 크다(KL 0.1~0.5). 약한 업데이트(64·64·2)의 P1은 학습 수익이 꾸준히 올랐다 | P2(같은 설정)는 51만까지 무너지지 않았다(그 뒤는 미실행) | **유력** |
| **B. 보상 보정이 영양 생장을 유도** (Φ = 단가 × η × 지상부 건물중) | 관수로 지상부가 늘면 바로 보정 보상이 생기고, 개화기 물 부족 손해는 70~80일 뒤 수확에서야 드러난다. GAE λ 0.95의 실효 시야는 약 20일이라 늦은 손해가 가치함수 추정에 의존한다. 나쁜 체크포인트는 3단계 관수가 많고(112~142 mm) 5단계가 적다. Ng 1999의 불변성은 최적 정책에 대한 것이지 학습 과정에 대한 보장이 아니다 | 최고 체크포인트도 같은 보정으로 학습됐다. η를 바꾼 실험이 없다 | **가능** |
| **C. 감축 계약의 유인** (남은 물 비례 감축이라 감축 전에 쓴 물은 깎이지 않음) | 학습 시즌의 75 %에 13~112일 감축이 있어 "먼저 써 두기"가 일부 시즌에서 이득일 수 있다 | 143.4만은 감축 전 67 mm를 써서 총 사용 가능량은 늘었지만 순수익은 크게 낮았다. 이 토양에서는 초기 관수의 가치가 작아 유인이 약하다 | 약함 |
| D. 관측 정리(sw 등) | P3가 초반에 훨씬 빨리 배웠다(10만 단계에 규칙 초과). 빨리 배운 만큼 불안정 구간에 일찍 들어갔을 수 있다 | 하락 자체의 원인이라는 근거는 없다 | 학습 속도에만 관여 가능 |
| E. 시드 우연 | 모두 시드 1개, 초기 가중치도 다름 | — | 배제 불가 |
| F. 물 예산 제거·성숙 뒤 마스크·동시 실행 | — | 마스크가 같거나(물 예산이 먼저 막은 날 0일) 영향 기간이 시즌당 약 2일. 동시 실행은 속도만 바꿈 | 배제 |

**결론(해석).** 성능 흔들림의 직접 메커니즘은 **관수 시기 전략의 반복적 이동**(초기·영양기 관수 ↔ 개화·등숙기 보존)이다. 이를 키우는 요인으로 A(강한 업데이트)가 가장 유력하고, B(보상 보정의 단기 신호)가 방향을 정했을 수 있다. 관측 변경은 학습 속도를 높였을 가능성이 있지만 하락의 원인이라는 근거는 없다. 시드가 1개라 모두 잠정적이다.

### 분리 실험 제안 (결정 대기)

한 번에 하나만 바꾸고 나머지는 P3 설정(현재 단가·관수 규칙)으로 둔다. 각 100만 단계, 약 2.5시간.

| 실험 | 바꾸는 것 | 가설 | 기대 |
|---|---|---|---|
| ① | 시드 1·2 추가 | E | 같은 패턴이 나오면 시드 우연이 아님 |
| ② | 학습률 3e-4 → 0 선형 감쇠 | A | 후반 KL·흔들림 감소 |
| ③ | n_epochs 10 → 4 | A | 업데이트 강도 감소 |
| ④ | 보상 보정 끄기(또는 η 0) | B | 영양기 관수 쏠림 감소 |
| ⑤ | GAE λ 0.95 → 1.0 | B | 늦은 손해가 이점에 직접 반영 |

**문헌의 PPO 업데이트 설정 (`MARS_reference`, 2026-11-12 대조).** 업데이트당 경사 계산 = (롤아웃 ÷ 배치) × 에폭.

| 연구 | 롤아웃(업데이트당 자료) | 배치 | 에폭 | 경사 계산/업데이트 | 학습률 | 엔트로피 | 정한 방식 |
|---|---:|---:|---:|---:|---|---|---|
| Schulman 2017 MuJoCo | 2,048 | 64 | 10 | 320 | 3e-4 고정 | 0 | ε만 탐색, 나머지 고정 |
| Schulman 2017 Atari | 128 × 8 = 1,024 | 256 | 3 | 12 | 2.5e-4 **선형 감쇠** | 0.01 | 고정 |
| SB3 기본값 (Balderas 2025, Kallenberg 2023) | 2,048 | 64 | 10 | 320 | 3e-4 고정 | 0 | 기본값 그대로, 탐색 보고 없음 |
| Huang 2022 (행동 마스킹) | — | — | 10 | — | 3e-4, **감쇠** | 0.01 | 구현 세부 목록에 학습률 감쇠 포함 |
| Baja 2025 (질소, 제약 PPO) | 2,208 | 276 | 10 | 80 | 1e-3 | 0.01 | 표로만 제시, 탐색 절차 없음 |
| 이 연구 P1 | 64 × 8 = 512 | 64 | 2 | 16 | 3e-4 고정 | 0 | |
| 이 연구 P2·P3 | 256 × 8 = 2,048 | 256 | 10 | 80 | 3e-4 고정 | 0 | 시험 학습 51만 단계 비교 |

- 작물 RL 논문들은 업데이트 설정을 탐색해 고르지 않았고 SB3 기본값이나 한 가지 값을 썼다. Balderas 2025는 하이퍼파라미터 조정을 후속 과제로 남겼다.
- 현재 256·256·10(경사 80회)은 SB3 기본값(320회)보다 약하고 Baja 2025와 같은 수준이라, 업데이트 강도 자체가 문헌보다 과한 것은 아니다.
- 문헌과 다른 점은 **엔트로피 계수 0**(Atari·Huang·Baja는 0.01)과 **학습률 감쇠 없음**(Atari·Huang은 감쇠), **관측 정규화 없음**(Kallenberg는 VecNormalize)이다. 분리 실험 ②가 감쇠를 시험하고, 엔트로피 0.01은 다음 후보다.

**실행 (2026-11-12, 사용자 결정: ①②④ 먼저).** 네 실행을 동시에(각 CPU 3개) 102.4만 단계까지 돌린다: 시드 1, 시드 2(①), 시드 0 + 학습률 선형 감쇠(②), 시드 0 + η = 0(④). 모두 현재 설정(15.5 % 단가, 새 관수 규칙).
- `pilot_learning_curve.py`에 `--lr-schedule linear`(점검 구간마다 전체 단계 기준으로 3e-4 → 0, 구간 중간값), `--no-shaping`(η = 0으로 잠재항만 끄고 1/1,000 척도는 유지) 옵션을 추가했다. 처음 구현한 "보정 끄기"는 1/1,000 척도까지 꺼져 가치 손실이 약 5만 배로 커져, 척도가 교란되지 않게 η = 0 방식으로 바꿨다.
- 업데이트마다 SB3 학습 통계(KL, 클리핑 비율, 엔트로피, 가치 손실, 설명 분산, 학습률)를 점검 구간 평균으로 기록한다(`train_stats`).
- **첫 실행 실패 (2026-11-12 08:06~16:04).** 네 실행을 동시에 각 CPU 3개·메모리 4 GB로 띄웠으나, Docker 전체 메모리가 8.2 GB라 합계 16 GB가 넘쳐 모두 시작 직후 `Legacy DSSAT worker response timed out`으로 멈췄다(체크포인트 0개, 약 8시간 손실). 결과가 없는 실행 폴더 4개(`outputs/runs/20261111T2306*_pilot_b1_s*`)가 남아 있다. 이후 `scripts/run_separation_experiments.ps1`로 **한 번에 하나씩**(CPU 12, 메모리 7 GB) 학습률 감쇠 → η 0 → 시드 1 → 시드 2 순서로 다시 돌린다. 각 약 2시간.
- **교란 주의:** 비교 기준인 P3(시드 0)는 이전 단가(0.158)로 학습했다.

**② 학습률 선형 감쇠 결과 (2026-11-12 18:09 종료).** 근거: `outputs/runs/20261112T070529Z_pilot_b1_s0_ef2d5faa/pilot_state.json`. 시드 0, 현재 설정, 102.4만 단계. 정책 0 = 1270.1 / 1031.8(현재 단가). 최대확률 행동, 순수익 USD/ha.

| 단계 | 학습률 | 학습 시즌 수익 | 감축 없음 | 초기 40 % | 엔트로피 | 업데이트당 KL | 확인 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 5.1만 | 2.9e-4 | 964.6 | 1283.9 | 890.1 | 0.30 | 0.0079 | [ ] |
| 20.5만 | 2.5e-4 | **1133.4** | 1270.2 | **1140.0** | 0.21 | 0.0052 | [ ] |
| 30.7만 | 2.2e-4 | 1089.3 | 1234.8 | 879.4 | 0.19 | 0.0040 | [ ] |
| 46.1만 | 1.7e-4 | 949.1 | 1063.2 | **532.7** | 0.16 | 0.0039 | [ ] |
| 61.4만 | 1.3e-4 | 1029.6 | 1105.3 | 770.7 | 0.20 | 0.0031 | [ ] |
| 81.9만 | 6.8e-5 | 1007.0 | 1144.9 | 687.1 | 0.24 | 0.0024 | [ ] |
| 102.4만 | 8e-6 | 1107.0 | 1224.9 | 899.5 | 0.19 | 0.0009 | [ ] |

해석:
- **감쇠로도 중반 하락은 막지 못했다.** 20만 단계 최고(규칙보다 초기 40 % +108) 뒤 30~46만 단계에서 초기 40 %가 533까지 떨어졌다. 이때 학습률은 아직 1.7~2.2e-4로 높았다. 후반에 학습률이 작아지면서 899.5까지 일부 회복했지만, 마지막 점검은 여전히 규칙 정책보다 낮다(감축 없음 −45, 초기 40 % −132).
- **하락 시점이 P3와 거의 같다**(P3: 26~46만, ②: 31~46만). 둘 다 시드 0이고, 학습 시즌 순서는 시드와 무관해 두 실행이 같은 단계에서 같은 시즌을 봤다.
- **업데이트당 KL은 작다**(0.004 안팎). 정책이 큰 도약 없이 작은 업데이트를 같은 방향으로 계속 쌓아 나빠졌다. 최적화 잡음(가설 A)보다는 그 구간에서 일관되게 나쁜 쪽을 가리키는 학습 신호가 있었다고 보는 편이 맞다(해석).
**④ η = 0(보정 끄기) 결과 (2026-11-12 20:14 종료).** 근거: `outputs/runs/20261112T090949Z_pilot_b1_s0_bb8f6b92/pilot_state.json`. 시드 0, 학습률 고정, 잠재항 없음(1/1,000 척도 유지).

| 단계 | 학습 시즌 수익 | 감축 없음 | 초기 40 % | 엔트로피 | 업데이트당 KL | 확인 |
|---:|---:|---:|---:|---:|---:|---|
| 10.2만 | **1084.1** | 1196.0 | **1098.4** | 0.27 | 0.0059 | [ ] |
| 20.5만 | 1023.2 | 1136.6 | 1059.0 | 0.25 | 0.0067 | [ ] |
| 30.7만 | 855.3 | 1153.3 | 816.9 | 0.23 | 0.0071 | [ ] |
| 35.8만 | 1021.5 | 1206.8 | **711.7** | 0.18 | 0.0071 | [ ] |
| 61.4만 | 1006.9 | 1112.5 | 729.9 | 0.24 | 0.0064 | [ ] |
| 81.9만 | 945.3 | 1025.5 | **679.0** | 0.25 | 0.0067 | [ ] |
| 102.4만 (마지막) | 957.6 | 1120.0 | 851.9 | 0.26 | 0.0084 | [ ] |

해석:
- 보정을 꺼도 **같은 모양**이다: 10만~20만 단계에 최고(초기 40 %가 규칙보다 +67), 30만~36만 단계에 하락(같은 구간), 이후 규칙 정책 수준으로 돌아오지 못함(마지막 −150 / −180).
- 하락의 깊이는 P3·②보다 얕다(초기 40 % 최저 679 대 ② 533, P3 224). 대신 후반 개선도 없어 학습 시즌 수익이 950 안팎에 머물렀다. 가치 예측 설명 분산은 0.89로 보정 있을 때(0.94)보다 낮다.
- 따라서 **가설 B(보정이 원인)도 약하다.** 보정은 하락 폭을 키웠을 수는 있지만 하락 자체를 만들지 않았다.
- 세 실행(P3·②·④)이 모두 시드 0이고 **같은 30만~46만 단계 구간에서 떨어졌다.** 남은 후보는 G(그 구간의 학습 시즌 묶음)와 E(시드 0 초기화)이며, 시드 1·2가 가른다.

**① 시드 1 결과 (2026-11-12 22:18 종료).** 근거: `outputs/runs/20261112T111456Z_pilot_b1_s1_5df93d33/pilot_state.json`. 현재 설정 그대로(학습률 고정, η 0.45).

| 단계 | 학습 시즌 수익 | 감축 없음 | 초기 40 % | 엔트로피 | 업데이트당 KL | 확인 |
|---:|---:|---:|---:|---:|---:|---|
| 10.2만 | **1116.6** | 1082.3 | **1111.7** | 0.24 | 0.0049 | [ ] |
| 30.7만 | 1074.6 | 1225.3 | 1010.8 | 0.19 | 0.0064 | [ ] |
| 41.0만 | 994.4 | 1168.3 | 808.3 | 0.21 | 0.0060 | [ ] |
| 51.2만 | 1030.7 | 1168.2 | 757.8 | 0.25 | 0.0066 | [ ] |
| 61.4만 | 1104.1 | 1197.9 | 885.0 | 0.23 | 0.0066 | [ ] |
| 71.7만 | **787.0** | 1015.8 | 668.9 | 0.31 | 0.0096 | [ ] |
| 87.0만 | 971.0 | 1143.8 | **531.1** | 0.28 | 0.0079 | [ ] |
| 102.4만 (마지막) | 942.1 | 1039.1 | 821.3 | 0.26 | 0.0078 | [ ] |

해석:
- 시드 1도 **초반 최고 → 이후 하락 → 규칙 정책 아래로 끝남**(마지막 −231 / −211). 시드 0만의 문제가 아니다.
- 시드 1은 10만~36만 단계까지 초기 40 %에서 규칙 수준 이상(1,000~1,110)을 유지해 시드 0보다 오래 버텼다. 41만·51만 단계에 한 번 내려갔다가(808·758) 회복했고, 큰 하락은 70만 단계 이후에 왔다.
- 41만~51만 단계의 하락은 시드 0의 하락 구간(31만~46만)과 겹친다. 같은 시즌 순서의 영향(G)을 약하게 지지하지만, 큰 하락 시점은 시드마다 다르다(시드 0: 30만대, 시드 1: 70만대).

**① 시드 2 결과 (2026-11-13 00:30 종료).** 근거: `outputs/runs/20261112T131858Z_pilot_b1_s2_f84384ae/pilot_state.json`.

| 단계 | 학습 시즌 수익 | 감축 없음 | 초기 40 % | 엔트로피 | 확인 |
|---:|---:|---:|---:|---:|---|
| 15.4만 | 1115.9 | **1273.1** | 1135.4 | 0.19 | [ ] |
| 20.5만 | **1167.9** | 1141.7 | **1147.7** | 0.18 | [ ] |
| 25.6만 | 1025.8 | 1181.9 | 1064.0 | **0.15** | [ ] |
| 35.8만 | 973.8 | 1093.8 | **578.5** | 0.16 | [ ] |
| 61.4만 | 1097.4 | 1245.4 | 924.5 | 0.16 | [ ] |
| 102.4만 (마지막) | 1104.6 | 1141.2 | 988.3 | 0.18 | [ ] |

시드 2도 15만~20만 단계에 최고(규칙보다 초기 40 % +116), **30만~46만 단계에 하락**(시드 0과 같은 구간), 이후 일부 회복해 마지막은 −129 / −44.

**학습 시즌 묶음(G) 점검.** 30만~46만 단계에 들어오는 학습 시즌(시즌 번호 약 2,259~3,463)이 특별한지 두 가지로 봤다.
- 감축 추첨(`scripts/inspect_training_window.py`): 감축 비율 0.744(다른 구간 0.741~0.767), 평균 감축일 62.0일(63.0~63.3), 평균 감축률 0.395(0.397~0.421), 이른·큰 감축 비율 0.094(0.090~0.110). **차이 없음.**
- 시즌 난이도·초기 관수의 가치(`scripts/inspect_early_irrigation_value.py`, `outputs/runs/20261112T152317Z_early_irrigation_value_by_window_6b27c96d`, 구간마다 48시즌): 규칙 정책 순수익 1194.6 / **1204.0** / 1209.9로 같다. 1·2단계에 하루 10 mm를 더 주면 세 구간 모두 −935 ~ −1,043 USD/ha(구간이 서로 겹침, 이득인 시즌 0 %)로 크게 손해다. 이 시험은 초기 관수를 과하게 넣은 것이라 크기보다는 **구간 간 차이가 없다는 점**만 의미가 있다.
- 결론: **G는 지지되지 않는다.** 그 구간의 시즌이 초기 관수를 부추긴다는 근거가 없다.

### 다섯 실행 종합 (2026-11-13)

| 실행 | 최고 시점 | 최고 (감축 없음 / 초기 40 %) | 하락 구간 | 하락 직전 엔트로피 최저 | 마지막 (규칙 대비) |
|---|---|---|---|---|---|
| P3 시드 0 (이전 단가) | 10만~15만 | 1043.8 / 915.5 (이전 단가) | 26만~46만 | — (미기록) | 규칙 아래 |
| ② 시드 0, 감쇠 | 20만 | 1270.2 / 1140.0 | 31만~46만 | 0.16 (41만~46만) | −45 / −132 |
| ④ 시드 0, η 0 | 10만 | 1196.0 / 1098.4 | 31만~36만 | 0.17 (41만) | −150 / −180 |
| ① 시드 1 | 10만~31만 | 1225.3 / 1111.7 | 41만~51만, 70만~ | 0.18 (36만) | −231 / −211 |
| ① 시드 2 | 15만~20만 | 1273.1 / 1147.7 | 30만~46만 | 0.15 (26만) | −129 / −44 |

- **다섯 실행 모두** 10만~31만 단계에 규칙 정책 이상인 정책을 냈고, 모두 그 뒤 나빠져 **마지막 체크포인트는 모두 규칙 정책보다 낮다.** 시드·학습률 일정·보정 여부와 무관한 일반적 현상이다.
- 하락은 **엔트로피가 0.15~0.18까지 내려간 직후**에 온다(②·④·시드 1·시드 2). 하락 뒤에는 엔트로피가 다시 오르며(0.20~0.31) 일부 회복한다. 정책이 너무 일찍 결정론적으로 굳으면서 탐색이 줄고, 적은 다양성의 자료로 추정한 이점이 정책을 나쁜 전략(초기·영양기 관수)으로 끌고 가는 것으로 보인다(해석). 엔트로피 계수 0(문헌은 보통 0.01)과 맞는 설명이다.
- 가설 판정: A(학습률 고정) 약함, B(보정) 약함(하락 폭만 키움), G(시즌 묶음) 지지 안 됨, E(시드 0) 배제. **새 주 가설 H: 탐색 소실(엔트로피 계수 0)로 인한 조기 수렴 후 이탈.**

**결정 (2026-11-13, 사용자): 둘 다 진행.**
1. **엔트로피 계수 0.01 시험**(가설 H): 시드 0·2, 102.4만 단계, 한 번에 하나씩(`scripts/run_entropy_experiments.ps1`, `pilot_learning_curve.py --ent-coef`). 시드를 2개 쓰는 이유: 시드 하나로는 하락이 안 보여도 운인지 효과인지 가를 수 없고(시드 1은 31만까지 버티다 70만 이후 무너짐), 시드 0·2는 같은 구간(30만~46만)·같은 엔트로피 최저 직후에 뚜렷하게 떨어져 둘 다 버티면 근거가 강하다.
2. **체크포인트 선택 도입** (`scripts/run_comparison.py`, 설정 `training.checkpoint_selection`): 저장 간격(102,400단계)마다 현재 정책을 선택용 검증 시즌 32개(1200~1231)에서 평가하고, 점수가 가장 높은 체크포인트를 그 적합의 정책(`{label}.zip`)으로 쓴다. 마지막 체크포인트는 `{label}_final.zip`으로 따로 남기고, 선택 이력·선택 단계·점수를 학습 기록에 남긴다. 동결 사슬(정책 2·3)은 앞 정책의 **선택된** 체크포인트를 쓴다.
   - 점수: a 정책은 감축 없음 평균, b 정책은 감축 없음·초기 40 %·중기 40 %·후기 40 %를 0.25씩(학습 감축 확률 0.75를 세 시점에 나눔).
   - 선택용 시즌은 평가(2000~2999)·측정(1000~1119)·b0′ 탐색(3100~3239)·기준선 탐색(4000~4879)과 겹치지 않으며, 겹치면 실행을 거부한다.
   - 비용: 점검마다 a 32회, b 128회 평가(약 15초·1분), 100만 단계 적합당 b 약 10분.
   - 선택 기준 시즌과 평가 시즌이 분리돼 있어 선택 편향이 평가 결과에 들어가지 않는다. 다만 선택 시즌이 32개라 선택 자체에 잡음이 있다(해석).
   - 소형 전체 실행 확인(`outputs/runs/20261113T003917Z_policy_comparison_0f62c5ca`, 시드 1개·적합당 4,096단계·평가 시즌 1개): 적합 8개 모두 선택 점수·선택 단계 기록, 정책 2의 동결 체크포인트가 정책 1의 **선택된** 체크포인트와 같음(해시 일치), 검사 통과. 이렇게 짧은 학습에서는 정책이 관수를 거의 하지 않아 b1의 네 조건 점수가 모두 같았다(419.9).

### 엔트로피 계수 0.01 시험 결과 (2026-11-13)

실행: `outputs/runs/20261113T003738Z_pilot_b1_s0_6d46c01a`(시드 0), `outputs/runs/20261113T024512Z_pilot_b1_s2_affaa19b`(시드 2). ent_coef 0.01 외에는 현재 설정과 같음(학습률 3e-4 고정, η 0.45, λ 0.95). 검증 시즌 4500~4515, 탐욕 평가, 규칙 정책 1270.1 / 1031.8.

| 실행 | 엔트로피 범위 | 최고 (감축 없음 / 초기 40 %) | 하락 구간 | 최저 | 마지막 (규칙 대비) | 학습 수익 최저 |
|---|---|---|---|---|---|---|
| 시드 0, ent 0.01 | 0.27~0.35 | 1165.5 / 1137.5 (10만) | 36만~46만 | 895 / 461 (46만) | 1111.6 / 714.0 (−158 / −318) | 558 (46만) |
| 시드 0, ent 0 (④·② 참고) | 0.16~0.31 | 1196 / 1098 (10만) | 31만~46만 | — | 1120 / 852 (④) | 855 |
| 시드 2, ent 0.01 | 0.23~0.37 | 1148.2 / 1107.7 (10만) | 26만~ | 700 / 399 (72만) | 969.5 / 416.3 (−301 / −616) | 496 (77만) |
| 시드 2, ent 0 (①) | 0.15~0.29 | 1273.1 / 1147.7 (15만~20만) | 30만~46만 | 1094 / 579 (36만) | 1141 / 988 (−129 / −44) | 862 |

- **엔트로피는 무너지지 않았는데도(최저 0.23~0.27, 이전 실행의 0.15~0.18보다 높음) 같은 구간에서 더 크게 떨어졌다.** 두 시드 모두 마지막 점수가 엔트로피 계수 0일 때보다 낮다(초기 40 % 기준 시드 0 −138, 시드 2 −572).
- 하락 때 **학습 시즌 수익도 함께 떨어진다**(시드 0: 1057 → 558, 시드 2: 970 → 496). 검증 시즌에만 나타나는 과적합이 아니라, 학습 분포에서도 정책이 실제로 나빠지는 것이다.
- 하락 구간에서는 갱신당 KL(0.007~0.010)과 클립 비율(0.06~0.08)이 이전 실행(0.005~0.007, 0.045~0.05)보다 높다. 반대로 학습률 감쇠(②)는 후반 KL이 0.001까지 줄면서 마지막에 1225 / 900으로 회복했다.
- **가설 H(탐색 소실) 기각.** 엔트로피를 높게 유지하면 오히려 정책이 더 많이 흔들린다. 지금 증거로는 **최적화 불안정(갱신 크기가 큼)** 쪽이 가장 맞다(해석): 학습률 감쇠에서만 후반 회복이 있었고, 엔트로피 보너스로 갱신이 커지면 더 나빠진다.
- **결정: ent_coef는 0을 유지한다.** 하락 자체는 아직 해결되지 않았으므로, 본 학습에서는 체크포인트 선택(위 2번)이 1차 대응이다. 다섯 + 두 실행 모두 10만~20만 단계에 규칙 정책 근처의 체크포인트가 있었으므로, 선택 방식이면 이 시점을 잡을 수 있다.
- 남은 후보(결정 대기): 갱신 크기를 줄이는 실험, 즉 ③ n_epochs 4, 또는 학습률 1e-4, 또는 학습률 감쇠를 체크포인트 선택과 함께 쓰는 것.

- 따라서 가설 A(학습률 고정이 원인)는 **약해졌다.** 남은 후보는 B(보상 보정의 단기 신호), 시드 0 초기화, 그리고 **새 후보 G: 그 단계에 들어오는 학습 시즌 묶음**이다. 시드 1·2(①)는 같은 시즌 순서를 보므로, 같은 구간에서 떨어지면 G, 아니면 시드 0 초기화 쪽이다. ②·④는 P3와 단가가 다르므로, 같은 단가인 ①(시드 1·2)과도 함께 비교한다. 단가 차이는 수익 부분만 1.183배라 이점 표준화로 대부분 상쇄되지만 완전히 같지는 않다.

## 26. 본 학습 전에 튜닝해야 하는 값 (2026-11-12 정리)

"튜닝"은 검증 시즌 탐색·시험 학습으로 값을 고르는 것이다. 근거로 정하는 값(가정·문헌)은 따로 적었다. 최종 시험 구간은 쓰지 않는다.

### A. 튜닝 완료 (24절, 15.5 % 단가 기준)

| 값 | 현재 | 방법 | 다시 튜닝해야 하는 경우 |
|---|---|---|---|
| 관수 단계 규칙 `stage_water` | [[3,0.5,20],[4,0.05,20],[5,0.3,15]] | 좌표 탐색 + 확인 시즌 | 단가·물 공급·작물 모형·해충 계수가 바뀔 때 |
| 시비 일정 `baseline_nitrogen` | {45:80, 65:54, 95:27} | 좌표 탐색 + 확인 시즌 | 위와 같음, 관수 규칙이 바뀔 때 |
| 질소 예산 | 441.03 USD (27절, 이전 190.39) | 시비 일정 + 1회 최대량 | 시비 일정이 바뀔 때 |
| 방제 임계 `survey_threshold` | 0.7 | 격자 탐색 | 해충 계수·살포비·단가가 바뀔 때 |
| b0′ 예비량·개화일·성숙일·간격·남은 수요 | 78.0 mm, 83, 130, 10.0일, … | 규칙 정책 측정 | 관수 규칙이 바뀔 때 |
| b0′ 여유 비율 | 0.4 | 격자 탐색 + 확인 시즌 | b0′ 값이 바뀔 때 |

### B. 튜닝 남음 — 본 학습 전 필수 (순서대로)

| 순서 | 값 | 현재 | 상태 | 결정 근거 |
|---:|---|---|---|---|
| 1 | **학습 안정화**: 학습률 일정, n_epochs(필요하면 ent_coef) | 3e-4 고정, 10, 0 | ② 감쇠: 하락은 남고 후반 회복만. ent 0.01: 더 나빠져 기각(ent_coef 0 유지). ③ n_epochs 4 또는 학습률 1e-4 대기 | 25절: 학습 후반 정책이 크게 흔들려 규칙보다 낮아짐 |
| 2 | **보상 보정 η** (켜기·끄기) | 0.45 | 분리 실험 ④(η 0) 진행 중 | 25절 가설 B. 끄는 쪽이 낫다면 D8 재결정 |
| 3 | GAE λ | 0.95 | ⑤ 대기(②·④ 결과에 따라) | 25절 가설 B |
| 4 | **체크포인트 선택 방식** | 검증 시즌 1200~1231 최고점 | 구현·소형 실행 확인 완료 (25절) | 학습 중 성능이 흔들리면 마지막 점검이 운에 좌우됨. 별도 검증 시즌으로 고르는 방식이면 그 시즌 구간·평가 간격도 정해야 함(평가 2000~2999, 튜닝 3100~4879와 겹치지 않게) |
| 5 | **학습량·시드 수** (D10) | 500만 × 10 (설정) | 1~4 뒤 결정 | 100만×10 또는 200만×5. 평가 시간 포함 약 12~14일 |
| 6 | 희소 초기 확률 (B1) | 0.13·0.03·0.03 | 미결 | 시험 학습 PPO는 무투입이 아니라 물을 다 쓰는 쪽이라, 관수 0.13의 탐색 여유는 필요 없어 보인다(해석) |
| 7 | **시비·방제 학습 확인** | — | 미실행 | 지금까지 시험 학습은 관수만 배우는 b1뿐이다. b2(시비)·b3(방제)·b4(동시)는 결정이 드물고 행동이 커서, 1~6을 정한 뒤 짧은 시험 학습으로 학습이 되는지 확인해야 한다 |

### C. 튜닝 대상이 아님 — 근거로 정하는 값 (결정 필요)

| 값 | 현재 | 상태 |
|---|---|---|
| 해충 유입 확률·크기, 증식률 범위 | 0.03·0.05, 0.05~0.15 | 가정. 사용자 결정 없음 |
| 살포 효능·잔효 | 0.8, 5일 | 가정으로 유지 결정(17절) |
| 피해 계수 α | 0.01 | 문헌 범위 맞춤으로 결정(17절) |
| 조사 잡음 | 0.01 (민감도 0.05) | 가정 |
| 살포 자재비·작업비, 관수·시비 작업비, 물·질소 단가 | 24.7·24.7, 2.04·34.8 USD, 1.17 USD/mm, 1.83 USD/kg | **2026-11-13 결정** (27절). A 재튜닝 필요 |

해충·경제 값은 A의 규칙 튜닝 결과에 영향을 준다. C를 바꾸면 A를 다시 튜닝해야 한다.

### 의존 관계

C(경제·해충 값) → A(규칙 기준선) → B1~B4(학습 설정) → B5(학습량·시드) → B7(시비·방제 확인) → 사전등록 동결 → 본 학습.

## 27. 경제 값 출처 확정 (2026-11-13)

C의 비용 값(살포 자재비·작업비, 관수·시비 작업비)은 출처가 없었다. 원 실험 지역(Gainesville, 플로리다 북부)에 가까운 공개 자료로 바꾸고, 물·질소 단가도 같은 기준으로 맞췄다. **결정(사용자): 연도는 2025·2026 혼용, 값이 없는 항목은 다른 검증된 자료에서 가져온다.** 모든 숫자는 원문(PDF 텍스트·공식 데이터)에서 확인했다. $/acre × 2.471 = USD/ha.

| 항목 | 이전 | 새 값 | 출처 | 원문 값 |
|---|---|---|---|---|
| 물 `water_usd_mm_ha` | 1.1 | **1.17** USD/mm/ha | Alabama Extension ANR-2852 관개 옥수수 예산서 2026(2026년 2월 개정) | Irrigation AC/IN 11.00 × $12.00 |
| 질소 `nitrogen_usd_kg` | 0.79 | **1.83** USD/kg N | USDA AMS Alabama Production Cost Report(주간, 3051) 공식 데이터 | 질산암모늄 2025년 48주 평균 565.2 USD/톤(520~590), 유통상 출고가. ÷ (907.2 kg × 0.34) |
| 살포 자재비 `spray_product_usd_ha` | 35.0 | **24.7** USD/ha/회 | ANR-2852 2026 | Insecticides ACRE 1.00 × $10.00 |
| 살포 작업비 `spray_labor_usd_ha` | 15.0 | **24.7** USD/ha/회 | ANR-2852 2026 | Aerial Application ACRE 2.00 × $10.00 (1회 $10) |
| 관수 작업비 `irrigation_labor_usd_event_ha` | 3.0 | **2.04** USD/ha/회 | LSU AgCenter 2025 고구마 예산서 부록 표 2(이동식 관 고랑 관수, 9 acre-inch, 4회) | Irrigation Labor 0.223 h × $14.83 = $3.31/acre ÷ 4회 |
| 시비 작업비 `nitrogen_labor_usd_event_ha` | 5.0 | **34.8** USD/ha/회 | Iowa State 2026 Farm Custom Rate Survey(A3-10, 2026년 3월 개정) | Liquid side dressing $14.10/acre(중앙 14.50, 8.00~20.00, 응답 38) |
| 질소 예산 `budgets_usd_ha.nitrogen` | 190.39 | **441.03** USD/ha | (πB 161 + 1회 최대 80) kg × 1.83 | — |
| 살포 예산 `budgets_usd_ha.spray` | 150 | 150 (유지) | 1회 49.4라 3회(148.2)까지, 4회째(197.6)는 막힘. D5 3회 상한 유지 | — |

- **원 실험 방식과의 대응:** FileX(UFGA8201.MZX)의 관수는 고랑 관수(IR001), 시비는 질산암모늄 지표 살포(FE001/AP001)다. 질소 단가는 같은 비료의 시세를, 관수 작업비는 같은 고랑 관수 예산을 썼다. 시비일(45·65·95일)은 옥수수가 커서 일반 살포기가 들어갈 수 없으므로 생육 중 지상 시비(곁거름) 요금을 썼다. 관비는 모형이 시비와 관수를 독립 행동으로 다루고(`anfer`, `amir`) 관수 0인 날에도 시비할 수 있어 맞지 않는다.
- **Alabama에 없는 값:** 시비 작업비(예산서는 장비비 $38/acre에 묶음)는 Iowa 2026, 관수 1회 작업비(예산서는 시즌 노동 2 h만 표시)는 LSU 2025에서 가져왔다. UGA C1235(2021)의 acre-inch당 0.28 h는 1회 25.4 mm 가정이라 1회 5~25 mm인 이 환경에서 과대평가돼 쓰지 않았다.
- **Alabama 2025 예산서**(ANR-2852 CornIRR25)는 사이트에서 삭제돼(404) 읽지 못했다. 검색 요약상 관수 11 acre-inch × $12로 2026판과 같다.
- **곡실 단가 0.158 USD/kg(Tao 2023)은 바꾸지 않았다.**
- **영향:** 규칙 정책 기준 시즌 비용이 질소 +167 USD/ha(161 kg × 1.04), 시비 작업 +89(3회 × 29.8), 살포 −0.4, 관수 작업 −12.7(13.2회 × 0.96), 물 +약 9(132 mm × 0.07) 바뀐다(해석: 회수·사용량은 24절 규칙 정책 기준). 질소 단가가 2.3배, 시비 작업비가 7배라 **A(시비 일정·관수 규칙·방제 임계·b0′) 재튜닝이 필요하다.** 24절 결과는 이전 단가 기준이다.
- 코드: `ResourceRules` 기본값과 단가를 쓰는 테스트 기대값을 새 단가로 바꿨다(250개 통과). 관측 척도(nitrogen_used 241 kg 등)는 kg·mm 단위라 바뀌지 않는다.

## 변경 이력

| 날짜 | 항목 | 변경 | 사유 |
|---|---|---|---|
| 2026-11-10 | `management.baseline_nitrogen` | {40:27, 45:35, 80:54} → {45:54, 65:35, 85:27} | 비교 실험 지시 |
| 2026-11-10 | `scenarios.timing` 외 감축 키 | 단계 기준 → 달력일 기준 | 비교 실험 지시 |
| 2026-11-10 | `scenarios.evaluation_delay_days` | null → 3 | 단계 기준 보조 분석용 |
| 2026-11-10 | `training.n_steps`, `batch_size`, `n_epochs` | 코드 고정 → 설정 키 64, 64, 2 | 비교 실험 구현 |
| 2026-11-11 | `training.n_steps`, `batch_size`, `n_epochs`, `n_envs` | 64, 64, 2, 4 → 256, 256, 10, 8 | 시험 학습 비교, 임의 결정 (18절 B3) |
| 2026-11-11 | `reward_shaping.eta_by_stage`, `training.gae_lambda` | 0.45, 0.95 유지 | 임의 결정 (18절) |
| 2026-11-11 | 관측 (`observations.py` `FIELDS`), `environment.frame_size`, `observation_size` | 45개·315 → 28개·196, sw 뿌리 영역 평균(척도 0.15) | 임의 결정 C안 (22절) |
| 2026-11-11 | `economics.budgets_usd_ha.water` | 220.0 → 제거 | 공급량보다 먼저 제한한 날 0일, 임의 결정 (23절) |
| 2026-11-11 | `management.input_closed_istage` | 신규 6 | 성숙 뒤 관수·시비 마스크, 임의 결정 (23절) |
| 2026-11-12 | `baseline_policy.stage_water` | [[3, 0.5, 15], [4, 0.1, 20], [5, 0.2, 15]] → [[3, 0.5, 20], [4, 0.05, 20], [5, 0.3, 15]] | 15.5 % 환산 후 재탐색 채택 (24절) |
| 2026-11-12 | `economics.grain_moisture_fraction` | 신규 0.155 | 매출을 수분 15.5 % 시장 기준으로 환산, 임의 결정 (1절) |
| 2026-11-12 | `scenarios.sensitivity_seasons_per_condition`, `sensitivity_rows`, `evaluation_workers` | 신규 300, [a, b_none, b_cut], 8 | 평가 시간 단축 ①+③, 임의 결정 (5절) |
| 2026-11-11 | 무투입 대조 | 비교 실험 결과표에서 제외 확정 | 임의 결정 |
| 2026-11-11 | `environment.initial_water_mm` | 264.0 → 200.0 | 임의 결정, 감축 구속력 확보 |
| 2026-11-11 | `economics.budgets_usd_ha.water` | 290.4 → 220.0 | 공급량×1.1 연동 |
| 2026-11-11 | 관측 척도 water_used·water_left·initial_water·initial_water_budget | 264·264·264·290.4 → 200·200·200·220 | 공급량 연동 |
| 2026-11-11 | `reduction_response_rule.reserve_mm`, `event_interval_days` | 59.0, 8.1 → 58.6, 8.2 | 200 mm 재측정 |
| 2026-11-11 | `economics.budget_multipliers` | [0.6, 1.0, 1.4] → [1.0] | 임의 결정 |
| 2026-11-11 | 평가 감축일 방식 | 변경 없음, 13·37·83일 고정 유지 확정 | 임의 결정 |
| 2026-11-11 | `baseline_policy.stage_water` | 없음 → [[3, 0.5, 15], [4, 0.1, 20], [5, 0.2, 15]] | 기준선 탐색 채택 |
| 2026-11-11 | 시즌 물 공급량 | 변경 없음, 단계별 규칙 기준에서도 200 mm 유지 확정 | 임의 결정 |
| 2026-11-11 | `baseline_policy.stage_water` | 변경 없음, 범위 확장 탐색 결과 채택 기준 미달 | 확장 탐색 |
| 2026-11-11 | 12절 | 기준선 후보 1·2 완료, 3 미채택 표시. 관수 민감도 조건을 후속 연구로 이동 | 임의 결정 |
| 2026-11-11 | 감축일·감축률 | 변경 없음, 학습 13~112일·평가 13·37·83일·감축률 20·40·60 % 승인 | 임의 결정 |
| 2026-11-11 | b0′ `reserve_mm`, `event_interval_days`, `remaining_demand_mm` | 58.6, 8.2, 130.9 기준 → 74.3, 10.7, 151.5 기준 | 단계별 규칙 재측정 |
| 2026-11-11 | b0′ 적용 조건 | 감축 후 항상 예비 적용 → 남은 물이 πB 남은 수요보다 적을 때만 (`remaining_demand_mm` 추가) | 임의 결정 |
| 2026-11-11 | `management.baseline_nitrogen` | {45: 54, 65: 35, 85: 27} → {45: 80, 65: 54, 95: 27} | 시비 일정 탐색 채택 (+112.8 USD/ha) |
| 2026-11-11 | `economics.budgets_usd_ha.nitrogen` | 91.64 → 190.39 | πB 161 kg + 회당 최대 80 kg |
| 2026-11-11 | 관측 척도 nitrogen_used·initial_nitrogen_budget | 200·91.64 → 241·190.39 | 질소 예산 연동 |
| 2026-11-11 | b0′ `reserve_mm`, `event_interval_days`, `remaining_demand_mm` | 74.3, 10.7, 151.5 기준 → 80.3, 9.8, 161.0 기준 | 새 시비 일정 재측정 |
| 2026-11-11 | `environment.required_nitrogen_values` | [0, 10, 27, 35, 54] → [0, 27, 54, 80], 격자 9단계 유지 | 임의 결정 |
| 2026-11-11 | b0′ `reserve_mm`, `event_interval_days`, `remaining_demand_mm` | 80.3, 9.8, 161.0 기준 → 84.0, 9.3, 165.2 기준 | α 0.01 재측정 |
| 2026-11-11 | `reduction_response_rule.demand_margin` | 없음(1.0과 같음) → 0.4 | 임의 결정(여유 두기), 검증 시즌 탐색 |
| 2026-11-11 | `baseline_policy.survey_threshold` | 0.3 → 0.7 | 방제 임계 탐색 채택 (+10.5 USD/ha) |
| 2026-11-11 | b0′ `reserve_mm`, `event_interval_days`, `remaining_demand_mm` | 84.0, 9.3, 165.2 기준 → 83.5, 9.4, 163.6 기준 | 방제 임계 변경 재측정 |
| 2026-11-11 | `scenarios.evaluation_survey_noise_std` | 없음 → [0.05] | 임의 결정, 민감도 조건 |
| 2026-11-11 | `validation_gates.dssat_state_read` | false → true | 임의 결정, 요구 항목 모두 다른 검사로 통과 |
| 2026-11-11 | 연구 진입 조건 | 미충족 7개 → 2개 (원소 C, Q/F N, 수확 N, 단 B, 계보를 한계로) | 임의 결정, 20절 |

| 2026-11-11 | 해충 계수 출처 | 코드 고정 10·30 °C·0.01 → 설정에서 읽음, 설정 null → 10·30·0.01 | 방제 개선 1 |
| 2026-11-11 | `pest.alpha` | 0.03 → 0.01 | 문헌 적엽·손실 범위 (사전 규칙 0.005에서 벗어난 임의 결정) |
| 2026-11-13 | `economics.water_usd_mm_ha` | 1.1 → 1.17 | Alabama 2026 예산서 (27절) |
| 2026-11-13 | `economics.nitrogen_usd_kg` | 0.79 → 1.83 | USDA AMS Alabama 질산암모늄 2025 평균 (27절) |
| 2026-11-13 | `economics.spray_product_usd_ha`, `spray_labor_usd_ha` | 35.0, 15.0 → 24.7, 24.7 | Alabama 2026 예산서 (27절) |
| 2026-11-13 | `economics.irrigation_labor_usd_event_ha` | 3.0 → 2.04 | LSU 2025 고랑 관수 (27절) |
| 2026-11-13 | `economics.nitrogen_labor_usd_event_ha` | 5.0 → 34.8 | Iowa 2026 액비 곁거름 (27절) |
| 2026-11-13 | `economics.budgets_usd_ha.nitrogen` | 190.39 → 441.03 | 질소 단가 연동 (27절) |

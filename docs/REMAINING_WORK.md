# 남은 작업과 진행 순서

## 2026-11-10 현재 남은 작업

**본학습 보류.** 현장 검증에 3단 증거 기준을 채택했고 SIAZ 1995 물 반응이 단 A를 통과했다. 본학습 진입 조건은 7개가 미충족이다. [3단 기준과 판정](FIELD_VALIDATION_TIERS.md) · [준비 판정](../outputs/runs/20261109T231526Z_readiness_201ef9d7/readiness.json) · [진입 조건](PRETRAINING_READINESS.md)

| 순서 | 남은 작업 | 완료 조건 |
| --- | --- | --- |
| 기술 검증 후속 | **실패 당일 흡수 질소 차감** | 사질토 저온 실패에서 층별 차감 후보를 Q/F 각각 검증했다. 다음 범위는 다른 실패 경로·토양과 승인 대상 이미지에서의 회귀 및 적용 범위 확정이다. [격리 후보 검증](TERMINAL_N_DEBIT_CANDIDATE.md) |
| 병행 가능한 기술 검증 | **전체 원소 C와 Q/F N 배분** | 작물 재고·종자·동화·호흡·수확·피해 반출의 C를 단위와 시점에 연결한다. 수확·휴경·다음 작물에서 N 반출과 전달이 한 번씩 기록되는지 대상 이미지의 고정밀 출력으로 확인한다. |
| 다음 농학 검증 | **피해·회복 상대 수량비 검증 (단 B)** | 기준을 동결했다. Purdue 2024–2025년 적엽 9처리의 수량비를 16시즌 160회 실행과 비교한다. 9칸 RMSE 0.10 이하와 99% 적엽의 시기별 순서 재현이 합격 조건이다. 물×질소×피해 공동 처리와 신규 피해 조사 오차는 한계·민감도 항목으로 옮겼다. [동결 기준](FIELD_VALIDATION_TIERS.md) |
| 농학·수지 검증 후 | **기준 정책 선택과 최종 시험 설계 동결** | 공통 검증 시즌에서 규칙 정책·GAE·보상 계수를 선택한다. 최종 시험 접근 전에 이미지·자료 분할·시드·감축일 달력·H1/H2 대비·통계 절차를 고정한다. |
| 진입 조건 충족 후 | **본학습·최종 평가** | 관수 전용과 공동 관리 정책을 각각 10시드×500만 단계로 학습한다. 무감축 포함 10조건을 공통 시즌 1,000개로 평가하고 순수익·하위 10%·수량·투입량·실패율과 교차 부트스트랩·Holm 보정 결과를 보고한다. |

### 완료된 검증 범위

- **WGEN 수정 후 예비 학습.** 두 시비 제한 방식 각각 3시드를 새로 학습했고 검증 256회를 통과했다. 고정 관리를 기준으로 유지한다. [비교 결과](PEST_PPO_WGEN_RETRAIN.md)


- **다년 모형 질소.** 두 범용 토양의 관리 조건은 곡실/부산물 100%/0%와 50%/50%, 무관수·무시비는 50%/0%에서 2년 Q/F 원장을 검증했다. 최신 무관수·무시비 조건에서 질소 재고 2,936개와 전환 경계 12개를 검산했다. 부산물 N은 정의된 배분값이다. [관리 조건](MULTIYEAR_GENERIC_F.md) · [무관수·무시비](MULTIYEAR_ZERO_INPUT_QF.md)
- **수확·토양 탄소.** 단년 부분 수확의 후보 16개가 모형 N 검사를 통과했다. 대조의 잔사 부족을 재식 밀도와 이삭 밀도의 차이로 재구성했다. 기존 휴경 끝에서 누락된 144일을 확보해 토양 C 출력 5,840일을 검산했다. [부분 수확](QF_PARTIAL_HARVEST_N.md) · [잔사 부족 원인](QF_CONTROL_N_BOUNDARY.md) · [토양 C 출력](QF_TERMINAL_AND_SIAZ_CALENDAR.md)
- **현장 입력.** SIAZ 17처리의 관수 94건에서 날짜와 양이 논문·DSSAT 입력·실행 출력과 일치했다. 1995년 강수 집계 차이와 반복구 자료 공백이 남아 있다. [SIAZ 관수 검증](QF_TERMINAL_AND_SIAZ_CALENDAR.md) · [BRPI0202 입력 감사](BRPI2002_MANAGEMENT_AND_WEATHER_QUALIFICATION.md)
- **예비 정책과 소프트웨어.** 검사 204개와 CPU/CUDA 기술 실행을 완료했다. 공동 PPO에서 저장된 조기 시비를 늦춘 결과는 실험용 해충 환경의 사후 진단으로 보존한다. [시비 지연 진단](PPO_EQUAL_N_DELAY.md)

본학습 1억 단계의 기존 CPU 순차 실행 추정은 8.9~15.3일이다. 최종 평가·중단 후 재개 시간은 별도이며, 착수일은 진입 조건을 충족한 뒤 정한다. [처리량 근거](PEST_PRICE_GATE_VALIDATION.md)

## 2026-11-07 계획과 후속 자료 조사 기록

기준일2026-11-07. 기준폴더 `C:/Users/WD/Desktop/강화학습_MARS`.

현재 소프트웨어204개 검사와 CPU/CUDA 각각102,400단계 기술 실행은 통과했다. 공개10연구의 정량 검증 준비는0개이며 `research_ready=False`, `main_training_allowed=False`다. 이 문서는 저장된 근거의 요약이며 새 검사·학습 실행 결과가 아니다.

## 1. 가장 먼저: 보정자료와 독립 검증 입력

1. **별도 현장 건조 곡실 보정자료 선별.** 건조 수량 기준, 공동 처리값과 수치 불확실성/사전 허용범위, 토양층·초기 수분/N, 일별 기상·파종/물/N 일정, 품종계수 보정노출, 피해 기작을 갖춘 자료를 찾는다. 기존 독립 검증 연구를 보정용으로 전환하지 않는다.
2. **Oliveira 두 연구의 실험 중복·단위 확인.** 날짜/품종/포트/반복 식별자, 식물수와 곡실 무게·수분 기준을 대조한다. 같은 실험을 별도 보정·검증 연구로 세지 않는다.
3. **온도별 발육·생존 제약 추출.** 발육자료로 확인 가능한 범위를 수치화하되 개체군 증가율·도착·밀도·조사잡음으로 바로 대체하지 않는다.

Oveysi 입력 명세는17항목 작성 완료지만14항목은 부분 정보/미확정이다. 추가로 필요한 것은 실험연도 일별 기상, 전체 토양/초기상태, 밀도 단위 확인, SC704 계수와 계보, 실제 관수/시비·생육단계 날짜, 피해 매핑, 수치 오차다. 명세 작성 완료를 시뮬레이션 재현 완료로 해석하지 않는다.

LIRF는 일부 입력의 native 전달을 확인했으나 정확한 보정 계보·현장 입력·계측 불확실성이 미해결이다. 원자료의 수분 깊이 충돌과 요약/수분결핍 차이도 유지한다. Fang2014 원문은 미확보다. 이 항목들은 누락 명세로 추적하며 입력 또는 계수를 임의로 교정하지 않는다.

## 2. 농학·보존수지 검증

- 확보한 입력으로 무피해 생육·수량부터 재현한 뒤 초기/후기·반복/강한 피해, 수분×질소 조건에서 피해 전달과 회복을 검증한다. 반응이 반드시0이거나 건조 조건에서 반드시 악화돼야 한다는 조건을 넣지 않는다.
- 기존 모형N 검사는 확인한 토양·기간·모드 범위에 한정한다. 다른 실패 경로·초기화·잔사/부산물 조건으로 확장할 범위를 명시한다.
- 전체 원소C는 미완료다. 건물중을 탄소량으로 간주하지 않고 종자·작물C·동화·호흡·수확·피해 반출 항목의 측정 가능성과 수지를 확보한다.
- 온도 기준·조사잡음·피해 계수는 식별 가능한 범위에서만 보정한다. 부족한 근거는 가정/민감도 항목으로 유지한다. 현재 보상eta=.45도 민감도 검토가 필요하다.

완료 조건은 독립 자료·사전 판정 기준·원자료/설정/이미지 식별자로 적용 범위 안의 재현성을 입증하는 것이다. 소프트웨어 검사나 짧은 학습 수익만으로 통과시키지 않는다.

## 3. 기준선·예비 학습·실험 설정

- 규칙πB·무투입의 기존 기술 검사를 바탕으로 validation에서 관수/방제 임계값을 결정한다. 관수 전용πI는πB의 시비·방제 규칙을 공유하고 공동 관리πJ와 동일 자원 제약을 적용한다.
- GAE후보·보상계수 등은validation에서만 선택한다. 실제 CPU/GPU 비교는 동일 설정·유휴 조건으로 측정하고 그 실측으로 전체 계산 일정을 산정한다.
- 연구 진입 조건을 충족한 뒤 품종·모형·이미지·설정·시드·자료split을 동결한다. 최종 시험 감축일 달력, H1/H2사전 대비·통계 절차를 시험 전에 확정한다.

CPU/CUDA 장기 기술 실행 자체는 완료된 범위가 있으므로 이를 미완료 본 학습과 구분한다.

## 4. 본 실험과 보고

- πI·πJ 각10시드×500만 단계, 총1억 단계 학습.
- 공통 외생 시즌으로 감축 조건과 무감축 조건을 대응 평가.
- 평균 수익·하위10%평균·수량·투입량·실패율·제약 위반, 학습시드/시즌 교차 부트스트랩·Holm보정·효과크기/불확실성 보고.
- 보상·단가/예산·해충·초기화 등 민감도와 H3의 검증 가능한 범위를 보고. 대체 모형을 채택하면 연구 범위를 다시 명시하고 H3 제외 조건을 적용한다.

현재 이 단계는 시작하지 않는다. 자료 확보와 농학 검증이 끝나지 않아 완료율이나 전체 완료일을 수치로 확정하지 않는다.

## 추적 문서

- `PROGRESS.md`: 작업별 시작·완료·실패와 근거.
- `docs/AGRONOMIC_INPUT_PRIORITIES.md`, `configs/agronomic_input_priorities.json`: 연구10개/후속5작업의 상세 상태.
- `docs/OVEYSI2010_INPUT_DOSSIER.md`: 완료한 입력 명세와 미확정14항목.
- `docs/LIRF_MISSING_DATA_SPEC.json`, `docs/FANG_LINEAGE_FOLLOWUP.md`: 계측·보정 계보 공백.
- 최근 준비상태: `outputs/runs/20261107T105054Z_readiness_8efb2085/readiness.json`.

LIRF 2012–2013의 누적 관측과 재현 입력 공백을 정리했다. Battaglia R2 적엽 시행일 2건을 확인했고 포장별 실제 손실량·회복 쌍은 미확보다. 별도 포장 적엽 자료 5개에서도 실제 손실량–회복 연결을 확보하지 못했다. LeafScan 모의 피해 손실률 94개를 재현했으며 독립 판독은 확인하지 못했다. 실제 FAW 자료에서도 7일 신규 피해와 독립 판독의 연결은 미확보다. 물×질소×잎 피해 공동 처리 자료 7개에서 적격 포장 설계는 0개였다. KBS033 7시즌의 포장 수량과 2023년 관리 일지를 대조했다. 2023년 기온 결측 대체와 초기 토양·품종계수는 미확보다. KBS033 군 내 질소 대비 126개를 계산했다. 2023년 F1·F2 기비 계획의 차이를 확인했다. KBS033 2014년 관리·기상 자료를 대조했다. DKC52-59 독립 출사 관측 1개를 확인했고 계수는 미확보다. 미네소타 DKC52-59 밀도 6수준의 관측 평균을 확보했다. KBS033 2014년 실측 개체밀도 연결은 0개다. KBS033의 DSSAT 재현·정량 등록을 보류했다. FACETS 옥수수 수확 360개를 연결했다. Access 시장수량 180건을 검산하고 FDACS 시비 23행과 CERES 보정 처리를 확인했다. SWAT 옥수수 관리 입력 1,138행을 확인했다. FDACS 보고서의 공통 관수 9일과 보충 시비 단위를 대조했다. FDACS 180개 수량에서 본문 평균 23개를 재현했다. FDACS 분할구 수량 대비 72개를 계산했다. FACETS/FDACS 7개 밭–시즌의 현장 재현·독립 검증 자격을 대조했다. Ransom 49개 지점–연도에 건조 수량 3,095개와 관수 70건을 연결했다. Ransom 관수 8개 지점–연도에서 Becker 2016을 입력 명세 우선 후보로 선별했다. Becker 2016 입력 명세와 AP005 표층 배치 경로를 확인했다. 네이티브 AP005 질소 27.66 kg N/ha 입력이 26.00 kg N/ha로 전달됨을 확인했다. 격리 DSSAT 진단 빌드에서 관수 245.11 mm와 질소 27.66 kg N/ha의 정밀도 보존을 확인했다. Becker 4블록의 층별 수분·무기질소를 대조했다. 채취일과 수리값이 미확정이다. Becker 시험구 64개를 SSURGO D62A에 연결하고 대표 토양층 20개의 수리값 후보를 정리했다. Hubbard·Mosford 기술 시나리오 4개의 DSSAT 초기 수분·무기질소 재고를 확인했다. 4월 21–26일 수분 경로를 코어와 비교하고 무기질소 장부 잔차를 확인했다. 10개 기술 조건의 순무기화 민감도를 대조하고 토양 가스 재고와 배출을 포함한 무기질소 장부를 검산했다. NOAA와 SSURGO의 대리 근거를 정리하고 Becker 4블록×2 대표층 후보를 구성했다. 4블록의 고정 16조건에서 DSSAT 초기 재고와 4월 26일 코어를 대조했다. Becker의 P0157AMX 두 계수와 관리 입력 전달을 네이티브 4조건에서 확인했다. 수량을 가린 64시험구 256조건이 기술 재현을 통과했다. Becker 수량 관측 64개와 모의 256개를 대조했다. Becker 생육 중 토양 질산태 N과 식물 N을 대조해 추비 전부터 표층 질산 과대를 확인했다. Becker 조기 질소 공급의 8개 기술 조건을 대조했다. 코어 총질소 환산과 전층 기본값 대체를 확인했고, 층별 유기질소를 고정해 풀 배분을 비교했다. 4블록의 코어 입력 24개에서 전층 기본값 대체를 확인했다. 호환 층 24개를 층별 초기화로 보존했다. Becker를 기술 재현 근거로 분류하고 후속 세 지점을 선별했다. Waseca 2016 무관수 입력 명세를 작성했다. 채취일 강수와 포화수분 범위를 대조하고 공통 관측 초기화 자격을 보류했다. 파종 전 수분·무기질소 기술 조건 32개를 고정했다. 격리 DSSAT 32조건의 초기 재고와 장부를 검산했고 4월 26일 수분 과소를 확인했다. Waseca를 파종 전 기술 진단으로 보존하고 후속 두 시험을 확인했다. Plano·Lorenzo 입력 명세를 작성했고 PPNT와 첫 시비의 동일 일자를 확인했다. Plano의 날짜별 수분·질소 근거와 수리층 차이를 정리했다. Plano 무시비 기술 조건 16개를 고정했다. Plano 격리 DSSAT 16조건을 실행했고 6월 무시비 질소 과소를 확인했다. Plano 질소 장부를 분해하고 6월 과소가 모든 기술 조건에 남음을 확인했다. 현장 흐름별 계측 공백으로 정량 등록은 보류했다. [질소 경로와 활용 판정](RANSOM_WISCONSIN_PLANO_2016_DATED_N_RESPONSE_DISPOSITION.md) [Plano 네이티브 대조](RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_NATIVE_TECHNICAL_PROBE.md) [기술 설계](RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_TECHNICAL_PROBE_DESIGN.md) [초기화 자격](RANSOM_WISCONSIN_PLANO_2016_INITIALIZATION_TIMING_AND_SOIL_HYDRAULICS.md) [위스콘신 입력 명세](RANSOM_WISCONSIN_PLANO_LORENZO_2016_RAINFED_INPUT_DOSSIER.md) [Waseca 활용 판정](RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_DISPOSITION.md) [네이티브 기술 대조](RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_TECHNICAL_PROBE.md) [기술 대조 설계](RANSOM_WASECA_2016_PREPLANT_WATER_N_TECHNICAL_PROBE_DESIGN.md) [날짜별 초기화 판정](RANSOM_WASECA_2016_DATED_WATER_N_INITIALIZATION_QUALIFICATION.md) [Waseca 입력 명세](RANSOM_WASECA_2016_RAINFED_INPUT_DOSSIER.md) [후속 후보 선별](RANSOM_BECKER_REPLAY_DISPOSITION_AND_FOLLOWUP_SITE_SCREEN.md) [층별 초기화](RANSOM_BECKER_2016_LAYERWISE_CN_INITIALIZATION_PROBE.md) [4블록 C:N 대조](RANSOM_BECKER_2016_FOUR_BLOCK_JOINT_CN_SUPPORT.md) [총질소·풀 검증](RANSOM_BECKER_2016_TOTAL_N_POOL_INITIALIZATION_QUALIFICATION.md) [조기 질소 경로](RANSOM_BECKER_2016_EARLY_N_SUPPLY_MECHANISM_PROBE.md) [생육 중 대조](RANSOM_BECKER_2016_INSEASON_N_RESPONSE_DIAGNOSIS.md) [수량·질소 대비](RANSOM_BECKER_2016_FROZEN_YIELD_N_CONTRAST_AUDIT.md) [64시험구 재현](RANSOM_BECKER_2016_YIELD_MASKED_TECHNICAL_REPLAY.md) [품종·관리 전달](RANSOM_BECKER_2016_CULTIVAR_MANAGEMENT_REPLAY_GATE.md) [4블록 네이티브 비교](RANSOM_BECKER_2016_FOUR_BLOCK_NATIVE_INITIALIZATION_MATRIX.md) [4블록 초기화 후보](RANSOM_BECKER_2016_FOUR_BLOCK_INITIALIZATION_EVIDENCE.md) [순무기화 검사](RANSOM_BECKER_2016_PREPLANT_MINERALIZATION_PROBE.md) [파종 전 수분·무기질소 추적](RANSOM_BECKER_2016_PREPLANT_WATER_N_BRIDGE.md) [초기 재고 검사](RANSOM_BECKER_2016_NATIVE_INITIAL_STOCK_PROBE.md) [SSURGO 수리값 대조](RANSOM_BECKER_2016_SSURGO_HYDRAULIC_CROSSWALK.md) [초기 토양 감사](RANSOM_BECKER_2016_INITIAL_SOIL_PROFILE.md) [정밀도 검사](RANSOM_BECKER_NATIVE_SERIALIZATION_PRECISION.md) [네이티브 대조](RANSOM_BECKER_IRRIGATION_N_NATIVE_MASS_PROBE.md) [Becker 입력 명세](RANSOM_BECKER_2016_DSSAT_INPUT_DOSSIER.md) [관수 후보 판정](RANSOM_IRRIGATED_SITE_REPLAY_SHORTLIST.md) [Ransom 입력 검사](RANSOM_CORN_N_2014_2016_INPUT_SCREEN.md) [범위 판정](FACETS_FDACS_REPLAY_READINESS_DISPOSITION.md) [분할구 대비](FDACS_21894_SPLIT_PLOT_YIELD_CONTRASTS.md) [수량 재구성](FDACS_21894_GRAIN_YIELD_RECONSTRUCTION.md) [보고서 대조](FDACS_21894_MEASURED_OPERATIONS_CROSSWALK.md) [일별 관리 입력 감사](FACETS_LIVE_OAK_DAILY_OPERATIONS_SOURCE_AUDIT.md) [관리·보정 계보](FACETS_LIVE_OAK_OPERATIONS_AND_CALIBRATION_LINEAGE.md) [옥수수 원자료 점검](FACETS_LIVE_OAK_CORN_INPUT_AUDIT.md) [재현 범위 판정](KBS033_REPLAY_READINESS_DISPOSITION.md) [개체밀도 출처](KBS033_2014_FINAL_STAND_LINEAGE.md) [밀도·수량 구성 감사](DKC52_59_MINNESOTA_DENSITY_COMPONENT_AUDIT.md) [독립 생육 관측 선별](DKC52_59_INDEPENDENT_PHENOLOGY_SCREEN.md) [2014년 입력 점검](KBS033_2014_REPLAY_INPUT_SCREEN.md) [시비 이력 감사](KBS033_F1_F2_NITROGEN_HISTORY_AUDIT.md) [시즌별 대비](KBS033_WATER_NITROGEN_DESCRIPTIVE_CONTRASTS.md) [2023년 입력 감사](KBS033_2023_WEATHER_SOIL_LINEAGE.md) [KBS033 원자료 감사](KBS033_FIELD_DATA_AUDIT.md) [공동 처리 설계 선별](FIELD_WATER_NITROGEN_DAMAGE_JOINT_DESIGN_SCREEN.md) [LIRF 활용 범위와 진입 조건](LIRF_2012_2013_EVIDENCE_QUALIFICATION.md)

Lorenzo의 수분 초기화와 6월 무시비 관측을 검토했다. 같은 기상 아래 관측 비교로 보존한다. 코어 수분의 측정 기반, 현장 수리값 및 하부 경계, 4월 13일 질소 재고의 근거가 있어야 재현용 입력을 확정할 수 있다. [Lorenzo 초기화 자격](RANSOM_WISCONSIN_LORENZO_2016_INITIALIZATION_QUALIFICATION.md)

Ransom에서 Lewis 2015와 Shumway 2016을 독립 기본 생육·수량 검증 후보로 좁혔다. 별도 품종 계수와 토양 초기화 자격을 확보한 뒤 정량 등록을 판정한다. [독립 현장 후보 선별](RANSOM_INDEPENDENT_BASELINE_SCREEN.md)

Lewis 지도 수리값의 정적 자격을 검토했다. 외부 Shelby P1498AM 원자료는 곡실 수량과 기상을 확보했지만 초기 토양·관수·생육 자료 공백으로 보정 자격을 보류했다. Lewis 수량값을 보정에 쓰지 않은 상태로 유지한다. [Lewis 수리값과 보정 자료](RANSOM_LEWIS_2015_HYDRAULICS_AND_CULTIVAR.md)

Novelty P1498AM 자료는 동일 시험의 두 보고서를 연결했다. 공개 기상은 후보로 보존했고 품종과 침수의 공동 수량, 초기 수분·무기질소, 계수 및 생태형이 남아 정량 보정을 보류했다. [Novelty 보정 자료 감사](P1498AM_NOVELTY_CALIBRATION_EVIDENCE.md)

Ohio의 동일 품종 출아 관측과 Western 기상을 대조했다. 포장별 출아·센서 원자료와 정확한 CERES 계수는 미확보다. Shumway를 독립 검증 후보로 유지한다. [Ohio 출아 관측 감사](P1197AM_OHIO_EMERGENCE_EVIDENCE.md)
Adnan 2019년 질소 관측은 외부 반응 비교로 보존한다. Figshare 원본 입력과 2020년 보정·평가 시험구 연결이 미확보라 네이티브 재현 및 정량 등록은 보류했다. [Adnan 자료 감사](ADNAN_CERES_CALIBRATION_EVALUATION_AUDIT.md)
PREPCLIM 모의 입력은 기술 후보로 보존한다. 한 연도·시나리오의 날짜·시비량·기상 파일과 배치를 확정하고 동일 실행기로 확인해야 한다. 독립 현장 평가에는 시험구 관측 계보가 필요하다. [PREPCLIM 감사](PREPCLIM_NATIVE_INPUT_AND_EVALUATION_AUDIT.md)
출아 후 저온·수분 스트레스 실패와 보상 η·GAE의 기술 비교는 검증했다. 브라질 2002년 8처리 재실행은 별도 연도에서 보정된 외부 기본 생육 후보로 보존한다. 시험구 불확실성, 전체 원소C, 물·질소 조건별 독립 잎 피해·회복 평가, 기준 정책 선택이 남았다. [환경 검증](ENVIRONMENT_VALIDATION_SWEEP.md)
BRPI0202 관수량·기비·일사 입력 차이를 확인했다. 배포 기상과 6월 일사 교체 결과를 함께 보존하며, 현장 재현 등록은 관수 일정과 일사 원본 계보를 확보할 때까지 보류한다. [BRPI0202 입력 검증](BRPI2002_MANAGEMENT_AND_WEATHER_QUALIFICATION.md)
SIAZ의 별도 보정 연도와 평가 입력을 확보하고 실제 DSSAT에서 재실행했다. 1995년의 정량 등록에는 기상·토양의 현장 연결, 반복 관측 불확실성 및 사전 허용범위가 남았다. [SIAZ 검증](SIAZ1995_1996_FROZEN_CULTIVAR_REPLAY.md)

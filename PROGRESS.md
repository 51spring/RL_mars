# 구현 진행상황

기준 제안서: `docs/proposal_revised.pdf` (2026-11-05 개정)
작업 폴더: `C:/Users/WD/Desktop/강화학습_MARS`
마지막 갱신: 2026-11-10 (한국 시간, 새 WGEN PPO 재학습 및 실패일 N 차감)

이 파일을 작업 시작·검증 완료·중단 시 갱신합니다. 완료 판정은 검증 근거와 함께 남깁니다.
소프트웨어 검사와 실제 DSSAT 및 농학 검증을 구분합니다.

| 단계 | 상태 | 산출물 / 완료 조건 |
|---|---|---|
| 1. 환경 설정 | 완료 | 전용 venv, CPU/CUDA PPO 검사, Docker DSSAT 163단계 실행 |
| 2. 자원·감축·마스크 | 완료 | `resources.py`, 17개 검사 통과; 실제 백엔드 연결은 5단계 |
| 3. 실제 백엔드 계약 확인 | 일부 완료 | 종료·HWAH·깊은 파종/수분 부족 발아 실패·실제 기상 달력/행동일 대조 통과; 메타데이터20쌍 회귀·기본 보정 프로필 통과; 출아 후 저온·수분 스트레스 실패의 기술 검증 통과 |
| 4. 관측·난수·보상 | 일부 완료 | 45×7 관측·raw 수익·독립 외생 흐름·실험용 온라인 조사 연결 통과; 잠재함수·실제 수확/실패/시간제한 망원합 검증 통과; 고정행동 η·공통 GAE 민감도 통과; 최종 계수 선택 남음 |
| 5. Gymnasium 환경 연결 | 일부 완료 | 무해충 회귀 및 실험용 해충/조사 실제 환경 2시즌 통과; 실제 CPU PPO 4환경·두 모드 연결 통과; 본 학습 남음 |
| 6. 실제 잎 피해 쓰기 | 일부 완료 | v2 기존64조건 및 범용 토양8쌍/실제22회 확장 통과; 부산물 N 배분/초기화 경고·정밀도 제한 유지, 기본 승격·전체 C·농학 미완료 |
| 7. 농학 검증 | 물 반응 독립 연도 통과/피해·회복 대기 | SIAZ 1995 8처리 nRMSE 19.97%로 단 A 통과(사후 판정). 피해·회복 상대 수량비(단 B) 대기. 공동 처리·조사 오차는 한계 항목 |
| 8. 예비 학습·기준선 | 일부 완료 | 동일 이미지 CPU·CUDA 각 102,400단계 2회 통과. 무해충 규칙/무투입 공통 4쌍 기술 검사 통과. 기준선 튜닝 대기 |
| 9. 본 실험·통계 | 대기 | 공동/관수 정책, 공통 시즌, 교차 부트스트랩·Holm·민감도 |


## 새 WGEN 배정에서 공동 PPO 재학습 (2026-11-10)

두 시비 제한 방식 각 3시드, 총 98,304단계 학습과 새 16개 시즌 DSSAT 256회 검증을 완료했다. 학습부터 제한한 확률 실행은 실행 때만 제한한 경우 대비 평균 −3.37, 하위 10% +3.45 USD/ha였다. 고정 관리를 비교 기준으로 유지했다. [비교 및 검산](docs/PEST_PPO_WGEN_RETRAIN.md)


## 실패일 질소 흡수 차감의 Q/F 격리 후보 검증 (2026-11-10)

Q와 F에서 사질토 저온 실패일 질산태 질소 0.214787 kg N/ha를 휴경 초기화 시 한 번만 차감했다. 두 후보의 질소 원장 2,936행이 일치했고, 토양 C 8,760일 및 수확 잔사 C 전달 24건을 검산했다. 전체 원소 C는 미검증이다. [격리 후보](docs/TERMINAL_N_DEBIT_CANDIDATE.md)


## 피해·회복 상대 수량비 기준 동결 (2026-11-10)

단 B의 기준 자료를 Purdue 2024–2025년 적엽 9처리로 정하고 단계·제거율 대응, 16시즌 160회 모의 조건, 합격 기준(9칸 수량비 RMSE 0.10 이하, 99% 적엽의 V8 > V13 > R1 순서)을 비교 전에 동결했다. 비교 실행은 0회다. 기준 파일 해시를 고정했고 소프트웨어 검사 216개가 통과했다. [동결 기준](docs/FIELD_VALIDATION_TIERS.md)

## 현장 검증 3단 증거 기준과 SIAZ 1995 물 반응 판정 (2026-11-10)

책임자 승인으로 현장 검증을 물 반응·피해 회복·검증 불가 항목의 3단으로 나눴다. 1996년 PEST 계수와 현장 줄 간격 75 cm로 고정한 SIAZ 1995 8처리는 nRMSE 19.97%, 편향 −1,000.3 kg/ha로 통과했다. 수량을 이미 본 뒤의 문헌 관례 판정이며 모의 수량 범위는 관측의 75.6%다. 미충족 진입 조건은 7개, 소프트웨어 검사 213개 통과. 본학습은 보류다. [3단 기준과 판정](docs/FIELD_VALIDATION_TIERS.md)

## 학습·검증·시험 WGEN 시드 분리 (2026-11-10)

학습 10001–99998, 검증 1–4999, 시험 5000–9999로 중복 없이 배정하고 PDI에 직접 전달했다. 기존 검증 334개·시험 348개의 학습 시드 충돌을 재현했으며 새 예정 시즌 39,594개의 충돌은 0건이었다. 이전 체크포인트의 새 배정 재개를 차단했다. [원인 및 검증](docs/WGEN_SPLIT_SEED_FIX.md)


## 실패일 질소 흡수 배열 초기화 위치 확인 (2026-11-10)

출력 계측 전용 빌드로 Q 4회를 재실행했고 기존 상태와 C/N 출력이 일치했다. 사질토 저온군의 첫 휴경 `RUNINIT`에서 `PLANT` 호출 직전 남아 있던 질산태 흡수 0.214787 kg N/ha가 호출 직후 0이 됐다. 초기화의 층별 토양 무기질소 재고는 그대로였다. [휴경 초기화 계측](docs/TERMINAL_N_UPTAKE_RESET.md)

## Q 출아 후 첫해 실패와 둘째 해 수확 검증 (2026-11-10)

첫해만 저온을 적용한 두 토양의 Q 처리와 대조 4회를 완료했다. 두 처리 모두 첫해 출아 후 실패했고 둘째 해에 수확했다. 미사질 양토와 대조 2개의 통합 N은 통과했다. 사질토 저온군에서 실패일 흡수 0.214787 kg N/ha가 휴경 초기 재고 차감에 반영되지 않은 경계를 확인했다. [출아 후 실패 검증](docs/MULTIYEAR_POST_EMERGENCE_COLD_Q.md)

## 첫해 출아 실패 뒤 둘째 작물 질소 검증 (2026-11-10)

두 토양에서 F 첫해만 실패하고 둘째 해에 수확했다. Q에서는 깊은 파종 실패가 두 해에 반복됐다. 네이티브 4회에서 질소 재고 2,936개와 전환 경계 12개를 검산했고, 첫날 적용한 관수 5 mm·질소 10 kg N/ha를 확인했다. 소프트웨어 204개 통과. [실패 뒤 질소 전달](docs/MULTIYEAR_FIRST_CROP_FAILURE.md)

## 남은 작업 정리 (2026-11-10)

최근 무관수·무시비 2년 Q/F 검증을 반영했다. 작물 실패 뒤 다년 질소 전달, 전체 원소 C와 N 배분, 독립 현장 자료, 최종 설정 및 본학습을 구분했다. [남은 작업](docs/REMAINING_WORK.md)

## 범용 토양 2종의 2년 무관수·무시비 Q/F 검증 (2026-11-10)

곡실 50%·부산물 0%에서 Q/F 4회를 실행했다. 관수·시비 0을 네이티브 이벤트와 대조했고, 모형 N 재고 2,936개 및 초기화 경계 12개를 검산했다. 기존 관리 원장 8개를 정확히 재현했고 소프트웨어 204개가 통과했다. [무관수·무시비 검증](docs/MULTIYEAR_ZERO_INPUT_QF.md)

## 범용 토양 2종의 2년 F 모드 질소 검증 (2026-11-10)

두 토양과 수확률 100%/0%·50%/50%에서 F 모드 1년 대조 4회 및 2년 실행 4회를 완료했다. 모형 N 재고 2,936개와 초기화 경계 12개를 검산했다. 동일 Q 조건의 기록 상태와 질소 원장이 정확히 일치했고, 변형 입력 8개를 거부했다. [2년 F 모드 검증](docs/MULTIYEAR_GENERIC_F.md)

## 범용 토양 Q/F 부분 수확 검증 (2026-11-10)

곡실 50%에 부산물 0%·50%를 교차해 DSSAT 32회를 실행했다. 후보 16개가 수확·휴경 및 모형 N 검사를 통과했다. 무투입 대조 4개는 50%/0%에서 잔사 N 부족을 재현했고, 50%/50%에서는 두 항의 차이가 상쇄됐다. [부분 수확 검증](docs/QF_PARTIAL_HARVEST_N.md)

## Q/F 무투입 대조 질소 차이 원인 확인 (2026-11-10)

기존·무버퍼 출력의 Q/F 8쌍에서 작물 원장이 정확히 일치했다. 무투입 대조 실패는 첫 휴경 행에서 시작됐으며, 재식 밀도와 이삭 밀도 기준의 곡실 N 차이로 표면 잔사 부족 0.878549·0.508111 kg N/ha를 재구성했다. 후보 8개는 기존 검사를 통과했다. [원인 감사](docs/QF_CONTROL_N_BOUNDARY.md)

## Q/F 휴경 종료일 수지와 SIAZ 관수 대조 (2026-11-10)

후보 이미지 DSSAT 22회를 무버퍼 출력으로 재실행했다. Q/F 수지 16개에서 마지막 144일을 확보해 토양 C 출력 5,840일을 검산했다. 통합 모형 N은 후보 8개 통과와 무투입 대조 4개 실패가 재현됐다. SIAZ 17처리 관수 94건의 날짜와 양이 논문·입력·네이티브 출력에서 일치했다. 전체 원소 C, 현장 기상 계보와 반복구 수량은 미확정이다. [검증 보고서](docs/QF_TERMINAL_AND_SIAZ_CALENDAR.md)

## 공동 PPO의 동일 질소량 조기 시비 지연 (2026-11-09)

검증 16시즌·3시드·2행동 난수로 DSSAT 192회를 실행했다. 회차별 질소량·횟수는 그대로 두고 45일 전 시비만 옮겼다. 평균 순수익 +142.07 USD/ha, 건조 곡실 +948.52 kg/ha였다. 대조군 96회와 일정 불변 22회는 저장 기록과 정확히 일치했다. [조기 시비 지연 보고서](docs/PPO_EQUAL_N_DELAY.md)


## 질소량을 맞춘 조기 시비 비교 (2026-11-09)

동일 16시즌에서 질소량·시비 횟수·관수·살포를 맞춰 DSSAT 48회를 완료했다. 첫 시비만 45일에서 2일로 옮기자 평균 건조 곡실 −374.63 kg/ha, 평균 순수익 −59.19 USD/ha였다. 전체 시비 일정을 43일 앞당긴 보조 대비는 순수익 −72.02 USD/ha였다. 결정일 6,411개를 검산했다. [시비 시점 비교](docs/NITROGEN_TIMING_MATCHED_DOSE.md)


## 공동 PPO 시비 채널 분리 진단 (2026-11-09)

같은 검증 16시즌·3시드·2행동 난수로 DSSAT 192회를 완료했다. 대조군 96회는 저장 기록과 정확히 일치했다. 시비를 고정하자 평균 순수익은 702.58에서 828.03 USD/ha, 하위 10% 평균은 281.90에서 474.44 USD/ha로 높아졌다. 45일 전 질소는 평균 78.46에서 0 kg N/ha로 줄었다. 결정일 25,644개 검산을 통과했다. [시비 채널 분리 보고서](docs/PEST_PPO_FIXED_N_ABLATION.md)


## 남은 작업 정리 (2026-11-09)

최신 PPO 비교를 반영해 질소 채널 분리 진단과 본학습 선행 조건을 구분했다. 저장된 근거를 정리했으며 신규 실행은 없다. [남은 작업](docs/REMAINING_WORK.md)


## 45일차 전 시비를 학습 단계부터 제한한 공동 PPO (2026-11-10)

공동 PPO 3시드 49,152단계를 재학습하고 새 16개 시즌에서 DSSAT 256회를 검증했다. 실행 때만 제한한 모델 대비 재학습의 확률 실행은 평균 −19.06 USD/ha, 하위 10% +22.26 USD/ha였다. 최대확률 실행 48회는 고정 관리와 일치했다. 결정일 34,112개를 검산했다. [비교 보고서](docs/PEST_PPO_NITROGEN_GATE_TRAINING.md)


## 45일차 이후 시비 간격과 회당 투입량 비교 (2026-11-10)

DSSAT 288회를 추가했다. 45일 제한만 적용한 경우 대비 7일 최소 간격 −3.77, 회당 상한 54 kg N/ha −2.17, 두 제한 −4.45 USD/ha였다. 결정일 37,890개를 검산했다. [비교 보고서](docs/PEST_PPO_NITROGEN_SPACING_DOSE.md)


## 공동 PPO의 45일차 이전 시비 제한 (2026-11-10)

새 16시즌에서 DSSAT 304회를 실행했다. 45일차 전 시비 제한은 기존 공동 PPO 대비 +89.24 USD/ha였고, 고정 관리 대비 평균 +2.65 USD/ha 및 하위 10% −6.55 USD/ha였다. 결정일 39,995개를 검산했다. [비교 보고서](docs/PEST_PPO_ONLINE_NITROGEN_GATE.md)


## 공동 관리 PPO의 시비 시점과 투입량 분리 비교 (2026-11-10)

같은 시즌·행동 난수에서 시비 시점과 총량을 교차해 DSSAT 288회를 추가했다. 원래 공동 PPO 대비 날짜만 늦추면 +142.48 USD/ha, 총량만 제한하면 −26.22 USD/ha, 둘을 적용하면 +122.83 USD/ha였다. 결정일 38,466개를 검산했다. [비교 보고서](docs/PEST_PPO_NITROGEN_TIMING_AMOUNT.md)


## 공동 관리 PPO의 질소 결정 고정 비교 (2026-11-10)

동일 시즌·행동 난수에서 공동 PPO의 질소만 고정해 DSSAT 96회를 비교했다. 평균 순수익은 +125.45 USD/ha 회복했고 고정 규칙과의 차이는 −4.97 USD/ha였다. 결정일 12,822개 검산을 통과했다. [비교 보고서](docs/PEST_PPO_NITROGEN_LOCK.md)


## 실험용 해충 환경의 PPO 확률적 실행 비교 (2026-11-09)

새 검증 시즌 16개에서 저장 PPO 각 2개 행동 난수와 고정·예산 연동 규칙을 DSSAT 224회로 비교했다. 고정 대비 평균 순수익은 관수 전용 −4.57, 공동 관리 −130.43 USD/ha였다. 손실이 큰 공동 관리 시드 42·43은 첫 시비 결정일이 평균 2.03·1.09일이었다. 결정일 29,918개 검산을 통과했다. [비교 보고서](docs/PEST_PPO_SAMPLED_VALIDATION.md)


## 실험용 해충 환경의 관수 전용·공동 관리 PPO 예비 비교 (2026-11-09)

관수 전용과 공동 PPO를 각 3시드·16,384단계 학습해 검증 128회를 완료했다. PPO의 결정적 실행 96회는 고정 0.30과 일별 행동이 같았다. 고정/PPO의 평균은 808.11 USD/ha, 예산 연동은 820.22 USD/ha였다. 결정일 16,984개 검산을 통과했다. [비교 보고서](docs/EXPERIMENTAL_PEST_PPO_PILOT.md)


## 방제 규칙의 조사 잡음과 약효 민감도 (2026-11-09)

기존 시즌 12개에 조사 잡음과 약효를 교차해 DSSAT 432회를 추가 실행하고 기준 144회를 재사용했다. 50 USD/ha에서 조사 잡음이 커지면 예산 연동의 평균 차이는 +16.77 USD/ha, 하위 10% 차이는 −7.30 USD/ha였다. 결정일 58,212개 검산을 통과했다. 다음 PPO 예비 비교에서 고정 0.30을 기준으로 유지한다. [민감도 보고서](docs/PEST_SURVEY_EFFICACY_SENSITIVITY.md)


## 고가 살포 조건의 방제 규칙 검증과 남은 일정 (2026-11-09)

새 검증 시즌 12개에서 DSSAT 324회를 완료했다. 회당 100 USD/ha의 수정 규칙은 기존 예산 연동보다 +4.62 USD/ha였고 고정 0.30과 36개 조합에서 정확히 일치했다. 전체 평균 고정 대비 +8.05 USD/ha의 시즌 단위 구간은 0을 포함했다. 결정일 43,659개 검산을 통과했다. [비교 보고서와 남은 일정](docs/PEST_PRICE_GATE_VALIDATION.md)


## 예산 연동 방제의 두 동작 분리 비교 (2026-11-09)

Docker 엔진 복구 후 완료분 144회를 이어받고 나머지 144회를 실행해 12시즌 비교를 완료했다. 고정 0.30 대비 살포 여유 시 임계값 인하 +6.59 USD/ha, 마지막 1회 임계값 인상 +4.00 USD/ha였다. 결정일 38,472개 검산을 통과했다. [비교 보고서](docs/PEST_CAPACITY_RULE_ABLATION.md)


## 남은 살포 예산을 반영한 방제 규칙 비교 (2026-11-09)

새 검증 시즌 12개에서 예산 연동 규칙과 고정 0.30을 DSSAT 288회로 비교했다. 예산 연동 규칙은 평균 +10.58 USD/ha, 시즌 기준 10승 2패였다. 살포비 100 USD/ha에서는 −2.35 USD/ha였다. 결정일 38,472개 검산을 통과했다. [비교 보고서](docs/PEST_BUDGET_ADAPTIVE_RULE.md)


## 살포비를 예산에 반영한 해충 방제 재실행 (2026-11-09)

같은 검증 시즌 12개를 살포비 25·75·100 USD/ha에서 실제 DSSAT 324회로 재실행했다. 100 USD/ha에서 사후 정산의 평균 1위 0.45가 예산 반영 후 0.30으로 바뀌었다. 가격별 살포 일정 변화는 108개 조합 중 10·3·42개였다. 결정일 43,146개 검산을 통과했다. [재실행 보고서](docs/PEST_SPRAY_BUDGET_PRICE_REPLAY.md)


## 새 시즌에서 방제 임계값 재검증과 살포비 민감도 (2026-11-09)

새 검증 시즌 12개에서 DSSAT 144회를 완료했다. 0.30은 무방제 대비 평균 +179.00 USD/ha, 0.15 대비 −1.62 USD/ha였다. 회당 살포비 25·50·75·100 USD/ha 사후 정산에서 0.30은 각 비용의 최고 평균과 5.10 USD/ha 이내였다. 결정일 19,176개 검산을 통과했으며 작물 실패와 제약 위반은 0건이었다. [비교 보고서](docs/PEST_SPRAY_THRESHOLD_CONFIRMATION.md)


## 해충 유입 확률에 따른 방제 임계값 비교 (2026-11-09)

선택 시비에서 새 검증 시즌 8개에 유입 확률 1.5·3·6%와 네 방제 규칙을 교차해 DSSAT 96회를 완료했다. 임계값 0.30은 유입 조건별 최고 평균 순수익과 3.20 USD/ha 이내였고 세 조건을 같은 가중치로 평균했을 때 737.14 USD/ha로 가장 높았다. 결정일 12,660개를 검산했으며 생육 실패와 제약 위반은 0건이었다. [비교 보고서](docs/PEST_SPRAY_THRESHOLD_SENSITIVITY.md)


## 실험용 해충의 시비·방제 비교 (2026-11-09)

공통 해충 시즌 8개에서 두 시비 일정과 무방제·고정 방제를 교차해 32회 실행했다. 선택 시비와 고정 방제의 평균 순수익은 781.82 USD/ha였다. 선택 시비에서 고정 방제를 추가한 순수익 차이는 +190.27 USD/ha이며 6승 1무 1패였다. [비교 보고서](docs/PEST_SPRAY_NITROGEN_COMPARISON.md)

## 시비 일정의 물 예산·가격 민감도 (2026-11-09)

새 무해충 검증 시즌 8개에서 두 시비 일정을 물 예산 세 수준으로 48회 실행했다. 선택 일정의 순수익 차이는 물 예산 100·75·50%에서 +58.59·+57.30·+52.13 USD/ha였다. 가격 사후 재계산에서도 세 예산에서 평균 순위가 유지됐다. [비교 보고서](docs/NITROGEN_WATER_BUDGET_SENSITIVITY.md)

## 시비 일정 후보 비교 (2026-11-09)

관수 규칙을 고정하고 시비 12조합을 학습 시즌 8개에서 비교했다. 선택한 45·65·85일 54·35·27 kg N/ha 일정은 새 검증 시즌 16개에서 기존 대비 평균 순수익 +27.84 USD/ha, 12승 4패였다. [비교 보고서](docs/NITROGEN_RULE_GRID_PILOT.md)

## 관수 규칙 후보 비교 (2026-11-09)

시비를 고정한 관수 임계값·요청량 12조합을 학습 시즌 8개에서 비교했다. 기존 0.30·10 mm가 평균 순수익 1위였으며, 새 검증 시즌 16개에서 두 동일 규칙의 결과가 일치했다. 검사 204개 통과. [비교 보고서](docs/IRRIGATION_RULE_GRID_PILOT.md)

## 기존 규칙 변경 PPO 예비 비교 (2026-11-09)

관수 변경과 관수·시비 변경 PPO를 각각 16,384단계 학습했다. 검증 시즌 32–47에서 두 정책은 모두 고정 규칙과 동일한 행동을 선택했고 평균 순수익은 825.00 USD/ha로 같았다. 48개 결과와 체크포인트 해시를 검산했다. [예비 비교](docs/RULE_OVERRIDE_PPO_PILOT.md)

## 관수 및 관수·시비 PPO 예비 비교 (2026-11-09)

무해충 DSSAT에서 두 PPO 정책을 각각 16,384단계 학습했다. 새 검증 시즌 16개에서 평균 순수익은 기존 규칙 838.18, 관수 PPO 511.13, 공동 PPO 185.16 USD/ha였다. 평가 48회의 기록을 체크포인트 재실행으로 일치 확인했다. [예비 비교](docs/WATER_NITROGEN_PPO_PILOT.md)

## 관수·시비 단독과 병행 비교 (2026-11-09)

같은 무해충 DSSAT 16시즌에서 관수만·시비만 32회를 추가했다. 평균 순수익은 병행 741.40, 시비만 493.13, 무투입 177.71, 관수만 117.86 USD/ha였다. 병행은 13시즌, 시비만은 3시즌에서 순수익 1위였다. [비교 보고서](docs/BASELINE_WATER_NITROGEN_16_SEASON_COMPARISON.md)

## 무투입과 고정 규칙 공통 16시즌 비교 (2026-11-09)

무해충 DSSAT에서 두 정책을 16쌍·32회 실행했다. 고정 규칙의 평균 순수익이 563.69 USD/ha 높았고 16시즌 모두에서 순수익과 수량이 증가했다. 두 정책의 생육 실패와 제약 위반은 0건이었다. 시뮬레이션 내 비교로 기록했다. [비교 보고서](docs/BASELINE_16_SEASON_COMPARISON.md)

## SIAZ 보정 계수와 독립 연도 재실행 (2026-11-09)

1996년 보정·1995년 평가를 분리하고 계수 4세트로 총 68회 재실행했다. 원 현장 관수 총량 17개와 실행을 연결했다. 1995년 PEST의 건조 곡실 RMSE는 배포 줄 간격 1 cm에서 1,164.8 kg/ha, 현장 75 cm 대조에서 1,511.6 kg/ha였다. 기상 좌표·토양 깊이·시험구 오차 계보를 확인할 때까지 정량 등록은 보류한다. 검사 204개 통과. [SIAZ 검증](docs/SIAZ1995_1996_FROZEN_CULTIVAR_REPLAY.md)

## BRPI0202 관리·기상 입력 검증 (2026-11-09)

관수 누계 304 대 261 mm 및 관수구 기비 N 4.4 kg/ha 차이를 확인했다. USP 자동관측 자료로 6월 일사량 26일만 바꾼 8처리의 RMSE는 854.5 kg/ha로 배포 기상의 399.0보다 컸다. 원본·민감도 결과를 분리해 보존하고 정량 등록을 보류했다. 검사 204개 통과. [입력 검증](docs/BRPI2002_MANAGEMENT_AND_WEATHER_QUALIFICATION.md)

## 환경 검증과 외부 현장 재실행 (2026-11-09)

Docker에 다시 연결했다. 실제 DSSAT에서 동일한 파종 후 초기 궤적을 비교해 대조구 793 kg/ha 수확과 출아 후 저온 처리구 실패 0 kg/ha, 기존 지출 12.90 USD/ha 보존을 확인했다. 저온을 배제한 무강수 시험에서도 5·10 mm 관수 후 출아한 작물의 생육 실패와 비용 보존을 검증했다. 브라질 2001년 공개 보정 계수로 2002년 평가 8처리를 재실행해 건조 곡실 수량 RMSE 399.0 kg/ha를 얻었다. 공식 연구 등록과 본 학습은 대기 상태다. 소프트웨어 검사 204개 통과. [검증 기록](docs/ENVIRONMENT_VALIDATION_SWEEP.md)

## PREPCLIM DSSAT 입력 및 독립 평가 자격 감사 (2026-11-09)

공개 예제 v1·v2와 모델링 배포본 체크섬을 확인했다. v2에서 기후모델 WTH 678개와 모의 출력 270개를 확인했다. 실험·품종·생태형·토양은 연결되며 한 시나리오 재실행에는 배치와 날짜·시비량 치환이 필요하다. 독립 현장 관측 계보는 미확인이다. 검사 204개가 통과했다. [감사 보고서](docs/PREPCLIM_NATIVE_INPUT_AND_EVALUATION_AUDIT.md)

## Adnan CERES-Maize 보정·평가 자료 감사 (2026-11-09)

2019년 품종 10개·두 경로의 계수와 SAMMAZ 32의 4년×3시비 수준 지상부 질소를 검산했다. 2020년 공개 통합문서의 보정 256행과 평가 64행 중 9행이 품종·관측·모의 수량에서 일치한다. 시험구 키와 네이티브 입력이 미확보라 재실행·독립 평가 등록을 보류했다. 검사 204개가 통과했다. [감사 보고서](docs/ADNAN_CERES_CALIBRATION_EVALUATION_AUDIT.md)

## P1197AM Ohio 출아 관측과 Shumway 활용 자격 (2026-11-09)

- 동일 P1197AM 학위논문과 학술지의 출아 자료를 대조했다. 부록 12개 패널에서 2019년 본문 파종일과 달력 축 기준의 차이를 확인했다.
- Western 관측소 기상 636일을 검산하고 미보고 6일을 보존했다. 학위논문 월별 평균기온 최대 차이 0.058 °C, 강수 최대 차이 0.984 mm다.
- Ohio는 출아 비교 근거로 분류했다. CERES 계수·생태형 미확보로 Shumway 정량 재현은 보류했다. 검사 204개 통과. [감사 보고서](docs/P1197AM_OHIO_EMERGENCE_EVIDENCE.md) · [검산 결과](outputs/runs/20261108T155545Z_p1197am_ohio_emergence_evidence_97206da7/verification.json)

## Novelty P1498AM 외부 보정 자료 감사 (2026-11-09)

- Novelty 2013–2015 수량·질소 원문 두 편의 관리 날짜 15개와 0–30 cm 토양화학 9행을 연결했다. 공개 Greenley 기상의 파종~침수 강수는 세 해 모두 논문 반올림 범위에 들어왔다.
- P1498AM 수량 주변평균 8개를 복원했다. 두 표를 결합해도 침수×품종별 공동 평균을 식별하지 못했다. 구제 질소 83/84 kg N/ha 기록 차이는 유지했다.
- 시험구 원자료와 CERES 계수·생태형 미확보로 Novelty 보정과 Lewis 정량 재현을 보류했다. 소프트웨어 검사 204개 통과. [감사 보고서](docs/P1498AM_NOVELTY_CALIBRATION_EVIDENCE.md) · [검산 결과](outputs/runs/20261108T154227Z_p1498am_kaur_calibration_evidence_0a81dbe4/verification.json)

## Lewis 2015 수리값과 P1498AM 외부 보정 자료 (2026-11-09)

- 코어 4곳과 관리 좌표를 USDA Marshall 9B에 연결했다. 29개 비교 구간의 수분은 모두 지도 대표 33 kPa 수분보다 높고 포화 추정 범위의 낮은 값 이내였다.
- Shelby 2015 P1498AM 공개 CSV 13개와 옥수수 시험구 24개를 대조했다. 초기 토양·일별 관수 공백과 CSV·논문의 시비 질소 4.28 kg N/ha 차이를 보존했다.
- 품종계수와 생태형이 미확정이어서 Lewis 재현·정량 등록을 보류했다. 소프트웨어 검사 204개 통과. [수리값과 보정 자료](docs/RANSOM_LEWIS_2015_HYDRAULICS_AND_CULTIVAR.md) · [Lewis 검산](outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/lewis_verification.json) · [Shelby 검산](outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/shelby_verification.json)

## Ransom 독립 현장 후보 선별 (2026-11-09)

- 49개 시험 중 Zhen 논문의 보정·평가·추가 시험 8개를 분리했다. 나머지 41개에서 네 블록의 파종 전 질소·동일일 수분 자료가 91.44 cm 깊이 기준을 충족한 곳은 Lewis 2015와 Shumway 2016이다.
- Lewis는 120 cm 수분 관측 4블록과 건조 수량 기록 64개를 확인했다. 두 후보의 정확한 CERES 계수는 미확보이며 수량값은 선별에 사용하지 않았다.
- Lewis를 후속 입력 검토 우선 후보로 두고 두 후보의 정량 등록을 보류했다. 검사 204개 통과. [후보 선별](docs/RANSOM_INDEPENDENT_BASELINE_SCREEN.md) · [검산 결과](outputs/runs/20261108T152911Z_ransom_independent_baseline_screen_4f1dc844/verification.json)

## Lorenzo 2016 초기화 자격과 Plano 비교 범위 (2026-11-09)

- 지도 포화값을 적용하면 Lorenzo의 측정 지원 구간에서 블록별 7.69–17.30 mm를 잃는다. 한 블록은 수분과 실측 밀도가 함께 있는 층이 없고, 지도 포화 상한도 결측이다.
- 공통 기상 195일을 재확인했다. 예정 무시비 6월 표층 질산은 Lorenzo 6월 10일 15.88, Plano 6월 13일 22.88 mg N/kg이었다. Lorenzo 두 번째 깊이는 1개 결측이다.
- 관측 비교로 보존하고 현장 재현용 입력 생성과 정량 등록을 보류했다. 검사 204개 통과. [초기화 자격](docs/RANSOM_WISCONSIN_LORENZO_2016_INITIALIZATION_QUALIFICATION.md) · [검산 결과](outputs/runs/20261108T152317Z_lorenzo_2016_initialization_qualification_dc86945c/verification.json)

## Plano 2016 질소수지 분해와 활용 판정 (2026-11-09)

- 저장 출력 16조건·992개 조건–일을 재검산했다. 6월 13일까지 전층 순무기화 평균 21.48, 작물 흡수 13.24, 하단 용탈 2.68 kg N/ha였다. 독립 누적 잔차는 최대 0.0027 kg N/ha였다.
- 높은 초기 질소 가정에서 관측 성분·깊이의 모의 재고가 평균 26.78 kg N/ha 늘었지만, 6월 과소가 16조건에 남았다. 현장 흡수 대조 자료는 7월과 9월 시료로 한정된다.
- Plano를 기술 진단으로 보존하고 정량 현장 재현 등록을 보류했다. 소프트웨어 검사 204개 통과. [활용 판정](docs/RANSOM_WISCONSIN_PLANO_2016_DATED_N_RESPONSE_DISPOSITION.md) · [검산 결과](outputs/runs/20261108T151633Z_plano_dated_n_response_disposition_8ce9ff3f/verification.json)

## Plano 2016 무시비 네이티브 기술 대조 (2026-11-09)

- 격리 DSSAT 16조건, 992개 조건–일을 검산했다. 독립 누적 잔차는 최대 물 0.09 mm, 무기질소 0.0027 kg N/ha였다. 수분·무기질소 일별 출력은 200 cm까지 확인했다.
- 4월 29일 암모늄과 6월 13일 무시비 질소 관측에 전 조건 과소가 나타났다. 6월 표층 질산 평균 과소는 14.96 mg N/kg이다. 소프트웨어 검사 204개 통과.
- 다음은 초기 질소·순무기화·작물 흡수·용탈 분리 및 현장 재현 활용 판정이다. [실행 문서](docs/RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_NATIVE_TECHNICAL_PROBE.md) [검증 결과](outputs/runs/20261108T150946Z_plano_native_technical_probe_1c983a42/verification.json)

## Plano 2016 무시비 기술 대조 설계 (2026-11-09)

- 4블록 × 심층 수분 2수준 × 초기 무기질소 2수준의 16조건을 고정했다. 초기 질소는 별도 2014–2015년 무관수 시험 16곳으로 범위를 정했다.
- 4월 13일 코어 수분을 보존하고 2Bt2 포화 상한 0.40을 네 블록에 공통 적용했다. 4월 29일과 6월 13일 질소는 사후 대조용이다. 검사 204개 통과.
- 다음은 격리 DSSAT 실행과 두 날짜의 깊이별 상태·물질수지 대조다. [설계 문서](docs/RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_TECHNICAL_PROBE_DESIGN.md) [검증 결과](outputs/runs/20261108T150448Z_ransom_wisconsin_plano_2016_dated_initialization_technical_probe_design_2bb18f17/verification.json)

## Plano 2016 초기화 시점과 수리값 (2026-11-09)

- 4월 29일 채취·첫 시비의 당일 순서는 미확정이다. PPNT를 초기값으로 소급하지 않고 6월 13일 무시비 시험구 4개의 질소 관측을 별도 대조용으로 연결했다.
- 코어 수분 재고를 4블록에서 보존했다. 블록 3의 117–120 cm 수분이 대표 포화 근사값보다 높고 지도 상한 안에 있다. 검사 204개 통과.
- 다음은 4월 13일 수분 초기화와 명시적 질소 가정을 분리한 무시비 기술 대조 설계다. [판정 문서](docs/RANSOM_WISCONSIN_PLANO_2016_INITIALIZATION_TIMING_AND_SOIL_HYDRAULICS.md) [검증 결과](outputs/runs/20261108T145938Z_ransom_wisconsin_plano_2016_initialization_timing_and_soil_hydraulics_ee1391b4/verification.json)

## Plano·Lorenzo 2016 입력 명세 (2026-11-08)

- 각각 64시험구와 공통 195일 기상을 원자료에서 대조했다. PPNT는 파종 6일 뒤이자 첫 시비일이며 코어 수분과 16일 차이다. 당일 순서와 공통 초기 상태는 미확정이다.
- USDA 지도에 8개 코어 좌표를 연결했다. Plano는 체적수분 계산이 가능한 20개 층 모두 대표 포화 근사값 이내였다. Lorenzo는 체적수분 계산 가능 4개 층과 심층 질산 1블록이다.
- 다음은 Plano 초기화 날짜와 수리값 검토다. 검사 204개 통과. [명세 문서](docs/RANSOM_WISCONSIN_PLANO_LORENZO_2016_RAINFED_INPUT_DOSSIER.md) [검증 결과](outputs/runs/20261108T145424Z_ransom_wisconsin_plano_lorenzo_2016_rainfed_input_dossier_af20d8f7/verification.json)

## Waseca 2016 재현 활용 판정 (2026-11-08)

- 32조건 모두 60 cm 아래 모의 수분이 관측보다 적었다. USDA 월별 습윤층과 지역 수분 차트를 확인했고, 시험구 수위·배수 시계열은 미확보다. 기술 진단으로 보존했다.
- Plano·Lorenzo를 Dryad 시험 49·48에 연결했다. 366일 기상값이 일치하고 Plano의 토양 관측이 더 완전하다. 다음은 두 지점의 무관수 입력 명세다. 검사 204개 통과. [판정 문서](docs/RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_DISPOSITION.md) [검증 결과](outputs/runs/20261108T144954Z_ransom_waseca_2016_preplant_water_n_native_disposition_3a3bac89/verification.json)

## Waseca 2016 파종 전 네이티브 기술 대조 (2026-11-08)

- 격리 DSSAT 32조건 모두 완료했다. 수분·무기질소 초기 재고 및 200 cm 일별 수분 출력을 대조했다. FileX→내부 입력의 최대 질소 차이는 0.040725 kg N/ha였다.
- 출력에서 독립 재계산한 최대 누적 잔차는 물 0.02 mm, 무기질소 0.0017 kg N/ha였다. 26일 기상 처리 후 전 조건이 관측보다 44.13–155.59 mm 건조했다. 검사 204개 통과.
- 다음은 지하수위·배수와 코어 근거를 대조해 Waseca 현장 재현 활용 범위를 판정하는 작업이다. [실행 문서](docs/RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_TECHNICAL_PROBE.md) [검증 결과](outputs/runs/20261108T144145Z_ransom_waseca_2016_preplant_water_n_native_technical_probe_a3cf17b2/verification.json)

## Waseca 2016 파종 전 기술 대조 설계 (2026-11-08)

- 4블록 × 초기 수분 2수준 × 심층 무기질소 2수준 × 배수율 2수준의 32조건을 고정했다. 관측 구간 질소량은 반올림 전 모두 보존했고, 입력 정밀도에 따른 최대 차이는 0.004505 kg N/ha였다.
- 초기 재고 환산에서 4월 26일 용적밀도를 대리값으로 사용했다. 다음은 입력 파일 생성, 격리 DSSAT 초기 재고·수분·장부 대조다. 검사 204개 통과. [설계 문서](docs/RANSOM_WASECA_2016_PREPLANT_WATER_N_TECHNICAL_PROBE_DESIGN.md) [검증 결과](outputs/runs/20261108T143652Z_ransom_waseca_2016_preplant_water_n_technical_probe_design_95336c1e/verification.json)

## Waseca 2016 날짜별 초기화 자격 (2026-11-08)

- 4월 22–26일 보고일 합계는 Ransom 보간 16.5 mm, 약 10 km 떨어진 NOAA 관측소 13.2 mm였다. NOAA 08:00 경계의 4일 합계는 11.7 mm였다.
- 20층 중 9층이 SSURGO 포화 대표값, 5층이 상한을 초과했다. 두 채취일을 하나의 관측 초기 상태로 합치지 않았다. 소프트웨어 검사 204개를 통과했다.
- 다음은 무기질소의 깊이별 질량 대응과 심층 결측·배수 조건을 고정하고 날짜별 DSSAT 기술 대조를 준비하는 작업이다. [판정 문서](docs/RANSOM_WASECA_2016_DATED_WATER_N_INITIALIZATION_QUALIFICATION.md) [검증 결과](outputs/runs/20261108T143216Z_ransom_waseca_2016_dated_water_n_initialization_qualification_136fe29b/verification.json)

## Waseca 2016 무관수 입력 명세 (2026-11-08)

- 원본 7개를 대조해 64시험구 시비 일정, 186일 기상 출처, 4블록의 초기 무기질소와 코어 수분을 묶었다. USDA 지도에서 1번 코어는 Le Sueur, 2–4번은 Cordova였다.
- 코어 수분이 대표층 포화 근사값보다 큰 층 9개와 채취일 4일 차이를 확인했다. 소프트웨어 검사 204개를 통과했다. 다음은 날짜별 수분·질소 초기화 자격 대조다. [입력 명세 문서](docs/RANSOM_WASECA_2016_RAINFED_INPUT_DOSSIER.md) [검증 결과](outputs/runs/20261108T142505Z_ransom_waseca_2016_rainfed_input_dossier_68cc84d2/verification.json)

## Becker 재현 판정과 후속 지점 선별 (2026-11-08)

- Becker의 256개 실행은 기술 검증으로 분류했다. 평균 수량 과대 2.72–3.74 t/ha와 분시 반응 불일치로 정량 등록을 보류했다.
- Dryad 원본 6개의 SHA-256을 대조하고 Brandes, Waseca, Troth를 선별했다. 무관수 Waseca 2016을 질소 전이 입력 명세 우선 후보로 정했다. 원 연구 평가 지점이라는 자료 역할을 기록했다.
- 다음 작업은 Waseca 초기 수분·무기질소 채취일과 Cordova 수리값, 기상 출처 및 처리표 대조다. [판정 문서](docs/RANSOM_BECKER_REPLAY_DISPOSITION_AND_FOLLOWUP_SITE_SCREEN.md) [실행 근거](outputs/runs/20261108T141444Z_ransom_becker_replay_disposition_and_followup_site_screen_aee915f8/verification.json)

## Becker 층별 유기질소 초기화 (2026-11-08)

- 전층 대체와 층별 초기화 16조건을 대조했다. 허용 층 24개의 요청량을 확인했고, 나머지 60개 층은 기본 풀 값을 유지했다.
- Hubbard의 질산·식물 N 과대가 줄었지만 관측과 차이가 남았다. 소프트웨어 검사 204개 통과.
- 다음은 Becker 현장 재현 자격 종합 판정과 독립 자료 후보 확인이다. [층별 초기화](docs/RANSOM_BECKER_2016_LAYERWISE_CN_INITIALIZATION_PROBE.md) · [검산](outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/verification.json)

## Becker 4블록 탄소·질소 관측 범위 (2026-11-08)

- 기준 8개와 코어 총질소 입력 24개를 실행했다. 코어가 완전히 덮는 68개 모형층 중 24개가 C:N 허용 범위였다. 입력 24개 모두에서 전층 기본값 대체를 확인했다.
- 다음은 호환 층을 보존하고 결측·비호환 층에 기본값을 적용하는 층별 초기화의 기술 대조다. 소프트웨어 검사 204개 통과. [4블록 대조](docs/RANSOM_BECKER_2016_FOUR_BLOCK_JOINT_CN_SUPPORT.md) · [검산](outputs/runs/20261108T140239Z_ransom_becker_2016_four_block_joint_cn_support_5d774a3d/verification.json)

## Becker 코어 총질소와 초기 풀 배분 검증 (2026-11-08)

- 4블록 18개 층의 총질소 단위와 DSSAT 유기질소 환산을 확인했다. 결측 또는 C:N 범위 이탈로 코어 입력 6조건 모두 초기 유기질소를 전층 기본값으로 대체했다.
- 초기 총 유기질소를 층별로 고정해도 안정 풀 배분에 따른 순무기화 감소가 남았다. 네이티브 14조건 및 소프트웨어 검사 204개 통과.
- 다음은 4블록의 측정 C:N 호환 범위와 심층 결측·기본값 대체 처리 검토다. [총질소·풀 검증](docs/RANSOM_BECKER_2016_TOTAL_N_POOL_INITIALIZATION_QUALIFICATION.md) · [검산](outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/verification.json)

## Becker 조기 질소 공급 경로 진단 (2026-11-08)

- 처리 비료 0의 두 기준과 초기 풀·분해·이동 변경 6개를 격리 실행했다. 분해 감속은 표층 질산과 식물 N 과대를 줄였다. 이동 지연은 표층 질산을 높였다.
- 초기 풀 배분 변경에서 총 유기탄소는 같았지만 모델 초기 유기질소도 달라졌다. 소프트웨어 검사 204개 통과.
- 다음은 코어 총질소의 입력 자격과 풀 배분·초기 N 재고의 분리다. [조기 질소 경로](docs/RANSOM_BECKER_2016_EARLY_N_SUPPLY_MECHANISM_PROBE.md) · [검산](outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/verification.json)

## Becker 생육 중 질소·수분 경로 대조 (2026-11-08)

- 256개 모의에서 토양 질산태 N 544쌍과 식물체 N 512쌍을 채취일·깊이·시험구 기준으로 대조했다. 소프트웨어 검사 204개 통과.
- 추비 전에 처리 비료 0의 표층 질산태 N이 관측보다 높았고, 315 단회와 45+270 분시의 모의 식물 N 흡수는 7월 19일에 같았다.
- 다음은 초기 유기물 풀·무기화와 깊이별 질산 이동의 조기 질소 공급 민감도 검사다. [생육 중 대조](docs/RANSOM_BECKER_2016_INSEASON_N_RESPONSE_DIAGNOSIS.md) · [검산](outputs/runs/20261108T095818Z_ransom_becker_2016_inseason_n_response_diagnosis_abad1243/verification.json)

## Becker 수량과 질소 처리 대비 (2026-11-08)

- 관측 수량을 열기 전에 건조수량 연결 키와 17개 질소 처리 대비를 고정했다. 관측 64개와 모의 256개를 연결했고 소프트웨어 검사 204개가 통과했다.
- 네 조합의 모의 평균 편향은 +2.72~+3.74 t/ha였다. 같은 총량의 분시 효과는 관측 +2.48 t/ha, 모의 −0.002~+0.021 t/ha였다. 농학 정량 등록은 0건이다.
- 다음은 저질소·단회·분시의 생육 중 질소·물 경로를 현장 관측과 맞춰 차이가 커지는 시점을 확인하는 작업이다. [수량·대비 보고서](docs/RANSOM_BECKER_2016_FROZEN_YIELD_N_CONTRAST_AUDIT.md) · [검산](outputs/runs/20261108T094828Z_ransom_becker_2016_frozen_yield_and_nitrogen_contrast_audit_fc7c0854/verification.json)

## Becker 64시험구 기술 재현 (2026-11-08)

- 시험구 64개에 토양 2종·품종 계수 2세트를 교차한 256조건을 고정했다. 첫 실행은 기상 파일 탐색 오류로 종료돼 각 실행 폴더에 동일한 기상 파일을 배치하고 재실행했다.
- 재실행 256개가 모두 통과했다. 관리·기상 45,312일과 출아·출사·성숙·수확 및 일별 생육 출력을 대조했다. 소프트웨어 검사 204개 통과.
- 다음은 관측 수량과의 비교에 앞서 건조수량 단위와 블록 내 처리 대비를 고정하는 작업이다. [기술 재현](docs/RANSOM_BECKER_2016_YIELD_MASKED_TECHNICAL_REPLAY.md) · [검산](outputs/runs/20261108T093833Z_ransom_becker_2016_yield_masked_technical_replay_6b1e22de/verification.json)

## Becker P0157AMX와 관리 입력 전달 검사 (2026-11-08)

- P0157AMX 수동·자동 계수 두 세트를 격리 DSSAT의 INP에서 원문과 대조했다. 원 연구 생태형은 미확정이며 공통 기술 생태형 IB0001로 실행했다.
- 64시험구의 질소 일정을 정리했다. 무시비·고질소 분시 두 포장과 두 계수 세트의 4조건에서 708일의 물·질소 투입을 검증했다. 소프트웨어 검사 204개 통과.
- 다음은 수량을 가린 64시험구 기술 재현 조건과 평가 항목의 사전 고정이다. [품종·관리 전달](docs/RANSOM_BECKER_2016_CULTIVAR_MANAGEMENT_REPLAY_GATE.md) · [검산](outputs/runs/20261108T093207Z_ransom_becker_2016_cultivar_and_management_replay_gate_cbd8adb3/verification.json)

## Becker 4블록 DSSAT 초기화 비교 (2026-11-08)

- 4블록·2대표층·2초기 수분의 16조건을 고정해 실행했다. 168개 세분층과 초기 재고를 대조했다. FileX→INP 질소 반올림에 따른 최대 재고 차이는 0.00456 kg N/ha였다.
- 4월 26일 기상 적용 전후의 코어 수분 오차를 별도로 보관했다. 소프트웨어 검사 204개 통과.
- 다음은 P0157AMX 생태형·품종 파일 연결과 수량을 가린 관리 입력 검토다. [4블록 비교](docs/RANSOM_BECKER_2016_FOUR_BLOCK_NATIVE_INITIALIZATION_MATRIX.md) · [검산](outputs/runs/20261108T092659Z_ransom_becker_2016_four_block_native_initialization_matrix_dc08e77e/verification.json)

## Becker 4블록 초기화 후보 (2026-11-08)

- St. Cloud 기온 평년값으로 TAV 6.1°C·AMP 16.25°C 후보를 산출했다. Sandstone 2016 층별 토양온도는 지역 비교 자료로 별도 보존했다.
- 잔사 피복 환산과 심층 유기탄소의 SSURGO 대리값을 정리하고, 4블록×2개 대표층 후보를 구성했다. 소프트웨어 검사 204개 통과.
- 다음은 고정한 비교 조건의 네이티브 초기 재고와 4월 26일 코어 대조다. [공개 근거와 후보](docs/RANSOM_BECKER_2016_FOUR_BLOCK_INITIALIZATION_EVIDENCE.md) · [검산](outputs/runs/20261108T092154Z_ransom_becker_2016_four_block_initialization_evidence_5331edc3/verification.json)

## Becker 파종 전 순무기화·질소 장부 검증 (2026-11-08)

- 전작 콩과 잔사 피복률 25%를 확인했다. Hubbard·Mosford 각 5조건에서 코어 유기탄소·콩 잔사·토양온도 가정의 순무기화 민감도를 대조했다. 소프트웨어 검사 204개 통과.
- 상세 장부에서 토양 내 가스 재고와 배출을 확인했다. 10개 조건의 6일 네이티브 무기질소 수지 잔차는 0.0001 kg N/ha 이내였다.
- 다음은 토양온도·잔사량·하부 유기탄소의 공개 근거와 4블록 초기화 후보 구성이다. [순무기화 검사](docs/RANSOM_BECKER_2016_PREPLANT_MINERALIZATION_PROBE.md) · [검산](outputs/runs/20261108T091554Z_ransom_becker_2016_preplant_mineralization_provenance_probe_8204151d/verification.json)

## Becker 파종 전 물·무기질소 추적 (2026-11-08)

- 4월 21일 시작 조건 두 개에서 26일까지 네이티브 기상과 재고를 대조했다. 강수 합계 39.2 mm가 원자료와 일치했다. 26일 기상 처리 전후를 1블록 수분 코어와 각각 비교했다.
- 일별 수분 장부 잔차는 최대 0.48 mm였다. 26일 무기질소 장부 잔차 −0.18 및 −0.20 kg N/ha는 출력 반올림 범위를 넘었다. 소프트웨어 검사 204개 통과.
- 다음은 코어 유기탄소·잔사·토양온도 가정의 순무기화 민감도와 무기질소 잔차 원인 확인이다. [파종 전 추적](docs/RANSOM_BECKER_2016_PREPLANT_WATER_N_BRIDGE.md) · [검산](outputs/runs/20261108T091207Z_ransom_becker_2016_preplant_water_n_bridge_af3417f2/verification.json)

## Becker DSSAT 초기 재고 검사 (2026-11-08)

- Becker 1블록의 4월 21일·26일 초기화 가정을 Hubbard·Mosford에 적용했다. 격리 DSSAT 4회가 완료됐고, 두 내부 입력 파일과 초기 수분·무기질소 재고가 출력 정밀도 내에서 일치했다. 소프트웨어 검사 204개 통과.
- 4월 26일 조건의 질소는 4월 21일 채취값을 그대로 적용한 가정이다. 깊은 층 질소와 초기 수분 공백을 별도 기록했다.
- 다음은 4월 21일에서 26일까지 이어지는 모의의 물·무기질소 경로와 4월 26일 코어 수분 대조다. [초기 재고 검사](docs/RANSOM_BECKER_2016_NATIVE_INITIAL_STOCK_PROBE.md) · [검산](outputs/runs/20261108T090642Z_ransom_becker_2016_native_initial_stock_probe_f8652ad8/verification.json)

## Becker SSURGO 수리값 대조 (2026-11-08)

- 시험구 64개와 관리표 좌표가 모두 SSURGO D62A에 포함됐다. 5개 구성 토양의 20개 층에서 수분·전도도 후보값을 환산했다. 소프트웨어 검사 204개 통과.
- Hubbard는 토성, Mosford는 용적밀도가 코어에 더 가까웠다. 블록별 구성 토양은 미확정으로 유지했다.
- 다음은 두 후보의 초기 수분과 무기질소 결측 조건을 명시하고 DSSAT 초기 재고를 기술 대조하는 작업이다. [수리값 대조](docs/RANSOM_BECKER_2016_SSURGO_HYDRAULIC_CROSSWALK.md) · [검산](outputs/runs/20261108T090216Z_ransom_becker_2016_ssurgo_hydraulic_crosswalk_134964f6/verification.json)

## Becker 초기 토양 프로필 검증 (2026-11-08)

- 4블록 18개 층의 수분과 무기질소를 깊이별로 매핑했다. 실측 용적밀도 결측 8개 층은 별도 Saxton 민감도 조건에서만 채웠다. 소프트웨어 검사 204개 통과.
- 수분과 질소 채취일은 5일 차이고 그 사이 기상표 강수 합계는 39.2 mm다. 단일 초기일과 수리값 4종이 미확정이어서 현장 실행을 보류했다.
- 다음은 Becker 포장 위치와 SSURGO 구성 토양·층별 수리값 대조다. [토양 프로필 감사](docs/RANSOM_BECKER_2016_INITIAL_SOIL_PROFILE.md) · [검산](outputs/runs/20261108T085740Z_ransom_becker_2016_initial_soil_profile_qualification_91959907/verification.json)

## Becker DSSAT 내부 투입량 소수점 보존 (2026-11-08)

- 격리 빌드의 INP·INH 작성 형식을 보정하고 관수 245.11 mm와 AP005 질소 27.66 kg N/ha가 소수점까지 보존되는지 확인했다.
- 두 비교 조건과 높은 투입량 회귀 조건을 실행했다. 총 888일의 모델 내부 누적·일별 값 및 수송 전 표층 질산태 투입이 허용오차 내에서 일치했다. 소프트웨어 검사 204개 통과.
- 다음은 Becker 초기 토양 프로필의 수리 특성·용적밀도·층별 수분과 무기질소 매핑 검토다. [정밀도 검사](docs/RANSOM_BECKER_NATIVE_SERIALIZATION_PRECISION.md) · [검산](outputs/runs/20261108T085006Z_ransom_becker_native_serialization_precision_0eaf15b3/verification.json)

## Becker 관수수 질소 네이티브 투입량 대조 (2026-11-08)

- Docker 임시 통신 폴더를 백업하고 Linux 엔진을 복구했다. 같은 기술 입력으로 관수만 적용한 조건과 AP005 조건을 네이티브 DSSAT에서 실행했다.
- 두 조건의 관수 출력은 같았다. AP005 질소는 원본 27.66 kg N/ha에서 내부 파일 및 누적 투입 26.00 kg N/ha로 바뀌었다. 소프트웨어 검사 204개 통과.
- 다음은 격리 진단 빌드에서 두 내부 작성 경로의 소수점 정밀도 보존과 일별 투입량 검증이다. [네이티브 대조](docs/RANSOM_BECKER_IRRIGATION_N_NATIVE_MASS_PROBE.md) · [검산](outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/verification.json)

## Becker 2016 DSSAT 입력 명세 및 관수수 질소 (2026-11-08)

- Becker 기상 177일, 관수 20건, 포장 시비 64개, 블록별 토양, P0157AMX 계수 두 세트를 입력 명세로 묶었다.
- 소스에서 관수 수심과 별도 AP005 표층 질산태 N 경로를 확인했다. 내부 포맷을 모사하면 관수수 N은 27.66에서 26.00 kg N/ha로 바뀐다. Docker Linux 엔진 미연결로 네이티브 투입량은 미확인이다.
- 다음은 AP005 관수수 N의 네이티브 질량·출력 정밀도 대조다. [명세](docs/RANSOM_BECKER_2016_DSSAT_INPUT_DOSSIER.md) · [검산](outputs/runs/20261108T051811Z_ransom_becker_2016_dssat_input_dossier_9eb3c36f/verification.json)

## Ransom 관수 8개 지점–연도 재현 후보 선별 (2026-11-08)

- 관수 8개 지점–연도의 포장 512개와 관수 70건을 대조했다. Becker 2016을 입력 명세 우선 후보, Brandes 2015와 Troth 2016을 조건부 후보로 기록했다.
- P0157AMX 수동·자동 보정 계수와 Becker의 평가 역할을 확인했다. Becker 초기 수분 코어 18개 층 중 8개는 실측 용적밀도가 없고, 관수수 질소 27.66 kg N/ha의 입력 경로 확인이 남았다.
- 다음은 Becker 2016 DSSAT 입력 명세다. [후보 판정](docs/RANSOM_IRRIGATED_SITE_REPLAY_SHORTLIST.md) · [판정 근거](outputs/runs/20261108T051025Z_ransom_irrigated_site_replay_shortlist_c04feffa/verification.json)

## Ransom 49개 지점–연도 질소 반응 입력 선별 (2026-11-08)

- Dryad 원본 16개를 체크섬과 대조했다. 49개 지점–연도에 건조 곡실 수량 3,095개, 필수 기상값 7,935 지점–일, 관수 8개 지점–연도·70건을 연결했다.
- 관수수 질소와 처리 비료량을 구분하고 이상 사건 및 시비 날짜 충돌을 기록했다. 토양 초기 조건·품종계수 근거가 부족해 정량 검증 등록은 0건이다.
- 다음은 관수 지점–연도 8개의 DSSAT 질소 반응 재현 후보 선별이다. [입력 검사](docs/RANSOM_CORN_N_2014_2016_INPUT_SCREEN.md) · [판정 근거](outputs/runs/20261108T045904Z_ransom_corn_n_2014_2016_input_screen_6a64338e/verification.json)

## FACETS·FDACS 재현 및 독립 검증 범위 판정 (2026-11-08)

- 7개 밭–시즌 중 6개에서 관측 수량 360개, 4개에서 처리별 SWAT 관리 입력 일부를 확보했다. 현장 DSSAT 재현과 독립 검증 자격은 각각 0개다.
- FDACS 2016년 북쪽은 남쪽 CERES 윤작 범위 밖 후보로 보류했다. FACETS 2020년 북쪽 60개는 수확 결측으로 유지했다.
- 다음은 Ransom 공개 자료 49개 지점–연도의 질소 반응 재현 입력 선별이다. [범위 판정](docs/FACETS_FDACS_REPLAY_READINESS_DISPOSITION.md) · [판정 근거](outputs/runs/20261108T045310Z_facets_fdacs_replay_readiness_disposition_d3bb5ecd/verification.json)

## FDACS 21894 분할구 수량 대비 (2026-11-08)

- 3시즌 각 4블록에서 관수·질소 대비 72개와 블록별 차이 288개를 계산했다. 관수는 주구, 질소는 세구 단위로 집계했다.
- 비관수−달력 관수는 블록–시즌 12개에서 모두 음수였다. 센서·달력 관수의 질소 대비 차이는 해마다 블록별 부호가 섞였다. 독립 검증 등록은 0건이다.
- 다음은 FACETS/FDACS의 시즌별 DSSAT 재현 및 독립 검증 가능 범위 판정이다. [대비 상세](docs/FDACS_21894_SPLIT_PLOT_YIELD_CONTRASTS.md) · [검산 결과](outputs/runs/20261108T044909Z_fdacs_21894_split_plot_yield_contrasts_916a4bb7/verification.json)

## FDACS 21894 옥수수 곡실 수량 재구성 (2026-11-08)

- FDACS 옥수수 180개를 명목 9.290304 m²와 수분 15.5%로 환산했다. 보고서 본문 평균 23개 모두 반올림 범위에서 일치했다.
- Figure 66의 2017년 관수 막대 높이는 2016년 패널과 동일하다. 2017년은 본문과 원자료로 대조하고 그림 판독값을 별도 보존했다. 정량 등록은 0건이다.
- 다음은 분할구 설계를 반영한 블록별 수량 대비다. [감사 문서](docs/FDACS_21894_GRAIN_YIELD_RECONSTRUCTION.md) · [검산 결과](outputs/runs/20261108T044436Z_fdacs_21894_grain_yield_reconstruction_d38ca783/verification.json)

## FDACS 21894 현장 관리 기록 대조 (2026-11-08)

- 공통 관수 9일이 SWAT 입력과 날짜가 일치하고, 깊이를 보고한 7일도 환산 후 일치했다. 반복구별 관수·시비 원장은 미확보다.
- 2016년 보충 질소 원 단위 30 lb N/ac를 확인했다. 약 33.63 kg N/ha로 SWAT 입력 및 학위논문 각주와 일치한다. 보고서·워크북과 SWAT의 파종·수확일 차이를 기록했다.
- 다음은 FDACS의 15.5% 수분·명목 수확 면적을 적용해 180개 탈곡 표본의 수량을 환산하고 처리 평균을 대조하는 작업이다. [감사 문서](docs/FDACS_21894_MEASURED_OPERATIONS_CROSSWALK.md) · [검산 결과](outputs/runs/20261108T043413Z_fdacs_21894_measured_operations_crosswalk_794d91b1/verification.json)

## FACETS Live Oak HydroShare 일별 관리 입력 감사 (2026-11-08)

- Rath 2015–2017과 Lee 2018 남쪽의 옥수수 관리 입력을 원본 체크섬과 대조하고 관수 867행·비료 271행을 추출했다.
- Rath 2016년에는 관수 합계가 논문과 다르고, 저·고 질소의 폴더 설명이 입력량과 반대다. 처리별 SWAT 입력과 실측 원장을 구분해 정량 등록은 0건이다.
- 다음은 FDACS 계약 21894 최종보고서와 부록에서 일별 적용량의 측정 및 반복구 키를 대조하는 작업이다. [감사 문서](docs/FACETS_LIVE_OAK_DAILY_OPERATIONS_SOURCE_AUDIT.md) · [검산 결과](outputs/runs/20261108T042622Z_facets_live_oak_daily_operations_source_audit_b0ccf1d7/verification.json)

## FACETS Live Oak 관측 수량·관리 작업·CERES 보정 계보 (2026-11-08)

- Access 원본의 2018년 120개와 2020년 남쪽 60개 시장수량을 재현했다. 원본 계수와 FDACS 15.5% 수분 기준을 분리했다.
- FDACS 시비표의 날짜·제형·처리별 투입량 23행과 표·각주 차이를 보존했다. 일별 실측 관수 원장은 미확보다. CERES 보정 처리와 품종 계수를 확인했고, 개별 관측의 보정·평가 분리는 미확정이다.
- 소프트웨어 검사 204개 통과. 정량 등록 0건. 다음은 HydroShare SWAT 관리 입력에서 실측 일별 적용량의 출처를 확인하는 작업이다. [감사 문서](docs/FACETS_LIVE_OAK_OPERATIONS_AND_CALIBRATION_LINEAGE.md) · [검산 결과](outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/verification.json)

## FACETS Live Oak 옥수수 원자료 점검 (2026-11-08)

- 옥수수 포장–시즌 420개에서 수확 360개를 일대일 연결했다. 2020년 북쪽 60개는 수확 키가 비어 있다. 7개 밭–시즌의 기상 필수 수치 결측은 0개다.
- 실제 관수·시비 이벤트 표는 통합 파일에서 미확보다. 다음은 일별 관리·수확 면적과 저자 DSSAT 보정 계보의 출처 대조다.
- 검사 204개 통과. 근거는 `docs/FACETS_LIVE_OAK_CORN_INPUT_AUDIT.md`와 `outputs/runs/20261108T040902Z_facets_live_oak_corn_input_audit_4cbeabab/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 재현 범위 판정과 FACETS 선별 (2026-11-08)

- KBS033 2014·2023년은 초기 토양과 독립 품종계수 등이 없어 DSSAT 재현을 보류했다. 7시즌 관측 수량 495개와 군 내 대비 126개는 기술적 근거로 보관한다.
- 다음 후보는 플로리다 Live Oak FACETS다. 공개 버전 1의 파일 목록과 관수×질소 분할구 설계를 확인했다. 다음은 옥수수 시즌·포장 키와 보정 계보 감사다.
- 검사 204개 통과. 근거는 `docs/KBS033_REPLAY_READINESS_DISPOSITION.md`와 `outputs/runs/20261108T040503Z_kbs033_replay_readiness_disposition_4d043d05/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 2014년 실측 개체밀도 출처 확인 (2026-11-08)

- KBS033 72포장의 실측 개체수 연결은 0개였다. 농작업 일지 21건과 MCSE 옥수수 개체수 120행을 대조했고 MCSE의 T1–T4 표본을 분리했다.
- 파종 첨부는 종자 라벨이며 발아율 95%를 현장 밀도로 사용하지 않았다. 다음은 KBS033 2014·2023년 DSSAT 재현 범위 종합 판정이다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_2014_FINAL_STAND_LINEAGE.md`와 `outputs/runs/20261108T035847Z_kbs033_2014_final_stand_lineage_ef40a642/verification.json`에 있다. 정량 승격 0건이다.

## 미네소타 DKC52-59 밀도·수량 구성 감사 (2026-11-08)

- 독립 6개 지점–연도에서 최종 밀도 6수준의 LAI·차단 PAR·수량·낟알 관측 평균을 회귀값과 분리했다. 포장별 원자료 0행이다.
- KBS033의 파종량을 미네소타 최종 개체밀도로 대입하지 않았다. 다음은 KBS033 2014년의 실측 개체밀도 출처 확인이다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/DKC52_59_MINNESOTA_DENSITY_COMPONENT_AUDIT.md`와 `outputs/runs/20261108T035003Z_dkc52_59_minnesota_density_component_audit_05eb3e37/verification.json`에 있다. 정량 승격 0건이다.

## DKC52-59 독립 생육 관측 선별 (2026-11-08)

- 캔자스주립대 2012년 Parsons의 DKC52-59 출사 소요일 71일을 확인했다. 출판사 보충 DOCX는 HTTP 403이었으며 독립 CERES 계수 확정은 0개다.
- 미네소타의 동일 품종 밀도·파종일 시험을 별도 후보로 확인했다. 다음은 공개 표의 반복 구조와 수량 구성 관측 감사다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/DKC52_59_INDEPENDENT_PHENOLOGY_SCREEN.md`와 `outputs/runs/20261108T033823Z_dkc52_59_independent_phenology_screen_1ae71d48/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 2014년 DSSAT 재현 입력 점검 (2026-11-08)

- 옥수수 수량·추비 72개 포장을 연결했다. 기상 171일의 필수 수치 결측은 0개였고 관수 일지 13회, 기록 깊이 243.84 mm를 확인했다.
- 관수군 파종량은 천수군보다 30% 많았다. 초기 토양과 DKC52-59 품종계수는 미확보이며, 다음은 독립 품종 생육 자료 선별이다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_2014_REPLAY_INPUT_SCREEN.md`와 `outputs/runs/20261108T033436Z_kbs033_2014_replay_input_screen_2ca09982/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 F1·F2 시비 이력 대조 (2026-11-08)

- 2023년 첨부 시비표를 확인했다. F1·F2 추비는 모두 0이며 파종 시 기비 계획은 0·30 lb N/ac다. 앞선 공통 기비 표기를 정정했다.
- 2014년은 F1 8포장 모두 기비 제외가 확인됐다. 2011년은 203/230 포장번호 불일치를 보류했다. 다음은 2014년 DSSAT 재현 입력 선별이다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_F1_F2_NITROGEN_HISTORY_AUDIT.md`와 `outputs/runs/20261107T164800Z_kbs033_f1_f2_nitrogen_history_audit_e20a7023/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 시즌별 질소–수량 대비 (2026-11-08)

- 현재 시험지 옥수수 7시즌과 유효 수량 495개에서 물 처리군별 블록 대비 126개와 군 간 기술 차이 63개를 계산했다. 2020년 질소량 공백은 시비 일지에서 72개 포장과 연결했다.
- 2020·2023년 F1과 F2는 추비가 모두 0이었고 F2−F1 수량차는 물 처리군별 1.04–1.71 t/ha였다. 다음은 F1·F2의 연도별 처리 이력과 시비표 대조다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_WATER_NITROGEN_DESCRIPTIVE_CONTRASTS.md`와 `outputs/runs/20261107T164451Z_kbs033_water_nitrogen_descriptive_contrasts_fa33df3f/verification.json`에 있다. 정량 승격 0건이다.

## KBS033 2023년 기온·토양·품종 감사 (2026-11-08)

- KBS 일별 표 3개에서 기온 결측일 28일을 보완할 극값은 0개였다. Gull Lake에서 최고·최저가 모두 있는 15일을 확인했지만 오후 4시 집계 차이로 원본에 병합하지 않았다.
- 2016년 표토 12포장을 연결했다. 2023년 파종 전 층별 수분·무기질소와 P0306Q 독립 품종계수는 미확보다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_2023_WEATHER_SOIL_LINEAGE.md`와 `outputs/runs/20261107T163916Z_kbs033_2023_weather_soil_lineage_57bfd7c6/verification.json`에 있다. 다음은 시즌별 물 처리군 내부의 질소 반응 대비다. 정량 승격 0건이다.

## KBS033 물×질소 포장 원자료 감사 (2026-11-08)

- 현재 시험지 7개 옥수수 시즌에서 504개 포장–시즌 키와 수량 관측 495개를 확인했다. 관수 보조표는 828개 키가 일치했지만 열을 대조한 뒤에도 수량 813개가 달라 통합표를 사용했다.
- 2023년 질소 처리 일지와 72포장을 연결했고 관수 기록 28회를 확인했다. 기온 결측과 파종 전 초기 토양·품종계수 공백이 남는다.
- 소프트웨어 검사 204개 통과. 근거는 `docs/KBS033_FIELD_DATA_AUDIT.md`와 `outputs/runs/20261107T163419Z_kbs033_field_data_audit_8a08a553/verification.json`에 있다. 다음은 2023년 기온·토양·품종 입력 계보 감사다. 정량 승격 0건이다.

## 물·질소·잎 피해 공동 처리 설계 선별 (2026-11-08)

- 공개 1차 자료 7개에서 적격 공동 포장 설계 0개를 확인했다. 가장 가까운 FAW 연구는 온실 복합비료와 실험실 유충 바이러스 접종을 사용했다.
- 세 요인 이진 대비에 필요한 8개 조합과 쌍별 자료만으로 생기는 결측 조합을 재현했다. 검사 204개가 통과했다. 근거는 `docs/FIELD_WATER_NITROGEN_DAMAGE_JOINT_DESIGN_SCREEN.md`와 `outputs/runs/20261107T162947Z_field_water_nitrogen_damage_joint_design_screen_13672d25/verification.json`에 있다.
- 다음은 KBS033 포장 원자료의 물×질소 처리, 반복구 배치, DSSAT 입력 감사다. 정량 검증·본 학습은 보류 중이다.

## 실제 FAW 잎 피해 면적과 독립 판독 자료 선별 (2026-11-08)

- Jerez 현장 1일·7시퀀스·302프레임의 공식 목록을 확인했다. USDA 9,120개 식물 키에서 유효 잎 등급 7,751개를 확인했다.
- USDA mm 측정은 이삭 피해 길이였다. 공개 열화상 자료는 피해 감지 범위이고 Abang CSV는 엠바고 표시였다. 7일 신규 손실과 독립 판독의 연결은 0쌍이다.
- 소프트웨어 검사 204개 통과 및 증거 해시 재현. `docs/FAW_PHYSICAL_LOSS_INDEPENDENT_RATING_SOURCE_SCREEN.md`와 `outputs/runs/20261107T162524Z_faw_physical_loss_independent_rating_source_screen_ac65dddb/verification.json`에 기록했다.
- 다음은 물×질소×실제 잎 피해의 공동 처리 자료 선별이다. 정량 검증과 본 학습은 보류 중이다.

## LeafScan 잎 손실률과 독립 판독 가능성 대조 (2026-11-08)

- LeafScan 면적 94쌍에서 손실률 94개를 재현했다. 원본 면적 단위는 미확인이다.
- 미디어 인덱스 1,750행에서 면적쌍 91개와 연결했고, 이 중 88개는 두 방식의 전후 원본 미디어가 인덱스에 있었다. 91개의 미디어 수치 라벨은 잎 단위 값과 일치했다. 독립 판독 확인 0쌍이다.
- 소프트웨어 검사 204개 통과, 증거 재생성 해시 일치. `docs/LEAFSCAN_LEAF_LOSS_MEASUREMENT_QUALIFICATION.md`와 `outputs/runs/20261107T162202Z_leafscan_leaf_loss_measurement_qualification_f7cf3dc3/verification.json`에 기록했다.
- 다음은 실제 FAW 피해의 물리 면적과 동일 시점 독립 판독을 연결하는 공개 자료 확인이다. 정량 검증과 본 학습은 보류 중이다.

## 독립 포장 적엽·회복 공개자료 선별 (2026-11-08)

- 독립 포장·잎 자료 5개를 선별했다. Padova 공식 보충자료는 원격 LAI 방법·지도이며 포장별 원자료는 미공개다. Miyazaki·Purdue·Thomason은 관측 범위를 구분했다.
- LeafScan 원본 메타데이터에서 6포장·18식물·150잎, 자연 피해 22잎의 수치 손실률 0개, 모의 피해 면적 수치쌍 94개를 확인했다. 실제 포장 손실량–회복 연결 0개다.
- 소프트웨어 검사 204개 통과, 증거 재생성 해시 일치. `docs/INDEPENDENT_FIELD_DEFOLIATION_RECOVERY_SOURCE_SCREEN.md`와 `outputs/runs/20261107T161709Z_independent_field_defoliation_recovery_source_screen_447bf04b/verification.json`에 기록했다.
- 다음은 LeafScan의 면적 단위·모의 손실률·독립 판독 가능성 대조다. 정량 검증과 본 학습은 보류 중이다.

## Battaglia 적엽 시행일과 회복 관측 연결 (2026-11-08)

- 2018년 논문 본문에서 R2 적엽일 2012-07-17 및 2013-07-23을 확인했다. Spindletop 기상으로 해당 구간의 293·249°C·일을 재현했다. 부록의 당일 단계는 처리군별 R2~R3였고 V7·V14 조사일은 시행일과 분리했다.
- 공개 조회 범위에서 포장·반복구의 실측 손실량과 피해 전후 녹색 LAI 또는 잎 건물중을 연결한 쌍은 0개다. 정량 검증과 본 학습은 보류 중이다.
- 소프트웨어 검사 204개 통과, 증거 재생성 해시 일치. `docs/BATTAGLIA_PLOT_DAMAGE_RECOVERY_LINKAGE.md`와 `outputs/runs/20261107T161257Z_battaglia_plot_damage_recovery_linkage_49d1e32a/verification.json`에 기록했다.
- 다음은 별도 포장 적엽 시험의 시행일·실제 피해량·회복 원자료 선별이다.

## LIRF 2012–2013 관측 활용 범위와 연구 진입 판정 (2026-11-08)

- 증거 9건에서 원본 워크북 해시, 포장 96개, 수량 결측 2개, 처리·연도 24개, 수량·물 노출 대비 28개를 교차 확인했다.
- SWD 감사의 동일 파일명 해시 키를 통합 기록에서 전체 경로로 구분했다. 격리 재실행은 기존 SWD 결과와 동일한 해시를 반환했다.
- 관측 활용 범위와 재현 입력의 완료 조건을 확정했다. 정량 준비 연구 0개, 활성 등록 승격 0건, 연구 및 본 학습은 보류다. 소프트웨어 검사 204개 통과.
- 상세는 `docs/LIRF_2012_2013_EVIDENCE_QUALIFICATION.md`와 `outputs/runs/20261107T115633Z_lirf_2012_2013_evidence_qualification_79134edd/verification.json`에 있다. 다음은 Battaglia의 피해 시행일·실제 손실량·포장별 회복 관측 연결이다.

## LIRF 2012–2013 생육일과 0–105 cm 토양수분 결핍 대조 (2026-11-07)

- 처리별 생육 기록을 공통 달력에 연결했다. 2012년 인접 단계 역행 13건과 2013년 R6 단독 기록 없는 6개 처리를 보존했다.
- SWD 관측 기반 값 909개를 층별 수분에서 재현했다. 최대 차이 0.475 mm. 같은 날 예측 RMSE는 2012년 8.87 mm, 2013년 14.00 mm였다.
- 2013년 9월 10–15일 강수는 워크북 47 mm, GLY04 45.98 mm, 논문 75 mm다. 강수 기간에 SWD 관측 행은 없었다.
- 소프트웨어 검사 204개 통과, 증거 해시 재현, 연도별 RMSE 재검산. `docs/LIRF_2012_2013_STAGE_SOIL_WATER_DEFICIT.md`와 `outputs/runs/20261107T115135Z_lirf_2012_2013_stage_soil_water_deficit_7ebe8eff/verification.json`에 기록했다.
- 다음은 LIRF 누적 증거의 활용 범위와 정량 진입 요건 재점검이다. 정량 검증과 본 학습은 보류 중이다.

## LIRF 2012–2013 관수 목표와 실제 물 노출 대조 (2026-11-07)

- 처리·연도 24개와 수량 대비 28개를 공통 생육 달력, 일별 총관수, 논문 ET에 연결했다. 생육기 총관수 72개 중 71개가 Zhang 표와 0.5 mm 이내였다.
- 2013년 80/40은 80/80보다 등숙기 관수 52.7 mm, 생식기 관수 27.6 mm가 적었다. Comas 표의 2013년 100/50 후기 영양생장기 ET 97%와 194/208 mm의 불일치를 보존했다.
- 워크북 ET 수치 합과 논문 연간 ET를 분리했다. 구간 합계 재검산·해시 재현·소프트웨어 검사 204개 통과. `docs/LIRF_2012_2013_ACHIEVED_WATER_EXPOSURE.md`와 `outputs/runs/20261107T114651Z_lirf_2012_2013_achieved_water_exposure_e1503af7/verification.json`에 기록했다.
- 다음은 생육기별 관측·예측 토양수분 결핍과 처리별 생육 달력 대조다. 정량 검증과 본 학습은 보류 중이다.

## LIRF 2012–2013 건조 곡실 수량의 블록 짝대조 (2026-11-07)

- 원본 수량 94개를 건조 기준으로 환산했다. 수분 보정 전 처리·연도 평균 24개는 Comas 표 1과 정수 반올림까지 일치했다.
- 해마다 완전관수 대비 11개와 시기 대비 3개를 블록 내 짝으로 계산했다. 2013년 40/40 대비는 결측 두 곳으로 2쌍이며, 짝 평균차가 가용 전체 평균차보다 0.61 t/ha 더 낮았다.
- 28개 평균·t 구간 재계산, 증거 재생성 해시 일치, 소프트웨어 검사 204개 통과. `docs/LIRF_2012_2013_BLOCK_PAIRED_YIELD.md`와 `outputs/runs/20261107T114320Z_lirf_2012_2013_block_paired_yield_contrasts_ee9d6b37/verification.json`에 기록했다.
- 다음은 목표 관수 비율과 실제 기간별 ET·총관수 노출의 대조다. 정량 검증과 본 학습은 보류 중이다.

## LIRF 파종 초기 관측 공개 경로 점검 (2026-11-07)

- DayCent 보충 PDF와 확장판 SSRN 원문은 HTTP 403. 대학 저장소 학위논문 3장에서 2008–2011 Greeley 본 분석과 2013년 별도 비엽면적 관측을 구분했다.
- USDA 공개 Figshare 및 DataCite를 조회하고 기존 2012–2013 파일 4개의 보존본을 공식 MD5와 대조했다. 확장판 실제 첨부와 초기 수분·질소 관측은 미확보 상태다.
- 증거 재생성 해시 일치, 소프트웨어 검사 204개 통과. 상세는 `docs/LIRF_INITIAL_OBSERVATION_SOURCE_FOLLOWUP.md`와 `outputs/runs/20261107T113819Z_lirf_initial_observation_source_followup_4fa2bb3c/verification.json`에 있다.
- 다음은 건조 곡실 수량의 연도·블록 짝대조와 결측에 따른 표본수·오차 정리다. 농학 검증과 본 학습은 보류 중이다.

## LIRF 2012–2013 초기 토양·품종 계보 대조 (2026-11-07)

- 작업 범위는 USDA 옥수수 배치도·작업일지와 같은 시험장의 역사적 토양 코어, 초기 수분·무기태 N 및 품종 계보 대조로 설정했다.
- 공식 배치도의 처리 번호 96개가 워크북과 일치했다. 포장·연도를 구역·블록의 토양 코어 16개에 연결했고, 층 117행과 압력판 시료 27행을 확인했다.
- 물수지표의 파종일까지 수분 수치 0개, 파종 전 질산염 채취 결과값 미확보. 2013년 5월 28일 수분 행의 계측 이력 미확인. 해바라기 수분은 같은 해 옥수수 포장 중복 0개다.
- 작업일지의 52-04 VT3/RIB와 Zhang 모형의 DCK52-59 표기를 구분했다. 품종 계수 할당, 정량 검증, 본 학습은 보류다.
- 소프트웨어 검사 204개 통과 및 증거 재생성 해시 일치. `docs/LIRF_2012_2013_INITIAL_SOIL_CULTIVAR.md`와 `outputs/runs/20261107T113128Z_lirf_2012_2013_initial_soil_cultivar_9a0dc0e5/verification.json`에 기록했다.
- 다음은 DayCent 보충자료와 LIRF 2008–2024 확장 파일에서 옥수수 포장별 초기 수분·무기태 N 및 채취 기록을 확인하는 단계다.

## LIRF 2012–2013 기상·관리 대조 (2026-11-07)

- 작업 시작 시 GLY04 QC와 원시 경로 요청 응답, 공개 워크북을 보존해 강수 7일, 관수·비료·생육 날짜를 대조하는 범위를 고정했다.
- 물수지 기간 354일에서 GLY04 일강수와 시간 합이 0.1 mm 이내로 일치했다. 2013년 7월의 하루 이동 패턴과 포장 우량계 기록의 공백을 분리했다. 원시 요청의 실제 응답은 QC였다.
- 정전 시비 처리별 적용일은 대조했다. 2013년 6월 첫 관수·시비량과 7월 마지막 시비일의 차이를 기록했다. 비료 N 합과 관개수 N 가정 산술을 분리했다.
- 소프트웨어 검사 204개 통과, 증거 재생성 해시 일치. 상세는 `docs/LIRF_2012_2013_WEATHER_MANAGEMENT.md`, 근거는 `outputs/runs/20261107T112354Z_lirf_2012_2013_weather_management_84ab810c/verification.json`에 있다.
- 다음은 블록·처리별 초기 수분·무기태 N과 토양층, DK 52-04 품종 계수의 계보다. 정량 검증과 본 학습은 보류 중이다.

## LIRF 2012–2013 기본 생육 입력 명세 (2026-11-07)

- 포장·연도 96개 중 수치 수량 94개의 건조 기준을 정리했다. 처리·날짜 4,248행과 시간별 기상 17,543행을 대조했다. 강수 불일치 7일과 파종 전 관수·관개수 N·초기 층별 수분/N 공백을 기록했다.
- 같은 시험의 기존 RZWQM2 보정 노출을 확인했다. 소프트웨어 검사 204개 통과, 검증 파일 재생성 해시 일치. 근거는 `outputs/runs/20261107T112037Z_lirf_2012_2013_baseline_dossier_d88fd233/verification.json`과 `docs/LIRF_2012_2013_BASELINE_INPUT_DOSSIER.md`에 있다.
- 다음은 GLY04와 Crop Log의 강수·관수·질소와 실제 날짜 대조다. 정량 검증과 본 학습은 보류 중이다.

## 연구 진입 요건 재점검 (2026-11-07)

- 등록 연구 10개와 시나리오 28개를 재평가했다. 정량 검증 가능 시나리오 0개, 계보 요건을 충족한 독립 후보 0/6이다. 기준선·관수 전용·이랑 폭 기술 검사와 농학 검증을 분리했다.
- 소프트웨어 검사 204개 통과, 검증 파일 재생성 해시 일치. 근거는 `outputs/runs/20261107T105231Z_research_gate_recheck_2d74e0b7/verification.json`과 `docs/RESEARCH_GATE_RECHECK.md`에 있다.
- 다음은 확보한 LIRF 2012–2013 통합 파일의 무피해 생육·수분 반응 입력 대조다. 포장·날짜 키, 건조 곡실 기준, 기상·관수·시비·토양·품종 계보를 대조한다. 농학 검증과 본 학습은 보류 중이다.

## 실험용 해충 환경의 관수 전용 규칙 공유 검사 (2026-11-07)

- 시작. validation 주소 0~3에서 고정 규칙, 관수 일치 래퍼, 관수 0 래퍼를 비교한다. 같은 관수의 실행 동일성, 현재 관측의 시비·방제, 마스크와 수익 원장을 검사한다.
- 완료. validation 4주소에서 고정 규칙·관수 일치·관수 0의 실제 DSSAT 12시즌을 수확까지 실행했다. 관수 일치는 522일의 관측·마스크·행동·보상과 결과를 재현했다. 관수 0은 126일의 관수 요청을 대체했으며 해당 관측에서 시비·방제 규칙을 검증했다.
- 일반 실행에서 막힌 관수가 나타나지 않아 별도 예산 0 검사로 거부 경로를 확인했다. 1,566일 제약 위반 0건, 소유 자식 프로세스 0개, 소프트웨어 검사 204개 통과. 근거는 `outputs/runs/20261107T104622Z_experimental_irrigation_only_shared_rules_8ca253fe/verification.json`과 `docs/BASELINE_PAIRED_DIAGNOSTIC.md`에 있다.
- 다음은 최근 기술 검사와 농학 근거를 반영해 연구 진입 요건을 재점검하고 입력 확보의 우선순위를 확정하는 단계다. 본 학습은 보류 중이다.

## 실험용 해충 환경의 기준선 공통 시즌 검사 (2026-11-07)

- 시작. 기존 미튜닝 규칙·무투입을 validation 주소 0~3에서 대응 실행한다. 공통 외생 입력, 행동 마스크, 비용·자원·종료 원수익을 검증한다.
- 완료. validation 4쌍·8시즌 모두 수확했다. 의사결정 1,044일의 마스크, 규칙 살포 3회, 무투입 0, 공개 감축 공지 6시즌, 일별 비용과 최종 원수익을 대조했다. 제약 위반과 종료 후 소유 자식 프로세스는 0건이다.
- 공지 기록을 추가한 재실행에서 8시즌의 행동·수확·수익 기록이 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T103710Z_baseline_pairs_experimental_pest_9ca027e1/verification.json`과 `docs/BASELINE_PAIRED_DIAGNOSTIC.md`에 있다.
- 다음은 관수 전용 정책의 시비·방제 규칙 공유를 실제 DSSAT에서 확인하는 기술 검사다. 농학 정량 검증과 본 학습은 보류 중이다.

## CERES 이랑 폭 복수 기상 시드 검사 (2026-11-07)

- 시작. 시드 123456을 재현하고 인접 시드 123457~123459를 고정해 총 4쌍의 UFGA 무피해 기술 실험을 실행한다. 각 시드에서 38·76cm 이외의 입력을 동일하게 두고 결과는 시드 단위로 비교한다.
- 완료. 4개 기상 시드에서 38·76cm 무피해 8시즌을 수확까지 실행했다. 같은 시드에서 PLRS만 달랐고 공통 기상은 동일했다. 이전 123456 시드의 두 폭 원본 파일 8개 해시가 일치했다.
- 38cm−76cm 평균 차단율 차이 +3.990~+5.023%p, 수확량 차이 +119~+346kg/ha였다. LAI 성분은 4개 중 3개 시드에서 폭 직접 효과를 일부 상쇄했다. 공통 성장일 490개를 재계산했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T103109Z_native_ceres_ipar_row_width_multiseed_b535b7ba/verification.json`에 있다.
- 다음은 미튜닝 규칙과 무투입 대조를 실험용 해충 환경의 공통 validation 시즌에서 연결하고 마스크·자원·수익 원장을 확인하는 기술 검사다. 농학 정량 검증과 본 학습은 보류 중이다.

## CERES 이랑 폭 실제 두 시즌 완료 (2026-11-07)

- Docker Linux 엔진이 응답해 기존 진단 이미지에서 38·76cm UFGA 무피해 두 시즌을 수확까지 실행했다. PLRS만 달랐으며 공통 기상 162일과 성장일 124일을 검증했다.
- 38cm−76cm 평균 차단율 차이는 +5.023%p였다. 폭 직접 성분 +4.938%p와 LAI 성분 +0.085%p로 분리했다. 수확량은 4,953과 4,607kg/ha였다.
- 네이티브 에너지에서 차단율을 별도 계산했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T102705Z_native_ceres_ipar_row_width_d7935f89/verification.json`과 `docs/NATIVE_CERES_IPAR_ROW_WIDTH.md`에 있다.
- 다음은 복수 공통 기상 시드의 폭 민감도 기술 검사다. 농학 정량 검증과 본 학습은 보류 중이다.

## CERES 무피해 이랑 폭 민감도 (2026-11-07)

- 시작. UFGA의 38·76cm FileX 차이와 LAI 고정 대비를 검증하고 동일 이미지에서 두 시즌을 실행한다.
- 고정 LAI 계산 완료. 보관한 61cm 무피해 성장 기록 124일에서 38cm−76cm의 평균 차단율 차이는 +4.94%p, 최대 +6.29%p였다. 원본 해시와 124일 대비를 대조했고 소프트웨어 검사 204개가 통과했다.
- Docker Desktop 시작 시간 초과 및 Linux 엔진 소켓 미생성으로 실제 두 시즌은 실행 대기다. FileX의 PLRS 변경·원복과 대비 분해를 검사했다. 근거는 `outputs/runs/20261107T102234Z_ceres_ipar_width_archive_ff3d4b4f/verification.json`과 `docs/NATIVE_CERES_IPAR_ROW_WIDTH.md`에 있다.
- 다음은 같은 진단 이미지에서 실제 두 폭을 실행해 LAI 반응과 수확을 대조하는 단계다.

## 광학 자료 적용 범위와 Battaglia 무피해 대조 (2026-11-07)

- 시작. 광학 지표의 측정 대상과 시간대를 정리하고 무피해 대조 광 차단율과 생육 조사 구간을 분리해 대조한다.
- 완료. 정오 차단율·층별 투과율·연속 광량·흡수율·기하학적 피복률·LAI 측정법을 분리했다. Battaglia 표 4의 2013년 무피해 평균 8개와 이랑 폭 대비 4개를 정리했다. 생육 도달 구간을 광학 측정일로 사용하지 않았고 직접 비교 가능 쌍은 0개다.
- 검증 파일 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T101446Z_optical_evidence_battaglia_control_1fa618f6/verification.json`과 `docs/OPTICAL_EVIDENCE_BATTAGLIA_CONTROL.md`에 있다.
- 다음은 기존 UFGA 무피해 실행에서 이랑 폭만 38·76cm로 달리한 기술 민감도 검사다. 농학 정량 검증과 본 학습은 보류 중이다.

## Duan 등 옥수수 군락 층별 PAR–LAI 자료 감사 (2026-11-07)

- 시작. 원문, DOI 데이터 링크와 후속 논문에서 층별 광량·잎 면적의 측정 조건과 공개 범위를 확인한다.
- 완료. 2024·2025년 출판사 XML을 확보했다. 수확 표의 8개 연도·밀도 조합에서 공통 지표 32개 값이 일치해 같은 시험 자료로 분류했다. 센서 관측 자체의 중복 여부는 미확인이다.
- 두 논문 모두 원자료는 저자 요청 조건이다. 같은 포장·날짜의 독립 LAI–PAR 쌍은 0개다. 파종일과 투과율 식의 원문 불일치를 기록했다.
- 검증 파일 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T101012Z_maize_canopy_layer_par_lai_c491655b/verification.json`과 `docs/DUAN_MAIZE_CANOPY_LAYER_PAR_LAI.md`에 있다.
- 다음은 누적 광학 자료의 적용 조건을 정리하고 Battaglia 무피해 대조에서 비교 가능한 범위와 추가 데이터 요건을 확정하는 단계다.

## Zhou 옥수수 PAR 보충자료 감사 (2026-11-07)

- 공식 PMC 보충 ZIP을 내려받아 원본 크기·CRC와 워크북 6개의 스키마를 확인했다. S1의 PAR 표는 369개 유전자형의 연도·명목 DAP별 혼합모형 효과다. 포장·날짜별 센서 원값과 독립 LAI 연결 쌍은 0개다.
- 검증 파일 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T100400Z_zhou_maize_par_supplement_22c658d4/verification.json`과 `docs/ZHOU_MAIZE_PAR_SUPPLEMENT.md`에 있다.
- 다음은 옥수수 군락 층별 광 차단 연구의 원자료를 확인한다. 농학 정량 검증과 본 학습은 보류 중이다.

## Kukal·Irmak PAR–LAI 공개 원자료 확인 (2026-11-07)

- 시작. 출판사, DOI 메타데이터, 대학 저장소, 관련 논문에서 옥수수 PAR 센서 기록과 독립 LAI의 관측 단위·시점·공개 파일을 대조한다.
- 완료. 옥수수 3개 성숙형·연도 계열에서 연속 PAR와 정오 광량계 측정을 구분했다. 보고된 LAI는 광량계 기반 전체 LAI이며, 일별 그래프는 보간 LAI를 사용했다.
- DOI 메타데이터·출판사 API·학위논문 서지를 확인했다. PAR와 독립 LAI 원본을 확보하지 못했고, 같은 포장·날짜 정량 쌍은 0개다. 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T075326Z_kukal_irmak_par_lai_ae7ab1c5/verification.json`과 `docs/KUKAL_IRMAK_PAR_LAI.md`에 있다.
- 다음은 Zhou 등의 보충 데이터 1에서 옥수수 PAR 기록과 독립 LAI의 연결 가능성을 확인한다. 농학 정량 검증과 본 학습은 보류 중이다.

## LIRF 피복률–LAI 연도 보류 진단 (2026-11-07)

- 시작. 2012년으로만 포화곡선과 평균 기준선을 추정하고 2013년의 날짜별·LAI 범위별 오차를 확인한다. 관측일을 고정하고 2013년 포장 단위로 반복 관측을 묶어 불확실성을 확인한다.
- 완료. 2012년 96행만으로 포화곡선을 적합했다. 2013년 84행의 MAE 7.93%p, RMSE 9.14%p, 평균 오차 −5.62%p였다. 연도별 조사 시기 차이와 2012년 LAI 관측 공백을 분리해 기록했다.
- 재실행 결과 두 파일의 해시가 일치했다. 2013년 원본 행과 예측을 별도로 대조했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T074436Z_lirf_cover_lai_heldout_5591d718/verification.json`과 `docs/LIRF_COVER_LAI_HELDOUT.md`에 있다.
- 다음은 Kukal·Irmak 공개 자료에서 독립 LAI와 같은 포장·날짜의 입사·투과 PAR를 연결할 수 있는지 확인하는 단계다.

## LIRF 피복률·LAI 포장·날짜 연결 (2026-11-07)

- USDA 2012~2013년 워크북의 포장별 LAI와 사진 피복률을 확인했다. 같은 포장·날짜에서 180쌍을 연결했다. 2012년 96쌍, 2013년 84쌍이다. 피복률 중복 키 3개는 LAI 조사일 밖에 있어 제외했다.
- 2008~2011년은 처리 단위로만 대조했다. LAI와 실측 표시 피복률이 같은 처리·날짜에서 23행 겹쳤고, 2011년 LAI 6행은 추정일이다. 광 차단율과 직접 비교할 수 있는 관측 쌍은 0개다.
- 소프트웨어 검사 204개 통과. 연결 근거는 `outputs/runs/20261107T073721Z_lirf_canopy_cover_lai_790eb9d6/verification.json`과 `docs/LIRF_CANOPY_COVER_LAI.md`에 있다.
- 다음은 2012년 개발·2013년 보류 평가로 기하학적 피복률–LAI 관계의 연도 간 재현성을 확인한다. 농학 정량 검증과 본 학습은 보류 중이다.

## ORNL–Mead 흡수율·LAI 연결 대조 (2026-11-07)

- Mead 옥수수 사이트·연도 3개를 확인했다. US-Ne3 2019년의 파괴 LAI 채취 11회가 보고된 분광 관측 기간과 겹친다. 두 논문의 파종일은 4월 24일과 27일로 달라 DAP를 합치지 않았다.
- ORNL 센서 fPAR은 반사광을 보정한 흡수율이다. 공개 스키마에 투과광·반사광 개별 열이 없어 Battaglia 차단율로 직접 변환할 수 없다.
- 원본 CSV는 Earthdata 401, AmeriFlux BADM은 로그인 화면이었다. 공개 체크섬·카탈로그를 대조했으며 실제 날짜별 비교 쌍은 0개다. 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T072300Z_ornl_mead_fpar_lai_0eda4047/verification.json`과 `docs/ORNL_MEAD_FPAR_LAI.md`에 있다.
- 다음은 LIRF 군락 피복률과 LAI의 포장·날짜 연결 확인이다. 농학 검증과 본 학습은 보류 중이다.

## 독립 광 차단율·LAI 자료 선별 (2026-11-07)

- 공개 후보 7개를 검토했다. MuST-C v3.0에서 같은 포장·같은 날의 SunScan–파괴 측정 LAI 쌍 2개와 하루 차이 3개를 확인했다. SunScan 상·하부 PPFD는 참조 ZIP에서 미확보다.
- COBS의 LAI는 IPAR 역산값이다. ORNL DAAC의 센서 기반 30분 fPAR은 독립 LAI 연결을 확인해야 한다. 현재 확보한 자료 중 정량 보정 가능 쌍은 0개다.
- 결과 파일 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T071234Z_independent_ipar_lai_screen_d2bd5770/verification.json`과 `docs/INDEPENDENT_IPAR_LAI_SCREEN.md`에 있다.
- 다음은 ORNL DAAC의 센서 관측 옥수수 fPAR과 Mead US-Ne2·US-Ne3 독립 LAI의 현장·날짜 대조다. 농학 검증과 본 학습은 보류 중이다.

## CERES 성장 시점 IPAR 진단 (2026-11-07)

- 진단 전용 Docker 이미지에서 성장 계산에 사용한 날짜·LAI·입사 PAR·차단 에너지를 별도 JSONL로 기록했다. UFGA 정상 수확 4시즌에서 계측을 켠 실행과 기준 실행의 전체 상태와 수확 결과가 두 쌍 모두 정확히 일치했다.
- 계측한 각 124일의 에너지 재계산 최대 절대차는 1.44×10⁻⁷ MJ/개체/일이었다. 피해 당일의 성장값은 대조와 같았고, 줄어든 LAI는 다음 날 성장부터 반영됐다. 성숙·수확일에는 수확 경계만 기록됐다.
- 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T070235Z_native_ceres_ipar_cee567c5/verification.json`과 `docs/NATIVE_CERES_IPAR.md`에 있다. 다음은 시간대별 IPAR와 LAI를 함께 측정한 독립 공개자료 검토다. 농학 검증과 본 학습은 보류 중이다.

## Battaglia IPAR·DSSAT 출력 대조 (2026-11-07)

- 맑은 날 11~14시의 포장 광 차단율과 CERES의 일별 성장 계산을 구분했다. 표 4 평균 16개로 8개 기술 대비를 보존했다. 2013년 V7 피해군은 대조군보다 V8에 36~59%p, R5에 5~8%p 낮았다.
- 보관된 UFGA 두 실행에서 각 136일의 종료 LAI와 일사를 대조했다. 다음 날 정책 trace의 LAI는 양쪽에서 각 135일 일치했으나 일사는 각 1일 불일치했다. 성장 계산 시점의 IPAR 직접 출력과 농학 정량 비교는 미검증이다.
- 결과 파일 3개의 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T065543Z_battaglia_ipar_crosswalk_f020491b/verification.json`과 `docs/BATTAGLIA_IPAR_CROSSWALK.md`에 있다.
- 다음은 CERES 내부 광 차단 계산을 별도 진단으로 기록해 피해 전후 및 종료일 날짜 계약을 확인하는 작업이다.

## Battaglia 누적 GDD·생육단계 대조 (2026-11-07)

- Spindletop 일별 기상의 최고·최저 평균에서 8°C를 빼고 0에서 절단했다. 파종일과 조사일을 모두 포함해 합산하면 부록의 누적 GDD 42개를 모두 정수 표시 정밀도로 재현했다. 논문 산식의 직접 확인과 DSSAT 생육계수 검증은 별도다.
- 무피해 대조군 8개에서 생육 관측 168개와 V7·V14·VT·R1·R2·R6 도달 구간 48개를 정리했다. 구간 폭은 2~16일이며 복합 단계 표기를 보존했다.
- 결과 파일 4개의 재생성 해시가 일치했고 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T064829Z_battaglia_gdd_phenology_167aefb4/verification.json`과 `docs/BATTAGLIA_GDD_PHENOLOGY.md`에 있다.
- 다음은 IPAR 측정값을 DSSAT 군락 광 차단 출력과 연결할 수 있는지 확인하는 작업이다. 농학 검증과 본 학습은 보류 중이다.

## Battaglia 토양·품종 출처 대조 (2026-11-07)

- 논문의 좌표와 농장 참고점은 약 10.8km 떨어져 있고, 두 좌표의 USDA 지도 단위에서 Loradale 구성요소를 확인하지 못했다. Fayette County의 Loradale 대표 단면 2개·토양 및 암반층 8행은 별도 보존했다. 포장 토양 수리 특성과 초기 수분·무기태 질소는 미확보다.
- 프로젝트 CERES-Maize 품종 파일 167행과 공식 공개 파일 168행을 대조했다. P1360HR·P2088YHR의 품종 계수는 확인되지 않았다. IB0035는 McCurdy 84aa이며 두 파일의 계수가 달라 커밋과 해시를 기록했다.
- 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T064354Z_battaglia_soil_cultivar_lineage_40c3b7a3/verification.json`과 `docs/BATTAGLIA_SOIL_CULTIVAR_LINEAGE.md`에 있다. 다음은 일별 기상과 논문 누적 GDD 42개 및 무피해 대조 생육단계의 대조다. 농학 검증과 본 학습은 보류 중이다.

## Battaglia 일별 기상 대조 (2026-11-07)

- 논문이 인용한 켄터키대 농장 관측을 조회해 2012·2013년 4~9월 일별 기상 366행과 생육 조사일 42개를 연결했다. 파종~일반 수확 강수는 321.1mm·789.9mm로 논문 집계에서 역산한 약 321mm·790mm와 일치했다.
- NOAA 공항은 459.6mm·702.6mm로 외부 비교에만 사용했다. 실제 관수는 22일 약 278mm 및 4일 약 45mm의 집계만 확인했다. 개별 관수일·일별 투입량과 GDD 값의 재현이 남았다.
- 원응답 해시와 두 결과 파일의 재생성 일치를 확인했다. 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T063827Z_battaglia_spindletop_weather_a2d097ca/verification.json`과 `docs/BATTAGLIA_SPINDLETOP_WEATHER.md`에 있다.
- 다음은 Loradale 층별 토양·초기 상태와 두 품종의 DSSAT 계수 출처 대조다. 농학 검증과 본 학습은 보류 중이다.

## Battaglia 포장 회복 자료 대조 (2026-11-07)

- 2018 수량 논문과 2019 IPAR 논문은 동일한 2012·2013 포장 시험으로 확인했다. 학위논문은 초록의 설계가 일치하나 PDF가 403이어서 세 문서를 한 시험 계열로 계산했다.
- 부록 생육 조사 날짜와 누적 GDD 헤더 42쌍, 파종·시비·수확일을 기록했다. 2013 V7 100%의 IPAR 23→75%를 잎 면적 회복과 분리했고, 수확의 이삭 선별 및 조기 수확 조건을 보존했다. 근거는 `outputs/runs/20261107T062535Z_battaglia_recovery_input_audit_caf7619e/verification.json`와 `docs/BATTAGLIA_RECOVERY_INPUT_AUDIT.md`에 있다.
- 소프트웨어 검사 204개가 모두 통과했다. 결과는 `outputs/runs/20261107T062535Z_battaglia_recovery_input_audit_caf7619e/software_tests.json`에 있다.
- 실제 일별 기상·관수 이벤트, 토양층·초기 상태와 피해 매핑, 포장별 원자료와 독립 계보가 남았다. 다음은 Spindletop 기상 및 관수 이벤트의 연결 검토다. 농학 검증과 본 학습은 보류 중이다.

## 농학 검증 진입 조건 재점검 (2026-11-07)

- 활성 연구 10개·시나리오 28개·독립 후보 6개의 준비 요건을 재검사했다. 정량 검증 가능 시나리오 0개이며 독립 계보를 충족한 연구도 없었다.
- Oveysi의 물×피해 기술 대비 4개를 계산했다. 같은 연구의 이원 주변합으로도 직접 3요인 대비가 식별되지 않음을 확인했다. 근거는 `outputs/runs/20261107T062039Z_agronomic_reentry_audit_4b41e2ac/verification.json`, 상세는 `docs/AGRONOMIC_REENTRY_AUDIT.md`에 있다.
- 소프트웨어 검사 204개가 모두 통과했다. 결과는 `outputs/runs/20261107T062039Z_agronomic_reentry_audit_4b41e2ac/software_tests.json`에 있다.
- 켄터키 Battaglia 회복 후보의 논문과 학위논문을 확인했다. 다음은 두 출처의 처리별 회복 관측·수확 기준·입력과 계보 대조다. 농학 검증과 본 학습은 보류 상태다.

## 동일 이미지 CPU·CUDA 장기 비교 완료 (2026-11-07)

- CPU→CUDA→CUDA→CPU 각 102,400단계 완료. CPU 130.23·75.77, CUDA 97.49·61.54단계/초였다. 두 쌍의 CPU 우위는 33.6%와 23.1%였다. 후반에는 별도 실험을 동시에 실행했다고 사용자가 확인했다. 처리량 원값을 보존하고 후반 저하 자체를 장치 판단에 반영하지 않았다.
- 총 409,600단계·3,200갱신·3,080시즌. 무효 행동·백엔드 오류·시간제한 0건, 시뮬레이터 워커 정리 통과. 근거는 `outputs/runs/20261107T045403Z_controlled_device_pair_42f9ad55/verification.json`, 상세는 `docs/CONTROLLED_DEVICE_THROUGHPUT.md`에 있다.
- 소프트웨어 검사 204개가 모두 통과했다. 결과는 `outputs/runs/20261107T045403Z_controlled_device_pair_42f9ad55/software_tests.json`에 있다.
- 기술 비교 항목을 완료 처리했다. 본 학습은 보류 중이며 다음은 농학 보정과 독립 회복·물×질소 검증의 진입 조건 재점검이다.

## 동일 이미지 CPU·CUDA 장기 비교 시작 (2026-11-07)

- 동일 CUDA 이미지에서 CPU→CUDA→CUDA→CPU 순서로 각 102,400단계의 기술 비교를 시작했다. 상위 실행 폴더는 `outputs/runs/20261107T045403Z_controlled_device_pair_42f9ad55`다.
- 첫 CPU 실행은 `outputs/runs/20261107T045407Z_benchmark_experimental_pest_cpu_45339909`에 진행 상태와 체크포인트를 저장한다. 비교 판정은 네 실행 완료 후 기록한다.

- 첫 CPU 실행은 102,400단계·800갱신·770시즌을 130.23단계/초로 완료했다. 첫 CUDA 실행은 `outputs/runs/20261107T050730Z_benchmark_experimental_pest_cuda_0235a505`에서 시작했다.

- 첫 CUDA 실행은 102,400단계·800갱신·770시즌을 97.49단계/초로 완료했다. 두 번째 CUDA 실행은 `outputs/runs/20261107T052517Z_benchmark_experimental_pest_cuda_ae6f0ac2`에서 시작했다.

- 두 번째 CUDA 실행은 102,400단계·800갱신·770시즌을 61.54단계/초로 완료했다. 마지막 CPU 실행은 `outputs/runs/20261107T055322Z_benchmark_experimental_pest_cpu_2642e24f`에서 시작했다.

## 동일 이미지 CPU·CUDA 예비 비교 (2026-11-07)

- 기존 102,400단계 기록의 체크포인트 설정은 일치했으나 이미지, 소스, 실행 부하가 달랐다. 동일 CUDA 이미지와 분포 검사 enabled에서 CPU→CUDA→CUDA→CPU 순으로 4환경·1,024단계씩 예비 실행했다.
- CPU 180.07·196.24, CUDA 121.54·138.78단계/초였다. 총 PPO 갱신 32회, 제약 위반·백엔드 오류·시간제한 0건, 소프트웨어 검사 204개 통과다. 근거는 `outputs/runs/20261107T043123Z_controlled_device_pair_8a6d1978/verification.json`, 상세는 `docs/CONTROLLED_DEVICE_THROUGHPUT.md`에 있다.
- 예비 비교로 장기 장치를 확정하지 않았다. 다음은 같은 이미지의 102,400단계 교차 순서 장기 기술 비교다. 정량 보정과 본 학습은 보류 상태다.

## DSSAT 공통 GAE 롤아웃 검증 (2026-11-07)

- 동일 고정 행동으로 수확과 60일 제한을 두 λ에서 비교했다. 6롤아웃·630전이에서 관측과 보상 및 가치 추정값은 λ 간에 일치했다. MaskablePPO 버퍼 어드밴티지의 직접 재계산 최대 오차는 4.65×10⁻⁷이었다.
- 수확에서 최종 가치 추가가 없었고, 시간제한에서는 리셋 이전 관측의 가치가 버퍼 보상에 더해졌다. 옵티마이저 갱신 0회, 소프트웨어 검사 204개 통과다. 근거는 `outputs/runs/20261107T042657Z_gae_common_rollout_3d7d6613/verification.json`, 해석 범위는 `docs/GAE_COMMON_ROLLOUT.md`에 있다.
- λ 후보 선택과 본 학습은 보류 중이다. 다음은 기존 CPU·CUDA 장기 실행의 비교 조건 점검이다.

## DSSAT 보상 계수 η 민감도 (2026-11-07)

- 고정 행동과 외생 시드를 공유해 η=0, 0.225, 0.45, 0.90을 대조했다. 두 시즌 수확 8회 및 60일 제한 4회에서 각 조건의 원보상과 정책 관측 해시가 η 간에 일치했다.
- 60일 제한에서 η=0.45는 마지막 잠재함수 224.614 USD/ha를 유지했다. 원보상 −214.980 USD/ha와 스케일 후 학습 보상 +0.009634를 구분했다. 수확 종료의 최종 잠재함수는 0이었다.
- 소프트웨어 검사 204개가 통과했다. 근거는 `outputs/runs/20261107T042324Z_reward_eta_common_season_4d0a9dae/verification.json`, 해석 범위는 `docs/REWARD_ETA_SENSITIVITY.md`에 있다. 본 학습은 보류 중이며 다음은 GAE λ 공통 롤아웃 기술 검사다.

## DSSAT 공통 시즌 민감도 전달 검사 (2026-11-07)

- Docker IPC 시작 오류를 복구한 뒤 기존 Gym/PDI 워커로 공통 두 시즌·네 설정을 실행했다. 8회 수확 완료, 1,008 의사결정일, 양의 네이티브 잎 피해 쓰기 632일을 확인했다.
- 같은 행동에서 조사 잡음은 조사값에만 반영됐다. α 두 배는 해충압을 바꾸지 않으면서 요청과 실제 잎 피해율을 늘렸다. 효능 0에서는 해충압이 기준보다 높아진 날을 두 시즌에서 확인했다.
- 소프트웨어 검사 204개가 통과했다. 실행 근거는 `outputs/runs/20261107T033439Z_faw_dssat_pairing_100018ed/verification.json`, 복구와 해석 범위는 `docs/FAW_DSSAT_SENSITIVITY_PAIRING.md`에 있다. 정량 보정과 본 학습은 보류 중이며 다음은 보상 계수 η 민감도 검사다.

## 해충 계수의 보정 요건·기술 민감도 검사 (2026-11-07)

- 온도·성장, 유입, 효능·잔효, 피해 계수와 조사 잡음의 공개 근거 및 보정 요건을 대조했다. 상세는 `docs/FAW_PARAMETER_SENSITIVITY.md`에 있다.
- 합성 온도 3종과 공통 난수쌍 8개로 17설정·408궤적을 실행했다. 무유입, 잠재 해충압 분리, 살포 효능 방향, 조사 횟수와 상태 범위를 확인했다. 결과는 `outputs/runs/20261107T032301Z_faw_technical_sensitivity_a8ded22d/sensitivity.json`에 있다.
- 소프트웨어 검사 204개가 통과했다. 결과는 `outputs/runs/20261107T032301Z_faw_technical_sensitivity_a8ded22d/software_tests.json`에 있다.
- 정량 보정과 본 학습은 보류 중이다. 다음은 공통 DSSAT 시즌과 제약을 만족하는 고정 행동을 적용한 선택 시나리오의 전달 검사다.

## Varella 포장 알·초기 유충 손실 대조 (2026-11-07)

- 공개 원문과 보충표 2개에서 알 10코호트와 초기 유충 6코호트를 대조했다. 7일 유충 손실 집계는 95.28–99.50%이며, 유실·이동·미발견을 실제 사망과 분리할 수 없다. 상세는 `docs/VARELLA_FIELD_STAGE_SURVIVAL.md`에 있다.
- 보충표의 단순 비율과 본문을 대조해 알 17/70개, 초기 유충 1/18개 불일치를 기록했다. 원값은 두 계열로 보존했다. 근거는 `outputs/runs/20261107T031752Z_varella_stage_survival_audit_585b135e/stage_survival.json`에 있다.
- 소프트웨어 검사 204개가 통과했다. 결과는 `outputs/runs/20261107T031752Z_varella_stage_survival_audit_585b135e/software_tests.json`에 있다.
- 온도별 성장률, 방제 효과, 조사 잡음은 미보정이며 본 학습은 보류 중이다. 다음은 계수별로 보정 가능한 범위와 기술 민감도 분석용 가정을 구분하는 단계다.

## 토고 포장 반복조사 자료 검토 (2026-11-07)

- Koffi 논문과 Dryad 메타데이터를 확보해 농가 월별 100식물 관측과 시험장 주별 10식물 관측을 구분했다. 시험장 무방제 조건은 원문에서 확인했다. 원본 XLSX·README 다운로드는 403으로 정확한 포장·날짜 및 기상·살포 연결을 확인하지 못했다. 상세는 `docs/TOGO_FAW_FIELD_LINKAGE.md`에 있다.
- 표 2·3 Pearson 상관 통계 32행을 대조했다. 로메의 출아기 성충–피해, 영양생장기 성충–유충 두 행은 반올림을 고려해도 양측 p값이 보고값과 맞지 않았다. 원표는 수정하지 않았다. 근거는 `outputs/runs/20261107T031344Z_koffi_togo_linkage_audit_88a5d3ae/linkage_audit.json`에 있다.
- 소프트웨어 검사 204개가 통과했다. 결과는 `outputs/runs/20261107T031344Z_koffi_togo_linkage_audit_88a5d3ae/software_tests.json`에 있다.
- 정량 보정과 본 학습은 보류 상태다. 다음은 Varella 공개 자료에서 옥수수 포장 알·초기 유충의 생존과 소실을 분리할 수 있는지 확인하는 단계다.

## 피해 척도·조사 오차 자료 검토 (2026-11-07)

- Toepfer의 판독자 교대와 척도 비교를 동일 척도 반복 판독과 구분했다. Soujanya 공개 보충표 3개(9시트)에서 독립 판독자와 기준 면적 열을 확인하지 못했다. Abang IITA의 CSV 엠바고 표시를 재확인했다. 근거는 `outputs/runs/20261107T030922Z_faw_survey_measurement_audit_e178d231/measurement_audit.json`에 있다.
- 피해 식물 비율, 순서형 피해 점수, 잎 조각 섭식 면적과 MARS 직전 7일 신규 손실을 구분했다. 조건을 충족한 자료는 0개이며 조사 잡음과 본 학습은 보류다. 상세는 `docs/FAW_SURVEY_MEASUREMENT_ERROR.md`에 있다.
- 소프트웨어 검사 204개가 통과했다. 결과는 `outputs/runs/20261107T030922Z_faw_survey_measurement_audit_e178d231/software_tests.json`에 있다.
- 다음은 토고 Koffi 공개 자료에서 반복 조사 키와 기상·방제 이력의 연결 가능성을 확인하는 단계다.

## Masii 시험 프로토콜 대조 (2026-11-07)

- 학회 초록 NMK_AKE89의 재배 기간에 원자료 조사일 28개가 모두 들어갔다. 지역과 처리별 농장 수, 장치 간격 20m가 일치했다. 배치 반경 112m(초록)와 127m(저장소) 및 포장 식별 연결은 미해결이다. 상세는 `docs/MASII_PROTOCOL_LINKAGE.md`에 있다.
- V1 통합문서 6개(시트 11개)를 구조 감사했다. 숨김 시트와 주석 파일은 없었고 시즌 2 곡실 수량 파일에 외부 참조 1개가 있었다. 연속 조사 구간 144개에서 확인된 기상·실제 살포 연결은 없었다. 근거는 `outputs/runs/20261107T025729Z_masii_faw_protocol_linkage_78d174c5/protocol_linkage.json`에 있다.
- 소프트웨어 검사 204개가 통과했다. 결과는 `outputs/runs/20261107T025729Z_masii_faw_protocol_linkage_78d174c5/software_tests.json`에 있다.
- 정량 보정과 본 학습은 보류 상태다. 다음은 피해 척도 연구에서 동일 식물의 독립 반복 판독과 기준 잎 면적 자료를 찾는 단계다.

## 열대거세미나방 포장 반복조사 자료 감사 (2026-11-07)

- 케냐 Masii V1 파일 6개를 확보했다. 두 시즌 합계 포장 방문 168회, 식물 관측 6,720행 중 생존 유충 수·피해 점수 동시 기록 6,717행을 확인했다. 세 행의 유충 수는 결측으로 두었다. 근거는 `outputs/runs/20261107T025203Z_masii_faw_field_audit_34ee11b0/field_audit.json`에 있다.
- 첫 시즌에서 한 포장의 처리 라벨 충돌과 발생률 표 방문 키 중복 1건을 확인했다. FAMEWS는 감염 식물 비율과 환경 맥락의 후보로, 우간다 연구는 조사 방법·집계 비교 자료로 분리했다. `docs/FAW_FIELD_SURVEILLANCE.md`에 상세를 기록했다.
- 소프트웨어 검사 204개가 모두 통과했다. 결과는 `outputs/runs/20261107T025203Z_masii_faw_field_audit_34ee11b0/software_tests.json`에 있다.
- 공개 자료에서 일별 기상·실제 살포일·동일 식물의 독립 반복 판독 연결을 확인하지 못했다. 정량 보정과 본 학습은 보류 상태다. 다음은 Masii 공개 프로토콜과 기상·살포 이력 연결 가능성을 확인하는 단계다.

## 온도별 번식·개체군 증가율 비교 (2026-11-07)

- Chen 2022 옥수수 코호트 3조건과 Adan 2024 ILCYM 5조건을 원문 XML에서 추출했다. 25→30°C에서 일별 증가율은 각각 +0.087, −0.031745였다. Chen 20°C 산란수는 원표 표기 오류로 결측 처리했다. Adan의 λ 5개는 exp(rₘ)과 표의 정밀도 내에서 일치했다. 상세는 `docs/FAW_THERMAL_DEMOGRAPHY.md`에 있다.
- 두 출처는 사육 조건과 산출법이 달라 온도 반응 형태의 민감도 근거로 분리했다. 추출은 `outputs/runs/20261107T024230Z_faw_thermal_demography_bdd7c079/thermal_demography.json`, 검사 204개 통과는 같은 폴더의 `software_tests.json`에 있다.
- `outputs/runs/20261107T024321Z_readiness_e7cc10af/readiness.json`에서 온도 기준 2개와 조사 잡음이 미설정이고 연구용 실행·본 학습이 보류 상태임을 확인했다. 다음은 기상·방제 이력과 연결된 포장별 반복 유충수·엽피해 자료 및 조사 반복 판독 탐색이다.

## Du Plessis 온도별 발육·유충 생존 근거 추출 (2026-11-07)

- Europe PMC 원문 XML을 보존하고 발육 기간 50개 셀, 유충 사망률 5개 셀, 발육 회귀 10개 행을 추출했다. 표 1과 표 3에서 공통 발육 기간 20개 셀을 대조했다. 22°C 유충 SE는 표 3의 0.15일을 채택했다. 상세 근거는 `docs/DUPLESSIS_THERMAL_CONSTRAINTS.md`에 있다.
- 사망률에서 환산한 유충 생존율과 발육 관측의 SE를 구분했다. 개체군 증가율과 조사 잡음은 미보정 상태이며 정량 보정과 본 학습은 보류 상태다.
- 검증 결과는 `outputs/runs/20261107T023641Z_duplessis_thermal_constraints_76046637/verification.json`에 있다. 소프트웨어 검사 204개가 통과했다. 다음은 온도별 번식과 개체군 증가율을 보고한 생명표 자료의 적용 범위 확인이다.

## Oliveira 실험 중복·단위·수분 기준 감사 완료 (2026-11-07)

- 구조논문기관PDF 방법3/4쪽과기존렌더,질소논문HTML/원DOCX,기존Dryad페이지/API메타데이터를대조해14항목명세를작성했다. 같은온실/연구진/절단방법이나구조4×2×5포트/KWS9606 포함과질소2×3×8포트/KWS9668은보고설계가다르다. 품종별칭/실험일/포트ID를추정하지않아정확중복과독립성은미검증이다.
- 구조논문2개체/포트vsDryad1개체,포트총량÷2의개체평균vs원열g/plant표기를분리했다. 13%수분은100립중과HI분자만명시,HI분모는논문전체건물(지상+뿌리)vsDryad지상부차이유지. 원XLSX미확보·×2/÷2/×0.87/ha환산0·반복수증가0이다.
- 질소Fig2C의포트/개체·수분기준미확정. n8평균±SE표기와DOCXS2곡실절단×추비F3.88/p.029원행대조. F/p를원평균/SE로복구하지않고그림수치화0. 기비40/추비80(해당처리)과5cm절단을현장투입/잎피해비율로전송하지않았다.
- 공식UNIFAL관련공개학위논문색인의V5절단표기vs저널V4를확인했다. 두학위논문항목은엠바고표시,동일실험미확정으로저널원값수정/전문접근우회0. 과거Dryad401/403재시도0,원자료/계보부족유지.
- 근거 `outputs/runs/20261107T023128Z_oliveira_overlap_units_dbd625d6/verification.json`,상세 `docs/OLIVEIRA_OVERLAP_UNITS.md`. 질소연구의독립계보게이트에이감사SHA를고정했다. 근거의존재와독립성통과를구분하며패키지/전체연구독립성false·역할변경0이다.
- 소프트웨어204검사실패/오류/건너뜀0 `outputs/runs/20261107T023255Z_unit_regressions_aa117333/verification.json`. 우선순위 `outputs/runs/20261107T023305Z_agronomic_input_priorities_03f103e0/verification.json`,준비상태 `outputs/runs/20261107T023307Z_readiness_56340a87/readiness.json`. 활성10연구/28처리/16대비·정량0개·연구/본학습false·새native/학습0이다.
- 우선순위3출처대조완료/미해결유지. 다음은우선순위4 Du Plessis 온도별발육·생존근거추출이다. 발육속도를개체군증가율/조사잡음으로치환하지않는다.

## Kenya 공식 원현장 파일·과거보정 이력 감사 완료 (2026-11-07)

- 공식학위논문기록HTML/rel=item HTTPS링크에서1800513bytes PDF확보·MD5/SHA대조. 실제3쪽(2012-11표지/선언ii/초록xvii)발췌로전체방법장아님. 공식bundle목록ORIGINAL1PDF와LICENSE/TEXT/THUMBNAIL각1파일확인범위에서추가원본문없음,다른공개위치부재로확대하지않는다.
- 별도초기파종논문공식PDF도6281bytes/1쪽초록이었다. 전4쪽렌더링/추출문대조,수량보정식/정확품종·관리/토양·기상·계수표미확보유지. 다운로드성공을프로토콜전문으로승격하지않았다.
- 초록의여러현장실험/AquaCrop보정·검증은과거노출가능성근거일뿐정확포장/시즌/계수/분할미확정이다. DSSAT독립성/보정노출로대체0,분할N실험의70N을파종실험비료량/미표시kg단위로할당0.
- 초기초록LR09무곡실진술vs현재CSV18 Machanga LR09 17/18실패·1곡실(Wet/Duma43)차이를정확동일성/집계/실패정의미확정으로보존했다. 현재양성관측삭제/실패18로교정0·독립연구추가0.
- 검색색인repository호스트인증서불일치실패보존/검증해제0,공식ARM목록이별도명시한유효ir-library기록링크로취득했다. localhost메타링크미사용,외부연락/접근우회0.
- 취득 `outputs/runs/20261107T014953Z_kenya_thesis_pdf_5b37285e/verification.json`,공식목록 `outputs/runs/20261107T015050Z_kenya_thesis_bundle_inventory_cdebf755/verification.json`,초기PDF `outputs/runs/20261107T015203Z_kenya_early_protocol_source_eb106ea9/verification.json`,감사 `outputs/runs/20261107T015403Z_kenya_legacy_protocol_audit_337a03f4/verification.json`. 상세 `docs/KENYA_LEGACY_PROTOCOL_AUDIT.md`.
- 우선순위 `outputs/runs/20261107T015513Z_agronomic_input_priorities_bac3ee70/verification.json`,준비상태 `outputs/runs/20261107T015513Z_readiness_58aea251/readiness.json`. 현장3후보의전체입력/보정완료조건미충족/대기,활성10연구/정량0개·연구/본학습false·새native/학습0유지. 이번출처조사로204소프트웨어검사새실행0,생산소스/기존역할불변을별도확인한다.
- 다음독립작업은기존우선순위3 Oliveira architecture/N두연구의실험중복·pot/plant단위·수분기준대조. 현장후보공백은새공개근거시후속하며같은파일을전체프로토콜로다시세지않는다.

## Kenya 분석대상·오차범위 교차대조 및 원논문 연결 완료 (2026-11-07)

- 원논문DOI10.1016/j.eja.2026.128364/PIIS1161030126003837의출판사검색색인Dataavailability가현재Mendeley자료를직접연결함을확인했다. Crossref공식제목/저자/DOI대조,권호2027-01·CCBY라이선스시작2026-10-07은다른필드로보존했다. 본문HTML403,공식Crossref연결XML은HTTP200/2083bytes이나coredata만있어전문확보false다.
- primary/season-specificEMM189행의평균검토차이0이나SE189개모두차이,df69차이. 대응대비126행의점추정차이0이나SE126차이. primary146대비방향을자기모형평균차이와대조해차이0확인,EMM독립SE공식으로대비오차교체0. cross-site잔사30행은별도모형결과로분리하고독립관측추가0이다.
- Machanga곡실/HI는생산SR09/LR10두시즌만포함한다. 제외LR09/SR10/LR11은54포장-시즌/실패53/곡실있음1로실패요약에존재하므로조건부평균을전체수익/실패율로사용하지않는다. 원모형적합행수복구나미공개원수량0대체0이다.
- 출처취득 `outputs/runs/20261107T012059Z_kenya_protocol_sources_72dfbf08/verification.json`,공식XML응답 `outputs/runs/20261107T012133Z_kenya_linked_fulltext_e59c8d07/verification.json`,범위명세 `outputs/runs/20261107T012319Z_kenya_estimand_crosswalk_af9712d0/verification.json`,상세 `docs/KENYA_ESTIMAND_CROSSWALK.md`.
- 우선순위 `outputs/runs/20261107T012446Z_agronomic_input_priorities_599e72ba/verification.json`,준비상태 `outputs/runs/20261107T012446Z_readiness_d1dddb67/readiness.json`. 활성10연구/28처리/16대비·정량0개·연구/본학습false·새native/학습/입력할당0유지. 생산소스불변확인,기존204검사를새실행으로표시하지않는다.
- 다음:공식Kenyatta저장소Ngetich학위논문/현장프로토콜파일확보,동일실험/전체시즌·품종·관리·AquaCrop보정노출/수량보정기준대조. 공식기록발견(334fc540-fd9b-4812-9920-6d116dbfe558)이나이번웹열람timeout·파일미취득,저자/지점중복만으로수치전송하지않음.

## Kenya 공개CSV20개 확보·원자료 범위/산술 감사 완료 (2026-11-07)

- DOI10.17632/tdw54wgvbf.1의공식익명API에서root/data폴더목록과CSV20개/2538행취득완료,파일별크기/저장소SHA256대조. README는페이지설명과달리이번반환목록에없었으며부재주장은확인범위에한정한다. 원CSV수정/기상복원/값채움0.
- 01포장날짜/집계강우90행과02처리강우12행을분리했다. 범위는KiamaogoLR10/LR11각27·MachangaLR10/SR09각18로전체10site-season의원자료가아니다. 90recordID고유/날짜역전0,동일물리포장5시즌의종속성은유지하고season별새독립실험으로세지않는다.
- 수량표는Corrected grain yield추정주변평균/SE등의적합모형출력이며포장별원곡실수량아님. 03–17/19–20의반복/season-specific/productive-season/cross-site결과를새관측으로합치지않는다. 전체일별기상/토양·초기상태/품종계수/관리/수분보정기준미확보로정량실행자격0.
- 강우48지표/12파종범위·실패75그룹분모/비율·대비602행estimate/SE=t·공분산18모형최소값선택산술검토차이0. 실패요약225포장-시즌/53실패는독립포장수나해충피해량이아님. AIC/BIC선택은6모형에서다르므로원선택/민감도를보존하며모형재적합/농학검증으로표시하지않는다.
- 취득 `outputs/runs/20261107T011325Z_kenya_public_dataset_f18ec4ef/verification.json`,감사 `outputs/runs/20261107T011553Z_kenya_input_audit_4f7c8ce1/verification.json`,상세 `docs/KENYA_INPUT_AUDIT.md`. 우선순위 `outputs/runs/20261107T011714Z_agronomic_input_priorities_bf911dc1/verification.json`,준비상태 `outputs/runs/20261107T011714Z_readiness_5e054a38/readiness.json`.
- 활성10연구역할/28처리/16대비·정량0개·연구/본학습false·새native/학습/입력할당0유지。출처조사로기존204검사새실행0. 최종 `scripts/qualify_kenya_input_audit.py`는20원파일SHA/75실패비율유리수산술·생산소스/레지스트리불변·이전폴더빈상태를검사하고release근거를남긴다.
- 다음:primary/season-specific/productive-season응답대상·오차범위교차표및원프로토콜/수분보정/누락원곡실·전체입력의공개연결확인. Iran/Nebraska/LIRF공백은유지한다.

## Iran 원출처 연결·주석 기반22입력명세 완료 (2026-11-07)

- DataCite공식등록JSON확보·SHA대조. Dataset/상위DOI IsVersionOf1건만있고Mendeley related_links/DataCite relatedItems에원논문연결없음. 영어/페르시아어검색의사료용옥수수모의논문단서는저자중복만으로현재실험에연결하지않고지역/품종값전송0,색인직접취득403을보존했다. 원논문부재주장아님.
- XLSX workbook→sheet→comments관계로주석16개를회수했다. 2014파종G5=7/15·관비6일/수확G125=11/13,2015파종G5=7/4·관비5일/수확G139=11/15를명시적주석으로연결했다. G9/H9관비주석2개는1관리행으로유지해15고유행(파종2/관비11/수확2)이다. 원본수정0·비료회차량/제품null·균등배분0·native입력할당0.
- 2014주석파종→수확경과121일vsDAP120/요일불일치,2015경과134=DAP134이나요일불일치유지. 날짜/DAP자동교정0. 기존숫자관수100행(2014:45,2015:55)은검출요일불일치구간밖이며DAP도있음. 관수행전체를충돌로확대하지않되전체달력/효율/일정자격은여전히미확정이다.
- 22입력명세:출처보고2·부분7·충돌1·미해결11·미지원1. 숨김시트/embedded객체/외부link/관계/definedNames0확인. No/N0별칭추정·R블록/연도연결·전체토양/기상/초기물N/품종/시비형태·배분/계측프로토콜공백을유지한다.
- 취득 `outputs/runs/20261107T005307Z_iran_protocol_link_sources_908cd3bd/verification.json`,명세 `outputs/runs/20261107T005540Z_iran_protocol_dossier_3687b1a6/verification.json`. 상세 `docs/IRAN_PROTOCOL_DOSSIER.md`. 통합우선순위 `outputs/runs/20261107T005653Z_agronomic_input_priorities_64e16634/verification.json`,준비상태 `outputs/runs/20261107T005654Z_readiness_3c8f63b5/readiness.json`.
- 기존10연구역할/28처리/16대비·정량0개·연구/본학습false·새native/학습0유지. source-only작업으로204검사새실행0,생산소스불변을별도확인한다. 최종 `scripts/qualify_iran_protocol_dossier.py`에서openpyxl독립주석16개/원셀/관리행중복/해시/레지스트리/이전폴더빈상태를검사해release근거보존.
- 다음:Kenya후보DOI10.17632/tdw54wgvbf.1의공개파일목록/실제자료확보. Iran외부프로토콜/회차량/달력및Nebraska/LIRF공백은대기로계속추적한다.

## Iran관수×N 실제 원자료 확보 및 입력 감사 완료 (2026-11-07)

- DOI10.17632/6zj7pzftwg.1의공식페이지가참조한클라이언트에서익명API경로/헤더/페이징을확인했다. snapshotV1/비기밀·폴더0·파일1개,Field Data.xlsx60147bytes취득·저장소SHA256일치. loading빈목록을부재로간주하지않은후속으로실제파일확보완료다.
- 수확36행=2년×6처리×3반복,12그룹의평균/표본SD를출처셀과연결했다. 건물구성36항등식/IWP72원수식·캐시/관수4합계산술통과. Growingseason은3반복평균이므로원행추가0,원No라벨을N0로자동치환하지않고블록/연도연결·대비SE미확정유지.
- 2014관수M1/M2일별합822.4834567901/852.1333333333mm,2015는765.2787379973/775.8008230453mm로수확적용량m3/ha÷10과일치했다. SUM꼬리표중복계산0·빈값0대체0·gross→native관수선택0이다.
- 달력진단:2014날짜행122개,10/31공백·요일13불일치·date-DAP기준일2후보;2015날짜행136개/공백0이지만요일29불일치. 파종일/원날짜자동교정0.0–60cm3구간204대상셀/198수분숫자확인하되처리·반복·중량법→용적%변환·초기물자격미확정이다.
- 전체일별기상/전체토양·초기N/품종계수·보정노출/파종밀도/비료형태·분할일정/계측·수확프로토콜미확보. snapshot관련링크없음·현재검색범위에서정확한원논문미식별은논문부재주장이아니다. No/N0·R계층·달력도추가확인이필요하다.
- API발견 `outputs/runs/20261106T235213Z_iran_public_api_discovery_0c8dd185/acquisition.json`,취득 `outputs/runs/20261106T235323Z_iran_public_dataset_d683006d/verification.json`,감사 `outputs/runs/20261106T235624Z_iran_input_audit_d9e85922/verification.json`. 상세 `docs/IRAN_WATER_N_INPUT_AUDIT.md`.
- 통합우선순위 `outputs/runs/20261106T235759Z_agronomic_input_priorities_362e5889/verification.json`,준비상태 `outputs/runs/20261106T235800Z_readiness_5c48cbfa/readiness.json`. 활성10연구역할/28처리/16대비·정량0개·연구/본학습false·새native/학습0유지。원본/수식재계산0. 이번자료감사는204소프트웨어검사를새실행한것이아니다.
- 최종검사는 `scripts/qualify_iran_input_audit.py`로Decimal12그룹/4관수합·달력원셀·소스/레지스트리불변·이전폴더빈상태를검사해release근거를보존한다. 초기에읽기전용EmptyCell에서행번호를얻으려던파서오류는실제값셀의행번호로수정했고원자료는변경하지않았다.
- 다음:원논문/공개프로토콜연결과날짜-DAP-요일·No/N0·R블록대응의해소가능성점검및전체입력공백명세. 정량보정실행은계속차단하고Nebraska/LIRF대기도유지한다.

## Nebraska 참조·부록 접근 및 부분집합 경계 점검 완료 (2026-11-07)

- Schmer2020/Sindelar2019a의대학/USDA공식HTML각2개와Li대학HTML1개,총5파일을보존·SHA대조했다. 대학이명시한참조PDF2개는403이며실제취득0,Li부록payload미확보다. 전문/입력확보완료가아닌공개접근점검완료로기록한다. 접근우회·외부연락0이다.
- Schmer전체실험은2011–2018/N125·200/manure·cover·control을포함하나현재Li8처리부분집합은N200이다. N흡수관측과N투입량반응대비를구분하고N반응보정자격을부여하지않았다.2010범위연결미확정,같은포장연구를신규독립연구로집계하지않음.
- Sindelar초록의관리후5/6년수리값·56%잔사제거를2010초기토양이나Li약59%로통합하지않았다. 정확층별토양/관리/품종·기존SD/N요약차이·관수실험단위의미는계속미확정이다.
- 최초linked_resources목록이초록content를URL처럼포함한문제를확인했다. 다운로드실행0이며원실행은보존하고실제href만읽는새목록으로한정했다. 수집스크립트에URL형식/HTML엔티티조건을보완했다.
- 취득 `outputs/runs/20261106T234559Z_nebraska_reference_sources_3fd38462/verification.json`,점검 `outputs/runs/20261106T234731Z_nebraska_reference_access_audit_aa4e4f99/verification.json`. 상세 `docs/NEBRASKA_REFERENCE_ACCESS.md`.
- 통합우선순위 `outputs/runs/20261106T234824Z_agronomic_input_priorities_39839233/verification.json`,준비상태 `outputs/runs/20261106T234824Z_readiness_24eb6d85/readiness.json`. 활성10연구역할/28처리/16대비·정량0개·연구/본학습false·새native/학습/입력할당0유지. 이번변경은출처조사/메타데이터이며기존204검사를새재실행결과로표시하지않는다.
- 다음: Iran관수×N DOI10.17632/6zj7pzftwg.1의공개파일목록과실제payload확보. Nebraska전문/부록/출처불일치해소는대기로추적한다. 같은거부링크반복대신다른공개후보의입력자격을우선확인한다.

## Nebraska 원자료·요약표·입력 자격 감사 완료 (2026-11-07)

- USDA 공식 원논문13쪽 확보·SHA고정,방법2/3쪽과 불확실성4쪽 렌더링 대조. 0%수분 건물·4반복 분할-분할구·연도반복측정·UAN200kgN/ha/V4–V6를 확인했다. XLSX A/N↔논문 M/R 처리 의미 대응과17입력명세를 기록했다.
- 4목표값×72연도/처리=288조합 원자료/요약표 대조. 곡실·건물평균은 산술 검토 범위 내 일치하나 SD각9건 차이. 곡실N평균1건/SD9건,지상부N평균9건/SD17건 차이. 원자료/요약값을 덮어쓰거나 SD를 SE/검증 허용오차로 승격하지 않았다. 설계상288칸 대비 공개271행으로17칸 미확보(2010년16/2018년1),32ID의 처리 일관성은 확인했으나 블록 계층 매핑은 미확정이다.
- 강수13문자열 날짜를 원헤더 DD/MM/YYYY로 진단 해석해3287일(2010–2018)중복/공백0확인. 원본 수정0,전체 기상 입력 확보로 간주하지 않음. 관수1344숫자행=336고유 날짜/처리/양/방식×각4회 확인,cm→mm변환을 진단 후보로만 보존했다. 빈량1904/빈날짜32미보정·네이티브 일정 선택0이다.
- RZWQM2의FXR/워크북FXN보정노출을 확인했다. 나머지 처리를 별도 독립 연구로 세지 않음. 전체 층별토양/초기물·N/일별기상/파종·관리/품종계수 미확보,본문토양Table1참조 불일치와 출판사403유지. 원 SD 차이 설명은 미해결이다.
- 출처: `outputs/runs/20261106T233714Z_nebraska_paper_384ae31b/verification.json`. 감사: `outputs/runs/20261106T233953Z_nebraska_input_audit_fd40b2ec/verification.json`. 상세: `docs/NEBRASKA_INPUT_AUDIT.md`. 기존10연구 역할·정량0개 유지,새native/학습/입력할당0·연구/본학습false다.
- 소프트웨어204검사 실패/오류/건너뜀0: `outputs/runs/20261106T234122Z_unit_regressions_5e7244f0/verification.json`. 통합우선순위 `outputs/runs/20261106T234132Z_agronomic_input_priorities_98dc477c/verification.json`,준비상태 `outputs/runs/20261106T234133Z_readiness_37151f19/readiness.json`. 별도 최종 검사는 `scripts/qualify_nebraska_input_audit.py`로 원SD차이 Decimal산술/원본해시/역할·게이트/이전폴더빈상태를 확인하고 release 근거를 보존한다.
- 다음 완료 지점: 공식 부록 및 Schmer2020·Sindelar2019a 공개 원문/입력에서 관리·토양·품종 보정 이력을 확보하고 SD/실험단위/관수 의미의 해소 가능성을 판정한다. 정량 보정은 그 전까지 차단한다.

## 별도 현장 건조곡실 보정자료 1차 선별 완료 (2026-11-07)

- 외부3후보(Nebraska/Iran/Kenya)와 기존LIRF확장1단서를 분리했다. Nebraska 공식 XLSX 1개를 취득해 저장소MD5·SHA256을 고정하고 읽기 전용 검사했다. 원본 수정/날짜·빈값 자동 대체0건이다.
- Nebraska 건조곡실271행·72연도×처리 그룹을 확보했다. 그룹 n1~4를 설계상 독립 반복으로 확정하지 않았다. 관수 빈값·혼재 날짜·일별기상/토양/초기/관리/품종 계보가 미확정이다. 수확 후 잔사 제거를 생육 중 잎 피해/회복 자료로 대체하지 않는다.
- Mendeley2후보는 메타데이터만 취득했다. 파일 목록 loading을 파일 부재로 해석하지 않았다. LIRF2008–2024 새 저자기록은 기존 연구 중복으로 추적하고 원문403/실제 통합파일 미확보를 기록했다. 이전12파일 부재 주장의 적용 범위를 확대하지 않는다.
- 근거: `outputs/runs/20261106T232619Z_field_calibration_candidates_9542cf1f/verification.json`, `outputs/runs/20261106T232859Z_field_calibration_screen_6e56601b/verification.json`. 상세: `docs/FIELD_CALIBRATION_CANDIDATE_SCREEN.md`.
- 기존10연구 역할/28시나리오/16대비 유지, 활성 추가0·정량 준비0·연구/본학습false·native/학습0. 제2작업은 입력 자격 검토 진행 중이다.
- 소프트웨어204검사 실패/오류/건너뜀0: `outputs/runs/20261106T233007Z_unit_regressions_c46dd35c/verification.json`. 준비상태: `outputs/runs/20261106T233307Z_readiness_6b058457/readiness.json`. 최종 셀/그룹 산술·해시·역할불변·이전폴더 빈상태 검사는 `scripts/qualify_field_calibration_screen.py`로 별도 release 근거를 남긴다.
- 다음 완료 지점: Nebraska 원자료–요약표의 평균/오차·실험단위·날짜/빈값 의미 및 원논문/모형 입력·보정 이력 자격을 확정한다. 새 LIRF 통합 데이터 공식 위치와 Mendeley 공개 파일 목록은 별도 후속이다.

## Oveysi2010 현장 재현입력 명세 완료 (2026-11-07)

- 고정원문6쪽·방법2/3쪽렌더링을대조해위치/기간/SC704/재식/토양/밀도/물특성/초기상태/계측/관수/계절량/N/피해/수량/설계/기상/기후기준17항목연결.14항목은부분정보/미확정유지.보고값과재현입력선택을분리해자동할당0.
- 파종2007-05-20/2008-05-30,밀도7plants/m2·열75cm·파종5cm·수확3.5m2확인.수확9/30의연도·시즌표기연결미확정.토양FC38%/WP18%는스칼라로만보존,가용수분75/25%기준→용적수분33/23%산술확인.관수7500/6000m3/ha→750/600mm이나일별일정아님.
- 밀도1.63g/cm2인쇄단위확인/자동g/cm3교정0.전체층·SAT/전도도·초기수분/무기N·SC704계수/계보·센서원자료/오차부재.25°CWatermark회귀R2.82를오차로대체하지않음.장기1978–2008기상을실험연도일별로사용하지않고기후본문/표의기준차이유지.
- DAP/urea각최대200kg/ha→보고N36+92=128기준이실제적용될경우에만32/64/32kgN/ha분할.원문maximum한정과제품별배분/날짜미확정반영.원수량10공동평균/8대비·3블록splitplot·독립역할유지,20연도셀/n6/SE역산0.
- 명세 `configs/oveysi2010_input_dossier.json`;근거 `outputs/runs/20261106T231818Z_oveysi_input_dossier_2283981d/verification.json`.우선순위첫작업명세완료/정량실행차단,다음별도현장건조곡실보정자료선별로갱신.통합근거 `outputs/runs/20261106T231934Z_agronomic_input_priorities_e045fb29/verification.json`.
- 204검사 실패/오류/건너뜀0: `outputs/runs/20261106T231934Z_unit_regressions_ef11aa9d/verification.json`;준비상태 `outputs/runs/20261106T231955Z_readiness_fabe51a3/readiness.json`.최종원문SHA/조건부산술/원평균·역할불변/이전Documents빈상태 `outputs/runs/*_oveysi_input_dossier_release_*/verification.json`.
- 신규native/학습/튜닝0·전체10연구정량가능0개·연구/본학습false.상세 `docs/OVEYSI2010_INPUT_DOSSIER.md`。다음:기존독립자료를보정전환하지않는별도현장건조곡실보정자료선별.

## 공개10연구 재현입력·검증경로 통합우선순위 완료 (2026-11-07)

- 기존출처근거로10연구×8항목(목표값/오차/토양초기/기상/관리/품종계보/피해/독립성)80상태와현용도·핵심공백·다음조치정리. 상태를품질점수/준비완료로쓰지않음.공개접근재시도·새자료취득0,역할변경0. 기존28시나리오·16대비를실제등록코드로재확인.
- 후속5작업:1Oveysi독립원문입력명세,2별도현장건조곡실보정자료선별,3Oliveira두연구실험중복/단위,4온도발육/생존제약추출,5조건부자료/외부공백보존.첫완료조건은값+쪽/셀또는명시결측의입력명세이며정량실행허용아님.
- 통합중계보검사가independent_validation…만인식하는역할명범위누락발견.모든independent_…로확장/회귀추가해외적타당성·초기/반복피해·N반응포함6역할모두검사.6연구현재계보미자격은필요근거미충족의뜻이며논문들이서로종속됐다는단정아님.
- 설정 `configs/agronomic_input_priorities.json`;근거 `outputs/runs/20261106T151837Z_agronomic_input_priorities_8e4335a1/verification.json`.204검사 실패/오류/건너뜀0: `outputs/runs/20261106T151838Z_unit_regressions_8b1cd7f5/verification.json`.준비상태 `outputs/runs/20261106T151953Z_readiness_3e953cc2/readiness.json`에설정경로/SHA연결.
- 최종80상태/원근거SHA/이전역할불변/6역할/이전Documents빈상태: `outputs/runs/*_agronomic_input_priorities_release_*/verification.json`.신규native/학습/계수채움0·정량가능0개·연구/본학습false.상세 `docs/AGRONOMIC_INPUT_PRIORITIES.md`.
- 다음:Oveysi2010의원문기반현장재현입력명세.독립결과로계수/임계값튜닝하지않고수치오차·품종·일별입력등공백을확정한다.

## Fang2014 계보 추적·근거 고정 독립성 검사 완료 (2026-11-07)

- DOI10.2134/advagricsystmodel5.c1과USDA기록308258/요약확인.2008–2011관수처리보정은기술되지만장원문/계수표/선택동결이력미확보.출판사HTTP403·목록PDF URL404보존,원문계수null.공식NAL Handle은200응답의도서관카탈로그HTML로연결,PDF미취득.접근우회/전세계부재주장없음.
- Zhang2021원문표5의초기/최종6계수를패키지와대조.각3/6정확일치하나서로일치키가달라전체행일치0.열별일치값조합/계수교체없음.같은현장후년자료를새연구로등록하지않고후년200cm오차를2008상부오차로옮기지않음.
- 새validation_lineage.py를준비상태보고서에연결.독립검증예정연구는레지스트리boolean3조건+작업폴더내근거/SHA/연구ID/보고서계보·독립성확인을요구.실제LIRF미확정거부,레지스트리만true로바꾸어도부정근거덮어쓰기거부.양성fixture는이단일문턱만통과하며전체연구게이트는false유지.
- 신규4검사최초시스템tmp sandbox권한오류는기존작업폴더tmp격리로수정.전체203검사 실패/오류/건너뜀0: `outputs/runs/20261106T150107Z_unit_regressions_152dae62/verification.json`.준비상태: `outputs/runs/20261106T150245Z_readiness_9e5411d4/readiness.json`.
- 취득/실패: `outputs/runs/20261106T145526Z_fang_lineage_sources_00e0e4ee/verification.json`;NAL: `outputs/runs/20261106T150207Z_fang_handle_followup_2b58cca2/verification.json`;감사: `outputs/runs/20261106T150015Z_fang_lineage_audit_0ab94133/verification.json`.
- 최종SHA/부정계보표시/위조SHA음성대조·이전Documents빈상태: `outputs/runs/*_fang_lineage_release_*/verification.json`.연구/본학습false·10연구정량준비0개·신규native/학습/계수교체/split변경0. 상세 `docs/FANG_LINEAGE_FOLLOWUP.md`.
- 다음:공개10연구의재현입력·측정오차·보정/독립역할통합우선순위정리.정확계보미확보를기록된외부근거공백으로유지하고실행가능한외부검증경로를선정한다.

## LIRF 품종계수·보정노출·독립검증 역할 감사 완료 (2026-11-06)

- 패키지045/native기본048/Saseendran2015/Fang2017초기·최종의5종6계수비교. 패키지와Fang초기3/6정확일치,나머지P2/G2/PHINT차이보존. 유사성으로계보/품종동일성추론없음. 뒤244.6/43.07미매핑유지.045기술수용과048농학이식성구분.
- 메타데이터가Ma2012를IsSupplementTo로참조함을확인.기간2008–2011표기와실제2008T1 ACE1실험/16행구분. Ma2012물리2쪽렌더링은다른2008처리/2009·10평가후재보정절차를확인,그노출범위를손대지않은독립test로보지않음. 정확패키지계수가그절차의어느산출물인지는미확정.
- Saseendran2015:2008최대관수량보정·나머지2008및2009–11검증으로기술하나결과합산,계수는패키지와다름. Fang2017:2012·13양극관수처리보정/나머지평가,초기계수는같은현장2008–11/지역연구참조.같은현장추가연도/논문을새독립연구로등록하지않음.
- 계획상전체연구holdout유지/보정전환0. 역할계약conditional_candidate_not_qualified·independent_validation_allowed=false명시. 정확계수의보정자료/목적함수/선택이력/동결시점은미발송명세에추가. 계수선택·모형오차임계값선택없음.
- 원문취득: `outputs/runs/20261106T144434Z_lirf_calibration_sources_a5f2fc47/verification.json`;감사: `outputs/runs/20261106T144720Z_lirf_calibration_provenance_94510be8/verification.json`.199검사실패/오류/건너뜀0: `outputs/runs/20261106T144849Z_unit_regressions_72e11b1e/verification.json`.준비상태: `outputs/runs/20261106T144929Z_readiness_cd053a37/readiness.json`.
- 최종전사/SHA/역할일치/이전Documents빈상태: `outputs/runs/*_lirf_calibration_provenance_release_*/verification.json`.신규native/학습·원계수교체0·연구/본학습false·10연구정량준비0개.상세 `docs/LIRF_CALIBRATION_PROVENANCE.md`.
- 다음:계보단서Fang2014원문·공개보정기록대조,정확패키지이력미확보시미확정유지. 검증역할을모형결과의적합도로선택하지않음.

## 일별 포장수분·계측/보정자료 가용성 점검 완료 (2026-11-06)

- 공식목록12종의파일ID를기존11종과대조하고누락PhotoLog18쪽확보. 공식카탈로그HTML·USDA공개Saseendran2015논문도별도SHA보존. Photo8(물리9쪽)의NMM/TDR사진검토,보정잔차수치로대체하지않음.
- 원XLSX10개/60시트·주석228개대조,숨김시트0.수분출처관련69주석/초기예측SWD관측추세맞춤36주석분리.2010FC헤더24주석은실제SeasonalFC와불일치하여미확정출처로보존·교정0. T2/T3 E57:H57/AD57설명주석0으로두차이유지.
- 특수8파트는기상4파일의connections/queryTable로GLY04_CLEAN.csv작성자PC로컬참조.새로고침/로컬경로탐색0.계측자료추가확보로간주하지않음.원본파일·사전·방법/계측사진·공식목록확인범위에서일별개별포장SWC·보정쌍원자료·일별오차공분산미확보.전세계부재주장없음.
- `docs/LIRF_MISSING_DATA_SPEC.json`에필드/단위/날짜/깊이/식별자·오차필요항목정리,미발송·연락0. 정적FC변동/모형RMSE/R2를일별계측오차로대용하지않고모형임계값null 유지.
- 취득: `outputs/runs/20261106T143430Z_lirf_availability_sources_018e2462/verification.json`;최종조사: `outputs/runs/20261106T143732Z_lirf_data_availability_cb685664/verification.json`.199검사실패/오류/건너뜀0: `outputs/runs/20261106T143925Z_unit_regressions_134e191c/verification.json`;준비상태: `outputs/runs/20261106T144001Z_readiness_a125694d/readiness.json`.
- 최종원SHA/댓글·시트/연결독립확인·이전Documents빈상태: `outputs/runs/*_lirf_data_availability_release_*/verification.json`.신규native/학습/입력교체0·연구/본학습false·정량가능0개. 상세 `docs/LIRF_DATA_AVAILABILITY.md`.
- 다음:확보모형패키지/관련논문의품종계수·보정대상연도·검증split근거대조. LIRF독립검증후보역할의조건확정,동일현장/연도를새독립연구로세지않음.

## 포장 FC 집계·수분 비교 계약 완료 (2026-11-06)

- 96포장×7깊이672FC값을수량표의연도/처리/블록/포장과연결. 평균/표본SD168쌍재구성,104쌍은1e-10%p내정확일치.2010/2011년84쌍전부일치.2008/2009평균차이최대.05/.026585%p,SD차이최대.033730/.028999%p를보존하고반올림원인확정/원표교체없음.
- 2010-07-01 T2/T3는포장FC에서직접계산해도SWD잔차−1.392802/−1.574002mm 유지.전후실관측6/25·7/6은정밀도내일치. FC요약집계로설명되지않으며일별포장SWC/상류식부재로오류셀식별0·행삭제/교정0.
- 상부105/135cm×24처리48개정적FC저장량요약:포장깊이짝을유지해SD/조건부SE·깊이공분산분산산출.일별SWC·변화량·모형잔차오차로대용하지않음. 비교계약에중첩깊이/반복측정비독립·전체연구split·일별ETc조정모형추정값한계·오차임계값null·모형점수불허명시.
- 근거: `outputs/runs/20261106T142730Z_lirf_fc_aggregation_b33c4f08/verification.json`. 검사199개 실패/오류/건너뜀0: `outputs/runs/20261106T142835Z_unit_regressions_aecf4216/verification.json`. 준비상태: `outputs/runs/20261106T142849Z_readiness_2147e1a5/readiness.json`.
- 최종원셀/Decimal평균·표본SD/쌍차이분산항등식·원SHA/이전Documents빈상태: `outputs/runs/*_lirf_fc_aggregation_release_*/verification.json`. 신규native/학습·원자료/기본입력변경0.공개10연구정량준비0개·연구/본학습false. 상세 `docs/LIRF_FC_AGGREGATION.md`.
- 다음:보유공개자료의일별포장수분·계측오차·보정이력가용성확인과입력해결/외부근거필요항목분리.2건원인을추측해교정하거나FC변동으로검증오차한계를만들지않음.

## 연도별 수분 깊이·산출식 대조 완료 (2026-11-06)

- 2008–2011×6처리24시트와Seasonal FC헤더·설명문·방법PDF8/9/10페이지를 대조. 전24시트에서하부135–165/165–200cm vs설명135–175/175–225cm충돌 유지. 방법문서의NMM대표반경·측정위치는최종하부층정의를확정하지못함.
- 공통상부0–105/0–135cm 각각633개후보를 원수분셀·날짜·처리와연결.2008/09/10/11 각각144/183/132/174처리관측일. 두깊이는같은자료의중첩구간으로1,266독립반복으로세지않음. 4반복처리평균/오차미확보·점적관열측정/1차원모형한계 유지.
- 날짜별수분/AD/AF관측영역 수식0개, 저장값으로분류. 다른ET수식과구분. FC열이2010/11에달라헤더로찾고처리번호검사. FC−상부SWC vsAD599건 중표시정밀도산술한계0.57500001mm 밖2건:2010-07-01 T2AD57 −1.392802/T3AD57 −1.574002mm. 원자료역산/수정·행삭제없이미해결보존.
- 최종근거: `outputs/runs/20261106T142102Z_lirf_water_depths_5a3fa17b/verification.json`. 검사196개 실패/오류/건너뜀0: `outputs/runs/20261106T142159Z_unit_regressions_b66a7d50/verification.json`. 준비상태: `outputs/runs/20261106T142224Z_readiness_b3e1358b/readiness.json`.
- 독립원자료셀/Decimal저장량산술·원SHA·이전Documents빈상태: `outputs/runs/*_lirf_water_depths_release_*/verification.json`. 신규native/학습/입력교체0. 연구/본학습false·10연구정량준비0개 유지. 상세 `docs/LIRF_WATER_DEPTH_AUDIT.md`.
- 다음:2010년두불일치행·포장별FC의처리평균집계근거대조, 상부수분후보의비교범위·반복단위·불확실성계약정리. 미해결깊이와초기일/품종/토양한계유지.

## D22 수분특성·밀도·초기 상태 매핑 완료 (2026-11-06)

- 기존8개 토성층 중 압력판4층의6압력×평균24값과 기술표본42값을 원 셀/수식과 연결.35.56–58.42cm층은표본1개로SDnull 유지, 포장반복으로 집계하지 않음. θ1500표기/설명1475kPa·체적함수·disturbed sample 구분, 추정SWC/측정/현장FC를 분리.
- 측정구간0–25.4/35.56–58.42/58.42–91.44/154.94–182.88cm는200cm중109.22cm(54.61%)를 덮음. native10층 중4층의 기하학적 전범위와 수리특성 검증을 구분. 미측정90.78cm를 보간/외삽하지 않았고LL/DUL/SAT선택0.
- D2밀도7깊이의2008–2015통합 평균/SD/n보존,2008개별D22지평에 미배정. 현장FC는같은포장다른위치·기간이며 설명의2007–2014평균/5년평균차이 유지. 토양표2007제목/2007·08특성조사를2008개별관측으로 바꾸지 않음.
- 최초완전수분6/10T1평균4반복 vs초기일1/1, N기록5/10 분리. 처리표J/K헤더135–165/165–200cm vs설명135–175/175–225cm 충돌발견. 조건부저장량339.327047mm(200cm)/378.424056mm(225cm)를각각보존하되해석선택0·서로다른깊이를오차로판정하지않음.
- 원장근거: `outputs/runs/20261106T141032Z_d22_hydraulic_mapping_4797116e/verification.json`. 검사192개 실패/오류/건너뜀0: `outputs/runs/20261106T141132Z_unit_regressions_f622b3a0/verification.json`. 준비상태: `outputs/runs/20261106T141149Z_readiness_5297e156/readiness.json`.
- 최종 원자료 셀/SHA/범위산술·이전Documents빈상태: `outputs/runs/*_d22_hydraulic_mapping_release_*/verification.json`. 신규native/학습/기본이미지·정책입력변경0. 공개10연구·정량가능0개·연구/본학습false 유지. 상세 `docs/D22_HYDRAULIC_MAPPING.md`.
- 다음: 방법 문서·연도별 수분 시트의 깊이 정의와 산출식을 대조, 충돌의 연도/시트 범위 확정. 해결 전 두해석을선택하지않고공통상부범위비교가능성을검토.

## LIRF 온도 정의·native 전달·민감도 진단 완료 (2026-11-06)

- WTH AMP→IPWTH TAMP→WEATHER 전달의 배율1 및 METMP D 기본 STEMP의 계절항1/2를 소스9파일 SHA/행으로 확인. Climate 파서도 직접 읽지만 WGEN 실행은 미검증, 과거 문서 정의 차이는 유지. MESOL2를 온도 모듈 선택과 혼동하지 않음.
- 사전 지정5조건(누락/명시20·5/TAV만8.58/AMP27.16/AMP13.58), 동일토양·일별기상·일정·명시048계수·고정이미지로 실제 실행. 각295일/총1,475일, 온도매개변수10값/기상5,900항목 대조 통과. 누락과 명시기본값의 일별 토양온도 및 PlantGro/SoilWat/SoilNi·수확요약 정확일치, 이전 기본값 궤적도 정확회귀.
- TAV변경 최대층별차이7.5°C, 고정TAV 전체/절반AMP 차이최대2.4°C. 다섯조건 수확일/출력HWAH는 같으나 무영향·현장동등성·정량적합도로 해석하지 않음. 온도 현장 적용값 선택0, RL/PPO/Fortran/기본이미지 변경0.
- 최초진단은 구분 공백을 수치에 채워 AMP첫자리를 잃은 오류를 검출. 원출력을 보존하고 해당실행을 evidence_qualifications에서withdrawn 처리. 소수2자리·구분열 보존으로 수정한5조건 재실행을 최종근거로 사용.
- 최종native: `outputs/runs/20261106T140011Z_lirf_temperature_1d320bb0/verification.json`; 출력/소스감사: `outputs/runs/20261106T140031Z_lirf_temperature_qualification_9dccaaa6/verification.json`. 검사188개 실패/오류/건너뜀0: `outputs/runs/20261106T140136Z_unit_regressions_bec28644/verification.json`.
- 준비상태: `outputs/runs/20261106T140154Z_readiness_003f1e1b/readiness.json`.10연구·정량가능0개·연구/본학습false. 원 SHA/실행컨테이너정리/이전Documents빈상태/최종파일 SHA는 `outputs/runs/*_lirf_temperature_release_*/verification.json`에 보관.
- 다음: D22측정 토양층의 수분특성·밀도·초기상태 대응 가능성을 검토. 온도후보는 진단으로 유지. 상세: `docs/LIRF_TEMPERATURE_PATH.md`.

## 패키지·native 기본값·현장 차이 원장 완료 (2026-11-06)

- 19항목의 출처·현장 측정/가정·기본값·미확정 상태와 후속 조치를 분리했다. 원자료 SHA를 확인하고 자동 값 대체를 전 항목에서 금지했다. 최초 원장의 파종 출처 행과 비료량 필드 표현을 정정한 실행을 최종 근거로 사용한다.
- 2008 T1 block2 D22 한 포장과 site5 토양8층(0–182.88cm)을 연결했다. pH7.57–8.06은 포화반죽 측정이며 native 물 pH 정의와 등가성 미확인. 바닥17.12cm·수리/밀도 매핑은 미완료이며 처리 평균 프로필로 승격하지 않았다.
- 기록된 일평균 기온1,461일의 원출처 셀과 관측소 태그를 보존. 4년 일수 가중 평균8.575459°C, 통합 월평균 차이27.160806°C/절반13.580403°C는 기술 통계다. 장기 기후 평년값 또는 토양온도로 간주하지 않으며 Climate AMP→WTH/native TAMP 정의 연결을 확인하기 전 적용값을 선택하지 않는다.
- 원장: `outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5/verification.json`. 검사185개, 실패/오류/건너뜀0: `outputs/runs/20261106T135314Z_unit_regressions_9a6ec3e4/verification.json`. 준비상태: `outputs/runs/20261106T135324Z_readiness_90cee1f2/readiness.json`. 공개10연구·정량가능0개, 연구/본학습false 유지.
- 신규 native 실행/학습/이미지·Fortran·정책 입력 변경0. 상세: `docs/LIRF_EVIDENCE_LEDGER.md`. 최종 원자료 셀/SHA/이전Documents빈상태 검사는 `outputs/runs/*_lirf_evidence_ledger_release_*/verification.json`에 보관한다.
- 다음: 실제 온도 모듈 경로에서 Climate AMP/WTH TAMP 정의·변환을 확인하고 민감도 범위를 사전 지정. D22 포장 입력은 미측정 깊이·수리 특성·밀도·pH 방법을 해결하기 전 제한 유지.

## 지정F모드 2년 달력·초기화·N 검증 완료 (2026-11-06)

- 기존v2 이미지 유지, 원UFGA0002/IBMZ910014/IB0035·시드123456·두수확률100/0·50/50에서각1년대조+2년연속 총4회 실제F실행 통과. F용2/4처리 배치를 임시실행기로 분리하고둘째해파종83057/최종휴경84029를 명시. Q/기본이미지 실행기를 교체하지 않음.
- F는각처리SDATE를다시읽으므로수확일주소82192/83185와연간경계83029를명시하고실제F수확1982192/1983185·토양초기화다음날을확인. Q관측주소는근거일뿐실제F일치검사없이수락하지않음. 매작물80mm/116kgN·DAP30–34피해.03·v2수확계약통과.
- 2년지원모형N1,468관측/6초기화 통과.100/0 최대N잔차 .009275·최종−.006975·한계 .274851kgN/ha;50/50 최대 .009049·최종−.006749·한계 .274746.1년365일/2년730일의완전출력,4회2,190일SoilCBal산술 및첫해정확회귀 확인. 고정밀경계와출력검사를함께요구하며전체원소C검증은아님.
- 같은입력Q와비교한두조건각731기록시점의기본native상태필드·작물N진단값 정확일치. RNMODE등메타데이터는의도적으로다르며미기록내부상태/다른조건의동등성은주장하지않음.둘째작물초기NO3+1kgN복사본과F자료에Q기대값을주는대조총4개모두거부.
- 네이티브근거: `outputs/runs/20261106T080958Z_multiyear_f_14b2a9ed/verification.json`; 원본SHA/QF대조/음성대조: `outputs/runs/20261106T081232Z_f_mode_output_qualification_e01ed844/verification.json`. 소프트웨어156개 통과: `outputs/runs/20261106T080939Z_unit_regressions_b35512ea/verification.json`.
- 최종근거: `outputs/runs/20261106T081509Z_multiyear_f_release_138b642a/verification.json`; 준비상태: `outputs/runs/20261106T081407Z_readiness_08037df3/readiness.json`. 소유자식/진단컨테이너정리·이전Documents빈상태 확인. Fortran/vendor/이미지/315관측·행동·마스크/PPO설정변경과신규학습0. 연구/본학습false 유지.
- 다음: 다른실패조건의종료/회계와농학재현입력. 원토양F의한시드·두수확률을범용토양F/다른기간·외부입력으로일반화하지않음. 부산물N배분·유기물/mulch·원소C6항목·독립농학한계유지. 상세: `docs/F_MODE_MULTIYEAR.md`.

## F모드 다년 달력·초기화 검증 시작 (2026-11-06)

- F모드는각처리의시작일을다시읽으므로별도4처리배치·명시적둘째해파종/휴경종료일을구성중. Q에서관측한수확일은초기주소근거로만사용하고실제F수확일/연속성을다시확인할예정. 기본이미지·Q경로·본학습게이트는유지.

## 범용 토양2종의 다년Q 모형N 확장 완료 (2026-11-06)

- 공급된 IB00000004 미사질 양토/IB00000010 사질토×곡실/부산물100/0·50/50의4조건. 기존이미지ID `sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98`, Q·시드123456·UFGA기상/IB0035 유지. 조건별1년대조+2년연속 총8회 실제 실행 통과. 초기210cm의층별중간수분·NH4/NO3 .5/.1µgN/g은명시적진단가정이며현장관측아님.
- 각조건 첫수확 및첫1년전체SoilCBal이대조와정확일치. 모든RUN에서토양ID확인, 최초초기화층의수분한계/수분확인. 작물별80mm/116kgN·두수확계약, 2년730일종료출력·4,380일토양C출력산술 및자식/컨테이너정리통과. 다년N2,936관측/2,920일·12개전체토양N초기화통과. 휴경→작물N증가잔차는4조건모두0.
- 최대일별절대N잔차: 미사질양토100/0 .016335·50/50 .016450kgN/ha, 사질토두조건 .009903. 최종잔차절대최대 .005754, 최종출력/binary32한계 .274718–.274891kgN/ha. 한계보다작은오류검출보장은없으므로고정밀수확/잔사경계검사를함께요구.
- 둘째작물초기NO3+1kgN을넣은별도복사본4개모두전체토양N초기화검사에서검출. 원본파일·SHA는보존. 두토양의C:N초기화/mulch제외경고와사질토의최소OC추정경고를유지하며초기화된유효모형상태의회계범위로제한.
- 네이티브근거: `outputs/runs/20261106T080104Z_multiyear_generic_soils_32a3fa7c/verification.json`; 소프트웨어153개재검사통과: `outputs/runs/20261106T080053Z_unit_regressions_c7971904/verification.json`. 선택적입력변환만추가했고기본호출·Fortran/vendor/이미지/315관측·행동·마스크·PPO설정변경없음.
- 최종근거: `outputs/runs/20261106T080432Z_multiyear_generic_soils_release_ec331073/verification.json`; 준비상태: `outputs/runs/20261106T080324Z_readiness_a195111d/readiness.json`.8개실행의원본파일SHA와이전Documents빈상태재확인. 신규학습0, 전체C/독립농학/기본승격/본학습false 유지.
- 다음: F모드의달력·초기화와다른실패조건을별도검증하고실제농학재현입력확보. 현재Q·한시드/기간을다른모드·더긴기간·외부입력으로일반화하지않음. 상세: `docs/MULTIYEAR_GENERIC_SOILS.md`.

## 범용 토양2종의 다년 모형N 확장 시작 (2026-11-06)

- 기존범용 미사질 양토/사질토에2년Q·두수확률을적용하고 첫해대조·초기화·전체지원N원장을확인중. 같은후보이미지와진단전용무버퍼출력을유지하며F/농학/전체C검증과구분함.

## 지정2년Q 통합 모형N 원장 검증 완료 (2026-11-06)

- 기존 완전 출력2년Q 자료를 재사용. UFGA0002/IBMZ910014/IB0035·시드123456·작물/휴경4RUN·곡실/부산물100/0과50/50의두조건. 지원된 토양 유기/무기N·작물N·누적종자/피해/수확/외부손실·전날흡수/고사지연을 연결. 새 시뮬레이션/학습/이미지 변경0.
- 첫 작물 최종 종자 공급/피해/수확 반출은 외부 원장에 보존하고 둘째 작물의 초기화된 카운터를 새 입력으로 더함. 휴경의 오래된 식물 진단을 서 있는 작물로 세지 않음. 초기 DAS0을 포함해1,468재고 관측·1,460일 및6개 전체 토양N 초기화 대조 통과.
- 조건100/0: 최대절대잔차0.009275kgN/ha, 최종−0.006975, 최종한계0.274851. 조건50/50: 최대0.009049, 최종−0.006749, 최종한계0.274746. 한계는 출력반올림/누적손실/binary32 계산에서 유도하고 초기오프셋·잔차맞춤상수 없음. 고정밀수확/잔사 검사도 동시에 요구하며 약0.275kgN/ha보다 작은 누락의 검출을 보장하지 않음.
- 두 해 시비232kgN·네이티브 출아 초기화 공급3.168kgN, 누적피해1.442807kgN/ha. 수확/정의된 부산물N 반출은179.612617/124.165844kgN/ha. 모두 모형 상태/배분 값이며 관측된 조직N이나 피해 회복의 농학 타당성을 뜻하지 않음.
- 각조건에 초기NO3+1kgN, 둘째 작물 시비누락, RNUP+0.1kgN, 첫 작물 종자공급 누락을 넣은 별도복사본8개 모두 검출. 원본 파일을 변경하지 않고 변형본·SHA·거부사유를 보존.
- 근거: `outputs/runs/20261106T075010Z_multiyear_integrated_n_42a66a28/verification.json`; 소프트웨어153개 통과: `outputs/runs/20261106T075036Z_unit_regressions_32ecc80a/verification.json`. 새 합성 테스트의 정확부동소수점 비교 실패를 근사비교로 수정했고 최초 실패도 보존. 기존2RUN 파서는 기본영역을 유지하고4RUN을 명시적으로만 허용.
- 최종 근거 묶음: `outputs/runs/20261106T075349Z_multiyear_n_release_d0d45578/verification.json`; 준비상태: `outputs/runs/20261106T075235Z_readiness_c4ed0c39/readiness.json`. 이전 Documents 빈 상태 확인. F·다른시드/토양/입력·긴기간·전체원소C/독립농학·기본승격/본학습으로 일반화하지 않음. 연구/본학습false 유지.
- 다음: 다른모드·토양·실패 및 외부입력 조건과 실제 농학 재현자료 확보. 원소C6항목은 미확인 유지. 상세: `docs/MULTIYEAR_MODELED_N.md`.

## 4RUN 다년 전체 모형N 원장 검증 시작 (2026-11-06)

- 완전 출력이 확보된 기존2년Q 자료를 재사용해 종자/피해/수확 반출의 연도 간 누적과 휴경→작물 토양초기화를 연결 중. 신규학습/이미지 변경 없이 수행하고 음성 대조로 누락 검출도 확인할 예정.

## 2년Q 잔사 경계·출력 완전성 검증 완료 (2026-11-06)

- 기존v2 후보 이미지 유지, 시드123456·UFGA/IBMZ910014/IB0035·Q모드의 작물→휴경→작물→휴경4RUN. 곡실100/부산물0과 곡실50/부산물50 두 조건에서 각1년 대조+2년 실행, 성공4회. 각 작물 관수80mm/N116kg 및DAP30–34피해.03을 native달력과 대조. F/다른 시드·토양·장기처리량은 미검증.
- 각2년 실행은1984029까지730일, 작물 수확은1982/1983년. 총6개 초기화 경계에서 실제 잔사DM/N 전달 및FOM/FON/mulch 증가 대조. 휴경→다음 작물의 이전HARVRES 재투입0 확인. 두 작물의v2 계약 통과. 첫 수확과 첫1년 전체SoilCBal은1년 대조와 정확 일치.
- 실제 근거: `outputs/runs/20261106T073828Z_multiyear_handoff_479f1d6c/verification.json`. 소유 자식0/컨테이너 정리. 기존2RUN 통합N 함수를 다년 전체N 통과로 재사용하지 않음. 다년 무기/유기N·작물 입력/반출·시점 원장은 다음 작업.
- 첫 시도2회에서는 native상태가 실제종료일에 도달했으나 SoilCBal말미가1년9일/2년7일 누락돼 전체 첫 해 회귀를 거부함. 보존: `outputs/runs/20261106T073608Z_multiyear_handoff_5e834581/failure.json`.
- 이번 진단에만 GFORTRAN_UNBUFFERED_ALL=y 적용, 모든 native상태가 버퍼링 전후 정확 일치.1년365일/2년730일 출력 완전성 및4성공 실행2,190일C산술 대조 통과. 기본 PPO/CPU-GPU 처리량 설정은 바꾸지 않음. 출력/상태SHA: `outputs/runs/20261106T074136Z_multiyear_output_qualification_29bae3c3/verification.json`.
- 이전 범용 토양16실행도 최종휴경9일씩 출력 누락. 기존5,696일 산술은 유효하지만 당시 native_final_cumulative_residual은 마지막 출력값이며 실제 종료일 값이 아님. 원본을 덮어쓰지 않고3개 탄소 감사/릴리스에 qualified 등록: `configs/evidence_qualifications.json`. 현재코드는 last_printed 명칭과 별도 종료일/중간RUN 공백 검사 사용.
- 소프트웨어151개 통과: `outputs/runs/20261106T074326Z_unit_regressions_a70bf999/verification.json`. 최종 근거: `outputs/runs/20261106T074422Z_multiyear_handoff_release_bb4b5456/verification.json`; 준비상태: `outputs/runs/20261106T074256Z_readiness_36b9f3c9/readiness.json`. 이전 Documents 폴더 비어 있음 확인. 신규학습0, 기본 이미지/315관측·행동·마스크 변경0, 연구/본학습false 유지.
- 다음:4RUN 다년 전체 모형N 원장과 휴경→작물 초기화 대조, 다른 실패·F모드/농학 입력 확장. 원소C6항목은 미확인 유지. 상세: `docs/MULTIYEAR_RESIDUE_HANDOFF.md`.

## 다년 잔사 전달 검증 시작 (2026-11-06)

- 기존 Q모드 작물→휴경을2년의 작물→휴경→작물→휴경으로 확장하는 별도 진단 입력을 작성 중. 첫 해 회귀·각 초기화 경계·두 수확을 확인하고, 기존2RUN 통합N 검사를 다년 통과로 재사용하지 않을 예정.

## 원소 탄소 측정 가능성·토양 출력 감사 완료 (2026-11-06)

- 실제 후보 빌드5개 소스의SHA·행 번호·식과 이전 성장 소스 재구성 지문 일치 확인. CARBO는 일일 biomass/PCARB는 잠재 건물 생산량이며 총 원소C 동화·작물 호흡으로 대체하지 않음. 토양FOM/잔사0.4 및 humus0.526은 각 네이티브 회계 가정으로만 제한.
- 측정 계약10항목 등록: `configs/carbon_measurement_contract.json`. 작물C재고·종자C·총동화C·작물호흡C·수확C·피해반출C의6개 미확인 항목을 기록. 임의0/전조직0.4/CH2O비율/잔차맞춤으로 전체C를 완성하지 않음. CO2ED는 토양의 탄소 질량 단위이므로 kgCO2로 오인해12/44를 다시 적용하지 않음.
- 기존 범용 토양 대조/후보16실행·5,696일의 SoilCBal을RUN별로 재구성. 전날 고사물·첫 휴경일 잔사·누적값 초기화를 적용해 모두 통과. 고정밀 incoming residue DM×0.4와 THRC0D/THRC1D16건 대조 및 중복 유입 거부.
- DAYBAL 재구성 최대 오차0.027400kgC/ha, 출력항별 반올림 최대한계0.100050kgC/ha. 당시 마지막 출력CUMBAL −0.0436~0.0175kgC/ha는 토양 출력이며 전체생태계C 통과 판정 근거가 아님. 후속 다년 감사에서 최종휴경9일 누락을 확인해 실제 종료일 값 해석을 철회함. CH4COD는 native plant-consumption으로 비영일 때 생태계 경계를 따로 확인해야 함.
- 근거: `outputs/runs/20261106T072659Z_carbon_measurement_audit_be266830/verification.json`; 소스 식·행·SHA: 같은 폴더 `source_anchors.json`. 소프트웨어147개 통과: `outputs/runs/20261106T072704Z_unit_regressions_36a07178/verification.json`. 새 합성 테스트의 @YEAR헤더 순서 오류를 수정했고 최초 실패 기록도 보존.
- 최종 근거 묶음: `outputs/runs/20261106T072935Z_carbon_measurement_release_61012ee8/verification.json`; 준비상태: `outputs/runs/20261106T072838Z_readiness_01358916/readiness.json`. 신규 시뮬레이션/학습0, 기본 이미지/315관측·행동·마스크 변경0, 이전 Documents 빈 상태 확인. 전체 원소C/농학/본 학습은 미완료 및false 유지.
- 다음: 다른 실패/수확률·다년 잔사 전달과 실제 농학 재현 입력 검증을 계속하며, 미확인6개 원소C 항목의 추가 관측 또는 모델 경계가 정의되기 전 전체C통계를 산출하지 않음. 상세: `docs/CARBON_MEASUREMENT_AUDIT.md`.

## 원소 탄소 측정 가능성 감사 시작 (2026-11-06)

- CERES 작물 건물중/동화물과 토양 원소C 출력을 구분하고 소스 단위·고정 환산·시간 경계를 확인 중. 기존 보존 출력으로 검사하며 신규학습/기본 이미지 변경은 없음.

## v2 범용 토양·깊은 파종 실패 확장 완료 (2026-11-06)

- 기존 후보 이미지ID `sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98` 유지. 공급된 범용 미사질 양토IB00000004/사질토IB00000010에 LL–DUL 중간수분·NH4 .5/NO3 .1µgN/g·210cm의 명시적 진단 초기값 적용. UFGA기상/IB0035품종은 유지하므로 실제 새 현장 재현이 아님.
- 시드123456·무투입/80mm+116kgN·DAP30–34 피해.03·Q/F·곡실100/부산물0의8쌍16회, C모드 날짜관측4회, C모드100cm 파종 실패 대조2회 = 실제22회. 모든8쌍에서 후보 수확 계약·휴경 전달·식물체N·통합 모형N 통과, 작물/기관/수량/N 보고 대조와 후보 정확 일치.
- 통합N2,936관측, 최대 일별 잔차0.012324kgN/ha·최종0.007924kgN/ha. 최종 반올림/계산 한계0.146767–0.146905kgN/ha. 잔차 보정 계수 추정 없음. 기존64조건과 새8쌍의 적용범위를 합쳐 다른 수확률/시드/현장까지 일반화하지 않음.
- 깊은 파종은 두 바이너리 모두1982117일 crop_failure/곡실0, 궤적 일치. 이는 기존 실패 처리의 v2 회귀이며 영개체 정상 수확 계약/다른 실패 원인까지 검증한 것은 아님. contract_applicable=false 유지.
- 네이티브 근거: `outputs/runs/20261106T070340Z_actual_harvest_domain_3ef3f2a6/verification.json`. 독립 입력 대조16실행: `outputs/runs/20261106T070851Z_domain_effective_inputs_6ddaad09/verification.json`. 실제 토양ID·층 수분 한계·실제 FileX 초기수분 확인.150–190cm의 네이티브 분할과 소수 반올림을 처리하되 원본 경계/속성 불일치는 거부.
- 기본 유기물 모듈의 surface mulch효과 제외·C:N10 재초기화, 사질토 최하층OC 최소값 추정 경고를 보존. 초기화된 유효 상태 이후 모형 회계만 검증했으며 물리/농학/원소C 타당성은 통과시키지 않음.
- 최초 입력검사에서 ID_SOIL 헤더 폭이 실제10문자보다 좁은 문제를 수정. 독립 감사의 UTF-8 해독/층 수 동일 가정/중간값 재반올림 오류는 각각 실패 기록으로 보존하고 실제 보존 FileX·네이티브 출력으로 재검사. 소프트웨어143개 통과: `outputs/runs/20261106T071019Z_unit_regressions_4f3e0f1d/verification.json`.
- 최종 근거 묶음: `outputs/runs/20261106T071200Z_actual_harvest_domain_release_762690a7/verification.json`; 준비상태: `outputs/runs/20261106T071108Z_readiness_2129074d/readiness.json`. 진단 컨테이너와 소유 자식 정리, 이전 Documents 폴더 빈 상태 확인. 기본 이미지/정책계약 변경·신규학습0, 연구/본학습false 유지.
- 다음: 전체 원소C의 네이티브 측정 가능항목·단위·미관측 흐름 확정, 다른 실패·수확률/다년 전달 및 현장 재현 입력 확보. 상세: `docs/ACTUAL_HARVEST_DOMAIN_EXTENSION.md`.

## v2 실패·범용 토양 경계 확장 시작 (2026-11-06)

- 기존 후보 이미지ID를 확인하고 변경 없이 사용. 공급된 범용 토양과 파종 실패 입력을 별도 진단 조건으로 구성 중. 실제 농학/다년 검증과 구분하고 실패 사례도 보존할 예정.

## 공통 시즌 기준선 기술 검증 완료 (2026-11-06)

- NoInputPolicy와 공통 평가 경로 구현. 정책 입력은315관측/17마스크만 사용하고 진단 기상/숨겨진 시즌 조건은 기록과 검사에만 사용. 규칙 임계값은 기존 미튜닝0.3/10mm, 제안서N 일정 유지. validation주소0–3의4쌍·실제8시즌 정상 수확, 최종test 미사용.
- 공통 결정 날짜129/123/137/133일의rain/tmax/srad 일치. 각 행동 비용·독립 물/질소/살포 합계·raw보상 합계·최종 수량수익을 대조. 제약 위반0, 행정 truncation0, 종료 후 소유한 live 자식 프로세스0·진단 컨테이너 정리 확인. 시나리오 발생일을 정책 사이에 강제로 동기화하지 않음.
- 실제 근거: `outputs/runs/20261106T065651Z_baseline_pairs_no_pest_35a55426/verification.json`; 보정 메타데이터 CPU 이미지ID `sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e`. v2 수확 계약의 추가 검증으로 집계하지 않음. 임계값 선택·정책 우열·통계검정·PPO 학습은 실행하지 않음.
- 소프트웨어139개 통과: `outputs/runs/20261106T064528Z_unit_regressions_5b13a6b4/verification.json`. 누락/중복 정책·기상 불일치·서로 다른 자원 조건·잘못된 비용·test split·시간제한의 오집계 거부 검사 포함.
- Docker가중지돼 있었고 Inference/Secrets Engine의AF_UNIX 소켓 접근 오류로 재시작 실패. Docker 종료/경로 확인을 거친 종료 후 임시 통신 폴더를 삭제 없이 백업명으로 보존·재생성해 엔진29.5.2 복구. 정상 종료 타임아웃과 경로/프로세스 보호 검사의 중단도 기록. 이미지/볼륨/가상디스크에 대한 직접 삭제/초기화/prune 없음. 백업 경로/재시도: `outputs/runs/20261106T064625Z_baseline_runtime_preflight_716c2bd7/runtime_recovery.json`.
- 최초 실행은 modern 이미지의psutil 미설치로 import 실패. 추가 설치/이미지 변경 대신 `/proc` 기반 소유 프로세스 검사로 수정해 실제 재실행 통과. 코드·정책·실행SHA·이미지ID는 별도 폴더에 보존.
- 최종 근거 묶음: `outputs/runs/20261106T065849Z_baseline_pair_release_9f05564a/verification.json`; 준비상태: `outputs/runs/20261106T065802Z_readiness_5a1b8802/readiness.json`. 연구/본 학습false, 농학 준비0개 유지. 이전 Documents 폴더 빈 상태도 확인.
- 공개 원문/Dryad 재확인에서도 포트당 식물 수 불일치가 해결되지 않아 원자료·단위 보정은 진행하지 않음. 다음은 현장 재현 입력·실험단위 확인과 v2의 다른 실패/토양 조건 확장을 이어서 수행. 농학 조건 충족 전에는 임계값/GAE/보상 계수를 선택하지 않음. 상세: `docs/BASELINE_PAIRED_DIAGNOSTIC.md`.

## 공통 시즌 기준선 기술 검증 시작 (2026-11-06)

- 원자료의 포트 정의 불일치는 공개 자료 재확인에서도 미해결. 농학/본 학습 제한을 유지하고 독립적으로 진행 가능한 규칙/무투입 공통 시즌 평가·원수익·자원 합계 검증을 구현 중. Docker 엔진이 중지돼 백그라운드로 시작함. 임계값 튜닝/정책 우열 판정/최종 test split 사용은 하지 않음.

## 건조 곡실 보정자료 추가 조사 완료 (2026-11-06)

- 공개 목록7→9연구. Ghana2017/18 현장 논문에서 지역×잎 제거9개 주변평균과 지역별 공유 SEM3개 확보.13% 수분 기준의 건조 곡실 환산과6개 기술 대비를 생성했으며 기존28개 factorial 시나리오에 복제하지 않음.
- PDF5·7·9쪽 시각 대조. 인쇄 Table2 제목은 cob이지만 열은 grain/stover, Table3는 반대임을 기록. 수량은7쪽/Table2/Grain Yield/Leaf stripping으로 고정. 주변평균 SEM을 cell SE/대비 SE로 바꾸거나 전체Mean을 독립 반복으로 세지 않음.
- 후기 처리의50% tasseling/silking은 생육단계 도달 비율이며50% 피해가 아님. 하엽 제거 매핑과 기비40kg/ha NPK의 제품/양분 기준 미확정. 일별 기상·토양·품종·셀별 반복/공분산 등은 미확보.
- 초기 회복 후보 DOI10.1002/agg2.70295 기관 PDF·Dryad 공식 메타데이터 확보. 논문2식물/포트 vs README1식물 불일치. 원자료 웹403/API401로 미확보, 기존 N 연구와 실험 중복 여부도 미확정. 반복 수/수분/field 면적 단위를 추정하지 않음. Ghana 원자료도 공개 목록상 restricted, 접근 요청/연락/우회 없음.
- 산출물: `outputs/runs/20261106T062446Z_agronomic_marginals_970a4c99`; 소프트웨어133개 통과: `outputs/runs/20261106T062447Z_unit_regressions_b7d78e31/verification.json`.
- 준비상태: `outputs/runs/20261106T062556Z_readiness_b072ec31/readiness.json`; 최종 근거: `outputs/runs/20261106T062639Z_grain_maize_evidence_release_c58146b0/verification.json`. 이전 Documents 폴더 비어 있음 확인. 신규 시뮬레이션/학습/계수 추정0, 정량 농학 준비0개·연구/본 학습false 유지.
- 다음: 제한 없는 현장 원자료와 전체 재현 입력 확보. 주변평균은 같은 품종/연도 집계가 가능한 경우에만 기술 비교. 상세: `docs/GRAIN_MAIZE_DATA_SEARCH.md`.

## 건조 곡실 보정자료 확보 작업 시작 (2026-11-06)

- 공개 grain maize 피해 실험과 DSSAT 재현용 입력·수치 오차 자료를 추가 조사 중. 기존 독립 연구의 역할과 연구/본 학습 제한은 유지.

## 공개 농학 시나리오·단위/역할 대응 완료 (2026-11-06)

- 최종 근거 묶음: `outputs/runs/20261106T061803Z_agronomic_scenario_release_b7ef4acb/verification.json`; 준비상태: `outputs/runs/20261106T061742Z_readiness_fbdba3c2/readiness.json`. 연구/본 학습 허용은 false이며 이전 Documents 폴더의 빈 상태도 재확인. 숫자 SE가 없거나 음수/NaN인 경우 및 비어 있는 허용범위 규칙은 검증 준비로 인정하지 않음.

- Santos12·Oveysi10·Oliveira6 처리, 총28개 시나리오와 같은 조건의 대조군 대비16개 등록. 연구 단위 보정/독립 검증 역할을 동결하고 독립 연구를 보정/임계값 선택에 쓰는 호출을 거부함.
- Santos는 R3/80DAE의 이삭 무게임을 기관 PDF와 시각 대조. 건조 곡실 HWAH와 비교하지 않도록 endpoint 분리. 35%의 특정 blade 제거와100% shoot 절단을 균일 잎 건물중 제거로 자동 매핑하지 않음.
- Oliveira 무추비도 기비 N40을 받으며 추비 시 총120kg/ha 상당임을 확인. 포트(20L/2식물) grain g를 field kg/ha로 환산하지 않음. 출판사 HTML/DOCX 보존; 수치 grain mean/SE는 미추출, 보충자료 F/p는 SE로 사용하지 않음.
- Oveysi 건조 곡실은 단위 변환 가능하지만 품종/기상/토양/관수·단계/피해·수치 오차가 부족해 독립 정량 검증은 미준비. 평균이 예측과 같아도 통계 통과를 부여하지 않으며 유의하지 않은 효과를0으로 강제하지 않음.
- 원문/자산: `outputs/runs/20261106T042630Z_agronomic_source_refresh_14759c5a`; 프로토콜: `configs/agronomic_protocols.json`; 시나리오·대비·개별 차단 사유: `outputs/runs/20261106T043914Z_agronomic_scenarios_a39943e3`.
- 소프트웨어128개 통과: `outputs/runs/20261106T043914Z_unit_regressions_bd6cbedb/verification.json`. 상세: `docs/AGRONOMIC_SCENARIOS.md`. 정량 검증/보정 가능0개, 모형/해충/보상 계수와 기본 작물 이미지는 변경하지 않았고 신규 시뮬레이션/학습도 실행하지 않음.

## 통합 작물·토양 모형 N 검증 완료 (2026-11-06)

- 보존된 실제 v2 출력64조건을 수확 전·휴경 초기화·최종일까지 독립 재구성. 신규 시뮬레이션/학습은 실행하지 않음. 초기화 단계 포함23,488개 N 재고 관측,23,360개 일별 지연 대조 통과.
- 식물의 당일 흡수와 토양의 전날 차감을 실제 누적 WTNUP 차이/RNUP로 대조하고, 당일 뿌리 고사와 다음 날 ASENN을 대조. 성숙 후 남는 TRNU를 일별 흡수로 오인하지 않음. 잔차 맞춤용 상수/계수는 추정하지 않음.
- 시비 행동·MgmtEvent·AFERT 대조, 피해·실제 곡실·정의된 부산물 N 반출은 한 번씩 계상. 수확 전 서 있는 곡실 N과 수확 후 토양 잔사/반출을 중복 합산하지 않음. 토양 재고 초기화 증가와 HARVRES 직접 대조.
- 최대 일별 절대 잔차0.010909kg N/ha, 최대 최종 절대 잔차0.007872kg N/ha. 최종 허용오차0.14677–0.14701kg N/ha는 출력 반올림/누적 손실·native float 정밀도에서 계산. 이보다 작은 누락 검출을 보장하지 않음.
- 이전 N-only 대조64조건에서는 출력 기반 일별 검사10조건 실패, 네이티브 경계24조건 실패.14개의 작은 경계 실패가 출력 한계에 숨으므로 고정밀 경계와 통합 재고 검사를 모두 요구함.
- 최종 근거: `outputs/runs/20261106T041921Z_integrated_crop_soil_n_fdce0905/verification.json`. 정밀도 대조: `outputs/runs/20261106T041244Z_integrated_n_precision_controls_3ab61638/verification.json`. 원본 실행의 이미지·설정/manifest·자료 지문을 보고서와 별도 스냅샷에 보존.
- 소프트웨어122개 통과: `outputs/runs/20261106T041926Z_unit_regressions_508bc1c9/verification.json`. 상세: `docs/INTEGRATED_CROP_SOIL_N.md`. v2 영역의 모형 N 검증만 추가하고 부산물 N 가정·전체 원소 C·독립 농학·다른 토양/다년/실패·기본 승격 제한은 유지.
- 최신 준비 상태: `outputs/runs/20261106T042108Z_readiness_3e7bc9d6/readiness.json`; `research_ready=false`, `main_training_allowed=false` 유지.

## EARS 직접 계측·실제 반출 수확 계약 완료 (2026-11-06)

- 직접 EARS/기관 계측16쌍·32실행에서 이전 N 후보의 궤적/수량/N·토양 전달 정확 일치. 무투입 EARS/PLTPOP 최종 비율0.996855/0.993058 확인. 전환 후 첫 차이 날짜는 시드별1982151/1982150. 발아 단계7–10을 최초 차이로 포함한 초기 날짜 필드는 교정 보고서로 대체함.
- 직접 근거: `outputs/runs/20261106T033647Z_direct_ears_d2131b0e/verification.json`; 날짜 자격: `outputs/runs/20261106T034154Z_ear_timing_qualification_5f536323/verification.json`. 원시 측정·불변 회귀는 유지.
- 별도 실제 반출 기준 v2 후보에서 Q/F64쌍+C8쌍,144실행 완료. 관리/무투입64조건 모두 정의한 건물중/N 수확 경계·실제 토양 전달 통과. 대조인 이전 N-only 후보는 같은 v2 기준40조건 통과. v1과 부산물 N 배분 정의가 다름을 명시함.
- 생육/실제 수확 보고를 바꾸지 않고 HRes_Ceres 지역 입력만 서 있는 재고와 실제 YIELD/GNUP에 맞게 변환. 부산물 N은 직접 측정이 아닌 배분 정의이며 농학 검증으로 확대하지 않음. 최대 경계 잔차 DM0.001534kg/ha·N0.00001240kg N/ha.
- 최종 근거: `outputs/runs/20261106T034830Z_actual_harvest_candidate_0ba65d42/verification.json`. 이미지 `sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98`. 빌드 소스3파일 재구성 SHA 확인: `outputs/runs/20261106T034354Z_actual_harvest_source_e7fc7428/verification.json`.
- 첫 시도2977a671은 기존 F 종료 코드의 자식 누수로 중단. 공통 백엔드는 소유한 시뮬레이터 트리를 종료/회수하고 완료 후 재시작하지 않도록 수정함. 최종144실행의 매 쌍 종료 후 잔존0건 확인. 기본 작물 이미지/수식은 유지하되 공통 종료 코드 변경은 별도 검증.
- 기본 CPU PPO 무해충/실험용 해충 각각1024단계·8업데이트·4완료 시즌·재로딩/raw 평가/정리 통과: `outputs/runs/20261106T035013Z_benchmark_no_pest_cpu_94cb2474`, `outputs/runs/20261106T035034Z_benchmark_experimental_pest_cpu_dfe5ff6a`.
- 소프트웨어116개 통과: `outputs/runs/20261106T035233Z_unit_regressions_b1221ccb/verification.json`. 상세: `docs/ACTUAL_HARVEST_CONTRACT.md`. 후보 적용 범위: `configs/actual_harvest_candidate_domain.json`. 기본 승격·전체 C/생태계 수지·독립 농학 검증은 보류.
- 최신 준비 상태: `outputs/runs/20261106T035427Z_readiness_d5009b1b/readiness.json`; `research_ready=false`, `main_training_allowed=false` 유지.

## N 후보 범위 확대·반출 기준 감사 완료 (2026-11-06)

- 두 시드×관리/무투입×피해 유무×Q/F×곡실100/50%×줄기0/100%의64조건을 원본/후보로 대조. C 수확일 측정8회를 포함해136실행 완료. F 시작일을 각 C 실행의 관측 수확일로 설정하고 실제 다음 날 초기화 대조.
- 첫 작물 궤적·옥수수 생육/N/수량 숫자64쌍 정확 일치. 실제 토양 전달과 독립 일별 식물체 N 원장은 모두 통과.
- 실제 곡실 반출 기준 후보 경계는 관리32조건 통과, 무투입32조건 부적합. 최대 절대 잔차는 건물중29.85102kg/ha·N0.155894kg N/ha. 실패를 제외하거나 PLTPOP 기준 값을 실제 반출로 대체하지 않음.
- BIOMAS/잔사의 PLTPOP 기준과 PODWT/YIELD/GNUP의 EARS 기준 차이를 확인. 원본/후보128개 출력의 잔차를 저장된 독립 기관/곡실 필드와 원본 식으로 재현. 경험적 오차 상쇄 계수는 추정하지 않음. EARS 자체는 아직 직접 계측하지 않았음을 기록.
- 실행: `outputs/runs/20261106T032225Z_harvest_n_scope_90413cc2/verification.json`. 소스/잔차 재구성: `outputs/runs/20261106T032702Z_harvest_scope_source_audit_bf7379b6/verification.json`. 상세: `docs/HARVEST_N_SCOPE.md`.
- `configs/harvest_n_candidate_domain.json`에 적용 범위·미확인 조건·승격 보류를 기록. 기존 제한된 관리 조건 통과는 유지하지만 광범위 적용 판정은 false. 기본 PPO 이미지·정책 관측/행동/마스크는 변경하지 않음.
- 소프트웨어106개 통과: `outputs/runs/20261106T032915Z_unit_regressions_8681b81e/verification.json`. 최신 준비 상태: `outputs/runs/20261106T032917Z_readiness_bc46368d/readiness.json`; `research_ready=false`, `main_training_allowed=false`.

## 독립 N 잔사 후보·공개 교차 평균 후속 완료 (2026-11-06)

- 별도 `mars-dssat:harvest-n-candidate`에서 HRes_Ceres 입력 지역 복사본의 표면 낙엽 N만 제외해 STOVN과의 중복을 제거함. 단위·건물중·기존 생육/수량·다른 작물 수식과 기본 PPO 이미지는 유지함.
- Q/F24쌍·C4쌍, 실제56실행 완료. 독립 일별 식물체 N 원장·실제 곡실 반출 경계·잔사 분배·다음 휴경 토양 전달 통과. 첫 작물 궤적·생육/N/수량 숫자 정확 일치. Q/F 검증은 관리 UFGA·시드123456에 한정함.
- 후보의 최대 N 분배/실제 반출 경계 잔차0.00001145kg N/ha, 일별 식물체 N 잔차0.00002701kg N/ha. 무피해 표준 조건 잔사 N61.001656→59.588055kg N/ha. 기본 원본의 보존 판정과 전체 수지 게이트는 false 유지.
- 근거: `outputs/runs/20261106T025157Z_harvest_n_candidate_8f5f18e3/verification.json`. 이미지 `sha256:370968c24053c98cb519386186bdfe4c2da5678293a06ef02f61b34f8a7265c4`. 상세: `docs/HARVEST_N_CANDIDATE.md`.
- 공개 Oveysi2010 Table4의 교차 처리 평균10개와 건조 수확 기준을 확인하고 PDF 표를 시각 대조함. Table3 주변평균과 분리, SE/원자료 미확보·D2 반올림 경계 차이 기록. 독립 검증 후보 역할을 유지하고 보정/튜닝에는 사용하지 않음.
- 자료: `configs/oveysi2010_table4_grain.json`; PDF·렌더링: `outputs/runs/20261106T025347Z_oveysi2010_source_1697e26e`; 자격 검사: `outputs/runs/20261106T025626Z_public_factorial_means_8dc9ccd5/verification.json`. `quantitative_fit_ready=false`.
- 소프트웨어101개 통과: `outputs/runs/20261106T025746Z_unit_regressions_32b0e32b/verification.json`. 최신 준비 상태: `outputs/runs/20261106T025748Z_readiness_ac4981d3/readiness.json`; `research_ready=false`, `main_training_allowed=false` 유지.

## C 모드 반출 회계·측정 범위와 Q/F 판정 정정 (2026-11-06)

- 생성식 `CumLeafSenes = SLAN / 600. * PLTPOP * 10.`과 원본 kg/ha 주석을 확인함. 이전 g/m² 판정은 오류이며 ×10 후보를 철회. 원본 vendor/기본 PPO 이미지는 변경되지 않았고 후보 패치의 함수/명령 실행을 차단함.
- 기존 020048의48실행은 변경 식과의 일치를 확인했으나 독립 물리 재고 보존을 입증하지 못했음. 보고서는 보존하고 `configs/evidence_qualifications.json`에서 철회/대체 근거를 표시하며 readiness 색인에서도 통과 근거로 제외함.
- 원본 Q/F24조건 재실행: 내부 수확률·건물중 분배·실제 토양 유입은 통과. N은 canopy 재고에 포함된 낙엽 N이 잔사에 다시 더해져16조건에서 보존 실패, 최대 초과1.413601kg N/ha. 전달 산술 통과와 물리 보존 판정을 구분함.
- 재감사 근거: `outputs/runs/20261106T023809Z_sequence_inventory_reaudit_76087465/verification.json`. 원본 계측 이미지 `sha256:601779824f0ef3c97cb67d32c9b85cd36d83f3cc86b127e92b45099325719f3a`.
- C 모드14조건에서 실제 HWAH/BWAH와 외부 반출/잔존 배분, 일별 식물체 N 원장을 검증. 최대 식물체 N 잔차0.00002701kg N/ha. 무투입2조건의 EARS/PLTPOP 차이도 검출하여 실제 곡실 반출값을 사용함. native 작물 재고/토양 상태는 물리적으로 변경하지 않음.
- C 근거: `outputs/runs/20261106T024226Z_c_harvest_accounting_f64e1770/verification.json`. 전체 수확 후 생태계 통과가 아닌 외부 종료 배분의 검증임.
- C/N 측정 목록과 소스 행/SHA: `configs/balance_observability.json`, `outputs/runs/20261106T024113Z_balance_observability_7b24b676/verification.json`. RUE/CARBO는 건물중 대용값이며 종자/총 동화/호흡/조직별 원소 C는 현재 미관측.
- 상세 정정과 범위: `docs/C_HARVEST_AND_OBSERVABILITY.md`. 연구 준비·전체 C/N·전체 수확 후 수지·농학 회복은 계속 false.
- 소프트웨어98개 통과: `outputs/runs/20261106T024535Z_unit_regressions_538aee39/verification.json`. 준비 상태: `outputs/runs/20261106T024555Z_readiness_ff6fa68a/readiness.json`; 철회된 보고서는 통과 근거에서 제외, `main_training_allowed=false`.

## 메타데이터·수확 경계 후속 완료 (2026-11-06)

- 정상 IOSTAT 반전, ModuleData FIELD 문자 저장/조회 누락을 별도 이미지에서 수정. UFGA 필드 경도/위도 열을 명시적으로 보정하고 표고40m는 보존. 원본 vendor·기존 이미지·토양 물성은 유지함.
- 두 시드·관리/무투입·원본/보정 좌표·무피해/피해 및 잘못된/결측 입력·깊은 파종의20조건(원본/수정40시즌) 전체 작물/기상 궤적 정확 일치. `outputs/runs/20261106T012719Z_metadata_harvest_51a6e718/verification.json`.
- 전도도 -99/0/근접0/정상/음수의 실제 Fortran 분기 검사 통과. 정규화 물성 동일, 결측의 허위0 경고만 제외. `outputs/runs/20261106T012933Z_conductivity_native_branch_6688e73e/verification.json`.
- 읽기 전용 수확 진단4시즌에서 기존 궤적 일치. RNMODE=C는 실제 잔사 HARVRES를0으로 두며 물리적 수확 후/다음 시즌 전송을 계산하지 않음을 확인. 경제적 수확 매출과 물리 재고 반출을 구분하고 전체 C/수확 후 게이트는 유지함.
- `mars-dssat:ppo-cpu-metadata`/`ppo-cuda-metadata` 생성. benchmark/smoke의 기본 실행은 보정 프로필, 원본은 `-LegacyMetadata`. 이미지 런타임 프로필은 manifest에 보존.
- 보정 기본 DssatBackend/LeafDiagnosticBackend 직접 실행에서 Summary 좌표29.6380/-82.3689/40 및 동일4707kg/ha 확인. 무해충CPU·해충CPU·해충CUDA 각각1024단계·8업데이트·4완료시즌·재로딩·raw 평가·원장·정리 통과.
- 최종 패치 출력과 실제 빌드 소스4개 SHA256 일치, vendor 지문 유지. `outputs/runs/20261106T013443Z_patched_source_fingerprints_13986721/verification.json`.
- 최신 소프트웨어 검사86개 통과: `outputs/runs/20261106T013712Z_unit_regressions_4a374e8d/verification.json`. 상세: `docs/METADATA_AND_HARVEST_BOUNDARY.md`.
- Docker 기동 장애는 오래된 실행용 소켓 디렉터리만 삭제 없이 같은 상위 폴더에 보존/분리해 복구. 이미지·볼륨·설정/자격증명 데이터는 삭제하지 않음.

## GPU 재검증 완료 (2026-11-05)

기본 분포 검사 **enabled** 그대로 실제 해충 실험 모드·4환경·102,400단계를 정상 완료했습니다. 실행 폴더 `outputs/runs/20261105T140204Z_benchmark_experimental_pest_cuda_7da9d805`.

- PPO업데이트800회·완료770시즌, 학습1081.106초(약18분)·94.718단계/초.
- 초기화3.241초·평가4.185초·체크포인트0.191초를 별도 기록. 프로세스 트리 최대3164.395MiB(장치 VRAM 값 아님).
- 백엔드 오류·무효 행동 예외·시간제한 종료0건, 최대 보상 망원합 잔차3.41e-13.
- 최종 체크포인트의 cuda:0 텐서 저장·102400단계/800업데이트 확인. 모델 재로딩·raw 마스크 평가·시뮬레이터 프로세스 정리 통과.
- 시작 GPU사용률5%, 1634MiB, 30°C를 기록. 지난 지연의 단일 원인은 확정하지 않으며 이번에는 동일한 기본 분포 검사 옵션으로 완주함.
- 이전 GPU 중단 기록은 보존. 통제되지 않은 과거 CPU 실행과 처리량을 직접 비교해 기본 장치를 변경하지 않음. 이번 결과는 기술 검증이며 농학 검증·본 실험은 아님.

## 이번 후속 계획의 실행 결과

- 실제 기상·행동 감사: 4시즌(두 모드×출력 대조), 정책 129일/시즌, 완료일 기상 543회와 관수/질소 이벤트 14건 일치. `outputs/runs/20261105T132240Z_model_contract_2d565fd6/verification.json`.
- 토양 C/유기 N/무기 N 각각 156일×두 모드의 네이티브 회계 재구성 통과. 전체 원소 C/수확 후 수지로 확대 해석하지 않음. 최신 근거 `outputs/runs/20261105T134149Z_soil_reconstruction_01437c13/verification.json`.
- 실험용 해충의 성숙 시점 토양+식물체+피해 반출 N 재고 잔차 0.000034343kg N/ha, 출력/네이티브 반올림 한도 0.0950732 이내. 수확 반출 전 재고이며 수확 후 검증은 아님.
- 공개 연구 7개 목록·역할 분리와 Santos 표 1의 12개 평균값 전사 완료. 원자료/SE/수확 기준 부족 및 IITA CSV embargo 표시 때문에 정량 보정 완료는 0개.
- 물 2×N 2×피해 8=32조건 실제 진단 통과. 생육단계 도달 후 피해 적용·제거 원장·식물체 N 검사; 농학 문헌 재현/보정으로 집계하지 않음. `outputs/runs/20261105T133449Z_damage_response_matrix_e447e94a/verification.json`.
- 규칙·무투입·관수 전용 Discrete(6) 인터페이스와 실제 관수 PPO 1,024단계/8업데이트 통과. 임계값은 진단 전용·미튜닝.
- 실제 worker 강제 종료 시 에피소드 무효화·원장 보존, 정상/강제 종료 후 살아 있는 자식 프로세스 0개 확인.
- 체크포인트에서 1,024단계 추가 학습 재개 통과. 정책/옵티마이저를 이어받고 미완료 시즌은 건너뜀(비트 단위 동일 재현 아님).
- CPU 장기 검사: 102,400단계, 800업데이트, 완료 시즌770, 오류/무효행동/시간제한0, 메모리 약1946.6MiB, 74.35단계/초. 이미지 빌드·진단 동시 작업 영향이 있어 장치 선택 확정값은 아님.
- CUDA 전용 이미지 빌드·pip check·실제 GPU 연산 통과. 기본 분포 검사 모드의 102,400단계 GPU 실행은 첫 체크포인트 전 지연으로 중단하고 근거를 보존함. 동일 옵션(분포 인자 검사 off, 프로젝트 제약 검사 유지)의 1,024단계 순차 비교: CPU188.50/GPU133.46단계/초, 각각8업데이트·4완료시즌·재로딩·정리 통과. 기본 CPU 유지.
- 비교 요약: `outputs/runs/20261105T135831Z_benchmark_summary_ec804518/verification.json`. 장기 통제 CPU/GPU 비교는 미완료로 명시.
- 원래 설정 스냅샷을 사용한 재개도 추가 검증. 루트 검증 상태가 갱신되어도 체크포인트 설정·분포 검사 옵션을 보존하며 새 시즌에서 학습을 이어감.
- 새 실행은 고유 폴더·설정/소스 스냅샷·SHA256·이미지 식별자를 보존. 레거시 공용 런타임 로그 경로를 발견해 실행별 고유 경로로 수정; GPU 실행 중 로그 변경 메타데이터 보존.
- 소프트웨어 80개 통과. 최신 근거 `outputs/runs/20261105T140030Z_unit_regressions_2139b9b2/verification.json`. 상세: `docs/VALIDATION_EVIDENCE.md`. 본 실험 게이트는 계속 닫힘.

## 현재 확인된 제약

- 기존 연구 코드와 제안서의 테스트 35개는 작업 폴더에 제공되지 않았습니다.
- 원본 공개 관측에 없는 rain은 내부 상태에서 연결했습니다. 정책은 전날 완료 기상, 행동 후 상태는 당일 완료 기상과 일치함을 독립 출력으로 확인했습니다.
- 기본 종료 메시지는 비어 있지만 새 백엔드는 SEASEND 이후 최신 상태와 실제 Summary.OUT 수확량을 전달합니다.
- 검증용 100cm 깊은 파종의 실제 실패는 확인했습니다. 냉해·발아 실패 등 다른 경로는 남아 있습니다. 기상 달력·관수/시비 적용일 독립 대조는 통과했습니다.
- 기본은 `mars-no-pest-v1`이며 조사 미사용입니다. 실험용 `mars-experimental-pest-v1`은 같은 315차원에 실제 모델 조사값을 연결하며 기존 모델과 자동 호환되지 않습니다.
- 별도 CPU/CUDA 이미지에서 레거시 PDI와 현대 학습 venv를 분리했습니다. 각각 실제 102,400단계 기술 검증을 통과했으며 농학/정책 성능 검증과 구분합니다.
- 실제 쓰기·누적 제거·식물체 질소 재고 수지는 통과했습니다. 원소 탄소·토양을 포함한 전체 수지와 농학적 회복 검증은 미완료입니다.
- 온라인 해충·실제 피해·정책 조사 관측은 별도 실험용 클래스에서 연결했습니다. 연구용 실행 거부는 유지합니다.
- 온도 증식 함수의 온도 기준 두 개와 조사 잡음 표준편차는 null이며 자동으로 가정하지 않습니다.
- 메타데이터/전도도 허위 경고는 별도 수정 이미지와 기본 보정 프로필에서 해결하고 실제 회귀를 통과했습니다. 원본 비교 이미지는 그대로 유지합니다. 전도도 결측을 임의 물성값으로 채우지 않았습니다.
- 최종 시험의 공지 지연일은 제안서에서 미확정입니다.

## 검증 기록

| 날짜 | 검증 | 결과 / 근거 |
|---|---|---|
| 2026-11-05 | pip 의존성 검사 | 통과, 충돌 없음 |
| 2026-11-05 | RTX 3060 Ti CUDA 연산 | 통과, `outputs/environment_check.json` |
| 2026-11-05 | CPU/CUDA PPO 인터페이스 | 각각 병렬 4개·512단계·업데이트 8회 통과, `outputs/smoke_*.json` |
| 2026-11-05 | DSSAT mode=all/UFGA8201/WGEN | 163단계 종료 확인, `outputs/dssat_check.json`; 농학 검증 아님 |
| 2026-11-05 | 자원·감축·마스크 회귀 | 17개 통과, `outputs/core_test_results.json` |
| 2026-11-05 | 108개 행동 마스크 일관성 | 한도 제한 상황에서 전체 조합의 허용/거부 검사 통과 |
| 2026-11-05 | 100개 무작위 시즌 | 총 12,000번 의사결정에서 자원·살포 한도 위반 0건 |
| 2026-11-05 | 실제 DSSAT 관수 10mm | 누적 관수 0→10mm, `outputs/dssat_contract_probe.json` |
| 2026-11-05 | 실제 DSSAT 동일 시드 재현 | 무투입 두 시즌의 전체 공개 관측 궤적 일치, 163단계 |
| 2026-11-05 | 종료 원본 메시지 검사 | 상태가 `{}`임을 확인; 최종 수확량·실패 분류 검증 미완료 |
| 2026-11-05 | 후속 소프트웨어 검사 | 총 32개 통과, 자원·관측·대역 백엔드·종료 계약 포함 |
| 2026-11-05 | 실제 종료 정보 보완 | 3시즌의 최신 종료 상태와 실제 HWAH 일치, `outputs/dssat_backend_verification.json` |
| 2026-11-05 | 실제 원본 생육 회귀 | 종료 보완 전후의 전체 비종료 공개 관측 궤적 일치, 3시즌 |
| 2026-11-05 | 무해충 Gymnasium 연결 | 파종 전 27일 자동 진행, 정책 136일, 315차원·17개 마스크 정상 |
| 2026-11-05 | 실제 원장·수익 대조 | 무투입/제약 관리 2시즌의 물·질소·보상 합계·최종 관리 수익 일치 |
| 2026-11-05 | 실제 래퍼 회귀·시간제한 | 원본 궤적 일치, 시간제한에 임의 매출 없음, `outputs/gym_integration_verification.json` |
| 2026-11-05 | 실제 작물 실패 | 진단용 파종 깊이 7→100cm, 자체 실패 경고와 stage=6, 61단계 후 매출 0·비용 21.4 유지; `outputs/crop_failure_verification.json` |
| 2026-11-05 | 독립 외생 시즌 | 기상·유입·조사·감축·예산 스트림, 재현·조건 변경 불변·날짜별 사전 생성 검사 통과 |
| 2026-11-05 | 공통 시즌 실제 대응 | 다른 정책/예산/감축 조건에서 공통 129일 기상 일치, Windows/Linux 배열 digest 일치; `outputs/paired_seasons_verification.json` |
| 2026-11-05 | 해충·조사 수식 | 당일 살포·잔효 재설정·V7 무억제·최근 7일 평균/alpha·잡음·조사 정보 시점 검사 통과 |
| 2026-11-05 | 최신 소프트웨어 검사 | 총 49개 통과; `outputs/core_test_results.json` |
| 2026-11-05 | 실험용 Fortran 빌드 | 배포 원본 유지, 동일 컴파일러 소스 대조+말기 피해 바이너리 생성; `outputs/leaf_build.log` |
| 2026-11-05 | 실제 잎 피해 무피해 회귀 | 배포 원본·소스 대조·수정 바이너리의 전체 궤적 및 수확량 4707kg/ha 정확 일치 |
| 2026-11-05 | 실제 국소 회계·시점 | 122개 활성일 검증; V3(DAP15)/V12(DAP50) 25% 피해의 녹색 면적·잎 무게·건물중/N 제거량 및 다음 관측 전달 확인 |
| 2026-11-05 | 실제 쓰기 결과 | `outputs/native_leaf_verification.json`, passed=True; 전체 탄소/N 수지·농학 검증·연구용 해충 허용은 False |
| 2026-11-05 | 최신 소프트웨어 검사 | 총 53개 통과, PDI 스키마·수지 항등식 검사 추가; `outputs/core_test_results.json` |
| 2026-11-05 | 기존 경로 재검증 | 실험 확장 후 기존 무해충 Gymnasium 실제 회귀 재통과 |
| 2026-11-05 | 시즌 반복/강한 피해 | 86일 3%, 단일 95%, 후기 50% 등 실제 누적 제거 원장과 Fortran 누적량 일치 |
| 2026-11-05 | 식물체 N 재고 수지 | 8개 조건의 종자·흡수·서 있는 식물체·뿌리 고사·제거 N 대조, 최대 절대 잔차 약 0.000051713kg N/ha (허용 0.001) |
| 2026-11-05 | 온라인 해충·조사 | 실제 완료일 Tmin/Tmax 평균 사용, 출아 전/종료일 전이 포함, 온라인 3개 조건 오프라인 수식 재실행 일치 |
| 2026-11-05 | alpha=0 실제 회귀 | 온라인 콜백을 켜도 무피해 작물 전체 궤적 정확 일치 |
| 2026-11-05 | 실험용 Gymnasium | 실제 2개 시즌, 315차원 공개 조사·마스크·살포 비용·raw 수익 합계 일치; info에 실제 밀도 제외 |
| 2026-11-05 | 최신 검사 | 소프트웨어 63개, 실제 무피해 원본 회귀·기존 환경 재통과 |
| 2026-11-05 | 보조 보상 실제 검증 | 수확136일·실패61일·시간제한20일, 궤적/경제 원장 불변·망원합 잔차 <1e-12; `outputs/real_reward_verification.json` |
| 2026-11-05 | 실제 CPU PPO 연결 | 두 모드 각각 4환경·1,024단계·8업데이트, raw 마스크 평가·모델 재로딩 통과; `outputs/real_ppo_*/verification.json` |
| 2026-11-05 | 최신 소프트웨어 검사 | 69개 통과; `outputs/core_test_results.json`, 상세 `docs/REWARDS_AND_REAL_PPO.md` |

## 작업 이력

- 2026-11-06: 공개3연구28처리·16기술 대비 등록. R3 이삭/건조 곡실/포트 단위와 기비/추비/피해 매핑을 구분하고 독립 연구의 보정 사용 차단. 소프트웨어128개. 정량 농학 가능0개, 다음은 grain maize 보정 자료·오차/재현 입력 확보.

- 2026-11-06: 공개 농학자료의 처리·단위·오차를 재확인하고 독립 검증 시나리오 등록 작업 시작. Santos R3 이삭 수량과 건조 곡실 수량의 차이, Oliveira 무추비/기비 N 구분을 원문에서 확인함. 연구 단위의 보정/독립 검증 역할은 유지할 예정.

- 2026-11-06: v2 통합 모형 N64조건·23,488관측 통과. 흡수/뿌리 고사 시차와 수확/휴경 경계를 검증하고, 출력 한계에 숨는 대조14조건을 확인해 네이티브 경계 병행 조건 유지. 소프트웨어122개. 다음은 독립 농학자료·시나리오와 영역 확대.

- 2026-11-06: 통합 작물·토양 N 수지 감사 시작. 보존된 v2의64조건을 수확 전·휴경 초기화·최종일까지 연결하고, 일별 흡수/뿌리 고사물의 실제 전달 시차와 외부 입력/반출을 독립 대조할 예정.

- 2026-11-06: 직접 계측32실행·실제 반출 기준 v2 계약144실행 완료. F 프로세스 종료 누수 수정 후 잔존0건·기본 CPU PPO 두 모드 재검증·소프트웨어116개 통과. 연구 준비와 기본 작물 이미지 승격은 보류.

- 2026-11-06: EARS/PLTPOP·기관별 재고 직접 계측 시작. 원본 N 후보에 읽기 전용 일별/불임 이삭 전환 이벤트를 추가한 별도 이미지에서 기존 궤적 회귀와 직접 측정을 대조할 예정.

- 2026-11-06: N 범위 확대136실행 완료. 관리32조건 통과·무투입32조건 부적합. EARS/PLTPOP 기관·곡실 기준 차이로 잔차 재현. 기본 승격 보류, 직접 EARS/기관 재고 계측과 계약 검토를 다음 작업으로 지정.

- 2026-11-06: N 후보 적용 범위 확대 검사 시작. 다른 시드·무투입에서 실제 곡실 반출과 PLTPOP 기반 재고를 구분하고, F 휴경 시작일은 해당 C 진단에서 관측한 수확일로 설정해 검증할 예정.

- 2026-11-06: N 잔사 후보 Q/F24쌍+C4쌍(56실행) 검증 완료, 첫 작물 정확 회귀. 공개 교차 처리 평균10개·수확 기준 확인. 후보는 별도 이미지에 유지하며 전체 수지·농학 게이트는 미완료.

- 2026-11-06: 독립 N 재고 기반 수확 잔사 후보 검증 시작. HRes_Ceres에 넘기는 지역 복사본의 표면 낙엽 N만 제외하여 STOVN과의 중복을 제거하고, 생육/단위/다른 작물 수식은 보존하는 별도 이미지에서 대조할 예정.

- 2026-11-06: C 외부 종료 배분14조건·원본 Q/F 전달/독립 재고24조건 재감사 완료. 이전 단위 후보 철회, N 중복16조건 확인. C/N 측정 목록·근거 자격 관리·98개 검사 완료. 다음은 독립 N 잔사 후보와 공개 연구 정량 자료 확보.

- 2026-11-06: C 모드 반출 회계·원소 C/N 측정 감사 시작. 생성식의 `CumLeafSenes = ... * PLTPOP * 10`과 명시된 kg/ha 주석을 확인하여 직전 ×10 후보의 단위 전제가 잘못됐음을 발견. 해당 후보의 승인/검증 판정을 철회하고 원본 출력과 독립 N 재고를 다시 대조함. 기본 PPO 이미지는 영향 없음.

- 2026-11-06: [후속 정정됨] Q/F48실행의 이전 단위 보정 판정은 생성식 단위 해석 오류로 철회. 원본 보고서는 보존하고 위 C/N 재감사 결과로 대체함.

- 2026-11-06: Q/F 수확 잔사·다음 시즌 전달과 단위 경계 감사 시작. 단일 시즌 C 모드 및 기존 보정 학습 이미지는 보존하고 별도 연속 시즌 진단을 구성함.

- 2026-11-06: 메타데이터 오류 수정·원본 회귀20쌍 및 수확 진단4시즌 통과. 기본 CPU/CUDA 보정 프로필 연결·PPO3모드 통과, 소프트웨어86개. C 모드의 잔사 미전송 범위를 확인하고 전체 C/수확 후 게이트는 유지.

- 2026-11-06: 입력 메타데이터 수정·원본 회귀·수확 경계 감사 실행 시작. 원본 vendor/기존 이미지를 유지하고 별도 수정 이미지를 생성할 예정. 정상 IOSTAT 반전과 ModuleData FIELD 문자 저장/조회 누락을 함께 확인함.

- 2026-11-06: 향후 작업을 입력/수지→농학 보정→기준선/예비 학습→설정 동결→본 실험→통계의 6단계로 정리. `docs/NEXT_STEPS.md`에 완료 조건과 병행 작업을 기록.

- 2026-11-05: GPU 재시도 완료. 기본 분포 검사 enabled, 4환경·102,400단계·800업데이트·완료770시즌 통과. 94.718단계/초, 약18분. 최종 모델 CUDA 저장·재로딩·raw 마스크 평가·원장·프로세스 정리 확인. 이전 중단 기록 보존.

- 2026-11-05: 사용자 요청으로 GPU 장기 검사 재시도 시작. 기존 결과는 보존하고 기본 분포 검사를 켠 상태에서 4환경·102,400단계를 우선 실행하며 상태를 추적함.

- 2026-11-05: 승인된 후속 계획의 다음 완료 지점 실행 완료. 실제 감사·토양 재구성·공개자료 목록·32조건 진단·CPU 장기·정책/재개 인터페이스 검증. 독립 농학 보정·전체 C/수확 후 검증은 미완료, 본 학습 미실행.
- 2026-11-05: 승인된 후속 계획 실행 시작. 기록 정리·기상/입력 감사·전체 수지 측정 가능성·공개 농학자료 조사를 우선 수행하며 장기 CPU 검사와 연구 진입 게이트를 준비함.

- 2026-11-05: 잠재함수 보상과 실제 PPO 연결 작업 시작·완료. eta=0.45는 제안서 미지정 수치에 대한 명시적 보상 전용 가정으로 기록.
- 2026-11-05: 실제 수확·실패·시간제한의 망원합 및 원래 작물 궤적 검증 통과. 시간제한 잠재값 유지.
- 2026-11-05: 별도 PPO venv와 레거시 DSSAT 프로세스 연결. 무해충/실험용 해충 각각 CPU 4환경·1,024단계·8업데이트·완료 시즌 4개 통과. 최종 업데이트 이후 raw 평가 및 저장 모델 재로딩 일치.
- 2026-11-05: 소프트웨어 69개 통과. 다음은 탄소/토양 수지·농학 보정과 10만~20만 단계 CPU/GPU 처리량·기준선 검증. 본 학습은 미실행.

- 2026-11-05: 시즌 수지·반복/강한 피해·온라인 연결 작업 진행. 네이티브 누적 제거량과 Python 독립 합계 대조 추가.
- 2026-11-05: CSM의 일별 OUTPUT 후 이벤트와 실제 당일 기상 기반 해충/조사 콜백 구현. 출아 전·종료일 실제 손실 0 처리.
- 2026-11-05: 초기에 누락된 종자 N 입력과 중복 고사엽 N 합산을 소스 확인 후 진단식에서 수정. 생육/흡수 식 보정은 하지 않음.
- 2026-11-05: 8개 조건의 식물체 N 수지와 누적 제거, 온라인 3개 조건, 실험용 환경 2개 시즌 검증 완료. 원소 탄소/토양/농학은 미검증 유지.

- 2026-11-05: 바탕화면 기본환경에서 실제 잎 피해 쓰기 작업 시작. 원본 피해 블록은 질소 흡수 전이므로 별도의 말기 INTEGR 실험 경로를 설계·검증.

- 2026-11-05: 사용자 요청으로 전체 파일을 바탕화면 기본환경으로 이전. 파일 32,928개 목록·크기 및 주요 파일 89개 SHA256 대조 완료. 이전 Documents 폴더는 비움. 가상환경 경로·실행 런처·활성화 경로 복구 완료. 새 위치에서 49개 검사·CUDA 연산·실제 DSSAT 통합 재검증 통과. 근거: outputs/migration_verification.json.

- 2026-11-05: 후속 작업 시작. 실제 작물 실패 검사 통과(검증용 100cm 파종). 독립 외생 난수·해충 조사 모듈 구현 중.

- 2026-11-05: 후속 작업 시작. 설치된 바이너리와 일치하는 Fortran 소스 a4ae650 확보, 종료 이벤트 조사 중.

- 2026-11-05: 최신 제안서 복사, 환경 설정, 공식 DSSAT 소스·이미지 확보.
- 2026-11-05: 진행상황 파일 생성. 자원·물 감축·마스크 모듈 구현 시작.
- 2026-11-05: 불변 자원 원장, 비용 회계, 2종 감축 계약, 살포 제한, 행동 인덱스 검증 구현 완료.
- 2026-11-05: 17개 회귀 검사 통과. 실제 DSSAT 단위·재현·종료 메시지 진단 완료.
- 2026-11-05: 공개 관측에 없는 rain이 내부 상태에 존재함을 확인. 최종 상태는 원본에서도 누락됨을 확인.
- 2026-11-05: PDI flag_done이 시즌 종료 후 빈 상태를 보내는 원인 확인. 최신 콜백 상태 전달 및 Summary.OUT 출력 활성화.
- 2026-11-05: 무해충 Gymnasium 환경, 45필드·7일 관측, 자원 회계, raw 보상, 종료·시간제한 분리 구현.
- 2026-11-05: 실제 DSSAT 회귀 및 통합 검사 통과. 생육 방정식·Fortran 바이너리는 수정하지 않음.
- 2026-11-05: 실제 깊은 파종 실패의 수익·종료 처리 검증 완료. 기본 시나리오 파종 깊이는 유지.
- 2026-11-05: 외생 시즌 생성기와 Gymnasium reset 연결, split별 10개(총 30개) 주소 manifest 기록.
- 2026-11-05: 제안서 원본 수식 이미지를 확인하여 해충·7일 조사 모듈 구현. 미정 보정값은 null로 유지.
- 2026-11-05: 최신 검사 49개 및 실제 공통 외생 시즌 대응 검사 통과.
- 2026-11-05: 별도 말기 INTEGR 피해 쓰기 구현. 원본 vendor 소스 대신 컨테이너 복사본만 패치.
- 2026-11-05: 개발 패키지 다운로드 지연을 공식 KAIST 미러로 해결. 바이너리는 공통 데이터 디렉터리에 별도 이름으로 배치.
- 2026-11-05: PDI data/metadata 구분 오류를 실제 실행으로 수정하고 렌더된 YAML 회귀 검사 추가.
- 2026-11-05: DAP10은 출아 전이므로 실제 잎이 존재하는 V3/DAP15로 검증 펄스 날짜 변경. V7 억제 조건은 추가하지 않음.
- 2026-11-05: 실제 Fortran 쓰기 검증 완료. 연구용 해충 실행 제한 및 전체 수지·농학 검증 미완료 상태 유지.

## 다시 실행하기

```powershell
.\.venv\Scripts\python.exe scripts/run_tests.py
.\scripts\probe_dssat_contract.ps1
.\scripts\verify_dssat_backend.ps1
.\scripts\verify_gym_integration.ps1
.\scripts\verify_crop_failure.ps1
.\scripts\verify_paired_seasons.ps1
.\scripts\verify_native_leaf.ps1
.\scripts\verify_season_balance_online.ps1
.\scripts\verify_experimental_env.ps1
.\scripts\audit_model_contract.ps1
# 장기 검사는 별도 실행 폴더에 보존
.\scripts\benchmark_real_ppo.ps1 -Device cpu -Steps 102400
```

소프트웨어 검사 결과는 `outputs/core_test_results.json`, 실제 DSSAT 진단은
`outputs/dssat_contract_probe.json`에 갱신됩니다.
설계·통합 순서는 `docs/RESOURCE_MODEL.md`를 참고합니다.
현재 실제 연결 계약은 `docs/BACKEND_INTEGRATION.md`를 참고합니다.
외생 시즌과 해충·조사 계약은 `docs/EXOGENOUS_AND_PESTS.md`를 참고합니다.
실험용 실제 피해 쓰기는 `docs/LEAF_WRITE_EXPERIMENT.md`를 참고합니다.
시즌 질소·온라인 연결은 `docs/SEASON_BALANCE_AND_ONLINE.md`를 참고합니다.

## 다음 작업

상세 순서와 완료 조건: `docs/NEXT_STEPS.md`.

1. v2 일별/수확 후 통합 모형 N과 범용 토양8쌍·깊은 파종 실패 회귀 완료. 원소C 측정 가능범위 감사도 완료했으며6개 미확인 항목으로 전체C는 보류. 다음은 다른 실패/수확률·다년 전달과 부산물 N 배분의 농학적 한계 확인. 기본 작물 이미지 승격 보류, 기존 ×10 후보는 사용 금지.
2. 28개 공개 시나리오의 누락 입력을 보완하고 native 건조 곡실과 맞는 grain maize 보정 자료를 확보. 수치 SE/사전 허용범위·전체 토양층/품종 계수·일별 기상/관수·피해 매핑 확인 후 무피해 대조부터 독립 검증. 독립 연구를 보정으로 전환하지 않음.
3. 규칙/무투입 공통4쌍 기술 검사는 완료. 농학 진입 조건을 충족한 뒤 validation에서 규칙 기준선 임계값·GAE·보상 계수를 선택하고 관수 전용/공동 정책 예비 학습.
4. 동일 유휴 조건 CPU/GPU 비교와 연구 진입 조건 확인 후 학습 설정·시험 공지 지연일·통계 대비 동결.
5. 통과 시 두 정책×10시드×500만 단계 본 학습 및 공통 시즌 평가.
6. 교차 부트스트랩·Holm·가설 대비, 기여도·민감도 분석과 결과 정리.

다음 실행의 우선순위는 **공개 농학 자료의 누락 입력과 검증 가능한 범위 확정**입니다. 수분 부족 발아 실패의 종료·회계는 아래4회 진단 범위에서 완료했으며 생육 중 사망/실패는 미검증입니다. 원토양의 지정2년F 달력·N 검증은 완료했습니다. 두 범용 토양의 지정2년Q N 확장은 완료했습니다. 지정2년Q의4RUN 모형N 원장은 두 수확률 조건에서 검증 완료했으며 다른 범위로 일반화하지 않습니다. 원소C6개 미확인 항목의 관측/모델 경계를 별도 정의해야 하며 전체C통과는 보류합니다. 현장 factorial 원자료·공분산과 포트/수분 정의 충돌 확인도 유지합니다. 확보한9개 주변평균은 기존28시나리오와 분리합니다. 독립 검증 연구의 역할을 유지하고 전체 원소 C·다른 실패/토양/다년 조건·부산물 N 배분 한계를 이어서 확인합니다. 철회된 ×10 후보는 사용하지 않습니다.

본 학습과 농학 검증은 아직 시작하지 않았습니다. 설치/소프트웨어 검사를 연구 성과로 집계하지 않습니다.

## 2026-11-06 추가 작업 시작: 발아 실패 경로
- 깊은 파종과 구분되는 수분 부족 발아 실패의 네이티브 조건을 확인한다. 진단 입력만 변경하고 원시 출력·종료·유료 투입 회계·프로세스 정리 근거를 별도 실행 폴더에 보존한다.
- 농학 검증이나 연구 실행 허용으로 해석하지 않는다.

## 2026-11-06 완료: 수분 부족 발아 실패의 종료·회계
- 실제 DSSAT 대조/후보 × 건조/첫날20mm 관수 =4회 통과. 무관수는 정책22회 후1982078 발아 실패, 곡실/수익0·비용12.9·raw합−12.9. 관수 대조는 출아했지만 수량0이므로 수량 회복 아님.
- 원시48파일 SHA·강수 이외 기상 열·최종 Summary·고정 파종 깊이7cm·소유 프로세스 잔존0건 확인. 조건별 두 바이너리의 저장 네이티브 상태 일치.
- 실제DSGT21일과 고정 경고문15일을 구분. 초기수분0.010은 대부분 층에서LL로 조정됨. 최초 출력 감사의 MDAT 예상 오류는 실패 근거를 보존하고 Summary MDAT/HDAT1982152 기준 재검증 통과.
- 네이티브: outputs/runs/20261106T082253Z_germination_failure_035e575a/verification.json
- 감사: outputs/runs/20261106T082549Z_germination_evidence_0b2ee5c4/verification.json
- 소프트웨어156개 전부 통과: outputs/runs/20261106T082551Z_unit_regressions_688128c0/verification.json
- 상세: docs/GERMINATION_FAILURE.md. 기본 관측/행동/마스크·종료 분류·네이티브 소스 변경 없음. 전체C·독립 농학·생육 중 실패는 미검증, research_ready/main_training_allowed=False 유지.
- 다음: 공개 grain maize 자료의 전체 실험 입력·오차/피해 정의 확인, 자료가 식별 가능한 검증 범위 확정.

## 2026-11-06 작업 시작: 공개 농학 입력 보완
- 건조 곡실과 비교 가능한 공개 자료의 원문·데이터를 조사하고 처리별 평균/오차·기상·토양·품종·피해 정의 누락을 대조한다. 독립 연구 역할과 연구 실행 제한을 유지하며 접근 결과와 근거를 새 폴더에 보존한다.

## 2026-11-06 완료: USDA LIRF 공개 원자료 확보·입력 감사
- 공식 공개11파일 확보(SHA256),96포장 건조곡실 수량·24처리요약·1,461기상일·4,086처리별 일별기록 구조화. 원본XLSX 수정/수식 재계산·새 DSSAT 실행·보정 없음.
- 공개 연구10개로 확장, LIRF2008–2011 전체를 독립 기본 작물/수분 반응 검증 후보로 고정. 기존28피해 시나리오/9주변평균과 분리. 정량 준비0개 유지.
-2009T3 보고9,435.27 대 포장평균9,121.1932kg/ha 불일치,3날짜4기상값 결측,2008 DOY142 스프링클러21mm의강수열 포함,초기 토양N/관개수N 구분 확인. 응애/우박/서리 관련14로그가 있어 무피해대조로 확정하지 않음.
- 최초 네트워크DNS 실패와 부가표DOY를 일별기록으로 혼합하지 못하게 막은 초기감사 실패를 별도 보존. 수정 감사 통과, 원본 변경 없음.
- 원본: outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab/verification.json
- 감사: outputs/runs/20261106T084019Z_lirf_input_qualification_62b909f8/verification.json
- 소프트웨어156개 전부 통과: outputs/runs/20261106T084328Z_unit_regressions_62500e92/verification.json
- 준비상태: outputs/runs/20261106T084336Z_readiness_d50fc51a/readiness.json. research_ready/main_training_allowed=False.
- 상세: docs/LIRF_INPUT_QUALIFICATION.md. 다음은 DSSAT 품종/모형 패키지·기상 원관측·토양/초기상태 대응 및 연도별 외란 포함 기준 확인.

## 2026-11-06 작업 시작: LIRF 기상 원관측·모형 패키지 확인
- 원본 일별 기상4결측을 시간별/공식 원관측과 대조하고 공개DSSAT 품종/모형 입력 패키지의 출처를 확인한다. 임의 보간/기본 품종 대체 없이 새 실행 폴더에 근거를 보존한다.

## 2026-11-06 완료: LIRF 기상 원관측·공개모형 감사
- 공식 USDA 모형ZIP5파일/중첩CUL·ACE/DOME 확보.2008년100ET 한처리/기상366일/생육16행. DEKALB521·IB1068·MZCER045는 현장52-59/048과 동등성·계수 보정 이력 미확인, 자동이식/전체24조건 확장 금지.
- CoAgMET 공식 QC6응답과API문서 보존. 같은 관측소에서4결측 확인. 일사 재집계 후보18.9888/30.8232/24.0534는 적용하지 않았고, 시간평균 최소값으로TMIN을 대체하지 않음.
-1,461일 감사/1,457개 일별-시간별 일사 비교. 표시정밀도 진단범위 초과292일, 최대차6.6618MJ/m2/day. 관측소 보완/단위 차이와 구분하며 모형 허용오차로 사용하지 않음. 원본 음수 센서62개 보존,2011-12-31 중복/누락 시간은 집계 제외.
- 초기 감사 실패2개를 보존. 음수값은 산술진단에서 원문대로 보존하도록 명시했고 중복시간 검사는 완화하지 않음.
- 모형: outputs/runs/20261106T084700Z_lirf_model_package_f84234e1/verification.json
- API: outputs/runs/20261106T084911Z_lirf_station_windows_0f693d5f/verification.json
- 감사: outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47/verification.json
- 소프트웨어163개 전부 통과: outputs/runs/20261106T085502Z_unit_regressions_b84e78d1/verification.json
- 준비상태: outputs/runs/20261106T085517Z_readiness_995e34a6/readiness.json. 공개10연구·정량 준비0개, 본 학습/연구 실행false. 새DSSAT/학습 실행 없음.
- 상세 docs/LIRF_WEATHER_MODEL_AUDIT.md. 다음:2008 공개 패키지의 토양·초기수분/N·관리와 현장 원본 대조, 품종/추정 이력·단위·외란 포함 기준 명시.

## 2026-11-06 작업 시작: LIRF2008 토양·초기상태·관리 대응
- 공개 ACE/DOME의 토양층·초기 수분/N·파종/시비/관수 일정을 현장 XLSX와 대조한다. 단위/초기 토양N/관개수N·관수/강수의 중복을 확인하고 자동 기본값 채움 없이 근거를 새 실행 폴더에 보존한다.

## 2026-11-06 완료: LIRF2008 토양·초기상태·관리 대조
- 공식ICASA 사전 커밋2168f366b7c35ce6997c8fb0055dc259e9341ad3의12CSV 보존. 현행 단위 정의와 과거 생성기 단위의 동등성은 미확인.
- 토양9층/초기7층을 겹침구간 밀도로 계산: 패키지1/1의0–200cm 물337.4mm·무기N23.683296kg/ha. 현장N5/10·수분6/10과 날짜가 달라 초기상태 검증으로 판정하지 않음.
- 관수459.1mm는 총량 일치.39.5mm의8/26–27 하루차이와±0.1mm 차이 유지. 같은5/10–10/23 강수는 패키지270 대 현장229.886mm(발아관수21분리), 차40.114mm.
- 패키지 전체시비134.4, 현장 초기일 이후만 비교하면84.0 대89.7kgN/ha. 초기토양N148을시비로 더하지 않음. 점적수109.525kgN/ha 유입은25mg/L 조건부 계산이며 패키지 포함여부/스프링클러수원 미확인.
- 현재사전기준SLFC1=204836·입도합1인9층의10개 문제를 원문 그대로 보존. 소수점수정/100배변환/기본품종교체·자동FileX 생성 보류.
- 감사: outputs/runs/20261106T090447Z_lirf2008_input_crosswalk_dbb8c54c/verification.json
- 사전: outputs/runs/20261106T085959Z_icasa_dictionary_8bbb3db6/verification.json
- 소프트웨어169개 전부 통과: outputs/runs/20261106T090643Z_unit_regressions_9f111fdf/verification.json
- 준비상태: outputs/runs/20261106T090709Z_readiness_e4f6287f/readiness.json. 공개10연구·정량 준비0개. 신규DSSAT/학습 실행 없음.
- 상세 docs/LIRF2008_INPUT_CROSSWALK.md. 다음은 공개AgMIP→DSSAT 변환기의 과거 단위·기본값 처리 확인과 패키지 재현/현장 검증 입력 계약 분리. 연구/본학습false 유지.

## 2026-11-06 재시도 시작
- 사용자 재시도 요청에 따라LIRF2008 입력 대조와 전체 소프트웨어 검사를 새 폴더에서 재실행한다. 기존 검증·원본자료를 덮어쓰지 않는다.

## 2026-11-06 재시도 완료: 입력 감사 동일 재현
- LIRF2008 입력감사 재실행 통과. 최초 통과 보고서와SHA256이 동일해 결과가 완전히 재현됨. 관수459.1mm·강수차40.114mm·시비/초기상태·토양10개문제 판정 동일.
- 재감사: outputs/runs/20261106T115533Z_lirf2008_input_crosswalk_5bf31995/verification.json
- 소프트웨어169개 전부 재통과: outputs/runs/20261106T115534Z_unit_regressions_retry_ad50fccc/verification.json
- 준비상태 갱신: outputs/runs/20261106T115554Z_readiness_f123cb01/readiness.json. 연구/본학습false, 자동입력생성 보류. 기존산출물 덮어쓰기 없음.
- 다음 작업: AgMIP→DSSAT 변환기의 과거 단위/기본값 처리와 패키지 재현/현장 검증 계약 확인.

## 2026-11-06 작업 시작: AgMIP→DSSAT 변환 규칙 감사
- 공개 변환기 코드를 버전으로 고정해PLDP·입도·SLFC1·초기N·누락값 처리와 기본값을 확인한다. 패키지 재현과 현장 검증의 입력 계약을 구분하고 자동수정 없이 근거를 보존한다.

## 2026-11-06 완료: 실제 AgMIP→DSSAT writer 출력 검증
- 공식현재/2015후보 소스2개커밋 보존. 공식Maven1.2.18/1.2.21과고정공통의존성으로 실제Java21 실행. 당시전체빌드/패키지생성기 동일성은 미확인.
-2버전×8조건=16변환조건, SOL/FileX32파일 검증통과. 원본ACE/XLSX·기본환경 변경 없음, DSSAT모형은 실행하지 않음.
-PLDP50→5 확인. 누락값은−99지만 명시적PLDP−99는−9.9로 변환돼 향후입력경계 차단요구를 계약에 기록(차단기구현/실행으로 주장하지 않음). 입도0.05/0.1은 그대로출력,100배자동보정 없음.
-SLFC1은두writer의토양출력대상에서제외.수정/삭제해도 두출력동일. 원본품질문제는유지하되 직접native입력영향으로 분류하지않음. DOME미적용원시writer의SLPF는−99.
-출력반올림으로초기물337.4→337.7mm(+0.3), 해당사례N재고유지. 전체ACE/DOME·native수용·농학 검증과구분.
- Java실행: outputs/runs/20261106T120239Z_agmip_writer_probe_d5efe8e9/verification.json
- 출력감사: outputs/runs/20261106T120430Z_agmip_writer_qualification_2ceac4e9/verification.json
- 계약: configs/lirf_translation_contract.json; 상세 docs/AGMIP_DSSAT_TRANSLATION_AUDIT.md.
- 소프트웨어169개전부통과: outputs/runs/20261106T120615Z_unit_regressions_12c90f7e/verification.json
- 준비상태: outputs/runs/20261106T120635Z_readiness_76367a86/readiness.json. 연구/본학습false 유지.
- 다음: 전체DOME 채움·날짜·토양/품종 주입 계약과 공개패키지 재현용 진단입력 준비. 현장 타당성으로 승격하지 않음.

## 2026-11-06 작업 시작: DOME 처리·진단 입력 경계 구현
- 원본DOME의FILL/날짜/연결을 확인하고 원본과 가정을 분리한 진단 입력을 준비한다. 결측PLDP/단위·비정상토양의 사전차단을 구현하고 실제writer로 재검증한다. 현장검증·본학습 허용은 계속false로 유지한다.

## 2026-11-06 완료: 실제DOME 처리·진단 입력경계 구현
- 공식DOME1.4.15로7개FILL을규칙/생성기/기존값보존/ENDAT누락의4조건 실행. SDAT4/12·ENDAT11/28·표면/시비깊이 채움 확인, 기존SDAT/SLPF/FEDEP 보존. ALNK실험명과ACE명불일치는 기록하고 자동연결로 주장하지 않음.
- require_export를실제Java writer직전에연결. 원본입도9층차단, 파종깊이/단위/NO3/DUL/품종/soil·weather연결/현장검증목적12음성대조 전부차단. Python−O에서도예외기반차단 확인.
- 진단복제본에한해입도27값의명시적변경이력을저장하고SOL/FileX/WTH/CUL4파일생성. 기상366일·PLDP5cm·SLPF.95/SLDR.5/SLRO60·시비깊이5·SDATE08103독립확인. 원본수정/자동현장보정없음.
- 최종통합: outputs/runs/20261106T131246Z_lirf_dome_boundary_8e93a2f4/verification.json
- 소프트웨어176개전부통과: outputs/runs/20261106T131249Z_unit_regressions_aff12738/verification.json; 같은폴더optimized_gate.json통과.
- 준비상태: outputs/runs/20261106T131404Z_readiness_ad36580f/readiness.json. 공개10연구·정량준비0개, native_ready/research_ready/main_training_allowed=False.
- 초기GENERAL자유문자열행파서실패는보존하고숫자접두부파싱으로수정. 추가기상출력/실행형경계확인완료. 신규DSSAT/학습실행없음.
- 상세 docs/LIRF_DOME_EXPORT_BOUNDARY.md. 다음은격리native의실제수용값·045/048품종호환성·초기/시작날짜·종료검사. 진단성공을현장농학통과로승격하지않음.

## 2026-11-06 작업 시작: LIRF 진단 입력 native 수용 검사
- 격리컨테이너에서생성한SOL/FileX/WTH/CUL의실제수용·품종045/048호환성·초기/시작날짜와종료를검사한다. 호환변경/추가가정은별도보존하며현장검증·본학습은false로유지한다.

## 2026-11-06 완료: LIRF 진단 입력 native 수용·종료 검사
- 최종native6조건: 원초기1/1·DOME시작4/12는IPSLIN오류2건; 시작1/1대조2건은원writer헤더SRAD오독을재현; 헤더호환2건은각1시즌완료/품종·날짜·투입·초기상태대조통과. 독립현장반복6건으로집계하지않음.
- 기본048에도IB1068이있지만패키지와계수가다름.045파일만복사하면기본값을읽음.048의해당6수치칸만명시적으로연결하고Overview에서실제계수확인.타품종행·원본/이미지변경없음.
-7자리날짜의DATE헤더5열끝때문에SRAD에날짜일부가섞임. 수치행/다른헤더위치는유지하고DATE끝만7열로맞춘명시적어댑터검증. 헤더호환조건296/295일×4기상변수=2,364항목오차출력정밀도범위내통과.
-native초기물338.2mm(writer337.7에서하부LL조정+0.5), 초기무기N출력23.7 확인. 토양9→10층분할, pH/PHOTO/SLNF/SLU1/TAV/TAMP등기본값·경고보존. 관수16회/시비10회일정확인. 실제수확은ENDAT보다이른2008296/295.
- 최초passive PDI는완료후재시작해시간제한에걸림. 해당출력보존/통계미사용. 최종은flag_done완료에서종료해RunList1행·단일Summary·잔존native0확인. 기본PPO드라이버는변경하지않음.
- 최종native: outputs/runs/20261106T133233Z_lirf_native_inputs_574604f1/verification.json
- 독립감사: outputs/runs/20261106T133507Z_lirf_native_qualification_f44ee96f/verification.json
- 소프트웨어181개전부통과: outputs/runs/20261106T133713Z_unit_regressions_874924ba/verification.json
- 준비상태: outputs/runs/20261106T133823Z_readiness_45053f7b/readiness.json. 연구/본학습false. 상세docs/LIRF_NATIVE_INPUT_QUALIFICATION.md.
- 다음: 패키지가정/native기본값/현장실측차이원장작성, TAV/TAMP·토양pH/증발·품종/입도/초기N·관개수N·기상/투입일정의측정가능범위확정. 기술수용을농학통과로승격하지않음.

## 2026-11-06 작업 시작: 패키지·native 기본값·현장 차이 원장
- 기존 공개원자료와native수용결과를대조해실측/추정/채움/호환변경을항목별로분리한다. TAV/TAMP·토양pH/증발·품종/입도/초기N·관개수N·기상/일정의확인가능범위를기록하고자동현장보정없이입력기준을정한다.

## 2026-11-06 작업 시작: 온도 정의·native 전달 경로
- WTH AMP→IPWTH→WEATHER→STEMP 및 WGEN Climate 경로, 기본값 대체 조건과 모듈 선택을 고정 소스에서 확인한다. 진단 전용5조건(누락/명시20·5/관측기간TAV만/월평균차이전체/절반)을 사전 기록하고 실제 출력 전달과 기준 회귀를 확인한다. 농학 적합도에 따라 값을 선택하지 않는다.

- 최초5조건 완주 후 새 진단 입력기의 구분 열 위반을 실제 출력에서 발견. AMP27.161→7.2/13.580→3.6로 잘못 읽혀 후보2조건을 거부하고 원출력 보존. 구분 공백+소수2자리로 수정해 별도 재실행(native소스 변경0).

## 2026-11-06 작업 시작: D22 토양 수분특성·밀도·초기상태 매핑
- 공개 토양 원자료의 압력판 수분/밀도 정의와 층 깊이, D22/site5 연결을 확인한다. 측정치·전환에 필요한 조건·연도/처리 범위를 분리하고 기존 native층에 대한 측정 범위 원장을 작성한다. 임의 LL/DUL/SAT·바닥층 채움과 초기상태 날짜 이동은 하지 않는다.

## 2026-11-06 작업 시작: 연도별 수분 깊이·산출식 대조
- 방법문서와2008–2011년6처리 시트의 수분 깊이/단위/저장 산출식을 원 셀·수식으로 대조한다. 동일 상부깊이에서만 조건부 저장량 후보를 작성하고 설명-헤더 충돌의 적용범위를 확인한다. 원본수식 재계산·native입력변경·모형값선택은 하지 않는다.

## 2026-11-06 작업 시작: 수분결핍2건·포장FC집계 대조
- 2010-07-01 T2/T3의 원수분·SWD·FC셀/수식·날짜주변값과24연도처리의포장별FC평균/SD를대조한다. 확인된집계범위·불일치·불확실성한계를별도계약으로보존하고원자료역산수정과native매개변수선택은하지않는다.

## 2026-11-06 작업 시작: 일별 포장수분·오차·보정자료 가용성
- 보유원본의전체/숨김시트·외부참조·사전정의와공식저장소파일목록을대조한다. 일별포장SWC·상류계측/보정원자료·오차공분산의공개가용성을구분하고부재주장은확인범위로제한한다. 관련논문의정성적보정설명을수치오차로대용하지않으며외부연락/자료요청발송은하지않는다.

## 2026-11-06 작업 시작: LIRF 품종계수·보정연도·독립검증 역할
- 고정모형패키지계수/메타데이터·기존품종행·공개관련논문의보정/검증연도와설계를대조한다. 수치일치와동일품종/보정이력증명을구분하고동일현장자료의독립성한계를기록한다. 성능기반계수선택·검증split변경·신규학습은하지않는다.

## 2026-11-06 작업 시작: Fang2014 원문·정확계수 계보추적
- Fang2017이인용한2014장/DOI를확인하고공식공개원문과보정기록을검색한다. 논문에제시된계수와패키지의완전동일성/보정노출/정확파일이력을구분한다. 접근불가원문은추측하지않고수치유사성으로독립성승격하지않는다.

- 독립성게이트 신규검사 최초4건은 시스템 임시폴더의sandbox권한으로오류.기존검사와동일하게작업폴더tmp에격리하도록경로를수정해재검사한다.모형/원자료문제와구분.

## 2026-11-07 작업 시작: 공개10연구 재현입력·검증경로 통합우선순위
- 기존출처/프로토콜/시나리오/계보근거를재사용해10연구의endpoint·오차·토양/기상/관리/품종·피해매핑·독립성미비를표준상태로정리한다. 역할변경·접근제한재시도·가정채움없이현실행가능진단과외부근거필요작업을분리하고다음자료선별기준을고정한다.

## 2026-11-07 작업 시작: Oveysi2010 현장 재현입력 명세
- 고정출판사원문을쪽/표/문구로대조해위치·기간·토양·SC704·관리/물/N·피해/측정·오차의값과미확정을분리한다. 독립역할유지/튜닝0,임의기상·계수·일정채움0,명세완료와정량실행자격을구분한다.

## 2026-11-07 남은 내용 요약 정리
- 최신입력명세/통합우선순위/준비상태를대조해 `docs/REMAINING_WORK.md` 작성. 자료선별→농학/수지→기준선/설정동결→본학습/통계 순서와완료조건을분리했다.204검사·CPU/CUDA기술실행완료와정량준비0개/본학습false를구분.이번요약에서신규검사/native/학습실행0.다음은별도현장건조곡실보정자료선별.

## 2026-11-07 작업 시작: 별도 현장 건조곡실 보정자료 선별
- 기존독립검증10연구역할을유지하며새공개후보의공동수량/오차·전체현장입력·품종보정이력·피해기작을선별한다. 기본작물/물·N보정후보와실제피해/회복보정가능성을분리하고공식파일목록·취득범위·보류사유를보존한다.

## 2026-11-07 작업 시작: Nebraska 원자료·요약표·재현입력 자격 대조
- 원본 보존 상태에서 평균/SD·실험단위·강수 날짜·관수 중복/빈값과 원논문 설계·관리·품종 보정 이력을 대조한다. 정량 준비 승격 없이 확인 범위를 기록한다.

## 2026-11-07 작업 시작: Nebraska 부록·참조 관리/수리 논문 확보
- Schmer2020/Sindelar2019a 원문과 공식 부록의 공개 위치를 확인하고 재현입력/실험범위 연결을 대조한다. 미확보·출처 불일치는 유지하고 원본/활성 역할/연구 게이트를 변경하지 않는다.

## 2026-11-07 작업 시작: Iran관수×N 공개 실제파일 확인
- 원페이지의loading목록을부재로간주하지않고공식클라이언트/공개API문서를확인해파일목록과payload를취득한다. 원자료/설계/전체입력자격을분리하고활성역할/게이트를유지한다.

## 2026-11-07 작업 시작: Iran원논문/프로토콜 연결·입력공백명세
- DOI메타데이터/공식원출처연결과워크북부속정보를확인하고달력/N라벨/R계층해소가능성을명세한다. 원값/역할/게이트변경없이진단범위를분리한다.

## 2026-11-07 작업 시작: Kenya공개파일/원자료자격확인
- 공식익명API로파일목록과실제파일을보존하고원자료/분석산출물·동일포장5시즌의종속성·수량/달력/기상/관리입력범위를구분한다.활성레지스트리/게이트변경없이추적한다.

## 2026-11-07 작업 시작: Kenya분석대상/오차범위·원프로토콜연결
- primary/season-specific/productive-season/cross-site응답대상을교차대조하고원논문/수분보정/원수량·전체입력공개연결을점검한다. 추정값을원자료로승격하지않고기존역할/게이트를유지한다.

## 2026-11-07 작업 시작: Kenya원현장프로토콜/과거보정이력
- 공식대학저장소후보파일을확보해현재2010–2011자료와범위/품종/파종/시비/수량보정·AquaCrop보정노출을대조한다. 원값/활성역할/연구게이트는유지한다.

## 2026-11-07 작업 시작: Oliveira 실험 중복/단위/수분 기준 대조
- 보존 원문/부록/Dryad와 공식 학위논문 공개 서지를 대조해 원자료·계보·단위의 확인 범위를 기록한다.

## 본학습 전 BRPI 입력 대조와 Q/F 수지 재검산 (2026-11-09)

ESALQ 2002년 공개 관측과 DSSAT 일사량의 차이, 관수구 파종 시 질소량 차이 및 토양층 차이를 확인했다. 범용 토양 Q/F 16개에서 토양 C 출력 산술을 재검산했고 최종 9일 출력이 빠져 있음을 확인했다. 일별 모형 N은 후보 8개가 통과했고 기존 대조 4개가 실패했다. 연구 및 본학습은 보류 상태다. [진입 점검](docs/PRETRAINING_READINESS.md) · [검증 산출물](outputs/runs/20261109T051546Z_pretraining_source_audit_a35072c9/verification.json)

## 비교 실험 설정 변경 (2026-11-11)

정책 0~4의 a/b 두 벌, 동결 사슬, b0′, 달력일 감축(학습 13~112일, 평가 13·37·83일), 공통 시즌 평가·결과표·대비·교차 부트스트랩을 `src/mars_env/comparison.py`와 `scripts/run_comparison.py`에 구현했다. 날짜 값은 승인 전 제안값이다. 소규모 동작 확인은 검증 split에서만 했고 본학습은 시작하지 않았다. [사전등록 초안](docs/PRETRAINING_READINESS.md) · [단계 진입일 측정](outputs/runs/20261110T144310Z_stage_entry_rule_policy_c809d4f4/verification.json) · [동작 확인](outputs/runs/20261110T144753Z_policy_comparison_b8ff2c42/verification.json)

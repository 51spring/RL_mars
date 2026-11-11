# Plano 2016 무시비 기술 대조 설계

4월 13일 코어 수분을 시작 조건으로 사용한다. 4블록에 코어 아래 수분 2수준과 초기 무기질소 2수준을 교차해 16개 조건을 고정했다. 블록별로 예정 시비 0 kg N/ha인 처리 1 시험구에 연결했다. 별도 공통 비료 질소량은 원 관리표 결측으로 보존했다. [Plano 초기화 자격](RANSOM_WISCONSIN_PLANO_2016_INITIALIZATION_TIMING_AND_SOIL_HYDRAULICS.md) · [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

## 수분과 수리값

코어 관측 범위의 수분 저장량을 보존하고 코어 아래 200 cm까지는 가용수분 50% 또는 33 kPa 수분을 적용한다. FileX 정밀도에서 0–200 cm 초기 저장량은 491.38–557.78 mm이고, 코어 구간의 반올림 차이 절댓값은 최대 0.1512 mm다.

블록 3의 117–120 cm 관측 수분을 입력할 수 있도록 117–145 cm의 2Bt2 지도층 전체에 SSURGO 포화수분 상한 0.40을 적용했다. 네 블록에 동일한 규칙을 썼으며 나머지 층은 지도 대표값을 사용한다. 지도 층의 용적밀도·입도·pH·CEC를 새로 조회했다. 코어 구간의 유기탄소는 두께 가중하고 하부는 SSURGO 유기물 함량을 1.724로 나눈 대리값을 사용한다. 배수 계수 0.50 day⁻¹, 암거 없음, 지정 지하수위 없음은 기술 설정이다. [USDA 토양 수리값 정의](https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Table-Column-Descriptions-Report.pdf) · [DSSAT 입력 정의](https://dssat.net/wp-content/uploads/2011/10/DSSAT-vol2.pdf)

## 초기 무기질소 범위

2014–2015년 Ransom 무관수 시험 가운데 파종과 첫 처리 시비보다 먼저 채취했고, 네 블록 모두 질산 3깊이와 표층 암모늄을 보고한 16곳을 사용했다. 시험별 네 블록 중앙값을 구한 뒤 각 성분·깊이의 25·75백분위수를 적용했다. 이 값은 Plano 초기 상태의 민감도 가정이다.

| 입력 농도 mg N/kg | 낮은 가정 | 높은 가정 |
|---|---:|---:|
| 질산 0–30.48 cm | 3.1875 | 6.0625 |
| 질산 30.48–60.96 cm | 2.4375 | 5.0000 |
| 질산 60.96–91.44 cm | 1.4375 | 3.5000 |
| 암모늄 0–30.48 cm | 3.6125 | 5.3750 |
| 각 성분의 심층 결측 구간 | 0.01 | 0.50 |

FileX 입력 후보의 0–200 cm 무기질소 재고는 낮은 가정 약 44.49 kg N/ha, 높은 가정 약 103.75 kg N/ha다. 층 경계를 가로지르는 농도는 겹치는 두께와 모델 용적밀도로 환산했다. 입력 반올림의 성분별 최대 재고 차이는 0.0050399 kg N/ha다. 4월 29일 Plano 관측값은 초기화에 사용하지 않았다. [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g) · [DSSAT 초기 재고 환산 소스](../vendor/dssat-pdi-source/InputModule/INSOIL.for)

## 네이티브 대조 범위

4월 29일에는 블록 합성 시료, 6월 13일에는 무시비 시험구 관측과 각각 비교한다. 채취 시각이 미확인이므로 두 날짜 모두 당일 기상 처리 전후를 기록한다. P0157AMX 자동 보정 계수와 기술용 생태형 IB0001을 고정했다. 파종 깊이 5 cm와 콩 잔사 500 kg/ha는 이전 기술 대조에서 이어받은 가정이다. 수량과 두 날짜의 관측값으로 조건을 선택하지 않는다. [품종 계수 출처](https://doi.org/10.1016/j.eja.2025.127870)

다음은 기후 메타데이터와 표면 설정을 고정하고, 격리 DSSAT에서 16조건의 초기 재고·물·무기질소 수지와 두 날짜의 깊이별 상태를 대조하는 작업이다. 이번 설계 단계에서 네이티브 실행과 신규 정량 등록은 없었다. 소프트웨어 검사 204개가 통과했고 설계와 검증 파일을 같은 SHA-256으로 재현했다.

[고정 조건](../outputs/runs/20261108T150448Z_ransom_wisconsin_plano_2016_dated_initialization_technical_probe_design_2bb18f17/frozen_cases.json) · [검증 결과](../outputs/runs/20261108T150448Z_ransom_wisconsin_plano_2016_dated_initialization_technical_probe_design_2bb18f17/verification.json) · [재현 코드](../outputs/runs/20261108T150448Z_ransom_wisconsin_plano_2016_dated_initialization_technical_probe_design_2bb18f17/audit.py)

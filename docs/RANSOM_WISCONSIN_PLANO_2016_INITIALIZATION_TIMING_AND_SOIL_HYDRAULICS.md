# Plano 2016 초기화 시점과 토양 수리값 자격 검토

## 질소 관측의 날짜와 역할

원본 관리표 두 판본에 파종 4월 23일, 첫 처리 시비와 PPNT 4월 29일이 동일하게 기록됐다. PPNT 네 행은 블록 합성 시료이고 시험구 ID·처리 번호·비고가 비어 있다. 공통 시험 방법은 질산암모늄의 표면 살포와 파종일 주변의 첫 시비를 설명한다. Plano의 4월 29일 채취·시비 시각 및 순서를 확정할 현장 기록은 확인하지 못했다. 해당 값은 **4월 29일 블록별 관측**으로 유지하며 4월 13일 또는 파종일 초기 질소로 소급하지 않는다. [시험 방법](https://doi.org/10.2134/agronj2017.04.0207) · [Dryad 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

6월 13일에는 예정 질소 투입 0 kg N/ha인 처리 1 시험구가 블록별로 하나씩 연결됐다. 0–30.48 cm 질산태 질소는 13.5–31.5 mg N/kg, 30.48–60.96 cm는 9–13 mg N/kg이었다. 표층 암모늄도 네 개 모두 있다. 이 자료는 이후 모의 경로와 비교할 별도 시점이며, PPNT와 채취 단위가 다르다. PPNT 표층의 7일 혐기 배양 잠재 무기화 4개도 확인했다. 실험실 잠재량은 현장 일별 무기화량의 직접 관측으로 사용하지 않는다. 자료 논문은 센서 신뢰도 문제로 현장 수분 시계열을 공개 자료에서 제외했다고 설명한다. [자료 논문](https://doi.org/10.1002/agj2.20812)

## 수분 재배분과 강수

4월 13일 코어의 수분 저장량을 SSURGO 대표층 경계와 겹치는 두께로 재배분했다. 상부 5 cm와 코어 끝을 별도 경계로 둔 뒤 관측 구간을 독립 적산해 4블록 모두 반올림 전 저장량이 일치함을 확인했다. 코어 아래 200 cm까지는 가용수분 50%와 33 kPa 수분 두 가정을 구분했다. 8개 후보의 0–200 cm 초기 저장량은 491.25–557.63 mm다.

| 블록 | 코어 끝 cm | 실측 기반 수분 저장량 mm |
|---|---:|---:|
| 1 | 109 | 419.70 |
| 2 | 102 | 370.83 |
| 3 | 120 | 448.82 |
| 4 | 104 | 402.65 |

코어층 평균 비교에서는 대표 포화 근사값을 넘는 층이 없었다. 수리 경계에서 다시 나누면 블록 3의 **117–120 cm** 수분 0.39552 cm³/cm³가 그 대표층의 0.31을 넘고, 지도 상한 0.40 안에는 들어온다. 관측값과 지도 대표·상한을 각각 보존했다. 수리 가정을 명시하고 입력 가능 여부를 확인하기 전에는 이 구간의 FileX를 생성하지 않는다. [USDA 수리값 정의](https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Table-Column-Descriptions-Report.pdf)

4월 13–29일 보고일 기준 강수는 시험 자료에서 24.9 mm, 30.42 km 떨어진 Lake Geneva 0.6 ENE 관측소에서 26.0 mm였다. 관측소 자료는 시험구 강수를 대체하지 않았다. 두 채취 시각 사이의 실제 포장 강수는 확정할 수 없다. [NOAA 일별 관측](https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=US1WIWW0002&startDate=2016-04-13&endDate=2016-04-29&dataTypes=PRCP&format=csv&units=metric)

다음 단계에서는 **4월 13일 코어 수분, 명시적 초기 질소 가정, 예정 무시비 처리**를 사용한 기술 대조를 설계한다. 4월 29일과 6월 13일 관측은 날짜별 비교에 남긴다. 신규 네이티브 실행과 정량 등록은 없었다. 검증 결과를 같은 SHA-256으로 재현했고 소프트웨어 검사 204개가 통과했다.

[검증 결과](../outputs/runs/20261108T145938Z_ransom_wisconsin_plano_2016_initialization_timing_and_soil_hydraulics_ee1391b4/verification.json) · [NOAA 원응답](../outputs/runs/20261108T145938Z_ransom_wisconsin_plano_2016_initialization_timing_and_soil_hydraulics_ee1391b4/noaa_regional_prcp.csv) · [재현 코드](../outputs/runs/20261108T145938Z_ransom_wisconsin_plano_2016_initialization_timing_and_soil_hydraulics_ee1391b4/audit.py)

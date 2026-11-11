# Waseca 2016 날짜별 초기 수분·무기질소 자격

4월 22일 파종 전 무기질소와 4월 26일 토양 코어를 각각 관측 시점에 보존했다. Dryad 입력 명세, NOAA 강수 응답과 USDA 포화수분 범위 응답의 SHA-256을 실행 근거에 기록했다. [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

## 두 채취일 사이 강수

NOAA Waseca Southern Research and Outreach Center 관측소 USC00218692는 시험 관리표 좌표에서 10.09 km 떨어져 있다. 아래 NOAA 일계의 관측 시각은 모두 현지 08:00이며 품질 플래그는 비어 있다. Ransom 자료의 해당 기간 강수는 모두 Pioneer 보간값이다. [NOAA 관측소](https://www.ncei.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USC00218692/detail) · [NOAA 속성 정의](https://www.ncei.noaa.gov/pub/data/cdo/documentation/GHCND_documentation.pdf)

| 보고일 | Ransom 보간 mm | NOAA 관측 mm |
|---|---:|---:|
| 4월 22일 | 0.0 | 1.5 |
| 4월 23일 | 0.0 | 0.0 |
| 4월 24일 | 12.9 | 0.0 |
| 4월 25일 | 3.6 | 10.9 |
| 4월 26일 | 0.0 | 0.8 |
| 보고일 합계 | 16.5 | 13.2 |

NOAA에서 22일 08:00부터 26일 08:00까지 집계한 양은 11.7 mm다. 인근 강수는 확인됐고, 포장 내 강수량과 두 시료의 채취 시각은 확인되지 않았다. 두 강수 자료는 서로 다른 위치·집계 구간의 비교 근거로 사용한다.

## 코어 수분과 USDA 포화수분 범위

블록별 SSURGO 주 구성 토양의 층별 하한·대표·상한을 코어 구간과 겹치는 두께로 가중했다. USDA 포화수분은 거의 포화된 상태의 체적수분 추정값이다. 코어 20층 중 하한을 초과한 층은 18개, 대표값을 초과한 층은 9개, 상한을 초과한 층은 5개다. 상한 초과는 네 블록에 걸쳐 있다. 이 숫자는 층별 대리값과의 비교 결과다. [USDA 수리값 정의](https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Table-Column-Descriptions-Report.pdf)

실측 용적밀도와 가정 입자밀도 2.60, 2.65, 2.75 g/cm³로 총공극률도 계산했다. 코어 수분이 총공극률을 넘는 층은 각각 3개, 3개, 0개였다. 입자밀도 실측이 없어 이 비교로 코어 오류 여부나 현장 포화수분을 확정할 수 없다. 수분을 잘라내거나 모델 포화값을 관측에 맞춰 높이는 처리는 적용하지 않았다. [USDA 공극률과 포화수분 정의](https://nrcs.usda.gov/sites/default/files/2022-10/SSIR45.pdf)

## 기술 대조에 사용할 조건

- **4월 22일**은 질산·암모늄 관측의 기준일이다. 해당 날짜의 물은 33 kPa 수분과 대표 포화 근사 수분으로 기술 대조한다. 두 값은 초기 수분의 가정으로 기록한다.
- **4월 26일**은 코어 수분 비교일이다. 모델의 당일 기상 처리 전후를 각각 비교한다. 26일 무기질소 관측은 미확보다.
- 기술 대조를 실행하기 전에 질산 91.44 cm 아래와 암모늄 30.48 cm 아래의 결측 처리, 관측 구간과 DSSAT 층의 질량 대응, 하부 수리 경계 및 배수 가정을 고정한다. 원본 Ransom 강수와 보간 플래그를 유지한다.

공통 관측 초기 상태의 자격은 보류했다. 네이티브 재현과 신규 농학 정량 등록은 대기 상태다. 검증 요약은 동일 SHA-256으로 재현했고 소프트웨어 검사 204개가 통과했다.

[검증 결과](../outputs/runs/20261108T143216Z_ransom_waseca_2016_dated_water_n_initialization_qualification_136fe29b/verification.json) · [NOAA 원응답](../outputs/runs/20261108T143216Z_ransom_waseca_2016_dated_water_n_initialization_qualification_136fe29b/noaa_usc00218692_prcp.csv) · [USDA 원응답](../outputs/runs/20261108T143216Z_ransom_waseca_2016_dated_water_n_initialization_qualification_136fe29b/horizons_saturation.json) · [재현 코드](../outputs/runs/20261108T143216Z_ransom_waseca_2016_dated_water_n_initialization_qualification_136fe29b/audit.py)

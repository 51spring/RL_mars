# Becker 2016 4블록 초기화 후보와 공개 근거

2026-11-08 한국 시간. 4블록 각각에 Hubbard와 Mosford를 연결해 4월 21일 초기화 후보 8개를 만들었다. 물·무기질소·유기탄소 가정은 각 후보에서 분리했다. 4월 26일 수분 코어와 수량은 초기화 후보 선택에 사용하지 않았다. 소프트웨어 검사 204개가 통과했다. [후보·원자료 해시](../outputs/runs/20261108T092154Z_ransom_becker_2016_four_block_initialization_evidence_5331edc3/verification.json)

## 공개 자료의 적용 범위

| 항목 | 확인한 자료와 적용 범위 |
|---|---|
| 장기 기온 | 21.5 km 떨어진 St. Cloud 공항의 1991–2020 기온 평년값으로 DSSAT 후보 `TAV=6.1°C`, `AMP=16.25°C`를 산출했다. 월 API 응답은 metric 요청에도 공식 월별 표의 °F 값과 일치해 월 진폭을 °C로 환산했다. 연평균 응답은 °C였다. [NOAA 월별 공식표](https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020&endDate=9996-12-31&format=pdf&startDate=0001-01-01&stations=USW00014926) · [DSSAT 기후 입력 정의](https://dssat.net/wp-content/uploads/2011/10/DSSAT-vol3.pdf) |
| 2016년 토양온도 | 106.6 km 떨어진 Sandstone 6 W에서 4월 21–26일의 5·10·20·50·100 cm 관측 30개를 확보했다. 5 cm는 5.5–8.5°C, 100 cm는 4.8–5.5°C였다. 이 관측소의 해당 기간 강수는 57.3 mm로 Becker의 39.2 mm와 차이가 있어 지역 비교용으로 유지했다. [NOAA USCRN 2016 일별 원자료](https://www.ncei.noaa.gov/pub/data/uscrn/products/daily01/2016/CRND0103-2016-MN_Sandstone_6_W.txt) · [NOAA 관측 정의](https://www.ncei.noaa.gov/access/crn/measurements.html) |
| 잔사 | 전작 콩과 파종 시 피복률 25%는 Dryad에 있다. SALUS의 콩 계수 0.00032 ha/kg와 지수 피복식으로 환산한 표면 건물중은 약 899 kg/ha다. 이 값은 파종 시 피복에 근거한 타 연구의 관계식 추정이며 4월 21일 잔사량은 결측이다. 10·500·900 kg/ha를 민감도 후보로 기록했다. [Dryad](https://doi.org/10.5061/dryad.66t1g1k2g) · [Basso 등 Table 2](https://doi.org/10.4081/ija.2006.677) |
| 심층 유기탄소 | SSURGO의 Hubbard·Mosford 9개 층을 기존 수리층의 키·깊이와 연결했다. 4블록 코어 아래에서는 최하층 실측값 0.03–0.05%를 연장하는 경우와 SSURGO 유기물 낮음·대표·높음을 1.724로 나눈 경우를 분리했다. 200 cm까지의 하부 대표층에서 환산한 범위는 Hubbard 0–0.174%, Mosford 0–0.290%다. 이 범위는 지도 대표층 값에 기반한다. [USDA SSURGO](https://www.nrcs.usda.gov/resources/data-and-reports/soil-survey-geographic-database-ssurgo) · [US EPA 환산 가정](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P100ZPSA.txt) |

## 초기화 후보

- 4월 21일 수분은 실측값이 비어 있어 각 대표층의 가용수분 50%와 33 kPa 배수상한을 기술 조건으로 구성했다. 모델 깊이 0–200 cm에서 Hubbard는 121.79·185.98 mm, Mosford는 153.03·217.59 mm다.
- 4월 21일 질소 관측은 원본 깊이와 블록을 보존했다. 질산태 질소는 91.44 cm보다 깊은 구간, 암모늄태 질소는 30.48 cm보다 깊은 구간에 0.01·0.50 mg N/kg 두 가정을 적용했다. 층별 환산 재고는 별도 시료 구간 적산과 일치했다. 두 값은 감도 조건이다.
- 4월 26일 수분 코어 18개 층은 날짜를 유지해 별도 비교 관측으로 등록했다. 실측 용적밀도 결측 8개는 그대로 표시했다.

다음은 후보에서 비교 조건을 고정해 네이티브 DSSAT의 4블록 초기 재고와 4월 26일 코어 비교를 실행하는 작업이다. 이번 단계의 8개 후보는 입력 명세이며 현장 재현·농학 정량 등록은 0건이다. [재현 코드](../outputs/runs/20261108T092154Z_ransom_becker_2016_four_block_initialization_evidence_5331edc3/audit.py) · [소프트웨어 검사](../outputs/runs/20261108T092154Z_ransom_becker_2016_four_block_initialization_evidence_5331edc3/unit_tests.json)

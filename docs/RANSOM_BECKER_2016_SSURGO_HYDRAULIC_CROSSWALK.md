# Becker 2016 시험구와 SSURGO 층별 수리값 대조

2026-11-08 한국 시간. Dryad의 WGS84 경계 64개를 포장 ID·블록·처리로 입력 명세와 대조했다. USDA SDA의 폴리곤 교차 계산에서 시험구 64개 전체와 관리표 좌표가 모두 MN141의 D62A, `mukey=2765436`에 해당했다. 시험구별 면적은 같은 WGS84 평면에서 산출한 교차 면적 비율이며 합계 1을 허용오차 0.000001로 확인했다. 이번 조회에서 반환된 조사 자료 버전은 2026-09-07이다. [Dryad 경계 자료](https://doi.org/10.5061/dryad.66t1g1k2g) · [USDA 공간 조회 문서](https://sdmdataaccess.nrcs.usda.gov/documents/AdvancedQueries.html)

| 주요 구성 토양 | 지도 단위 구성비 | 층 수 | 18개 코어 층 모래 / 점토 평균 절대 차이 | 실측 10개 층 용적밀도 평균 절대 차이 |
|---|---:|---:|---:|---:|
| Hubbard | 60% | 4 | 4.18 / 1.62 %p | 0.150 g/cm³ |
| Mosford | 35% | 5 | 8.30 / 3.89 %p | 0.089 g/cm³ |

코어와 겹치는 대표 토양층을 두께로 가중했다. Hubbard가 토성에서 더 가까웠고 Mosford가 용적밀도에서 더 가까웠다. 구성비는 지도 단위의 대표 비율이며 시험구나 블록에 구성 토양을 지정할 근거는 확보되지 않았다. 두 주요 토양을 별도 민감도 후보로 유지한다. 소수 구성은 Sandberg 3%, Isan 1%, Duelm 1%다. [USDA SSURGO 지도 단위 설명](https://www.nrcs.usda.gov/resources/data-and-reports/soil-survey-geographic-database-ssurgo)

5개 구성 토양의 20개 층에서 `SLLL` 후보는 1,500 kPa 수분, `SDUL` 후보는 33 kPa 수분, `SSAT` 후보는 거의 포화된 상태의 수분을 체적분율로 변환했다. 20개 층 모두 후보 수분값이 하한 < 배수상한 < 포화수분 순서였다. 10 kPa 수분도 별도로 저장했으며 Mosford의 상부 3개 층(0–41 cm)은 이 값이 결측이다. `SSKS`는 µm/s에 0.36을 곱해 cm/h로 환산했다. Hubbard의 대표값은 32.40 cm/h, Mosford는 상부 0–41 cm에서 10.08 cm/h, 41–200 cm에서 33.12 cm/h였다. SSURGO의 수분과 전도도는 대표층 자료이며 Becker 포장에서 측정한 값은 확보되지 않았다. [USDA 수리값 필드 정의](https://sdmdataaccess.nrcs.usda.gov/documents/TableColumnDescriptionsReport.pdf)

4월 26일 실측 기반 체적수분 10개는 두 주요 후보 모두에서 하한과 포화수분 사이였으며 각 후보에서 4개 층이 33 kPa 후보값을 넘었다. 이 비교는 채취일 수분과 대표층 값의 관계를 보여준다. 초기일이나 배수상한 선택의 검증에는 별도의 시간 경로 대조가 필요하다. 다음은 4월 21일 질소와 4월 26일 수분의 역할을 분리하고, 초기 수분·깊은 층 질소 결측을 명시한 기술 시나리오의 DSSAT 초기 재고를 대조하는 작업이다. 현장 재현과 농학 정량 등록은 0건이다.

[검증 결과](../outputs/runs/20261108T090216Z_ransom_becker_2016_ssurgo_hydraulic_crosswalk_134964f6/verification.json) · [재현 코드와 조회 SQL](../outputs/runs/20261108T090216Z_ransom_becker_2016_ssurgo_hydraulic_crosswalk_134964f6/audit.py) · [소프트웨어 검사](../outputs/runs/20261108T090216Z_ransom_becker_2016_ssurgo_hydraulic_crosswalk_134964f6/unit_tests.json)

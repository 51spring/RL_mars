# Lewis 2015 초기 수리값과 P1498AM 외부 보정 자료

Lewis의 2015년 3월 31일 수분 코어와 블록별 질소 시료를 대조했다. 같은 날의 두 자료는 블록 수준에서 연결했다. Lewis 수량값은 평가용으로 보존했다. [후보 선별](RANSOM_INDEPENDENT_BASELINE_SCREEN.md) · [Dryad 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

## Lewis 수분과 질소 초기 재고

USDA Soil Data Access에서 코어 4개 좌표와 관리 좌표 모두 IA155의 **Marshall silty clay loam, 2–5% 경사, 9B**에 연결됐다. 지도 대표층은 0–200 cm의 6층이며 제한층 깊이는 해당 응답에서 결측이다. 지도층의 대표 포화 수리전도도는 3 μm/s(1.08 cm/h)다. 이 값은 지도 구성 단위의 대리값이다. 현장 배수 속도나 DSSAT의 일별 배수계수로 해석하지 않았다. [USDA 조회 서비스](https://sdmdataaccess.nrcs.usda.gov/WebServiceHelp.aspx) · [Marshall 계열 설명](https://soilseries.sc.egov.usda.gov/OSD_Docs/M/Marshall.html)

| 블록 | 0–120 cm 코어 환산 수분 mm | 보고 성분·깊이의 환산 무기질소 kg N/ha |
|---|---:|---:|
| 1 | 446.89 | 64.41 |
| 2 | 444.82 | 61.45 |
| 3 | 410.94 | 62.46 |
| 4 | 455.79 | 69.85 |

중량수분과 실측 용적밀도가 있는 코어 19층을 지도층 경계에서 29개 구간으로 나눴다. 수분 저장량은 분할 전후에 일치했다. 모든 구간에서 수분이 지도 대표 33 kPa 값보다 높았고, 그중 24개는 해당 지도 범위의 높은 값도 넘었다. 29개 모두 지도 포화 추정 범위의 낮은 값 이내였다. 지도 0–120 cm 저장량은 33 kPa에서 334.75 mm, 대표 포화에서 601.80 mm다. 33 kPa 값을 초기 수분 상한으로 쓰면 네 블록에서 76.19–121.04 mm를 잃는다. 지도값 기준으로는 코어 수분을 줄이지 않고 보존할 수 있으며, 현장 수분 보유 곡선과 배수는 별도 검증 대상이다. [SSURGO 항목 정의](https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Table-Column-Descriptions-Report.pdf)

질소는 질산태 N 0–91.44 cm와 암모늄태 N 0–30.48 cm에 한해, 각 시료 깊이와 겹치는 코어의 실측 밀도를 이용해 환산했다. 더 깊은 성분의 공백은 유지했다. 코어 아래 120–200 cm 초기 수분과 3월 31일 이후 파종까지의 배수·질소 이동은 미확인이다. 4월 29일 파종 전까지 29일에 기록된 강수는 86.5 mm이므로 3월 31일 수분을 파종일 재고로 옮겨 쓰지 않았다. [날짜별 입력 근거](RANSOM_INDEPENDENT_BASELINE_SCREEN.md)

## P1498AM 외부 자료

**Shelby 2015, Missouri.** USDA Ag Data Commons의 Transforming Drainage CSV 13개를 받아 공개 목록의 크기와 MD5로 검증했다. 같은 품종의 옥수수 24시험구를 파종·수확·시비·수량·배수 처리표에 연결했다. 자유 배수, 무배수, 지하관수 병행 제어배수가 각각 8시험구다. 4월 3일 첫 비료 작업부터 9월 24일 수확까지 기온·강수·일사 175일이 이어진다. 24개 곡실 수량의 기준 수분은 15.5%이며 건물 환산은 원 수량에 0.845를 곱했다. 파종일과 수확일은 원 논문과 일치했다. [공식 원자료](https://doi.org/10.15482/USDA.ADC/1521092) · [Helmers 등 Table 3](https://doi.org/10.1002/agj2.20579)

- CSV의 시비 질소는 4월 3일 26.90과 4월 23일 235.38의 합 262.28 kg N/ha이며, 논문 Table 3의 258보다 4.28 많다. 두 출처를 그대로 보존했다.
- 2015년 관수 관리표에 시점과 양 미상이라는 기록이 있고 일별 관수표의 Shelby 행은 0개다. 제어배수·지하관수 처리명으로 관수 날짜나 양을 부여하지 않았다.
- 2015년 토양 특성 120행은 모두 수확 뒤 11월 18일 자료다. 파종 전 토양 수분·무기질소와 시험구별 생육단계 날짜·생체량·식물체 N의 보정 목표는 확보되지 않았다. 2,700°F·day는 카탈로그 숙기값으로 보존했다.

**Bruns 2014–2016, Mississippi.** P1498AM의 15.5% 기준 곡실 수량과 100립중이 연도별로 공개됐다. P1498AM 수량은 관수·무관수와 반복을 합한 평균이다. 강수표에도 여러 날을 합친 행이 있다. 검토한 공식 원문·출판 기록에서 포장별 원수량, 전층 초기 상태와 CERES 계수는 확인하지 못했다. [USDA 공개 원문](https://www.ars.usda.gov/ARSUserFiles/60663500/Publications/Bruns/2019/Bruns_2019_AJ_111-2-1-7.pdf)

**Kaur 2013–2015, Missouri.** 별도 Novelty 시험에서 P1498AM의 침수×질소 처리, 깊이별 초기 토양 특성 일부와 식물체 질소 관측을 확인했다. 현 단계에서는 실험 처리 단위의 원자료와 보정 입력을 확보하지 못했다. [Kaur 등 원문](https://doi.org/10.3390/agronomy8070102)

Lewis는 검증 후보로 보존했다. 지도 토양값은 수리 민감도 대조에 쓸 수 있고, Shelby·Bruns·Kaur는 외부 보정 자료 후보로 분리했다. 현재 자료에서는 출처가 확인된 P1498AM CERES 계수 6개와 생태형을 확정하지 못해 품종 보정, Lewis 현장 재현 및 정량 등록을 보류했다. 소프트웨어 검사 204개가 통과했고 두 검산 JSON의 SHA-256을 각각 재현했다.

[Lewis 검산](../outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/lewis_verification.json) · [Shelby 원자료 대조](../outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/shelby_verification.json) · [Lewis 재현 코드](../outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/audit_lewis.py) · [Shelby 재현 코드](../outputs/runs/20261108T153336Z_ransom_lewis_2015_hydraulics_and_cultivar_7204f5e4/audit_shelby.py)

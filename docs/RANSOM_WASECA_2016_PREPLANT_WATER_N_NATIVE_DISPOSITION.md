# Waseca 2016 파종 전 네이티브 결과 활용 판정

Waseca의 32조건은 입력 전달, 200 cm 수분 출력과 물·무기질소 장부를 검증한 기술 근거로 보관한다. 무관수 포장 재현과 독립 농학 정량 등록은 보류했다. 이번 단계에서는 저장된 네이티브 출력을 재검산했다. [네이티브 대조](RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_TECHNICAL_PROBE.md)

## 깊이별 수분 부족

모델층과 실측 코어층을 각각 60 cm에서 나눠 수분을 적산했다. 관측 범위의 끝은 블록별 92–119 cm다. 4월 26일 처리 후 32개 모두 하부 구간의 모의 수분이 관측보다 작았다.

| 초기 수분 | 26일 처리 후 0–60 cm 평균 차이 mm | 26일 처리 후 60 cm–코어 끝 평균 차이 mm | 하부 차이 범위 mm |
|---|---:|---:|---:|
| 33 kPa 수분 | −40.43 | −68.48 | −104.40~−38.70 |
| 대표 포화 근사 수분 | −29.35 | −62.00 | −100.82~−31.88 |

SSURGO 상한까지 각 층의 수분을 채운 정적 대조에서도 블록 1의 코어 총수분은 8.20 mm 더 많았다. 다른 블록은 전체 적산에서는 상한 이내였지만, 네 블록 모두 상한을 넘는 개별 층이 있었다. 이 계산은 지도 대리값으로 설명 가능한 저장량의 범위를 보여 주며 배수·수위의 원인을 확정할 근거는 아니다. [SSURGO 항목 정의](https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Table-Column-Descriptions-Report.pdf)

## 배수와 지하수위 근거

- Ransom 관리표는 시험 40의 암거 설치를 ‘없음’으로 기록한다. 검토한 공개 시험 자료에서 4월의 포장별 지하수위와 배수 유량 시계열은 확인하지 못했다. [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)
- USDA SSURGO의 4월 월별 습윤층 시작 깊이는 Cordova L81A 대표 0 cm(범위 0–20 cm), Le Sueur L90A 대표 45 cm(범위 30–60 cm)다. 토양 구성 단위의 월별 추정값으로 보존했다. 2016년 4월 26일 시험구 수위로 사용하지 않았다. [USDA Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/documents/SoilDataAccessQueryGuide.pdf)
- 미네소타 DNR이 공개한 Southern Research and Outreach Center의 2016년 자료는 60인치까지의 가용수분 차트다. 4월 26일에 인접한 표기일은 4월 18일과 5월 2일이고 시험 40과 연결할 근거가 없다. DNR의 Waseca 카운티 지하수 지도 편은 공개 진행표상 착수 전이다. 지역 자료는 보조 근거로 보관했다. [지역 수분 자료](https://www.dnr.state.mn.us/climate/agwx/soil_moisture.html) · [카운티 지도 진행표](https://www.dnr.state.mn.us/waters/groundwater_section/mapping/county-geo-atlas.html)

시험구 수위·배수량이나 현장 수리값으로 하부 경계를 정할 근거가 부족하다. Waseca를 기술 진단으로 보존하고 코어에 맞춘 배수·포화 계수 조정이나 수량 재현 등록은 보류했다.

## 후속 후보

Zhen 등의 위스콘신 추가 시험을 Dryad에 연결했다. 두 시험은 동일한 좌표와 2016년 366일 전체의 동일 기상값을 공유한다. 연구의 품종 보정 지점과는 구분되며, 이미 원 연구의 추가 평가에 쓰였다. 이후 MARS에서는 동일 기상 아래 토양·질소 반응을 대조할 후보로 분류한다. [Zhen 등 원문](https://doi.org/10.1016/j.eja.2025.127870) · [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

- **Plano 2016, 시험 49**를 입력 명세 우선 후보로 정했다. 코어 20층의 수분·실측 용적밀도가 있고, 4블록 모두 파종 전 질산 3깊이와 표층 암모늄이 있다.
- **Lorenzo 2016, 시험 48**은 토심·암편 차이를 검토할 짝 지점으로 보관한다. 코어 9층 중 실측 용적밀도는 5층이며, 가장 깊은 질산 구간은 4블록 중 1블록만 있다. 원 관리표에는 2–4블록의 생육 차이와 얕고 암편이 많은 토양이 기록돼 있다.

두 후보의 입력 명세에서 깊이·날짜·관리 근거를 먼저 대조한다. 신규 네이티브 실행과 정량 등록은 0건이다. 소프트웨어 검사 204개가 통과했고 저장 출력에서 검증 JSON을 동일한 체크섬으로 재현했다.

[검증 결과](../outputs/runs/20261108T144954Z_ransom_waseca_2016_preplant_water_n_native_disposition_3a3bac89/verification.json) · [USDA 원응답](../outputs/runs/20261108T144954Z_ransom_waseca_2016_preplant_water_n_native_disposition_3a3bac89/ssurgo_spring.json) · [지역 수분 원자료](../outputs/runs/20261108T144954Z_ransom_waseca_2016_preplant_water_n_native_disposition_3a3bac89/dnr_waseca_soil_moisture_2016.png) · [재현 코드](../outputs/runs/20261108T144954Z_ransom_waseca_2016_preplant_water_n_native_disposition_3a3bac89/audit.py)

# Waseca 2016 무관수 질소 전이 입력 명세

Dryad 시험 40의 원본 통합문서 7개를 공개 파일 목록의 SHA-256과 대조했다. 4블록 64시험구에 16개 질소 처리 일정이 각각 한 번씩 배정됐으며, 무기질소 자료의 시험구 행 132개를 시험구별 시비량과 대조했다. 후속 후보의 수량값은 분석에 사용하지 않았다. [Ransom 원자료](https://doi.org/10.5061/dryad.66t1g1k2g)

| 입력 | 확인 범위 |
|---|---|
| 관리 | 5월 6일 파종, 87,720립/ha, 이랑 76 cm, 전작 대두. 첫 처리 시비일 5월 16일, 추비일 6월 27일, 수확일 10월 24일. 관수 기록 0건이며 공통 시비의 질소는 원본 관리표에 0으로 기록됐다. |
| 기상 | 4월 22일–10월 24일 186일. 기온은 현장 HOBO 161일과 Pioneer 보간 25일이다. 강수는 MRMS 161일과 Pioneer 보간 25일이다. 일사 186일은 Bristow–Campbell 추정값이다. |
| 초기 무기질소 | 4월 22일 블록별로 질산태 N 0–30.48, 30.48–60.96, 60.96–91.44 cm와 암모늄태 N 0–30.48 cm를 채취했다. 이보다 깊은 해당 성분의 값은 결측으로 보존했다. |
| 초기 수분 | 4월 26일 코어 4개, 총 20층이다. 실측 용적밀도와 중량수분으로 체적수분을 계산했다. 코어 최심층 경계는 블록별 118, 101, 92, 119 cm다. |
| 품종 | P0157AMX의 수동·자동 보정 계수를 각각 원본 그대로 보존했다. Waseca는 원 연구 평가 지점이다. |

## 지도 단위와 수리값

USDA Soil Data Access의 MN161 지도에서 관리표 좌표와 블록 2–4 코어는 L81A Cordova clay loam, 블록 1 코어는 L90A Le Sueur loam에 교차했다. 이 결과는 관리표 좌표와 코어 지점에 적용된다. 전체 시험구의 경계별 지도 단위는 별도 근거가 필요하다. [USDA SSURGO](https://www.nrcs.usda.gov/resources/data-and-reports/ssurgo-portal) · [Cordova 토양 계열](https://soilseries.sc.egov.usda.gov/OSD_Docs/C/CORDOVA.html)

두 지도 단위의 주 구성 토양인 Cordova 85%와 Le Sueur 80%의 대표층 4개씩에서 1,500 kPa·33 kPa 수분, 포화 근사 수분과 포화전도도를 가져왔다. 포화 근사 수분을 코어 깊이와의 중첩 길이로 가중 평균했을 때 관측 체적수분이 이 대리값을 넘은 층은 20개 중 9개였다. 원자료와 대표값을 각각 보존했으며 이 차이를 해소할 현장 수리값은 미확보다. [USDA 열 정의](https://sdmdataaccess.nrcs.usda.gov/documents/TableColumnDescriptionsReport.pdf)

## 재현 진입 조건

무기질소 채취와 코어 채취는 4일 차이다. 그 사이 4월 24일 12.9 mm, 25일 3.6 mm가 기록됐고 모두 Pioneer 보간값이다. 두 날짜를 합친 초기 상태의 관측 자격은 보류한다. 다음 단계에서는 코어 수분과 대표 포화수분의 불일치, 4일 간 강수의 독립 자료, 심층 무기질소 결측을 함께 대조해 날짜별 기술 초기화 조건을 정한다. 현장 생태형과 시비 위치·깊이는 추가 확인 항목이다. [Zhen 등 품종 연구](https://doi.org/10.1016/j.eja.2025.127870)

DSSAT 현장 재현은 대기 상태다. 신규 정량 등록 0건이며 연구용·본 학습 진입은 보류했다. 소프트웨어 검사 204개를 통과했고 입력 명세와 검증 요약을 동일한 SHA-256으로 재현했다.

[입력 명세](../outputs/runs/20261108T142505Z_ransom_waseca_2016_rainfed_input_dossier_68cc84d2/input_dossier.json) · [검증 결과](../outputs/runs/20261108T142505Z_ransom_waseca_2016_rainfed_input_dossier_68cc84d2/verification.json) · [재현 코드](../outputs/runs/20261108T142505Z_ransom_waseca_2016_rainfed_input_dossier_68cc84d2/audit.py)

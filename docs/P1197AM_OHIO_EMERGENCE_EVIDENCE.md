# P1197AM Ohio 출아 관측과 Shumway 활용 자격

Shumway 2016의 품종 P1197AM을 외부에서 재배한 Ohio State Western Agricultural Research Station의 2017–2019 시험을 대조했다. Nemergut 학위논문과 2021년 논문은 같은 세 해, 같은 두 토양, 같은 깊이 처리를 보고한다. 학위논문 PDF를 확보했고 학술지 원문 HTML에서 Table 3을 확인했다. Wiley 부록 링크는 다운로드 시 HTTP 403을 반환했다. [OhioLINK 학위논문](https://rave.ohiolink.edu/etdc/view?acc_num=osu1587990466400837) · [Nemergut 등 원문](https://doi.org/10.1002/agj2.20701)

## 출아 관측의 해상도

시험은 Strawn–Crosby와 Kokomo 두 토양에 목표 파종 깊이 25·51·76 mm를 적용했다. 토양·연도별 네 블록이 설계됐고 파종 후 14일간 일별 출아를 조사했다. 각 포장 회귀곡선에서 구한 출아 시점의 깊이별 주변평균은 아래와 같다. 학술지 Table 3의 값은 두 토양과 세 해를 통합했다. [학술지 Table 3](https://doi.org/10.1002/agj2.20701)

| 목표 깊이 mm | 10% 출아 일 | 50% 출아 일 | 90% 출아 일 | 10–90% 출아 구간 일 |
|---|---:|---:|---:|---:|
| 25 | 3.8 | 6.2 | 11.8 | 7.9 |
| 51 | 4.4 | 5.9 | 7.9 | 3.5 |
| 76 | 4.9 | 6.4 | 8.6 | 3.8 |

출아 구간은 원 표 값을 유지했다. 표시 정밀도로 차감한 값과 최대 0.1일 차이가 있다. 50% 출아는 5.9–6.4일에 모여 있지만 10–90% 구간은 얕은 처리에서 더 길다. 학위논문 Table 6의 토양별 집계와 학술지 Table 3의 깊이별 통합 집계를 구분했다. 각 깊이의 20분 센서·일별 출아 원시값과 포장별 공동 관측은 공개본에서 확인하지 못했다.

학위논문 부록 그림 6–17의 12개 패널에는 연도·토양별 누적 출아와 가용수분 곡선이 있다. 달력 기준 6개와 토양 적산온도 기준 6개는 같은 실험의 다른 축 표현이다. 2019년 달력 그림 14·16의 축에는 6월 1일 기준이 표시돼 있고 본문과 학술지의 파종일은 6월 4일이다. 축의 원 날짜 인덱스가 없으므로 숫자를 임의로 3일 이동하지 않았고, 곡선을 포장별 원관측으로 수치화하지 않았다. [학위논문 본문 9·19쪽과 부록 42·44쪽](https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=osu1587990466400837&disposition=inline)

## Western 기상 확인

학위논문이 월별 집계에 사용한 기관의 Western 관측소(ID 13)에서 2017–2019년 4–10월 공개 일별 보고서를 받았다. 기대 642일 중 **636일**에 강수·최고/최저·평균기온·일사 값이 있었다. 2018년 8월 18일과 10월 11·12·15일, 2019년 10월 23·24일은 응답에 행이 없었다. 누락일은 0으로 채우지 않았다. [Western 관측소](https://weather.cfaes.osu.edu/stationinfo.asp?id=13)

강수는 기관 문서에서 단위가 명시된 인치 표시값을 25.4배 했다. 단위 표기가 없는 다른 화면의 강수 숫자는 cm로 해석할 때 636일 모두 두 화면의 표시 정밀도 안에서 일치했다. 기온은 °F와 °C 표시값을 독립 대조했고 일사는 두 화면의 Langley 값이 같았다. 5–10월 18개 월별 집계에서 학위논문 대비 최대 절대 차이는 **평균기온 0.058 °C, 강수 0.984 mm**였다. 강수 최대 차이는 누락일이 없는 2019년 6월에 발생했다. 이 대조는 관측소 자료와 논문 월별 요약의 대응을 뒷받침한다. 포장 종자 깊이의 토양온도·수분과 관측소 자료는 별개다. [CFAES 관측 단위](https://weather.cfaes.osu.edu/instruments.asp) · [학위논문 Table 2](https://rave.ohiolink.edu/etdc/view?acc_num=osu1587990466400837)

## DSSAT 적용 범위

고정 CERES-Maize 소스에서 출아는 파종 깊이가 반영된 열시간 기준을 지나면 한 개 날짜로 기록된다. 품종계수 P1은 그 뒤의 유년기 길이에 관여한다. Ohio의 출아 분포는 깊이별 초기 출아 과정의 관측 근거로 남긴다. 표준 네이티브 출력에서 10–90% 출아 구간을 직접 검증하거나 이 표로 CERES 품종계수 여섯 개를 보정할 수 없다. [CERES-Maize 생육 소스](../vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_PHENOL.for#L585)

검토한 공개 보정 연구에서 P1197 또는 P1197AM의 APSIM·Hybrid-Maize 모형 사용은 확인했다. Shumway에 사용할 정확한 P1197AM CERES 계수·생태형은 확보하지 못했다. Ohio는 출아 관측 비교로 보존하고, Shumway 수량은 평가용으로 보존했다. 신규 모형 실행과 정량 등록은 0건이다. 검산 결과를 같은 SHA-256으로 재현했고 소프트웨어 검사 204개가 통과했다. [APSIM 보정 연구](https://doi.org/10.1002/csc2.20857) · [Hybrid-Maize 연구](https://doi.org/10.3390/w16050788)

[검산 결과](../outputs/runs/20261108T155545Z_p1197am_ohio_emergence_evidence_97206da7/verification.json) · [재현 코드](../outputs/runs/20261108T155545Z_p1197am_ohio_emergence_evidence_97206da7/audit.py) · [학위논문 PDF](../outputs/runs/20261108T155545Z_p1197am_ohio_emergence_evidence_97206da7/nemergut_thesis.pdf)

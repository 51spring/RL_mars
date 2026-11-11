# Battaglia 시험장 일별 기상과 관수 자료 대조

켄터키대 기상센터의 보안 주소에서 논문이 인용한 Spindletop 농장 조회 양식을 열고, 각 연도 4월 1일~9월 30일 일별 요약을 조회했다. 각 183일, 총 366일의 최고·최저기온, 강수, 일사를 보존했다. 날짜 누락·중복, 최저기온이 최고기온보다 큰 행, 음수 강수·일사, 0 일사는 없었다. 논문 부록의 생육 조사일 42개가 일별 기록에 모두 연결됐다. GDD 수치 자체의 재현은 별도다. [켄터키대 조회 양식](https://weather.uky.edu/php/farm_www.php) · [Battaglia 등, 방법과 그림 2](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

| 연도 | 파종~일반 수확 | 농장 강수 | 논문에서 역산한 강수 | NOAA 공항 강수 | 논문 관수 집계 |
|---|---|---:|---:|---:|---:|
| 2012 | 4월 26일~9월 13일, 141일 | 321.1mm | 약 321mm | 459.6mm | 22일, 약 278mm |
| 2013 | 5월 2일~9월 20일, 142일 | 789.9mm | 약 790mm | 702.6mm | 4일, 약 45mm |

양 끝 날짜를 포함해 집계했다. 2012년 R2 100%의 8월 30일 조기 수확은 별도 처리로 보존했다. 농장 일별 자료에서 2012년 6월·7월 강수는 2013년보다 각각 69.5%·73.2% 적어 논문에 보고된 70%·73%와 일치한다. NOAA 렉싱턴 공항은 두 해에 각각 약 +139mm·−87mm 차이가 있어 외부 비교로만 보관했다. [논문 기상 결과](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths) · [NOAA 공항 관측소](https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND%3AUSW00093820/detail)

원응답의 표기 단위는 °F, inch, langley이며 시간 표기는 EST다. CSV에 원 단위와 °C, mm, MJ/m² 환산 열을 함께 보존했다. 강수 원자료의 표시 정밀도는 0.01inch로 약 0.254mm다. 농장과 논문 역산 강수의 0.1mm 미만 차이는 산술 대조 결과이며 개별 관측의 정확도를 나타내지 않는다. IPM의 2012·2013 링크는 동일한 2012년 파일을 가리킨다. 파일에는 온도 열이 있지만 강수·일사·관수나 별도 관측소 식별자가 없어서 모형 입력에 사용하지 않았다. 기상센터 관측소 로그는 확보한 내용에 2011년 강수계 결측만 기록돼 있었다. [대학 IPM 아카이브](https://ipm.mgcafe.uky.edu/swcb) · [농장 관측소 로그](https://weather.uky.edu/spinlog.txt)

농장 기상 응답에 관수 항목은 없다. 그림 2 개별 페이지는 직접 요청 시 HTTP 403이었으며, 공개 본문에서 집계와 그림 설명을 확인했다. 관수 날짜·일별 투입량은 미확보다. 공항 강수와의 차이나 계절 관수 총량에서 이벤트를 역산하지 않았다. 정량 보정과 본 학습은 보류한다. 다음은 Loradale 토양의 층별 특성·초기 상태와 두 품종의 DSSAT 계수 출처를 확인하는 작업이다. [논문 그림 2](https://www.researchgate.net/figure/A-Daily-maximum-average-temperature-C-rains-mm-and-irrigation-mm-for-Lexington_fig2_321402722)

## 재현 근거

- 원응답, 조회 인자, SHA-256은 [출처 기록](../outputs/runs/20261107T063827Z_battaglia_spindletop_weather_a2d097ca/sources.json)에 있다.
- [정리한 일별 관측](../outputs/runs/20261107T063827Z_battaglia_spindletop_weather_a2d097ca/spindletop_daily.csv)과 [대조 결과](../outputs/runs/20261107T063827Z_battaglia_spindletop_weather_a2d097ca/weather_summary.json)를 보존했다.
- 재현 시 원응답 파일 두 개와 NOAA CSV를 새 폴더에 복사한 뒤, 프로젝트 가상환경에서 `scripts/audit_battaglia_weather.py`에 그 폴더와 이전 Battaglia 검증 JSON 경로를 전달한다. 검증 JSON은 파종·수확일과 논문 집계의 출처다.

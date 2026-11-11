# Battaglia 옥수수 포장 회복 자료 대조

2018년 곡실 수량 논문과 2019년 군락 광 차단 논문은 켄터키 렉싱턴 Spindletop Farm의 **2012·2013년 같은 시험**이다. 2019년 논문은 동일 처리의 수량을 2018년 논문에서 가져왔다고 명시한다. 2014년 학위논문 초록도 지역·연도·품종 성숙도·이랑 폭·피해 처리에서 일치한다. 학위논문 본문을 확보하지 못해 포장 ID 단위의 대조는 미완료이며, 이번 감사에서는 세 문서를 한 시험 계열로 계산했다. 계수 보정과의 독립성은 별도 확인이 필요하다. [2018 수량 논문](https://doi.org/10.2134/agronj2017.06.0322) · [2019 군락 논문](https://doi.org/10.2135/cropsci2018.05.0337) · [대학 학위논문](https://uknowledge.uky.edu/pss_etds/56/)

## 확인한 재현 입력

P1360HR·P2088YHR 두 품종, 38·76cm 이랑, 무피해·V7 100%·V14 50%/100%·R2 50%/100%의 6개 처리를 4개 블록에 배치한 분할구 설계다. 품종이 주구, 이랑 폭이 세구, 피해가 세세구다. 파종량은 94,000종자/ha이며, UAN 225kg N/ha와 K₂O 135kg/ha를 두 해 모두 적용했다. 물과 질소는 서로 교차한 실험 요인이 아니다. [2019 방법 공개 본문](https://www.researchgate.net/publication/333626126_Effects_of_Corn_Row_Width_and_Defoliation_Timing_and_Intensity_on_Canopy_Light_Interception) · [2018 표 1 공개 본문](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

| 연도 | 파종 | 질소 투입 | 수확 | 관수 집계 | 부록 생육 조사일 |
|---|---|---|---|---|---:|
| 2012 | 4월 26일 | 4월 23일 | 9월 13일. R2 100%만 8월 30일 | 22일, 약 278mm | 21일 |
| 2013 | 5월 2일 | 5월 1일 | 9월 20일 | 4일, 약 45mm | 21일 |

2018년 부록 A1·A2의 날짜와 누적 GDD 헤더 42쌍을 보존했다. 처리별 생육단계 표는 해당 단계에 도달한 식물 비율 50% 기준이며, 조사일을 피해 시행일로 대입하지 않았다. 2012년 관수 개시는 표 1의 V10–V11과 결과의 V11/V12가 달라 원 이벤트가 필요하다. 그림 2는 일별 강우·최고기온·관수를 그린 자료다. 그림에서 임의로 수치화하지 않았고 시험장 일별 원기상과 실제 관수 이벤트 파일은 미확보다. Loradale 미사질 양토와 표층 0–20cm 화학 분석은 확인했으나 전체 토양층과 초기 물·무기태 N은 미확인이다. [2018 방법·표 1·부록](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

## 회복과 수량의 관측 범위

- 2013년 V7 100% 처리의 평균 IPAR은 V8에서 23%, VT에서 75%였다. VT는 피해 후 약 25일 시점이다. IPAR은 군락이 차단한 광합성유효복사 비율이다. 녹색 잎 면적·건물중이 얼마나 회복했는지는 별도 측정이나 관측 변환이 필요하다. [2019 공개 본문, 표 4·5 설명](https://www.researchgate.net/publication/333626126_Effects_of_Corn_Row_Width_and_Defoliation_Timing_and_Intensity_on_Canopy_Light_Interception)
- V7 100%는 펼쳐진 잎 일곱 장을 제거하고 잎집이 만든 줄기 부분도 절단했다. V14에서는 덜 펼쳐진 위쪽 잎을 남겼고, 50% 처리는 펼쳐진 잎의 끝쪽 절반을 자르는 방식이다. 이 처리명은 모형의 균일 잎 건물중 제거율로 환산하지 않았다. [2019 방법 공개 본문](https://www.researchgate.net/publication/333626126_Effects_of_Corn_Row_Width_and_Defoliation_Timing_and_Intensity_on_Canopy_Light_Interception)
- 2018년 수량은 포장당 약 2.33m²에서 충분히 발달한 낟알이 10개 이상인 이삭을 채취해 65°C에서 항량까지 건조한 뒤 탈곡한 낟알 무게를 면적으로 환산했다. 15.5% 표준수분 환산을 가정하지 않았다. 모든 곡실을 집계하는 DSSAT 수확량과 비교하려면 이삭 선별 및 2012년 R2 100% 조기 수확의 영향을 확인해야 한다. 포장별 원수량과 반복 오차 자료는 확보하지 못했다. [2018 수확 방법 공개 본문](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

학위논문 PDF와 출판사 원문 파일의 직접 요청은 HTTP 403이었다. 대학 초록과 웹에서 확인 가능한 저자 본문을 사용했으며 PDF 원표를 렌더링해 대조하는 검사는 수행할 수 없었다. 다음은 시험장 기상 아카이브의 날짜별 자료와 2018년 그림 2의 관수 기록을 분리해 확보 가능성을 확인하는 단계다. 같은 농장의 대학 IPM 기상 보조 자료는 출처와 일자·단위 대조를 거쳐야 한다. [대학 IPM 아카이브](https://ipm.mgcafe.uky.edu/swcb)

확인한 숫자와 출처별 접근 결과는 `outputs/runs/20261107T062535Z_battaglia_recovery_input_audit_caf7619e/verification.json`에 있다. 독립 농학 검증과 본 학습은 보류 중이다.

후속 감사에서 두 해의 농장 일별 기상을 확보했다. 날짜별 관수 기록은 미확보다. [Spindletop 기상 대조](BATTAGLIA_SPINDLETOP_WEATHER.md)

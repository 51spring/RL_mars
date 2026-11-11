# Battaglia 누적 GDD와 무피해 대조 생육단계

Spindletop 일별 최고·최저기온과 논문 부록 A1·A2의 조사일 42개를 연결했다. 일 최고·최저기온의 평균에서 8°C를 빼고 음수는 0으로 처리한 뒤, 파종일과 조사일을 모두 포함해 더하면 **42개 모두 논문의 정수값으로 반올림된다**. 기온 상한은 적용하지 않았다. 2012년 두 날짜는 정확히 반 단위여서 0.5를 올리는 규칙을 적용했다. 논문 본문은 단위를 °C·일로 적지만 기준온도와 반올림 규칙을 명시하지 않아, 이 계산은 공개 기록으로 재현한 결과다. [논문 부록 A1·A2](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths) · [Spindletop 일별 조회](https://weather.uky.edu/php/farm_www.php)

| 연도 | 조사일 수 | 8°C 방식 평균 절대차 | 최대 절대차 | 켄터키대 표준 10~30°C 방식 평균 절대차 |
|---|---:|---:|---:|---:|
| 2012 | 21 | 0.29°C·일 | 0.50°C·일 | 138.03°C·일 |
| 2013 | 21 | 0.26°C·일 | 0.44°C·일 | 112.22°C·일 |

고정된 계산 방식 5개와 파종일·조사일 포함 여부 4가지를 비교했다. 8°C는 CERES-Maize 문서의 일부 품종계수가 사용하는 기준온도다. 이 대조에서 쓴 단순 일평균을 DSSAT 내부 생육 계산에 대입하거나 품종계수로 환산하지 않았다. [켄터키대 옥수수 GDD 지침](https://www2.ca.uky.edu/agc/pubs/agr/agr202/agr202.pdf) · [DSSAT 품종계수 정의](https://dssat.net/wp-content/uploads/2011/10/DSSAT-vol2.pdf)

연도 2개×품종 2개×이랑 폭 2개의 무피해 대조에서 **생육 관측 168개, 도달 구간 48개**를 정리했다. 구간은 목표 단계보다 확실히 앞선 마지막 관측일 다음부터, 목표 단계 이상이 확실한 첫 관측일까지다. 예를 들어 VT/R1은 VT 이상이지만 R1 도달을 단정할 수 없는 복합 표기로 처리했다. V7·V14·VT·R1·R2·R6 구간의 폭은 2~16일이었다. 이 구간은 논문에 실린 50% 생육단계 요약에서 계산했으며, 개체별 도달일·피해 시행일·신뢰구간으로 사용하지 않는다. [논문 생육 조사 방법과 부록](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

| 연도 | R1 도달 구간, 네 대조군 공통 | R6 도달 구간, 네 대조군 공통 |
|---|---|---|
| 2012 | 6월 30일 이후~7월 10일까지 | 8월 6일 이후~8월 22일까지 |
| 2013 | 7월 7일 이후~7월 17일까지 | 8월 26일 이후~9월 9일까지 |

다음은 논문의 IPAR 측정값을 DSSAT에서 관측 가능한 광 차단 출력과 연결할 수 있는지 대조하는 단계다. 관수 이벤트, 시험 포장 토양·초기 상태, 독립 품종계수는 미확보다. 농학 검증과 본 학습은 보류 중이다.

[날짜별 GDD 대조](../outputs/runs/20261107T064829Z_battaglia_gdd_phenology_167aefb4/gdd_comparisons.csv) · [무피해 관측](../outputs/runs/20261107T064829Z_battaglia_gdd_phenology_167aefb4/control_observations.csv) · [도달 구간](../outputs/runs/20261107T064829Z_battaglia_gdd_phenology_167aefb4/control_stage_intervals.csv) · [검증 결과](../outputs/runs/20261107T064829Z_battaglia_gdd_phenology_167aefb4/verification.json)

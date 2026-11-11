# FDACS 21894 옥수수 곡실 수량 재구성

2026-11-08 한국 시간. FACETS 워크북을 읽기 전용으로 열어 2015–2017년 FDACS 옥수수 탈곡 표본 **180개**를 포장·블록·관수·질소 키로 일대일 연결했다. 시즌당 60개로, 관수 5수준×질소 3수준×4블록이다. 수분을 세 번 측정한 값과 워크북에 기록된 평균은 180개 모두 0.1% 보고 정밀도에서 일치했다. [FACETS 원자료](https://doi.org/10.15482/USDA.ADC/1521079)

보고서 pp. 7, 10–11의 두 이랑×각 20 ft×이랑 간격 30 in을 적용해 명목 면적 **9.290304 m²**를 계산했다. 탈곡 무게에 `(100 − 시료 수분 %) / (100 − 15.5)`를 곱해 시장 수분으로 보정했다. 포장별 kg/ha와 56 lb/bu 기준 bu/ac를 둘 다 보존했다. 보고서에는 밀도가 낮으면 대표 이랑을 선택했다고 적혀 있어 면적은 프로토콜 기준으로 표기했다. 2018·2020 FACETS Access의 별도 환산식은 이 계산에 사용하지 않았다. [FDACS 수확 방법](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf#page=10)

## 보고서 대조

p. 28에 정수로 적힌 관수 평균 15개와 질소 평균 8개가 **모두 반올림 범위(±0.5 bu/ac)에서 일치**했다. 최대 차이는 약 0.47 bu/ac다. 2015년 F2는 본문에 수치가 없으며, 원자료 재구성은 180.39 bu/ac, Figure 67의 막대 판독값은 약 179 bu/ac다. 원자료 평균은 표본의 산술평균으로, 보고서의 분산분석이나 유의성 검정을 재실행하지 않았다. [결과 본문](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf#page=28) · [Figure 67](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf#page=108)

| 2017년 관수 | 원자료 재구성 | 보고서 본문 | Figure 66 막대 추정 |
|---|---:|---:|---:|
| I1 | 200.25 | 200 | 약 202 |
| I2 | 202.96 | 203 | 약 183 |
| I3 | 194.43 | 194 | 약 187 |
| I4 | 194.24 | 194 | 약 189 |
| I5 | 92.09 | 92 | 약 125 |

단위는 bu/ac다. Figure 66의 2017년 패널은 눈금에 맞춰 정규화한 다섯 막대 높이가 2016년 패널과 동일했다. 2017년 수치 대조에는 원자료 및 본문을 사용하고, 그래프는 출처 내 불일치로 기록했다. 나머지 19개 막대 판독값은 원자료 평균과 약 1.7 bu/ac 이내였으며 그림 판독 해상도만큼 불확실하다. [Figure 66](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf#page=107)

45개 관수×질소 처리–시즌 평균과 표본 표준편차를 보관했다. 반복구별 일일 관리 원장과 DSSAT 보정·평가 분리는 여전히 미확보라 정량 검증 등록은 0건이다. 다음은 관수를 주구, 질소를 세구로 둔 설계에 맞춰 블록별 대비를 계산하고, 해당 결과를 독립 검증에 쓸 수 있는 범위를 판정하는 작업이다. [시험 설계](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf#page=4)

[수량 180개](../outputs/runs/20261108T044436Z_fdacs_21894_grain_yield_reconstruction_d38ca783/plot_grain_yield.json) · [대조 결과](../outputs/runs/20261108T044436Z_fdacs_21894_grain_yield_reconstruction_d38ca783/verification.json) · [재현 코드](../outputs/runs/20261108T044436Z_fdacs_21894_grain_yield_reconstruction_d38ca783/audit.py)
# Becker 2016 조기 질소 공급 경로 진단

2026-11-08 한국 시간. 1블록 시험구 109(처리 비료 0)의 수동 품종 계수와 Hubbard·Mosford 토양을 사용했다. 격리 이미지에서 기준 2개와 경로별 변경 6개를 실행했다. 기준 실행은 기존 모의의 기상, 토양 질소·수분, 식물 질소·생육 및 유기물 수지의 일별 자료를 재현했다. 관수수 질소와 기존 관리 입력을 공통으로 유지했다. [고정 조건](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/frozen.json) · [검증 결과](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/verification.json)

- **초기 안정 풀 증가**는 비안정 유기물 풀의 절반을 SOM3로 옮기며 기존 98% 상한을 유지했다. 총 초기 유기탄소는 같았다. DSSAT의 풀별 C:N 초기화로 인해 초기 유기질소는 Hubbard 9,157 → 11,607, Mosford 12,225 → 13,929 kg N/ha로 함께 바뀌었다. 이 결과에는 풀 배분과 초기 유기질소 재고의 영향이 함께 들어 있다.
- **분해 감속**은 초기 풀과 재고를 유지하고 CENTURY의 SOM1·2·3 분해 흐름을 절반으로 줄였다. 탄소 흐름에 연결된 질소 계산을 사용했다.
- **질산 이동 지연**은 명목 하단 깊이가 60 cm 이하인 층의 이동 가능 질산 비율을 절반으로 줄였다. 첫 실행에서 일별 두께가 미세하게 변해 Hubbard의 명목 60 cm 층이 일부 날짜에 제외됐다. 명목 깊이로 조건을 고정해 다시 실행했고, 층별 비율과 이동량을 확인했다. [진단 패치](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/patch_probe.py) · [첫 실행 자료](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1/runtime.json)

| 토양·조건 | 6월 6일 누적 순무기화 kg N/ha | 6월 6일 표층 질산태 N mg N/kg | 7월 19일 지상부 N kg N/ha |
|---|---:|---:|---:|
| Hubbard 기준 | 120.94 | 17.20 | 235.4 |
| Hubbard 안정 풀 증가 | 65.17 | 9.28 | 132.2 |
| Hubbard 분해 감속 | 67.69 | 9.67 | 145.5 |
| Hubbard 질산 이동 지연 | 120.26 | 18.41 | 233.5 |
| Mosford 기준 | 69.42 | 12.25 | 148.9 |
| Mosford 안정 풀 증가 | 38.81 | 6.87 | 91.4 |
| Mosford 분해 감속 | 38.31 | 6.95 | 95.1 |
| Mosford 질산 이동 지연 | 68.87 | 13.11 | 148.0 |
| 시험구 109 관측 | 미확보 | 2.50 | 40.9 |

표층 질산태 N의 비교 깊이는 0–30.48 cm다. 이동 지연 조건에서 표층에 가까운 경계의 누적 순하향 질산 이동은 Hubbard 35 cm에서 9.34 → 2.76, Mosford 33 cm에서 9.05 → 4.14 kg N/ha였다. 이 설정에서는 이동이 줄면서 표층 농도가 올랐다. 모형 경계가 다르므로 두 토양의 이동량은 각각 자기 기준과 비교했다. 전체 층의 하단 용탈 누적값은 기존 용탈 출력의 자릿수 안에서 일치했다. 네이티브 무기질소 장부의 전체 기간 최대 절대 잔차는 0.0002 kg N/ha였다.

시험한 분해 감속은 과대를 줄였으나 두 토양 모두 현장 관측보다 높았다. 기술 인자값을 현장 자료에 맞춰 선택하지 않았다. 다음은 코어 총질소의 단위·깊이·가용 범위를 확인해 초기 유기질소를 별도로 제약할 수 있는지 검토하고, 풀 배분과 초기 N 재고의 효과를 분리하는 작업이다. 농학 정량 등록은 0건이며 소프트웨어 검사 204개가 통과했다. [재현 코드](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/probe.py) · [소프트웨어 검사](../outputs/runs/20261108T101400Z_ransom_becker_2016_early_n_supply_mechanism_probe_441fe3e1_nominal_depth/unit_tests.json)

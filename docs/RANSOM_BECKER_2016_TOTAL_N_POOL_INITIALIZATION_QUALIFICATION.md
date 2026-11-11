# Becker 코어 총질소와 CENTURY 초기 풀 배분 검증

2026-11-08 한국 시간. Becker 4블록 코어 18개 층에서 총질소 0.007–0.110% N을 확인했다. 원자료는 LECO FP-528 분석으로 기록돼 있다. 코어 깊이는 블록별 100–110 cm이며 채취일은 4월 26일이다. 4월 21일 초기화에 사용할 때는 채취일 차이와 코어 아래 총질소 결측이 남는다. 네 블록의 원자료 행과 측정 용적밀도 결측을 보존했다. [Dryad 원자료](https://doi.org/10.5061/dryad.66t1g1k2g) · [고정 입력과 원자료 행](../outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/frozen.json)

## 총질소 입력과 기본값 대체

격리 DSSAT에서 1블록·처리 비료 0의 Hubbard와 Mosford를 실행했다. 코어 총질소를 깊이 겹침으로 층에 대응시켜 `SLNI`에 넣고, 네이티브 층별 유기질소 요청량을 검산했다. `SLNI`를 mg/kg으로 환산한 뒤 초기 질산태·암모늄태 질소를 빼고 층의 토양 질량을 곱했다. 이 환산은 모두 일치했다. [SOILDYN 환산](../vendor/dssat-pdi-source/Soil/SoilUtilities/SOILDYN.for)

| 총질소 입력 조건 | Hubbard 기본값 대체 사유 | Mosford 기본값 대체 사유 |
|---|---|---|
| 코어 밖 결측 유지 | 하단 깊이 140·200 cm 층 결측 | 상부 5개 층에서 C:N 범위 이탈 및 하단 깊이 144·200 cm 층 결측 |
| 최하 코어층 총질소를 하부에 연장 | 하단 깊이 140·200 cm 층에서 C:N 범위 이탈 | 상부 5개 층과 하단 깊이 144·200 cm 층에서 C:N 범위 이탈 |
| 하부 연장 및 안정 풀 증가 | 7개 층에서 C:N 범위 이탈 | 7개 층에서 C:N 범위 이탈 |

층 깊이는 모형층 하단을 표시한다. 한 층이라도 조건을 충족하지 못하면 이번 CENTURY 실행에서는 전층 초기 유기질소가 기본값으로 대체됐다. 여섯 코어 입력 조건 모두에서 이 동작을 확인했고 해당 C:N 조정 경고 문구는 출력되지 않았다. 원자료 총질소의 입력 단위는 확인했으며, 현재 토양 프로필에서 현장 초기 유기질소를 제약하는 데에는 적용 자격을 보류했다. [CENTURY 초기화 경로](../vendor/dssat-pdi-source/Soil/CENTURY_OrganicMatter/SOMINIT_c.for) · [층별 진단](../outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/verification.json)

## 층별 초기 유기질소를 고정한 기술 비교

기준·안정 풀 배분의 층별 허용 재고 범위가 겹치는 구간의 중간값을 공통 초기 유기질소로 사용했다. 두 조건 모두 같은 규칙으로 각 풀의 C:N 허용 범위 안에서 질소를 배분했다. 현장 측정값을 사용해 중간값을 선택하지 않았다. 아래 차이는 총 유기탄소와 각 층의 총 유기질소를 고정한 상태에서 풀 배분과 그에 따른 풀별 C:N 조합을 바꾼 결과다.

| 토양 | 공통 초기 유기질소 kg N/ha | 6월 6일 순무기화 kg N/ha, 기준 → 안정 풀 증가 | 6월 6일 표층 질산태 N mg N/kg, 기준 → 안정 풀 증가 |
|---|---:|---:|---:|
| Hubbard | 10,881.39 | 197.94 → 53.71 | 28.47 → 7.48 |
| Mosford | 13,549.76 | 111.51 → 35.04 | 19.69 → 6.12 |

14개 실행을 완료했다. 기준과 안정 풀 조건 4개는 이전 진단의 일별 출력과 일치했다. 전체 기간 네이티브 무기질소 장부의 최대 절대 잔차는 0.0003 kg N/ha였다. 이 설정에서 안정 풀 배분의 효과는 초기 총 유기질소를 고정해도 남았다. 시험구 109의 표층 관측값 2.50 mg N/kg보다는 높았다.

다음은 현장 총질소·유기탄소의 공동 가용 범위와 C:N 제약을 4블록에서 점검하고, 측정 범위 밖 층이나 전체 프로필 기본값 대체를 어떻게 처리할지 명시하는 작업이다. 현장 보정·정량 등록은 0건이다. 소프트웨어 검사 204개가 통과했다. [재현 코드](../outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/probe.py) · [진단 패치](../outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/patch_probe.py) · [소프트웨어 검사](../outputs/runs/20261108T102223Z_ransom_becker_2016_total_n_pool_initialization_qualification_64c4348b/unit_tests.json)

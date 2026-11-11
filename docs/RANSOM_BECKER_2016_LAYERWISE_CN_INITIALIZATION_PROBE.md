# Becker 2016 층별 유기질소 초기화 대조

2026-11-08 한국 시간. 처리 비료 0의 4블록×2개 대표 토양에서 기존 전층 기본값 대체 8조건과 층별 초기화 8조건을 비교했다. 두 조건은 동일한 코어 총질소 입력과 토양·관리 파일을 사용했다. 격리 패치는 코어가 완전히 덮고 C:N 허용 범위에 든 층만 유기질소 요청량으로 초기화한다. 나머지 층의 세 유기질소 풀은 전층 기본값 경로의 값을 유지한다. [고정 입력](../outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/frozen.json) · [진단 패치](../outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/patch_layerwise.py)

- 코어 기반 요청량 24개를 층별 허용오차 0.002 kg N/ha 이내에서 확인했다. 결측·부분 관측·범위 이탈을 포함한 60개 층은 기준과 풀별 질소 재고가 같았다. 탄소 풀도 기준과 일치했다.
- 허용 층이 0개였던 2·4블록의 네 조건은 토양 및 식물 질소 일별 결과가 기준과 일치했다. 16개 실행이 완료됐으며 전체 기간 네이티브 무기질소 장부의 최대 절대 잔차는 0.0006 kg N/ha였다. [검산 결과](../outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/verification.json)

| 블록·토양 | 반영한 층 | 추비 전 표층 질산태 N 기준 → 층별 / 관측 (mg N/kg) | 7월 19일 지상부 N 기준 → 층별 / 관측 (kg N/ha) |
|---|---:|---:|---:|
| 1 Hubbard | 8 | 17.20 → 14.12 / 2.50 | 235.4 → 196.5 / 40.9 |
| 1 Mosford | 4 | 12.25 → 12.25 / 2.50 | 148.9 → 149.2 / 40.9 |
| 3 Hubbard | 8 | 17.20 → 15.91 / 4.00 | 247.3 → 236.5 / 35.4 |
| 3 Mosford | 4 | 11.62 → 11.63 / 4.00 | 155.6 → 157.2 / 35.4 |

추비 전 값은 6월 6일 0–30.48 cm다. 층별 반영으로 Hubbard의 과대가 줄었지만 관측과 차이가 남았다. Mosford의 모의값 변화는 작았다. 4월 26일 코어로 4월 21일 초기 상태를 대신하는 가정은 미검증이다. 기술 옵션의 농학 정량 등록은 0건이다.

다음은 Becker의 현장 재현 자격을 종합 판정하고, Becker 결과로 계수를 조정하지 않은 상태에서 독립 자료가 있는 후속 지점 후보의 초기 토양과 관리 입력을 확인하는 작업이다. 소프트웨어 검사 204개가 통과했다. [재현 코드](../outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/probe.py) · [소프트웨어 검사](../outputs/runs/20261108T140917Z_ransom_becker_2016_layerwise_cn_initialization_probe_4d7358ef/unit_tests.json)

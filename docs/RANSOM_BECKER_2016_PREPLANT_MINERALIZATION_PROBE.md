# Becker 2016 파종 전 순무기화와 무기질소 장부 대조

2026-11-08 한국 시간. Becker 1블록의 4월 21일 초기화에서 Hubbard·Mosford 각각 5개 조건을 실행했다. 동일한 격리 이미지에서 상세 출력만 활성화한 두 기준 조건의 4월 21–26일 무기질소 재고는 이전 결과와 모두 일치했다. 관수·시비 및 수량 보정은 적용하지 않았다. [검증 결과](../outputs/runs/20261108T091554Z_ransom_becker_2016_preplant_mineralization_provenance_probe_8204151d/verification.json)

원자료에서 전작 콩, 파종 시 추정 잔사 피복률 25%, 3월 29일 디스크 작업과 4월 27일 경운을 확인했다. 잔사 건물중과 파종 전 토양온도 관측은 확보되지 않았다. 민감도 비교에는 콩 잔사 10·500 kg/ha를 가정했다. 토양온도 입력도 모델 기본값(평균 20°C, 진폭 5°C)과 민감도 값(10°C, 10°C)을 비교했다. 유기탄소는 1블록 코어의 0–106 cm 실측값을 모델층에 두께로 가중했고, 106–200 cm에는 최하부 실측값인 0.03%를 연장했다. [원자료 항목과 조건 정의](../outputs/runs/20261108T091554Z_ransom_becker_2016_preplant_mineralization_provenance_probe_8204151d/inputs.json)

| 조건 | Hubbard 순무기화 kg N/ha | Mosford 순무기화 kg N/ha |
|---|---:|---:|
| 기술 기준 유기탄소 0.50%, 잔사 10 kg/ha | 38.26 | 32.36 |
| 코어 유기탄소와 하부 연장 | 17.97 | 9.79 |
| 콩 잔사 10 kg/ha | 38.26 | 32.36 |
| 콩 잔사 500 kg/ha | 38.60 | 32.70 |
| 토양온도 10°C / 10°C 가정 | 28.66 | 23.51 |

순무기화는 4월 26일까지의 누적 모의값이다. 이번 조건 범위에서는 코어 유기탄소로 바꿨을 때 감소가 가장 컸다. 콩 잔사 질소 함량에는 DSSAT의 콩 기본값 1.2%가 적용됐다. 4월 26일 무기질소 실측값은 없어 모의값을 검증 관측과 비교할 수 없다.

이전 간이 장부에는 토양 내 질소 가스 재고와 배출이 빠져 있었다. 두 기준 조건에서 26일까지 토양 내 가스 재고는 Hubbard 0.153, Mosford 0.163 kg N/ha 증가했고 누적 배출은 각각 0.0102, 0.0039 kg N/ha였다. 가스 재고·배출을 포함한 `SoilNiBal.OUT`의 6일 무기질소 수지는 10개 조건 모두 네이티브 잔차 절댓값 0.0001 kg N/ha 이내였다. 공개된 상세 출력 항목으로 장부를 독립 재계산한 6일 잔차의 최대 절댓값은 0.001 kg N/ha였다. 이 판정의 범위는 기술 조건의 무기질소 장부다. [DSSAT 상세 장부 항목](../vendor/dssat-pdi-source/Soil/Inorganic_N/SoilNiBal.for)

다음은 Becker 파종 전 토양온도·잔사량과 하부 유기탄소의 공개 근거를 확인하고, 자료가 비는 항목을 범위로 남겨 4블록 초기화 후보를 구성하는 작업이다. 현장 재현 및 농학 정량 등록은 0건이다. 소프트웨어 검사 204개가 통과했다. [재현 코드](../outputs/runs/20261108T091554Z_ransom_becker_2016_preplant_mineralization_provenance_probe_8204151d/probe.py) · [소프트웨어 검사](../outputs/runs/20261108T091554Z_ransom_becker_2016_preplant_mineralization_provenance_probe_8204151d/unit_tests.json)

# 실패일 흡수 질소가 휴경 전환에서 지워지는 위치

2026-11-10 한국 시간. 기존 Q 저온 대조·처리 4개를 일회용 DSSAT 컨테이너에서 재실행했다. SoilNi와 Land 소스 복사본에 층별 질산태·암모늄태 질소의 흡수 배열과 토양 재고를 출력하는 코드만 추가했다. 계산식은 그대로였고, 네 실행 모두 기존 상태·행동·수확 및 일별 토양 C/N 출력과 일치했다. [실행 설계](../outputs/runs/20261109T154751Z_terminal_n_plant_reset_3f67165b/design.json) · [계측 코드](../outputs/runs/20261109T154751Z_terminal_n_plant_reset_3f67165b/probe.py) · [결과 검산](../outputs/runs/20261109T154751Z_terminal_n_plant_reset_3f67165b/verification.json)

사질토 저온군의 첫 작물 종료 직후에만 미정산 흡수가 있었다. 질산태 흡수 배열 `UNO3`는 4층 0.127714, 5층 0.087073 kg N/ha였다. 합계 **0.214787 kg N/ha**는 식물 누적 흡수의 실패일 증가량과 일치했다. 암모늄태 흡수 배열 `UNH4`는 0이었다.

| 계측 시점 | 흡수 배열 | 토양 무기질소 재고 |
| --- | --- | --- |
| 첫 작물 `SEASEND`, 1982년 연중 98일 | 질산태 0.214787 kg N/ha | 층별 종료 재고 기록 |
| 첫 휴경 `RUNINIT`에서 `PLANT` 호출 직전 | 동일한 흡수량 유지 |  |
| `PLANT` 호출 직후 | 질산태·암모늄태 모두 0 |  |
| 휴경 `SEASINIT` | 흡수 배열 0 유지 | 두 형태의 모든 층이 작물 종료 재고와 일치 |

SoilNi는 일별 `RATE`에서 전날의 `UNO3/UNH4`를 토양에서 차감한다. 실패일 이후 작물의 다음 일별 단계가 열리기 전에 계절이 끝났고, 휴경 `RUNINIT`의 `PLANT`가 배열을 초기화했다. 휴경 첫날 출력에서도 흡수 차감이 0이었다. 작물에서 이미 계상한 질소와 토양 재고 사이의 차이는 이 전환에서 발생했다. 다른 11개 전환에서는 `PLANT` 호출 직전 흡수 배열이 이미 0이었다. [층별 원시 기록](../outputs/runs/20261109T154751Z_terminal_n_plant_reset_3f67165b/IB00000010/cold/runtime.log) · [기존 원장과 뿌리 잔사 대조](MULTIYEAR_POST_EMERGENCE_COLD_Q.md)

초기 계측은 소스 삽입 위치 검사에서 중단됐다. 이후 실행기 경로 및 컨테이너 소스 파일명을 바로잡고, 작물 초기화 호출 전후에 직접 계측했다. [삽입 위치 오류](../outputs/runs/20261109T154405Z_terminal_n_scheduler_probe_287e63fe/console.txt) · [실행기 경로 오류](../outputs/runs/20261109T154433Z_terminal_n_scheduler_probe_11a0c0ae/IB00000004/cold/runtime.log) · [최종 빌드](../outputs/runs/20261109T154751Z_terminal_n_plant_reset_3f67165b/build.log)

사질토 저온군의 통합 N 판정은 보류한다. 다음 검증은 마지막 일별 토양 출력과 휴경 초기화 사이에 이 층별 흡수를 한 번만 차감하고, 작물 수확·잔사와 흡수가 0인 경계를 함께 대조하는 것이다.

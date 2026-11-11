# Becker DSSAT 내부 투입량 소수점 보존 검사

2026-11-08 한국 시간. 고정된 DSSAT 진단 이미지를 기반으로 별도 이미지를 빌드했다. `DSSAT48.INP`와 `DSSAT48.INH`를 작성하는 두 경로에서 열 너비는 유지했다. 관수 깊이가 두 자리 소수로 표현 가능한 경우에 해당 정밀도를 적용하고, 질소는 같은 범위의 FE008/AP005 조합에만 적용했다. 범위를 넘는 투입량과 다른 비료 방식에는 기존 형식을 사용한다. [이전 네이티브 비교](RANSOM_BECKER_IRRIGATION_N_NATIVE_MASS_PROBE.md)

## 네이티브 대조

| 조건 | 두 내부 파일의 물 / N 합계 | 네이티브 누적 물 / N |
|---|---:|---:|
| 관수만 | 245.11 mm / 0 kg N/ha | 245.1100006 / 0 |
| 관수 + AP005 | 245.11 mm / 27.66 kg N/ha | 245.1100006 / 27.6599998 |
| 높은 투입량에서 기존 형식 확인 | 360.89 mm / 149.80 kg N/ha | 360.8900146 / 149.7999420 |

기존 Greeley 기술용 입력에서 같은 관수 20일을 사용했다. 높은 투입량 확인 조건은 첫 이벤트를 관수 123.4 mm와 질소 123 kg N/ha로 바꿨다. 세 조건 모두 내부 파일 두 개에서 날짜별 값이 원본과 일치했고, 별도 정밀 출력의 **조건당 296일, 총 888일**에서 일일 유효 관수·누적 관수·누적 비료 질소·표층에 전달되는 질산태 질소를 확인했다. 누적 모델값 허용오차는 각각 0.0002 mm 및 0.0002 kg N/ha다. 이 수치는 단정밀도 누적에 대한 검사 기준이다. 정밀 진단 출력은 기존 표준 출력 형식을 그대로 둔 채 별도 파일에 기록했다. [검증 결과](../outputs/runs/20261108T085006Z_ransom_becker_native_serialization_precision_0eaf15b3/verification.json)

현재 검증 범위는 **보고된 투입량의 전달과 수송 전 표층 배치**다. Becker 현장의 토양 수분·수량, 질산의 침투 경로, 전체 시스템 수지는 미검증이다. 기본 실행 이미지와 학습 설정의 승격은 하지 않았다. 소프트웨어 검사 204개가 통과했다.

다음은 Becker 블록별 토양에서 코어 수분의 용적밀도 공백, 포장 토양의 수리 특성, 날짜와 깊이가 다른 초기 질소 시료의 매핑을 대조하는 작업이다. 확인된 층과 가정이 필요한 층을 분리한 뒤 현장 재현 조건을 판정한다.

[실행 코드](../outputs/runs/20261108T085006Z_ransom_becker_native_serialization_precision_0eaf15b3/precision_probe.py) · [격리 패치](../outputs/runs/20261108T085006Z_ransom_becker_native_serialization_precision_0eaf15b3/patch_precision.py) · [정밀 출력](../outputs/runs/20261108T085006Z_ransom_becker_native_serialization_precision_0eaf15b3/water_plus_ap005/MARS_MGMT_PRECISION.OUT)
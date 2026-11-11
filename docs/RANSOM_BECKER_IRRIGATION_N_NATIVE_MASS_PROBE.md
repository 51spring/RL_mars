# Becker 관수수 질소 네이티브 투입량 대조

2026-11-08 한국 시간. 네이티브 DSSAT를 기존 Greeley 기술 입력으로 두 번 실행했다. 두 실행에 Becker 2016 관수 20건을 월·일 그대로 2008년 달력에 옮겨 같은 스프링클러 깊이를 지정했다. 토양·기상·품종은 기술 입력의 값을 사용했다. 각 관수일에 같은 FE008/AP005 행을 두고 질소량만 0과 원자료 값으로 달리했다. 20개 `FAMN` 차이와 소스 합계 27.66 kg N/ha를 입력에서 확인했다. 현장 재현과 작물 수량 검증은 별도다. [Becker 입력 명세](RANSOM_BECKER_2016_DSSAT_INPUT_DOSSIER.md)

| 확인 지점 | 물만 적용 | 동일한 물 + AP005 |
|---|---:|---:|
| FileX 관수 합계, mm | 245.11 | 245.11 |
| 내부 `DSSAT48.INP`·`DSSAT48.INH` 관수 합계, mm | 245.00 | 245.00 |
| `SoilWat.OUT` 종료 누적 관수, mm | 245 | 245 |
| FileX 비료 N 합계, kg N/ha | 0 | 27.66 |
| 내부 `DSSAT48.INP`·`DSSAT48.INH` 비료 N 합계, kg N/ha | 0 | 26.00 |
| `SoilNi.OUT` 종료 누적 비료 N, kg N/ha | 0 | 26 |

두 조건은 같은 날에 같은 관수 누적값을 출력했다. `SoilNi.OUT`의 `NAPC`는 누적값이므로 날짜별 차분으로 확인했다. 질소 적용 조건의 20개 증분이 내부 파일의 날짜별 양과 일치했다. 이 결과는 현재 빌드에서 AP005의 N이 비료 투입으로 전달되고, **내부 파일 작성 시 N 1.66 kg/ha와 물 0.11 mm가 원본 합계에서 달라짐**을 보여 준다. 토양 이동이 실측 관수수 질산과 같은지와 전체 질소 수지는 별도 검증 항목이다. [대조 결과](../outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/verification.json) · [네이티브 파일 작성 소스](../vendor/dssat-pdi-source/InputModule/OPTEMPXY2K.for)

Docker Desktop 기동 오류 로그에서 Inference와 Secrets Engine의 임시 소켓 접근 실패를 확인했다. 정상 종료가 끝나지 않아 경로와 PID를 확인한 오류 프로세스를 종료했다. Docker 종료 상태에서 두 임시 통신 폴더를 백업 이름으로 옮겼고, 두 번째 기동에서 Linux 엔진 29.5.2 연결이 복구됐다. 확인된 기존 진단 이미지를 사용했다. [백업 기록](../outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/runtime_recovery.json) · [재시도 기록](../outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/runtime_recovery_retry.json)

소프트웨어 검사 204개를 통과했다. 다음은 격리된 진단 빌드에서 내부 물·비료 출력의 정밀도를 높이고, 소수점까지 확인 가능한 관측 경로로 동일 비교를 재실행하는 작업이다. 기존 NAPC·IRRC는 출력 정밀도가 제한되어 소수점 보존 판정에 별도의 정밀한 근거가 필요하다. 정량 등록과 본 학습은 보류한다.

[실행 입력 해시](../outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/prepared_inputs.json) · [실행 및 검산 코드](../outputs/runs/20261108T053450Z_ransom_becker_irrigation_n_native_mass_probe_115e21de/probe.py)
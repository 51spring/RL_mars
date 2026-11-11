# 공통 외생 시즌과 해충·조사 수식

## 현재 완료 범위

`exogenous.py`는 독립 난수 흐름과 외생 시즌 생성,
`pests.py`는 밀도·잔효·잎 손실·최근 신규 피해 조사 수식을 구현합니다.
이 파일의 수식 모듈은 독립적으로 유지합니다. 후속 실험용 경로에서 실제 작물 피해·조사 관측에 연결했습니다.
기본 Gymnasium은 무해충만 허용하며, 별도 ExperimentalPestEnv의 미보정 연결 검증은
SEASON_BALANCE_AND_ONLINE.md에 기록합니다.

## 난수와 공통 시즌

입력 주소는 [split root seed, season_id, stream version, stream ID]입니다.
기상·유입·조사·감축·예산에 고정 ID 11/23/37/53/71을 사용합니다.
한 스트림의 추가 난수 소비나 분포 변경이 다른 스트림의 순서를 밀지 않습니다.
정책 종류와 PPO 학습 시드는 외생 시즌 주소에 넣지 않습니다.
버전은 1이며 ID·알고리즘을 변경하면 버전을 갱신해야 합니다.

`generate_season(config, split='test', season_id=0)`로 같은 시험 시즌 열을 생성합니다.
시즌 객체의 `with_condition(beta=..., shock=...)`은 물 감축/예산 조건만 바꾸며
기상 seed·날짜별 유입·조사 표준 잡음은 그대로 공유합니다.
`CropManagementEnv.reset(options={'season': season})`로 실제 무해충 환경에 적용합니다.
배열은 파종일 기준 0일째부터이며, 최대 실행일 뒤의 최종 아침까지 포함해야 합니다.
기본 길이는 400입니다. 배열은 생성 시 복사·읽기 전용으로 보관합니다.

기상 스트림은 DSSAT 백엔드의 정수 seed를 만듭니다.
gym-DSSAT 내부에서 이 seed를 다시 유한한 WGEN seed 범위로 매핑합니다.
서로 다른 season_id가 항상 서로 다른 기상 실현을 보장하는 것은 아니므로
본 실험 전 실제 WGEN seed·날씨 중복과 유효 표본 수를 확인해야 합니다.
pairing은 서로 다른 조건에서 **같은** 실현을 쓰기 위한 규칙입니다.

유입은 날짜별 0.05×Bernoulli(0.03), 조사 잡음은 날짜별 표준정규 값입니다.
조사 시에만 난수를 새로 뽑지 않고 해당 날짜의 값에 명시한 표준편차를 곱합니다.
감축 시나리오와 예산 배율은 별도 스트림에서 생성합니다.
미공지 감축 시나리오·해충 입력 배열은 정책 관측/info에 넣지 않습니다.
출력 manifest는 내부 재현 기록이며 정책 입력이 아닙니다.

```powershell
.\.venv\Scripts\python.exe scripts/generate_season_manifest.py --count 10
.\scripts\verify_paired_seasons.ps1
```

manifest는 split별 10개, 총 30개 외생 주소를 기록합니다. 실험을 실행하거나 학습하지 않습니다.
구성 파일·생성기 SHA256, NumPy 버전, seed, 조건, paired digest를 기록합니다.
실제 DSSAT 두 정책/조건에서 공통 129일의 rain/tmax/srad가 일치했고,
Windows NumPy 2.0.1과 Linux NumPy 1.24.1의 배열 digest도 일치했습니다.
결과: `outputs/paired_seasons_verification.json`.
이 대조는 같은 날짜의 **정책 간 대응** 검사입니다. 기상값의 완료일 시점과
실제 달력/기상 출력의 독립 대조를 대체하지 않습니다.

## 해충과 피해

밀도 전이는 제안서 8쪽 수식을 사용합니다:

- 유입 전 밀도 + g(T)×n×(1−n) + 당일 유입
- 마지막 살포 기준 E=e0×exp(−경과일/tau), 이력 없으면 E=0
- 당일 살포가 있으면 E=e0. 여러 살포의 잔효를 더하지 않습니다.
- 다음 밀도는 (1−E)×전처리 밀도를 [0,1]로 자릅니다.
- 잎 손실은 alpha×다음 밀도를 [0,1]로 자릅니다. V7 이전 손실을 0으로 만들지 않습니다.

온도별 증식률은 명시한 두 온도점 사이의 구간 선형 함수이고 밖에서는 끝값을 유지합니다.
제안서에는 0.05~0.15만 있고 그에 대응하는 정확한 두 온도점은 없으므로,
`temperature_low_c`·`temperature_high_c`는 null로 남겼습니다.
`PestParameters.from_config`는 이 값이 없으면 거부합니다.
검사의 10~30°C는 수식 확인용 입력이며 보정된 생물학 값이 아닙니다.

## 조사 시점

기준 식은 clip(mean(최근 7일 신규 잎 손실)/alpha + 잡음, 0, 1)입니다.
alpha=0이면 잡음 전 대리값은 0입니다. 잡음 자체까지 강제로 0으로 만들지 않습니다.
초기에는 존재하는 기록만 평균하며 기록이 없으면 대리값 0입니다.
조사는 0,7,14,...일 아침에 하고 사이에는 최근 값과 경과일을 제공합니다.
아침 조사에는 직전 완료일까지의 손실만 들어갑니다.
`morning(day, standard_noise)` → `complete_day(day, leaf_loss)` 순서를 강제합니다.
과거 손실이 창에서 빠지는 것은 작물 잎의 물리적 회복을 뜻하지 않습니다.

제안서에 조사 잡음 분포·표준편차가 정해져 있지 않아,
정규 잡음을 현재 소프트웨어의 선언된 후보로 구현하되 `survey_noise_std`는 null입니다.
`DamageSurvey.from_config`는 미정 표준편차를 자동 채우지 않습니다.
잡음의 분포/크기는 자료 보정과 민감도 분석 전에 확정해야 합니다.

## 실제 작물 실패 검사

검증 전용 FileX에서 파종 깊이만 7cm→100cm로 바꾸고 생육 방정식은 유지했습니다.
DSSAT 자체의 'Seed ran out of metabolite due to deep planting' 경고와 stage=6을 확인했습니다.
61개 정책 단계 후 terminated가 발생했고, 매출 0·기지출 21.4USD/ha·관리 수익 −21.4가 일치했습니다.
이 조건은 실패 경로의 소프트웨어 검사이며 현실 재배 처방/실패율 추정이나 농학 보정 자료가 아닙니다.
기본 시나리오에는 깊은 파종을 적용하지 않습니다.

```powershell
.\scripts\verify_crop_failure.ps1
```

결과: `outputs/crop_failure_verification.json`.
경고 파일에는 원본 시나리오의 좌표/표고 전달 및 토양 전도도 경고도 있습니다.
별도 입력자료 점검 항목으로 유지하며, 이 실행을 농학 검증 통과로 해석하지 않습니다.

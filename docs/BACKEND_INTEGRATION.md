# 실제 DSSAT와 Gymnasium 연결

현재 범위는 고정 UFGA8201·mode=all·WGEN의 **무해충 통합 검증**입니다.
이 문서는 기본 무해충 환경 계약입니다. 별도 보조 보상·실제 PPO 연결 진단은 REWARDS_AND_REAL_PPO.md에 기록하며 본 실험 학습은 아직 미실행입니다.
실제 피해 쓰기는 별도 실험 경로에서 국소 검증을 통과했으며 LEAF_WRITE_EXPERIMENT.md에 구분해 기록합니다.

## 종료 정보

설치 바이너리의 소스 commit은 `a4ae650548ad085f5776773cf15bb10688ef222a`입니다.
`vendor/dssat-pdi-source`에서 해당 소스를 확보했습니다.

- `CSM_Main/CSM.for`: 일별 interact는 RATE 이전이며 flag_done은 SEASEND 계산 이후입니다.
- `Plant/CERES-Maize/MZ_CERES.for`: SEASEND에도 ISTAGE·SDWT 등 현재 변수를 PDI로 내보냅니다.
- `Plant/CERES-Maize/MZ_OPHARV.for`: 실제 수확량 HWAH를 Summary에 전달합니다.
- `Plant/CERES-Maize/MZ_PHENOL.for`: 정상 생리적 성숙 시 ISTAGE=10입니다.
- 같은 코드의 실패 경로 및 MZ_GROSUB는 실패에도 ISTAGE=6·MDATE를 설정합니다.
  따라서 성숙일 존재나 stage=6만으로 정상 수확/실패를 구분하지 않습니다.

`dssat_backend.py`는 원본 Fortran 바이너리나 생육 방정식을 수정하지 않습니다.
실행 시 PDI 템플릿의 flag_done을 보완하여 SEASEND 이후 최신 콜백 값들로
종료 상태를 새로 조립합니다. 직전 interact의 state 딕셔너리를 재사용하지 않습니다.
FileX에서는 SUMRY 출력만 활성화합니다.

정상 수확은 stage=10·유효한 MDAT/HDAT·실제 HWAH를 함께 확인합니다.
매출의 수량은 `Summary.OUT`의 HWAH이며, 파일이 정수 kg/ha로 반올림하므로
최대 약 0.5kg/ha의 출력 양자화가 있습니다. 현재 단가에서는 약 0.079USD/ha입니다.
검증에서는 종료 PDI의 소수점 곡실량과 HWAH 차이가 0.51kg/ha 이하인지 확인합니다.
실패는 해당 시즌 WARNING.OUT의 소스에 명시된 실패 경고가 있어야 인정하며 매출은 0입니다.
판단할 수 없는 종료는 `BackendContractError`로 거부하고 에피소드를 폐기합니다.
후속 검사에서는 진단용 깊은 파종으로 실제 실패를 유발하여 매출 0·기지출 유지도 검증했습니다.
세부 근거는 EXOGENOUS_AND_PESTS.md 및 outputs/crop_failure_verification.json에 기록했습니다.
냉해·발아 실패 등 모든 실제 실패 경로를 검증한 것은 아닙니다.

## 환경 흐름

`CropManagementEnv(pest_enabled=False)`로만 현재 실행할 수 있습니다.
기본값인 pest_enabled=True는 실제 잎 피해 쓰기가 없으므로 실행을 거부합니다.
이 단계에서 살포 행동은 비용과 횟수만 반영하며 실제 해충·살충 효과는 없습니다.

1. reset마다 새 DSSAT 프로세스·작업 폴더를 사용하여 시즌 간 경고와 이력을 분리합니다.
2. 고정 FileX의 파종일 1982-057 이전은 무투입으로 진행합니다. DAP는 파종 전에도 0으로
   잘려 있으므로 파종 전 판정에 DAP를 사용하지 않습니다. 기준 시드에서는 27일입니다.
3. 당일 아침 원장과 마스크를 만든 뒤 행동을 사전 검증합니다.
4. 실제 생육 전이가 성공하면 비용·잔량을 확정하고 다음 공지를 반영합니다.
5. 완료된 수확/실패는 terminated, 관리상 일수 제한은 truncated로 구분합니다.
6. 수확에서만 매출을 지급합니다. truncated에는 매출이나 episode_result를 만들지 않습니다.
7. 기본 환경 보상은 raw_reward입니다. 선택적 PotentialRewardWrapper가 학습용 잠재함수 보상을 적용하며 raw 원장은 유지합니다.

45개 관측 필드와 고정 스케일은 `observations.py`의 FIELDS가 기준입니다.
버전은 `mars-no-pest-v1`이며 제안서의 묶음을 구체화한 현재 구현 명세입니다.
정확한 기존 45개 필드 순서가 제공된 것은 아니므로 기존 모델과 호환된다고 간주하지 않습니다.
토양 수분은 층 두께 가중 평균, 이력은 오래된 날부터 7프레임입니다.
초기 이력은 같은 초기 프레임으로 채우고 시즌마다 초기화합니다.
조사 모형이 없으므로 survey_value/age/available은 0이며 실측·모의 조사를 만든 것으로 해석하지 않습니다.
미공지 감축률·실제 해충 밀도·미래 기상은 관측에 넣지 않습니다.

소스상 일반 결정일의 기상은 RATE에서 다음 날짜의 기상을 읽기 전의 완료일 값입니다.
파종 전 자동 구간을 통해 초기화 직후의 첫날 기상을 정책에 바로 노출하지 않습니다.
기상 생성 배열과 달력의 독립 대조·스트레스 변환의 농학적 해석 검증은 별도 과제로 남깁니다.
기본 gym-DSSAT는 swfac와 nstres에 1−원본값 변환을 적용하므로 정책은 기존 gym-DSSAT 기준 값을 받습니다.

## 실행 및 검증 근거

```powershell
.\.venv\Scripts\python.exe scripts/run_tests.py
.\scripts\verify_dssat_backend.ps1
.\scripts\verify_gym_integration.ps1
```

Docker 통합 이미지는 `mars-dssat:integration`입니다. 기존 PDI 콜백의 ndarray.itemset 호환 때문에
Linux에서는 NumPy 1.24.1을 유지합니다. Windows 개발 venv의 NumPy 2.0.1과는 분리됩니다.
이 기본 이미지에는 Gymnasium만 추가했습니다. 후속 mars-dssat:ppo-cpu 이미지는 별도 venv에 PPO/PyTorch를 설치하고 기존 PDI 프로세스와 연결합니다.

- `outputs/dssat_backend_verification.json`: 3개 시즌의 종료 정보와 원본 궤적 일치.
- `outputs/gym_integration_verification.json`: 무투입·제약 관리 2개 시즌의 원본 궤적 일치,
  315차원 관측, 누적 물/질소와 원장 일치, raw 보상 합계=관리 수익, 수확 없는 시간제한.
- `outputs/core_test_results.json`: 소프트웨어 검사와 대역 백엔드 기반 검사 결과.
- `outputs/dssat-integration-image-id.txt`: 생성한 이미지 ID.

이 수익 값은 설치·회계 검사 결과이며 정책 비교나 연구 성과가 아닙니다.
새 프로세스 생성 비용과 최종 파일 출력이 있으므로 본 학습 처리량은 아직 추정하지 않습니다.

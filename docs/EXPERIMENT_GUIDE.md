# MARS 팀원용 실험 실행 가이드

[프로젝트 개요](../README.md) · [동결 실험 설정](../configs/proposal_v2.yaml)

전체 실험은 **환경 확인 → DSSAT 기술 검증 → 본학습과 검증 점수에 따른 모델 선택 → 독립 최종 평가와 민감도 분석 → 결과 확인** 순서로 진행한다. 아래 명령은 GitHub에서 클론한 저장소 루트의 PowerShell 7에서 실행한다.

## 1. 환경 준비와 기술 검증

Docker Desktop을 Linux 컨테이너 모드로 실행한다. 실험은 `linux/amd64` CPU 이미지를 사용하며 실행기는 컨테이너에 CPU 8개와 메모리 7 GB를 할당한다. 팀 공유 폴더의 `runtime/mars-dssat-ppo-cpu-metadata.tar`를 준비하고 경로를 지정한다.

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode Check -LoadImage -ImageArchive '<팀 공유 폴더>\runtime\mars-dssat-ppo-cpu-metadata.tar'
pwsh -NoProfile -File .\run_team.ps1 -Mode Smoke
```

- **Check**는 관측과 보상, 자원 제약, 자료 분할, 전체 정책 비교 구성의 자동 검사를 실행한다. 이미지가 Docker에 올라간 뒤에는 `-LoadImage`와 `-ImageArchive`를 생략한다.
- **Smoke**는 실제 DSSAT에서 a/b 정책 1~4의 축소 학습, 중단·재개, 동결 모델 연결 및 규칙 기준선을 포함한 validation 평가를 확인한다. 완료하면 `outputs/runs/*_final_pipeline_technical_*/technical_verification.json`이 생성된다.
- 실행기는 이미지 ID `sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e`와 플랫폼을 확인한다. 전달받은 tar의 SHA-256은 `0a29f9ade0f3f044f300667bbb062376a5be6aac67f0e7ce4582425f96f4648f`이다.

## 2. 전체 정책과 본학습

a 계열은 감축 없이 학습한다. b 계열에는 확률적으로 관개용수 감축이 발생하며, 결정된 감축량은 남은 공급을 기준으로 한다. 시즌 순수익은 수확 매출에서 관수·시비·방제의 투입비와 작업비를 뺀 값이다. 한도와 생육 단계 등으로 금지된 행동은 마스크를 적용한다.

| 정책 | 관수 | 시비 | 방제 | 각 계열·시드당 학습량 |
| --- | --- | --- | --- | ---: |
| 0 | 규칙 | 규칙 | 조사값 0.70 기준 규칙 | 0 |
| 1 | PPO | 규칙 | 규칙 | 1,024,000 |
| 2 | 같은 계열·시드의 정책 1 선택 모델 | PPO | 규칙 | 1,024,000 |
| 3 | 같은 계열·시드의 정책 1 선택 모델 | 같은 계열·시드의 정책 2 선택 모델 | PPO | 1,024,000 |
| 4 | 관수·시비·방제를 하나의 PPO로 공동 학습 | 공동 학습 | 공동 학습 | 3,072,000 |
| b0′ | 감축을 인지한 뒤 개화·등숙기에 쓸 물을 예비하는 대응 규칙 | 규칙 | 규칙 | 0 |

정책 0과 b0′는 평가에 포함된다. 정책 3과 4의 PPO는 해충 조사값과 생육·자원 상태를 보고 매일 살포 여부를 결정한다. a/b 각각 시드 0~9를 쓰며 총 **80개 적합, 122,880,000 환경 단계**다.

```powershell
# 새 본학습 실행
pwsh -NoProfile -File .\run_team.ps1 -Mode Train

# 중단된 실행을 재개할 때 콘솔의 RUN_DIR에 해당하는 로컬 경로 사용
$run = (Resolve-Path -LiteralPath '.\outputs\runs\<실행 폴더 이름>').Path
pwsh -NoProfile -File .\run_team.ps1 -Mode Train -RunFolder $run

# 일부 적합만 학습 (새 실행 또는 -RunFolder로 같은 실행에 이어서)
pwsh -NoProfile -File .\run_team.ps1 -Mode Train -Fits b4_s0
pwsh -NoProfile -File .\run_team.ps1 -Mode Train -RunFolder $run -Fits b2_s0,b4
```

- **일부 적합만 학습(`-Fits`).** `b4_s0`처럼 적합 하나, `b4`처럼 정책 전체(시드 0~9)를 쉼표로 이어 고른다. 필요한 동결 적합(b2←b1, b3←b1·b2)은 자동으로 함께 학습하고 끝난 적합은 건너뛴다. 정책 0과 b0′는 규칙이라 고르지 않는다. 최종 평가는 80개 적합이 한 실행 폴더에서 모두 끝나야 열리므로, 나눠 돌릴 때도 `-RunFolder`로 같은 실행에 이어 쌓는다. `-Fits` 추가 전에 만든 실행 폴더에는 이 옵션을 쓸 수 없다.

- **학습과 모델 선택.** 학습은 `train`을 사용한다. 20,480단계마다 validation 시즌 1200~1231에서 원순수익을 측정한다. a는 무감축 점수, b는 무감축·초기·중기·후기 40% 감축의 평균으로 최고점 모델을 고른다.
- **보관과 재개.** `RUN_DIR`의 전체 폴더를 보관한다. 재개는 폴더에 동결된 설정과 소스, 마지막 저장 시점의 체크포인트를 사용하며 미완료 학습 시즌은 건너뛴다. 완료하면 `training_complete.json`에 80개 적합, 총 단계 수, 선택 모델 해시가 기록된다.
- **학습 결과 읽기.** 예를 들어 `b2_s3.zip`은 b2 시드 3의 선택 모델, `b2_s3_final.zip`은 마지막 모델이다. `b2_s3_training.json`에서 단계별 validation 점수, 선택 단계, 동결 모델 해시, 소요 시간을 확인한다. 낮은 수익도 결과에 남긴다.

## 3. 독립 최종 평가와 민감도

본학습을 완료한 실행에 대해서만 최종 평가를 시작한다. `$run`은 위에서 지정한 로컬 실행 폴더다.

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode FinalEvaluate -RunFolder $run
```

실행기는 학습 완료 기록과 모델 해시를 확인한 뒤 공통 `test` 시즌 0~999를 사용한다. 조건은 무감축 1개와 **파종 후 13·37·83일 × 20·40·60% 감축** 9개다. 중단되면 같은 실행 폴더로 동일한 명령을 사용해 저장된 시즌 묶음 다음부터 재개한다.

| 결과표 행 | 평가 범위 |
| --- | --- |
| `a` | 무감축으로 학습한 a1~a4와 규칙 0의 무감축 성과 |
| `b_none` | 감축 가능 환경에서 학습한 b1~b4와 규칙 0의 무감축 성과 |
| `b_cut` | b1~b4, 기본 규칙 0, 감축 대응 규칙 b0′의 감축 성과 |
| `a_cut` | a1~a4를 감축 조건에 적용한 성과 |

민감도 분석도 같은 명령에 포함된다. 초기 공급 **120 mm와 160 mm**, 해충 조사 잡음 표준편차 **0.05**를 한 번에 하나씩 바꾸고, 기존 모델을 공통 test 시즌 0~299에 다시 적용한다. 민감도 표에는 `a`, `b_none`, `b_cut` 행이 들어간다.

## 4. 결과표, 가설 검정과 학습곡선

| 실행 폴더 아래 경로 | 확인할 내용 |
| --- | --- |
| `report_test/results_table.md` | 조건을 종합한 평균 순수익과 하위 10% 평균, 조건별 평균 실감축량 |
| `report_test/verification.json` | 수량, 물·질소·살포량, 실패율, 제약 위반과 평가 점검, 대비 추정치·95% 신뢰구간·Holm 보정 p값 |
| `report_test/episodes.json` | 정책·시드·시즌·감축 조건별 원자료 |
| `report_test/water_supply_120.json`, `water_supply_160.json`, `survey_noise_0.05.json` | 요인별 민감도 결과 |
| `report/learning_*.png`, `report/learning_curves.csv` | 별도 생성 명령으로 만드는 a/b 정책 1~4의 검증 학습곡선 |
| `report/report.md`, `report/reproduction.json` | 별도 생성 명령으로 만드는 결과 요약과 재현에 필요한 설정·이미지·모델 해시 |

최종 평가 결과를 인용하기 전에 `verification.json`의 `passed`와 `final_test_split_used`가 모두 `true`인지 확인한다. 수익은 USD/ha, 곡물 수량은 건물 kg/ha다. H1은 공동 관리의 추가 가치(b4−b1)가 20%에서 60% 감축으로 갈 때의 변화량을 초기 대 중기, 초기 대 후기로 비교한다. H2는 세 감축률에서 초기와 후기의 추가 가치 차이를 평균한다. 세 주 대비는 양측 검정과 Holm 보정을 적용한다. H3~H6은 방제 학습, 감축 대비 비용·이득, 관수 학습·대응 규칙, 순차·공동 학습을 다룬다. 평가에서는 시드와 공통 시즌을 교차 부트스트랩 10,000회로 재표집한다. [가설·통계 구현](../src/mars_env/comparison.py)

학습곡선과 결과 요약은 완료된 실행 폴더의 동결 소스로 생성한다. 본학습을 완료하면 학습곡선을 만들 수 있고, 최종 평가 통과 후 같은 명령을 다시 실행하면 독립 평가와 민감도 결과도 요약에 들어간다.

```powershell
$image = 'sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e'
docker run --rm --platform linux/amd64 --mount "type=bind,source=$run,target=/workspace" --workdir /workspace --entrypoint /opt/mars_ppo/bin/python $image /workspace/source_snapshot/scripts/report_experiment.py /workspace
```

가로축은 누적 환경 단계, 세로축은 고정 validation 시즌의 원순수익이다. 개별 10시드와 평균, 시드 간 표준편차를 표시한다. ×는 선택 모델, ○는 마지막 모델이다. 후반 점수 하락과 시드 간 변동을 함께 확인한다.

## 5. 기존 예비 실험 재현

아래 실행은 특정 설계 선택을 확인했던 예비 실험이다. 재실행 결과는 `outputs/replays/` 아래 새 실행 폴더에 저장된다.

| 실행 모드 | 비교 및 기존 결과 |
| --- | --- |
| `B1Entropy` | 관수 PPO 엔트로피 0.001과 0 대조군 비교. [결과 JSON](../outputs/b1_entropy_0p001_100k/results.json) |
| `B3Threshold` | 당일 가변 임계값과 고정 0.70 비교. [결과 JSON](../outputs/b3_threshold_100k/results.json) |
| `B3Weekly` | 주간 가변 임계값, 고정 임계값, 가변 모델의 평가 시 0.70 제한 비교. [결과 JSON](../outputs/b3_weekly_threshold_100k/results.json) |

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode B1Entropy -Quick
pwsh -NoProfile -File .\run_team.ps1 -Mode B3Threshold
pwsh -NoProfile -File .\run_team.ps1 -Mode B3Weekly -Quick
```

`B1Entropy -Quick`은 고정 대조군과 소스의 해시를 확인한다. `B3Weekly -Quick`은 축소 DSSAT 실험을 실행한다. 두 실행에서 `-Quick`을 빼면 전체 예비 실험을 재실행한다. 당시 코드는 `historical_source/`에, 필요한 대조군과 동결 모델은 `outputs/runs/`에 있다.

## 6. 파일 역할과 개발용 도구

| 파일 | 역할 |
| --- | --- |
| [`run_team.ps1`](../run_team.ps1) | 이미지 확인, 검사, 학습, 평가 진입점 |
| [`configs/proposal_v2.yaml`](../configs/proposal_v2.yaml) | 환경, 초기화, 학습량, 분할, 평가 조건의 동결 설정 |
| [`src/mars_env/`](../src/mars_env/) | DSSAT 연동, 관측·보상, 자원 제약, 정책과 통계 |
| [`scripts/run_comparison.py`](../scripts/run_comparison.py) | 본학습, 모델 선택, 재개, 평가와 민감도 |
| [`scripts/verify_final_pipeline.py`](../scripts/verify_final_pipeline.py) · [`tests/`](../tests/) | DSSAT 축소 실행과 자동 검사 |
| [`scripts/report_experiment.py`](../scripts/report_experiment.py) | 검증 학습곡선, 평가 요약과 재현 명세 생성 |

Windows 로컬 Python 환경을 구성했다면 개발용 환경 검사와 PPO smoke 테스트를 실행할 수 있다.

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cpu
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cuda
```

DSSAT 원본을 별도로 준비할 때는 아래 저장소를 사용한다. `vendor/gym_dssat_pdi`에는 테스트용 템플릿이 들어 있으므로 upstream 저장소를 별도 경로에 받는다.

```powershell
git clone https://gitlab.inria.fr/rgautron/dssat-csm-os.git vendor/dssat-pdi-source
git clone https://gitlab.inria.fr/rgautron/gym_dssat_pdi.git vendor/gym_dssat_pdi_upstream
```

# MARS 실험 실행 가이드

[프로젝트 개요](../README.md)

## 환경 준비

Windows에서 Docker Desktop을 Linux 컨테이너 모드로 실행하고 PowerShell 7을 사용한다. 실험은 `linux/amd64` CPU 이미지에서 실행하며 컨테이너에 메모리 7 GB를 할당한다. 팀에서 별도로 받은 Docker 이미지 파일의 경로를 지정해 클론한 폴더에서 실행한다.

```powershell
pwsh -NoProfile -File .\run_team.ps1 -LoadImage -ImageArchive '<팀 공유 폴더>\runtime\mars-dssat-ppo-cpu-metadata.tar' -Mode Check
```

`-LoadImage`는 최초 한 번만 필요하다. 실행기는 사용한 이미지의 ID `sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e`와 플랫폼을 검사한다. 이미지 아카이브의 SHA-256은 `0a29f9ade0f3f044f300667bbb062376a5be6aac67f0e7ce4582425f96f4648f`이다.

## 실행과 결과

| 작업 | PowerShell 명령 뒤에 붙일 옵션 | 결과 위치 |
| --- | --- | --- |
| 자동 검사 | `-Mode Check` | 콘솔 |
| 짧은 DSSAT 기술 검증 | `-Mode Smoke` | `outputs/runs/*_final_pipeline_technical_*/technical_verification.json` |
| b3 당일 가변과 고정 0.70 비교 | `-Mode B3Threshold` | `outputs/replays/b3_threshold_100k_*/results.json` |
| b3 주간 가변과 고정·제한 비교 | `-Mode B3Weekly` | `outputs/replays/b3_weekly_threshold_100k_*/results.json` |
| b1 엔트로피 0.001과 0 비교 | `-Mode B1Entropy` | `outputs/replays/b1_entropy_0p001_100k_*/results.json` |
| 본학습 | `-Mode Train` | 콘솔에 출력된 `RUN_DIR`의 모델, 학습 로그와 `training_complete.json` |
| 독립 최종 평가 | `-Mode FinalEvaluate -RunFolder '<완료된 실행 폴더>'` | 실행 폴더의 `report_test` |

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode Smoke
pwsh -NoProfile -File .\run_team.ps1 -Mode B3Weekly -Quick
pwsh -NoProfile -File .\run_team.ps1 -Mode B1Entropy -Quick
```

`B3Weekly -Quick`은 축소된 DSSAT 예비 실험을 실행하고, `B1Entropy -Quick`은 대조 모델과 코드 해시를 검사한다. 기존 예비 실험 결과는 [b3 당일](../outputs/b3_threshold_100k/results.json), [b3 주간](../outputs/b3_weekly_threshold_100k/results.json), [b1 엔트로피](../outputs/b1_entropy_0p001_100k/results.json)에서 확인할 수 있다. 수익 단위는 USD/ha, 수량은 건조 곡물 kg/ha다.

본학습은 80개 모델에 총 122,880,000 환경 단계를 사용한다. 같은 실행을 재개하려면 `-Mode Train -RunFolder '<중단된 실행 폴더>'`를 사용한다. 실행 폴더의 동결 소스와 설정이 사용된다. 최종 평가는 본학습 완료와 모델 해시를 확인하고 test 시즌 0~999를 열며, 같은 명령으로 완료된 평가 묶음 이후부터 재개할 수 있다.

## 파일 역할

| 파일 | 역할 |
| --- | --- |
| `run_team.ps1` | 이미지 확인과 검사·학습·평가 실행 |
| `configs/proposal_v2.yaml` | 학습, 모델 선택, 최종 평가의 동결 설정 |
| `src/mars_env/` | DSSAT 연동, PPO 환경, 관측·보상·평가 구현 |
| `scripts/run_comparison.py` | 본학습과 독립 평가의 진입점 |
| `scripts/verify_final_pipeline.py`, `tests/` | DSSAT 기술 검사와 자동 검사 |
| `historical_source/` | 예비 실험이 검증하는 당시의 동결 소스 |
| `outputs/` | 예비 실험 진입점, 필요한 동결 모델·대조군 입력과 결과 JSON |
| `licenses/` | 별도 전달하는 Docker 이미지 구성요소의 라이선스 |

## 개발용 환경 확인

Windows 로컬 Python 환경을 구성한 경우 환경 검사와 PPO smoke 테스트를 실행할 수 있다.

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cpu
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cuda
```

DSSAT 원본을 별도로 준비할 때는 아래 저장소를 사용한다. `vendor/gym_dssat_pdi`에는 테스트용 템플릿이 들어 있으므로 upstream 저장소를 다른 경로에 받는다.

```powershell
git clone https://gitlab.inria.fr/rgautron/dssat-csm-os.git vendor/dssat-pdi-source
git clone https://gitlab.inria.fr/rgautron/gym_dssat_pdi.git vendor/gym_dssat_pdi_upstream
```

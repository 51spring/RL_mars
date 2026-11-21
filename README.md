# MARS · 작물 관리 강화학습

옥수수 재배 중 관개용수 공급이 줄어들 때 관수·질소 시비·해충 방제를 함께 관리하면 순수익이 얼마나 달라지는지 연구하는 시뮬레이션 프로젝트다. DSSAT의 일 단위 생육 모형(UFGA8201, 플로리다)에 자원 제약, 해충 피해, 투입 비용을 연결하고, 규칙 정책과 MaskablePPO 정책을 같은 기상·해충 시즌에서 비교한다.

- **결정·값·수식·근거 전체:** [MARS_통합문서.md](MARS_통합문서.md) (본문이 현재 기준, 부록은 과거 기록)
- **단계별 실행 안내:** [docs/EXPERIMENT_GUIDE.md](docs/EXPERIMENT_GUIDE.md)
- **현재 상태:** 본학습 전. 최종 test 평가는 아직 열지 않았다.

## 1. 준비물

| 항목 | 내용 |
| --- | --- |
| Docker Desktop | Linux 컨테이너 모드. 실행기가 컨테이너에 CPU 8개, 메모리 7 GB를 할당한다 |
| PowerShell 7 | `pwsh` 명령. Windows 기본 PowerShell 5.1로는 실행하지 않는다 |
| 실행 이미지 | 팀 공유 폴더의 `runtime/mars-dssat-ppo-cpu-metadata.tar` (GitHub에는 없음). 이미지 ID `sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e`, tar SHA-256 `0a29f9ade0f3f044f300667bbb062376a5be6aac67f0e7ce4582425f96f4648f` |
| 디스크 | 본학습 실행 폴더에 체크포인트가 많이 쌓인다(모델 하나 약 3 MB × 적합당 10~30개 × 80적합) |

```powershell
git clone https://github.com/51spring/RL_mars.git
cd RL_mars
```

이후 명령은 모두 저장소 루트에서 실행한다.

## 2. 실행 순서

### ① 이미지 등록과 자동 검사 (Check)

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode Check -LoadImage -ImageArchive '<팀 공유 폴더>\runtime\mars-dssat-ppo-cpu-metadata.tar'
```

처음 한 번만 `-LoadImage -ImageArchive`를 붙인다. 이후에는 `-Mode Check`만 쓴다. 관측·보상·자원 제약·자료 분할·통계 구성의 단위 검사를 돌리고 결과는 콘솔에 나온다(`OK`면 통과).

### ② 실제 DSSAT 기술 검증 (Smoke)

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode Smoke
```

a/b 정책 1~4의 축소 학습, 중단·재개, 동결 모델 연결, 규칙 기준선을 포함한 validation 평가를 실제 DSSAT로 확인한다.

- **확인 위치:** `outputs/runs/<시각>_final_pipeline_technical_<id>/technical_verification.json`
- 설정이 바뀐 뒤에는 본학습 전에 반드시 다시 돌린다(2026-11-20 해충 온도 하한 변경 포함).

### ③ 본학습 (Train)

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode Train
```

a/b × 정책 1~4 × 시드 0~9 = **80개 적합, 122,880,000단계**를 차례로 학습한다. 시작하면 콘솔에 `RUN_DIR=...`가 나온다. 이 폴더를 통째로 보관한다.

중단됐을 때는 같은 실행 폴더로 이어서 학습한다(미완료 시즌은 건너뛴다).

```powershell
$run = (Resolve-Path -LiteralPath '.\outputs\runs\<실행 폴더 이름>').Path
pwsh -NoProfile -File .\run_team.ps1 -Mode Train -RunFolder $run
```

| 실행 폴더 안 파일 | 내용 |
| --- | --- |
| `config.yaml`, `design.json`, `source_snapshot/` | 동결된 설정·설계·소스 |
| `<적합>.zip` (예: `b2_s3.zip`) | validation 최고점으로 선택한 모델 |
| `<적합>_final.zip` | 마지막 모델 |
| `<적합>_checkpoint_<단계>.zip` | 20,480단계마다 저장한 중간 모델 |
| `<적합>_training.json` | 단계별 validation 점수, 선택 단계, 동결 모델 해시, 소요 시간 |
| `<적합>_partial.json` | 진행 중인 적합의 재개 기록 |
| `training_complete.json` | 80개 적합 완료 기록과 선택 모델 해시 |

### ④ 최종 평가와 민감도 (FinalEvaluate)

`training_complete.json`이 있는 실행에서만 시작된다.

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode FinalEvaluate -RunFolder $run
```

test 시즌 0~999에서 감축 없음 + 파종 후 13·37·83일 × 20·40·60% 감축의 10조건을 평가한다. 이어서 물 공급 120·160 mm, 조사 잡음 0.05 민감도를 test 시즌 0~299로 평가한다. 중단되면 같은 명령으로 이어서 한다. **test를 연 실행은 다시 학습할 수 없다.**

| `<실행 폴더>/report_test/` 안 파일 | 내용 |
| --- | --- |
| `results_table.md` | 평균 순수익 / 하위 10% 평균 (USD/ha) 결과표 |
| `verification.json` | 가설 대비 추정치·95% 신뢰구간·Holm 보정 p값, 수량·투입량·실패율·제약 위반, 점검 결과 |
| `episodes.json` | 정책·시드·시즌·조건별 원자료 |
| `water_supply_120.json`, `water_supply_160.json`, `survey_noise_0.05.json` | 민감도 결과 |

결과를 인용하기 전에 `verification.json`의 `passed`와 `final_test_split_used`가 모두 `true`인지 확인한다.

### ⑤ 학습곡선과 결과 요약

```powershell
$image = 'sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e'
docker run --rm --platform linux/amd64 --mount "type=bind,source=$run,target=/workspace" --workdir /workspace --entrypoint /opt/mars_ppo/bin/python $image /workspace/source_snapshot/scripts/report_experiment.py /workspace
```

- **확인 위치:** `<실행 폴더>/report/learning_*.png`, `learning_curves.csv`, `report.md`, `reproduction.json`
- 본학습만 끝났으면 학습곡선, 최종 평가까지 끝났으면 평가·민감도 요약까지 들어간다. 수렴 여부는 판정하지 않고 최고점·마지막·마지막 3개 평균을 그대로 보고한다.

### 예비 실험 재현 (선택)

```powershell
pwsh -NoProfile -File .\run_team.ps1 -Mode B1Entropy -Quick
pwsh -NoProfile -File .\run_team.ps1 -Mode B3Threshold
pwsh -NoProfile -File .\run_team.ps1 -Mode B3Weekly -Quick
```

결과는 `outputs/replays/<모드>_<시각>/`에 저장된다. 비교 대상인 기존 결과는 `outputs/b1_entropy_0p001_100k/`, `outputs/b3_threshold_100k/`, `outputs/b3_weekly_threshold_100k/`에 있다.

## 3. 비교 구조

| 정책 | 관수 | 시비 | 방제 |
| --- | --- | --- | --- |
| 0 | 규칙 | 규칙 (45일 80, 60일 60 kg N/ha) | 규칙 (조사 지수 0.70) |
| 1 | PPO | 규칙 | 규칙 |
| 2 | 정책 1 선택 모델 동결 | PPO | 규칙 |
| 3 | 정책 1 동결 | 정책 2 동결 | PPO |
| 4 | 공동 PPO | 공동 PPO | 공동 PPO |
| b0′ | 감축 공지 후 개화·등숙기 물을 예비하는 규칙 | 규칙 | 규칙 |

a 계열은 감축 없이, b 계열은 감축이 확률 0.75로 일어나는 환경(파종 후 13~112일, 남은 물의 10~70%)에서 학습한다. 주 가설 H1·H2는 b4 − b1의 추가 가치가 감축 강도·시점에 따라 달라지는지 양측 검정(Holm 보정, 시드·시즌 교차 부트스트랩 10,000회)으로 본다. 자세한 정의는 [통합 문서](MARS_통합문서.md) 9절.

## 4. 저장소 구조

| 경로 | 역할 |
| --- | --- |
| [`run_team.ps1`](run_team.ps1) | 이미지 확인, 검사, 학습, 평가, 예비 실험 재현의 진입점 |
| [`configs/proposal_v2.yaml`](configs/proposal_v2.yaml) | 동결 실험 설정 (환경·경제·해충·PPO·평가) |
| [`src/mars_env/`](src/mars_env/) | DSSAT 연결, 관측·행동·보상, 해충·자원 제약, 정책, 통계 |
| [`scripts/`](scripts/) | `run_comparison.py`(학습·선택·평가), `verify_final_pipeline.py`(Smoke), `report_experiment.py`(요약), `execute_project.py`, DSSAT 점검·환경 구성 도구 |
| [`tests/`](tests/) | 자동 검사 |
| [`docker/`](docker/) | 실행 이미지 레시피와 DSSAT 패치 |
| [`vendor/`](vendor/) | 검사에 쓰는 gym-DSSAT 템플릿 |
| [`historical_source/`](historical_source/) · [`outputs/`](outputs/) | 예비 실험 재현용 동결 소스·대조군·모델 |
| [`docs/`](docs/) | 실행 가이드, 개발 환경 기록 |

## 5. 로컬 Python 환경 (선택)

실험은 Docker 이미지로 실행하므로 필수가 아니다. 코드 수정·단위 검사용이다.

```powershell
pwsh -NoProfile -File .\scripts\setup.ps1 -Python python
$env:PYTHONPATH = 'src;tests'
# Check 모드와 같은 핵심 검사
.\.venv\Scripts\python.exe -m unittest tests/test_baseline_evaluation.py tests/test_comparison.py tests/test_economics.py tests/test_environment.py tests/test_exogenous_pests.py tests/test_protocol.py tests/test_resources.py tests/test_rewards.py
```

전체 검사(`-m unittest discover -s tests`)의 수확·다년 감사 검사 일부는 DSSAT 원본 소스가 필요하다. `git clone https://gitlab.inria.fr/rgautron/dssat-csm-os.git vendor/dssat-pdi-source`와 gym-DSSAT의 `UFGA8201.jinja2` 템플릿을 준비한 경우에만 통과한다.

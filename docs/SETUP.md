# 구현 환경

## 기준과 구성

기준: 2026-11-05 개정 proposal_revised.pdf (17쪽).
원본을 `docs/proposal_revised.pdf`로 복사했고, 검색용 텍스트도 함께 보관합니다.

Windows 개발 환경은 `.venv`에 설치하며 전역 Anaconda 환경을 수정하지 않습니다.
기존 `dl_study` 환경의 Python 3.10.19 실행 파일로 격리된 venv를 생성합니다.
현재 고정한 PyTorch 2.5.1 CUDA 11.8 휠과 호환되는 구성을 사용합니다.
Python 3.10은 향후 지원 종료 문제를 피하기 위해 실제 DSSAT 연결 확정 시
Linux Python 3.12 기반 구성으로 이전을 검토해야 합니다.

직접 의존성은 `pyproject.toml`, 실제 설치 전체 버전은 `requirements-lock-windows.txt`에 기록합니다.
CUDA 드라이버 표시 버전과 PyTorch 휠의 CUDA 런타임 버전은 일치할 필요가 없습니다.

## 실행

```powershell
# 최초 설치 또는 새 PC에서 Python 경로 지정
.\scripts\setup.ps1 -Python 'C:/path/to/python310/python.exe'
# CPU 전용 설치는 -CpuOnly

# 활성화 없이 실행할 수 있습니다.
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cpu
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cuda
```

스모크 검사는 315차원 관측, MultiDiscrete([6,9,2]), 17개 마스크,
별도 프로세스 4개, 정책·가치망 각각 [256,256], gamma=1,
초기 비영 행동 확률 0.13/0.03/0.03, PPO 512단계,
마스크 지원 평가, 모델 저장·재로딩을 확인합니다.
스모크용 n_steps·batch_size·n_epochs는 설치 확인용이며 본 실험 설정이 아닙니다.
스모크 환경에는 작물·날씨·실제 예산·해충 모형이 없습니다.
성능이나 학습 수익을 연구 결과로 사용하면 안 됩니다.

## 실제 DSSAT

공식 gym-DSSAT는 Linux를 지원하며 구형 Gym API를 사용합니다.
호스트의 Gymnasium 환경과 무조건 같은 pip 환경에 섞지 않습니다.
기존 WSL2 Ubuntu-24.04는 존재하지만 PDI와 Fortran 도구는 확인되지 않았습니다.

공식 설치 문서:
- https://rgautron.gitlabpages.inria.fr/gym-dssat-docs/Installation/index.html
- https://rgautron.gitlabpages.inria.fr/gym-dssat-docs/Installation/docker.html
- https://rgautron.gitlabpages.inria.fr/gym-dssat-docs/Basic_Usage/initialization.html
- https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html

```powershell
.\scripts\build_dssat.ps1
```

공식 stable 소스를 `vendor/gym_dssat_pdi`에 받았고, commit은
`63f2c529e0bd339b4553beb9aa56d56af83b5e2b`입니다.
상위 저장소와 Docker 레시피만 확보했으며 DSSAT 소스·데이터 submodule은 미수신 상태입니다.
빌드는 확보한 로컬 레시피를 사용합니다. 이번 빌드와 기본 예제는 성공했고,
이미지 ID를 `outputs/dssat-image-id.txt`에 기록했습니다.
패키지 서버의 배포가 변경될 수 있어 재빌드 시 패키지 버전을 함께 확인해야 합니다.

2026-11-05 Docker Desktop 기동 과정에서 Windows가 접근하지 못하는
오래된 임시 소켓 dockerInference, engine.sock, userAnalyticsOtlpHttp.sock 오류를 확인했습니다.
Docker를 종료하고 WSL 파일 API로 해당 소켓만 정리한 뒤 재시작했습니다.
기존 이미지·볼륨은 초기화하지 않았습니다. 최종 설치 상태는 아래 점검 기록을 참고합니다.

이후 구현 순서:
1. 완료: 공식 예제와 UFGA8201, mode=all, WGEN의 시즌 실행을 확인했습니다.
2. 무해충 Gymnasium 어댑터 구현과 실제 회귀 완료. 세부 내용은 BACKEND_INTEGRATION.md 참고.
3. 날짜·층별 수분·기상 시점·실제 수확/실패를 확인합니다.
4. 관수 입력 10mm 회귀와 무해충 회귀를 통과시킵니다.
5. 살아 있는 Fortran/PDI 상태의 잎 피해 쓰기를 구현합니다.
6. 쓰기 함수가 없으면 해충 활성 실행을 거부합니다.
7. 예산·감축·조사·마스크·보상 래퍼와 농학 검증을 추가합니다.
8. 실제 PPO 10만~20만 단계로 CPU/GPU 처리량을 비교한 뒤 본 학습량을 확정합니다.

## 미확정 값

PDF의 수식은 텍스트 추출에서 누락되어 원본 6쪽을 이미지로 확인했습니다.
관수 격자는 [0,5,10,15,20,25]mm,
질소 격자는 [0,10,20,27,35,40,54,60,80]kg N/ha입니다.
최종 평가의 감축일은 `scenarios.evaluation_days`의 제안값(파종 후 13·37·83일)입니다. 실험 전에 승인·동결해야 합니다. 공지 지연일 3일은 단계 기준 보조 분석에서만 씁니다.
45개 관측 필드 순서·정규화는 observations.py, 잠재함수 수식/계수와 실제 PPO 연결 진단은 REWARDS_AND_REAL_PPO.md에 명시했습니다.
PDF 텍스트 추출에서 수식 도형이 누락될 수 있으므로 수식 구현 시 원본 페이지를 확인합니다.
설정 파일의 validation_gates는 전부 false로 시작하며 실제 검증 후에만 변경합니다.

학습·검증·시험 seed와 5개 외생 난수 흐름을 설정으로 분리했습니다.
시드 생성기와 공통 외생 시즌 대응 검사는 구현·검증했습니다. 최종 평가에서는 정책·조건 간 같은 외생 시즌 열을 공유해야 합니다.
본 학습(두 정책 × 10시드 × 500만 단계)은 이번 환경 설정에서 실행하지 않습니다.

## 완료한 점검

- `pip check`: 의존성 충돌 없음.
- `check_environment.py`: RTX 3060 Ti, PyTorch CUDA 11.8 인식 및 행렬 연산 통과.
- CPU 스모크: 별도 환경 4개, 512단계, PPO 업데이트 8회 통과.
- CUDA 스모크: 별도 환경 4개, 512단계, PPO 업데이트 8회 통과.
- 두 장치 모두 마스크 지원 평가, 모델 저장·재로딩 통과.
- 결과 JSON과 스모크 모델은 `outputs/`에 저장.
- Docker Linux Engine 29.5.2 정상 기동 및 공식 gym-DSSAT 이미지 빌드 완료.
- DSSAT-PDI 4.8.0.24+2~a4ae650-1, 데이터 4.8.0.28~c1a31af-1,
  gym-DSSAT-PDI 0.0.9-1, libpdi1 1.11.1 설치 확인.
- 공식 기본 예제의 fertilization/irrigation/all 모드 및 멀티프로세스 실행 완료.
- `scripts/check_dssat.ps1`: mode=all, UFGA8201, WGEN으로 무투입 163단계 정상 종료.
  결과는 `outputs/dssat_check.json`에 저장.

실제 설치된 기본 공개 관측은 17개 키이며 `rain`이 없습니다.
후속 진단에서 내부 `_state`에는 rain과 yrdoy가 있음을 확인했습니다.
기본 백엔드는 종료 전이에 관측/보상을 None으로 반환합니다.
후속 어댑터에서 SEASEND 최신 상태와 Summary.OUT 실제 수확량 전달을 구현했습니다.
전날 수량으로 대체하지 않습니다. 자원·이력을 포함하는 45필드·7일 관측을 추가했으며
현재 무해충 버전에서는 조사 필드를 미사용으로 표시합니다.
설치 및 실행 검증 완료는 실제 잎 피해 쓰기·회복·농학 검증 완료를 뜻하지 않습니다.

## 후속 구현 현황

이 문서는 2026-11-05~06 개발 환경 구축 기록이다. 현재 결정·값·검증 근거는 루트 [통합 문서](../MARS_통합문서.md), 팀원 실행 방법은 [실험 실행 가이드](EXPERIMENT_GUIDE.md)를 본다. 실험은 공유 Docker 이미지로 실행하며, 아래 로컬 venv 절차는 선택 사항이다.

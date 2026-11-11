# MARS crop-management RL

2026-11-05 개정 `docs/proposal_revised.pdf`를 기준으로 준비한 개발 환경입니다.
작업 기준 폴더는 `C:/Users/WD/Desktop/강화학습_MARS`입니다.
기본환경은 이 바탕화면 폴더 하나로 관리합니다. 이전 Documents 작업 폴더는 비웠습니다.

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cpu
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cuda
```

- `configs/proposal_v2.yaml`: 제안서의 연구 설정과 미완료 검증 항목
- `PROGRESS.md`: 단계별 진행상황, 검증 근거, 다음 작업
- `src/mars_env/resources.py`: 자원 원장·감축·행동 마스크
- `src/mars_env/environment.py`: 실제 DSSAT용 무해충 Gymnasium 환경
- `docs/BACKEND_INTEGRATION.md`: 종료·관측·회계 연결 계약과 실행 방법
- `docs/EXOGENOUS_AND_PESTS.md`: 공통 외생 시즌·해충·조사 수식·실제 작물 실패 검사
- `docs/LEAF_WRITE_EXPERIMENT.md`: 실제 Fortran 잎 피해 쓰기 실험과 검증 범위
- `docs/SEASON_BALANCE_AND_ONLINE.md`: 식물체 질소 수지·온라인 해충·실제 조사 관측 연결
- `docs/METADATA_AND_HARVEST_BOUNDARY.md`: 기본 메타데이터 보정·원본 회귀·실제 수확 경계
- `docs/C_HARVEST_AND_OBSERVABILITY.md`: C 반출 배분·측정 범위·Q/F 단위 판정 철회와 N 중복 확인
- `docs/HARVEST_N_CANDIDATE.md`: 별도 N 중복 제거 후보·56실행 대조·공개 교차 평균 확보
- `docs/HARVEST_N_SCOPE.md`: 136실행 확대 감사·무투입 적용 한계·EARS/PLTPOP 경계
- `docs/ACTUAL_HARVEST_CONTRACT.md`: 직접 EARS 계측·실제 반출 기준 수확 인터페이스 후보
- `docs/INTEGRATED_CROP_SOIL_N.md`: 일별·수확·휴경 N 재고와 전달 시차·출력 정밀도 한계
- `docs/AGRONOMIC_SCENARIOS.md`: 공개 연구28처리·16대비, 단위/처리 대응과 독립 검증 준비 상태
- `docs/VALIDATION_EVIDENCE.md`: 기상·입력·토양 수지 감사, 공개 농학자료와 검증 범위
- `scripts/benchmark_real_ppo.ps1`: CPU/CUDA 장기 기술 검사와 체크포인트 재개
- `docs/REWARDS_AND_REAL_PPO.md`: 잠재함수·실제 CPU PPO 연결과 검증 범위
- `scripts/run_tests.py`: 자원 모듈 회귀 검사 및 결과 JSON 저장
- `scripts/setup.ps1`: 전용 가상환경 재설치
- `scripts/build_dssat.ps1`: 공식 Linux DSSAT 이미지 빌드 및 기본 예제
- `scripts/check_dssat.ps1`: 실제 DSSAT mode=all 한 시즌 실행 확인
- `docs/SETUP.md`: 구성, 제약, DSSAT 연결 단계
- `outputs/`: 환경 점검, 모의 PPO 확인 결과

모의 환경은 학습 라이브러리·멀티프로세스·마스크 인터페이스만 점검합니다.
실제 DSSAT 설치와 기본 시즌 실행은 완료했습니다.
자원·감축·관측·종료·외생 난수·실험용 해충/조사·식물체 N·농학자료 대응 검사 156개를 통과했습니다.
무해충 Gymnasium/DSSAT 연결과 원본 생육 궤적 회귀도 통과했습니다.
실제 작물 실패의 매출 0·비용 유지 및 공통 외생 시즌의 실제 기상 대응도 확인했습니다.
별도 실험용 이미지에서 반복/강한 피해, 식물체 N 재고 수지, 온라인 해충·실제 조사 관측 연결을 검증했습니다.
잠재함수 보상과 실제 DSSAT CPU PPO를 연결했고, 두 모드 각각 4환경·1,024단계·8업데이트를 검증했습니다.
전체 탄소·토양 수지, 농학 보정, 장기 CPU/GPU 처리량 비교와 본 학습은 남아 있습니다.
연구용 해충 실행은 거부하며 실험용 클래스는 experimental_only/research_ready=False를 명시합니다.
기존 35개 테스트나 기존 연구 코드는 이 작업 공간에 제공되지 않았습니다.

실제 날짜·행동 감사와 토양 회계 재구성을 통과했고 공개 연구 7개를 정리했습니다.
최신 검사는 기존 결과를 보존하는 `outputs/runs/`의 실행별 보고서와 진행상황 파일에서 확인합니다.

GPU 재검증도 기본 분포 검사 enabled 상태로102,400단계·800업데이트를 완주했습니다. 검증 범위와 최신 실행 근거는 PROGRESS.md에 기록합니다.

2026-11-06: 메타데이터 보정 프로필이 실제 benchmark/smoke의 기본입니다. 원본 비교는 -LegacyMetadata를 사용하며 수확 후/전체 C 검증은 계속 미완료입니다.

건조 곡실 보정자료 조사와 주변평균 제한: [자료 조사](docs/GRAIN_MAIZE_DATA_SEARCH.md).

공통 시즌 기준선의 원수익·자원·기상 검증: [기술 검증](docs/BASELINE_PAIRED_DIAGNOSTIC.md).

v2 범용 토양/실패 경계 확장(현장·다년 검증과 구분): `docs/ACTUAL_HARVEST_DOMAIN_EXTENSION.md`. 두 범용 토양8쌍 및 깊은 파종 실패까지22회 실행 통과, 유기물 초기화 경고는 유지합니다.

원소 탄소 측정 가능성 감사: `docs/CARBON_MEASUREMENT_AUDIT.md`.16개 보존 출력5,696일의 토양C 산술/잔사 인터페이스 통과, 작물/종자/동화/호흡/수확/피해의6개 원소C 항목 미확인으로 전체C 게이트 유지.

2년Q 잔사 경계/출력 완전성: `docs/MULTIYEAR_RESIDUE_HANDOFF.md`.2개 수확률·4성공 실행에서6개 경계 통과. 기존 탄소 최종 휴경 출력9일 누락을 한정하고 진단 전용 무버퍼 설정으로 보완했습니다. 다음은 다년 전체N 원장입니다.

2년Q 통합 모형N: `docs/MULTIYEAR_MODELED_N.md`. 두 수확률·4RUN1,468재고 관측과8개음성대조 통과. 연도 간 누적·휴경→작물 초기화까지 검증했으며 원소C/농학은 미완료입니다.

후속 범용 토양2종의 다년Q 검증: `docs/MULTIYEAR_GENERIC_SOILS.md`. 8회 실행·2,936개N재고 관측·12개 초기화 및4개 음성 대조 통과. 실제 현장/독립농학과 구분하며 F모드는 미검증입니다.

F모드 지정2년 달력·N 검증: `docs/F_MODE_MULTIYEAR.md`.4회 실행·1,468관측/6초기화와4음성대조 통과. 범용토양F/다른실패/농학으로 일반화하지 않습니다.

# FACETS·FDACS DSSAT 재현 및 독립 검증 범위 판정

2026-11-08 한국 시간. 7개 밭–시즌의 포장 420개를 판정했다. **관측 수량 활용 6개 밭–시즌 360포장**, **SWAT 관리 입력 일부 확보 4개**, **DSSAT 현장 재현 가능 0개**, **독립 검증 가능 0개**다. 현장 재현은 관측 기상·파종·수확 달력과 연결된 물·질소 이력, 초기 토양 프로필, 품종 계수가 모두 확인될 때 열도록 했다. [USDA 원자료](https://agdatacommons.nal.usda.gov/articles/dataset/Floridan_Aquifer_Collaborative_Engagement_for_Sustainability_FACETS_-_Field_trial_data_from_Live_Oak_Florida/25212830)

| 연구·밭–시즌 | 관측 수량 | 관리 입력 및 공백 | 독립 검증 판정 |
|---|---:|---|---|
| FDACS 2015 남 | 60, 수분 15.5%로 재구성 | Rath 9처리. SWAT 수확일이 2일 빠름 | 남쪽 CERES 보정·평가 관측 분리 미확인 |
| FDACS 2016 북 | 60, 수분 15.5%로 재구성 | Rath 9처리. 달력 일치, 관수 합계 차이 | 남쪽 윤작 범위 밖 후보. 보정 관측 목록·입력 미확인 |
| FDACS 2017 남 | 60, 수분 15.5%로 재구성 | Rath 9처리. SWAT 파종 1일, 수확 10일 빠름 | 남쪽 CERES 보정·평가 관측 분리 미확인 |
| FACETS 2018 남 | 60, Access 시장수량 | Lee HRU 9개. 처리명이 있는 HRU 8개 | Pioneer 1870 DSSAT 계수와 보정 계보 미확인 |
| FACETS 2018 북 | 60, Access 시장수량 | 대응하는 일별 일정 미확보 | Pioneer 1870 DSSAT 계수와 보정 계보 미확인 |
| FACETS 2020 남 | 60, Access 시장수량 | 대응하는 일별 일정 미확보 | Pioneer 1870 DSSAT 계수와 보정 계보 미확인 |
| FACETS 2020 북 | 수확 연결 0 | 대응하는 일별 일정 미확보 | 곡실 수량 검증 대상 없음 |

FDACS 180개는 15.5% 수분 보정 기준이며 블록별 대비 72개가 있다. FACETS 180개는 Access에 저장된 수량으로, 원본 환산 계수의 수분 기준은 별도로 관리한다. 2020년 북쪽의 빈 수확 키 60개는 결측이다. [수량 재구성](FDACS_21894_GRAIN_YIELD_RECONSTRUCTION.md) · [블록별 대비](FDACS_21894_SPLIT_PLOT_YIELD_CONTRASTS.md) · [Access 수량 기준](FACETS_LIVE_OAK_OPERATIONS_AND_CALIBRATION_LINEAGE.md)

Rath 일정은 각 해 달력·센서·비관수 3전략과 질소 3수준의 모형 입력이다. Lee 일정은 2018년 남쪽에 한정된다. 두 자료는 모형의 처리별 일정에 대한 기술 대조와 민감도 설계에 사용할 수 있다. 현재 현장 DSSAT 재현으로 실행할 수 있는 밭–시즌은 없다. 7개 밭–시즌의 파종~수확 기간 기상 필수 수치는 모두 연결됐다. 파종 전 같은 시료에서 암모늄·질산태 질소가 있는 포장은 FDACS 시즌별 36개, FACETS 2018년 두 밭 모두 0개, 2020년 두 밭 각각 40개다. 이 수치는 토양층별 초기 수분·무기질소와 물리 특성이 연결된 프로필의 완전성을 의미하지 않는다. [현장과 SWAT 일정 대조](FDACS_21894_MEASURED_OPERATIONS_CROSSWALK.md) · [원자료 감사](FACETS_LIVE_OAK_CORN_INPUT_AUDIT.md)

FDACS 북쪽 2016년은 남쪽 윤작에서 분리해 보관한다. 독립 검증 재개 조건은 보정에 쓰인 관측 목록, Pioneer 1498 YHR/Bt의 사용 계수와 출처, 현장 입력의 일별·포장별 계보다. 2018·2020년 Pioneer 1870에도 별도 계보가 필요하다. 이 시험의 관수·질소 수량 관측은 물×질소×잎 피해 공동 검증에 등록하지 않았다. 본 학습 진입 조건은 미충족이다. [CERES 보정 방법](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf#page=226)

## 다음 자료

다음은 Ransom 등의 미국 중서부 옥수수 질소 반응 자료를 선별한다. Dryad에는 2014–2016년 49개 지점–연도와 관수·기상·토양 질소·수량 파일이 공개되어 있다. 질소 반응 보정 후보로 한정하고, 관수와 질소의 공동 무작위 처리 자료로 분류하지 않는다. 지점–연도 키를 연결해 관수 시점, 층별 초기 토양, 품종, 수량 기준을 확인하고 과다 시비·침수·도복 등 자료에 명시된 사건을 분리한다. [Dryad 원자료와 사용 주의사항](https://datadryad.org/dataset/doi:10.5061/dryad.66t1g1k2g)

[시즌별 판정과 출처 해시](../outputs/runs/20261108T045310Z_facets_fdacs_replay_readiness_disposition_d3bb5ecd/verification.json) · [재현 코드](../outputs/runs/20261108T045310Z_facets_fdacs_replay_readiness_disposition_d3bb5ecd/audit.py)
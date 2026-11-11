# FACETS Live Oak 관측 수량·관리 작업·CERES 보정 계보

2026-11-08 한국 시간. USDA 원본 Access ZIP의 공개 MD5를 대조했다. DB를 읽기 전용으로 열어 저장된 수량 쿼리, 실제 결과와 테이블 스키마를 보존했다. FDACS 2015–2017 옥수수의 시비표와 CERES-Maize 방법은 Zamora Re 학위논문에서 대조했다. [USDA 원본](https://doi.org/10.15482/USDA.ADC/1521079) · [학위논문](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf)

## 수확 무게 환산

| 원본 Access 쿼리 | 검산 통과 | 범위 |
|---|---:|---|
| `Market_Yield_corn2018` | 120 | 남·북 각 60 |
| `Market_Yield_corn2020` | 60 | 남쪽만, `studyID=1 AND cropID=9` |

두 쿼리는 `(탈곡 무게 kg / 12.192 × 13123) × (1 − 수분율 / 100) × 1.155`로 kg/ha를 계산한다. 180개 모두 원본 결과를 재현했다. 면적 계수에서 역산한 유효 면적은 **약 9.2906 m²**다. 포장별 실측 면적은 확인이 필요하다. 2020년 북쪽 60개는 앞선 통합 파일 감사에서도 수확 키가 비어 있었다. 이들을 수량 0으로 집계하지 않는다.

FDACS 학위논문 p. 159의 곡실 수량은 15.5% 수분 기준이다. 이 기준의 건조중량 환산 계수는 약 1.18343이다. Access의 1.155는 수식상 약 13.42%에 해당하며 계수 선택의 근거는 확인되지 않았다. 논문 p. 158의 질소 이용효율 산정 문구에는 별도로 10.5%가 적혀 있다. 논문 pp. 158–159의 수확 방법은 통상 중앙 두 이랑을 설명하지만 6 m와 6.1 m가 함께 나오고, 2017년에는 드문 개체 분포에서 대표 이랑을 골랐다. p. 225의 0.762 m 이랑 간격을 적용하면 명목 면적은 약 9.14–9.30 m²다. 두 연구의 수량 기준은 분리하고, FDACS의 개별 포장 수량은 임의 환산하지 않았다. [수확 방법과 수량 기준](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf#page=158)

## 관리 작업과 수치 충돌

FDACS Table 3-3의 **질소 시행 23행**을 날짜·제형·처리별 투입량과 함께 전사했다. 2017년 4월 6일의 일반 추비와 보충 시비는 별개 행이다. 아래 값의 단위는 kg N/ha이며 저·중·고 처리 순서다.

| 옥수수 시즌 | 시비 행 / 일자 | 날짜별 표기 합 | 논문 총량 |
|---|---:|---|---|
| 2015 | 7 / 7 | 158 / 246 / 337 | 157 / 247 / 336 |
| 2016 | 8 / 8 | 188 / 276 / 367 | 191 / 280 / 370 (Table 3-7) |
| 2017 | 8 / 7 | 175 / 263 / 354 | 174 / 263 / 353 |

2016년 4월 19일 보충 질소는 본문과 각주에 34, 시행일 행에 30으로 적혀 있다. 34를 적용하면 192 / 280 / 371이다. 2017년 중간 질소 처리에는 p. 227의 264와 표의 263이 함께 존재한다. 2015년 파종일은 워크북과 Tables 3-3·4-7이 4월 3일, 3장 결과 서술은 4월 4일이다. 모든 출처 값을 보존했다. Table 4-3의 2016년은 땅콩이다. [시비표](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf#page=187)

Access의 `irrigation`과 `fertilization`은 처리 코드 사전이며 `SMS_Data`는 센서 시계열이다. 공개 DB에서 확인한 저장 쿼리와 임시 테이블에도 포장별 실측 관수·시비 이벤트 원장은 없었다. 논문 Figure 4-1은 2015년 옥수수·2016년 땅콩·2017년 옥수수의 관수량을 도식화했다. 일별 관수량이 처리·포장 키에 연결된 원자료는 미확보다.

## 보정 계보와 판정

논문 p. 226에서 **SMS 관수·고질소(I3 F1, 명목 336 kg N/ha)** 처리를 CERES-Maize 보정에 사용했다. 생육 관측 중 개화 57 DAP와 성숙 115 DAP, 지상부 건물중과 수량을 사용했다. Table 4-5의 `McCurdy 84aaMod` 계수는 P1 260, P2 0.3, P5 1100, G2 800, G3 10, PHINT 43이다. 논문이 보고한 남쪽 윤작의 2015·2017 옥수수 관측에서 보정과 평가에 쓴 개별 관측의 분리는 확인되지 않았다. 해당 두 시즌을 저자 계수의 독립 검증에 사용하지 않고, 북쪽 2016년과 FACETS 2018·2020년의 독립 평가 자격도 보류한다. [보정 방법](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf#page=226) · [품종 계수](https://ufdcimages.uflib.ufl.edu/UF/E0/05/39/46/00001/ZAMORA_RE_M.pdf#page=260)

정량 등록은 0건이다. 실제 관수·시비의 재현 입력과 독립 검증 범위가 부족해 본 실험 진입 조건은 미충족이다. 다음은 HydroShare SWAT 공개 아카이브의 관리 입력과 관측 출처를 추적하고, 실측 적용량과 모형에 지정한 일정을 분리하는 작업이다. [HydroShare 아카이브](https://www.hydroshare.org/resource/e992c4484f864ef8bccdc2924ed6e9ba/)

[검산 결과](../outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/verification.json) · [재현 코드](../outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/audit.py) · [시비 전사](../outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/fdacs_n_events.json) · [Access 원본 쿼리와 결과](../outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/mdb_corn_views.json) · [스키마](../outputs/runs/20261108T041522Z_facets_live_oak_operations_and_calibration_lineage_8bee73f4/mdb_schema.json)

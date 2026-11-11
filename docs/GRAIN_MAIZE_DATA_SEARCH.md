# 건조 곡실 보정자료 추가 조사

2026-11-06. 공개 목록을 7연구에서 9연구로 확장했습니다. 신규 시뮬레이션·계수 추정·독립 농학 통과 판정은 하지 않았습니다. 기존 3연구28개 시나리오는 유지하며, 새 주변평균은 별도 자료로 저장합니다.

## Ghana 현장 잎 제거 연구

[Abdul Rahman et al. (2022), DOI10.3390/agriculture12020275](https://www.mdpi.com/2077-0472/12/2/275)의 공개 논문 사본을 보존했습니다. Ghana의 세 지역에서 2017/2018년에 세 품종과 세 잎 제거 처리를 교차한 strip-plot 실험입니다. 원자료 저장소는 [Dataverse](https://doi.org/10.7910/DVN/UKCEVO)이며 공개 검색 목록에는 XLS 파일이 restricted로 표시됩니다. 원자료 접근을 요청하거나 제한을 우회하지 않았습니다.

수확 곡실은 13% 수분으로 조정됩니다. 건조 곡실 비교를 위한 질량 변환은 `dry_mass = reported_mass * (1 - 0.13)`으로 한정하며, 같은 배율을 보고된 주변평균 SEM에도 적용합니다. 예를 들어 Northern 무제거2708.9kg/ha는 건물2356.743kg/ha입니다. 숫자 환산은 모형 적합도나 현장 재현 완료를 뜻하지 않습니다.

PDF 7쪽의 인쇄된 Table2는 제목이 cob dimension인데 실제 열 머리글은 Grain Yield/Stover Yield입니다. 반대로 9쪽 Table3는 제목이 grain/stover인데 열은 cob length/width입니다. 5쪽 방법과 7·9쪽 표를 렌더링해 대조했고, 수량값의 출처를 **7쪽/Table2/Grain Yield 열/Leaf stripping 행**으로 명시했습니다. 제목만 보고 길이(cm)를 수량으로 가져오지 않습니다.

`configs/rahman2022_marginal_grain.json`에는 지역×잎 제거 **9개 주변평균**과 지역별 공유 SEM3개가 있습니다. 이는 품종·연도를 평균한 값으로, 원래 품종×처리×연도 셀값이 아닙니다. 전체 Mean 열도 추가 독립 지역으로 세지 않습니다. 6개 처리/대조 비율은 기술 대비이며, strip-plot 공분산·자유도가 없어 비율 SE·신뢰구간·통과 여부는 null로 유지합니다. SEM을 SD로 오인하거나 임의 n으로 환산하지 않습니다.

50% tasseling/silking은 절반의 개체가 해당 생육단계에 도달했다는 뜻입니다. 50% 잎 제거가 아닙니다. 처리도 아래쪽 잎의 위치별 제거이므로 균일 leaf-mass 손실로 바꾸지 않습니다. NPK40kg/ha의 비료 제품량/영양소량 기준도 미확정이므로 총 N을60 또는26으로 확정하지 않습니다.

실제 정량 재현에는 품종·연도별 평균/반복자료, strip-plot 오차 구조, 일별 기상, 지역/포장별 파종일, 토양층·초기 상태, 품종 계수, 기비 기준, 하엽 제거 매핑이 필요합니다. 역할은 **후기 잎 제거 보정 후보**로 등록했으며 독립 검증 성과로 세지 않습니다.

## 초기 피해 온실 원자료 후보

[de Oliveira et al. (2026), DOI10.1002/agg2.70295](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1184134/1/Alterations-in-plant-architecture-and-physiology-allow-maize.pdf)의 기관 PDF와 [Dryad 메타데이터](https://datadryad.org/dataset/doi:10.5061/dryad.z8w9ghxtc)를 확보했습니다. 기존 N 처리 Oliveira 연구와 **다른 DOI**입니다. 네 품종×대조/V4 절단, 조합당5개 포트의 실험으로 초기 회복 보정 후보입니다.

논문은 포트당 두 식물과 포트 수량/2의 per-plant 수량을 설명하지만 저장소 README는 단일 식물이라고 적습니다. 원자료 XLSX는 웹 다운로드403, 익명 공식 API 다운로드401로 이번 실행에서 미확보입니다. 원자료 획득과 정의 확인 전 평균·SEM을 계산하지 않습니다. 같은 포트의 식물 둘을 독립 반복 둘로 세지 않습니다.

논문은 100립중의13% 수분 보정을 명시합니다. 이를 모든 grain-yield 열에 자동 적용하지 않습니다. 논문/저장소 간 실험 단위, 실제 열의 수분 기준, 같은 연구진의 기존 N 연구와 실험 중복 여부를 먼저 확인합니다. 별도 DOI만으로 독립성을 보장하지 않습니다. 포트 g를 field kg/ha로 환산하지 않으며, 평균 온도로 일별 온실 기상을 만들지 않습니다.

## 재현과 현재 상태

```powershell
.\.venv\Scripts\python.exe scripts/build_agronomic_marginals.py
.\.venv\Scripts\python.exe scripts/run_tests.py
```

`agronomic_marginals.py`는 검증된 수분 기준/단위만 환산하고 주변평균을 factorial 관측으로 넘기는 것을 거부합니다. 생성물은 `marginal_targets.json`, `descriptive_contrasts.json`, `verification.json`입니다. 기존 실행 폴더를 덮어쓰지 않습니다.

원문/접근 결과와 SHA256:

- `outputs/runs/20261106T062010Z_grain_maize_source_fetch_eb958dfa`: Dryad 웹 메타데이터와 다운로드403 기록.
- `outputs/runs/20261106T062043Z_grain_maize_public_api_a275f354`: Dryad 공식 JSON, API401 기록, 기관 PDF와 확인 페이지3·4.
- `outputs/runs/20261106T062143Z_ghana_field_source_97a1ea05`: 출판사 직접 접근403 기록.
- `outputs/runs/20261106T062235Z_ghana_paper_mirror_ee9e39d6`: CC BY 공개 논문 사본, 텍스트, 시각 대조 페이지5·7·9.

정량 농학검증/보정 준비 완료는 여전히0개입니다. 신규9개 주변평균이 기존28개 시나리오를37개 실행 조건으로 확장한 것은 아닙니다. 다음은 제한 없는 현장 원자료와 전체 재현 입력 확보를 계속하고, 현재 확보한 주변평균으로는 입력이 준비된 뒤 동일 품종·연도 가중을 재현한 기술 비교만 진행하는 것입니다. 물·질소 교차 검증, 실제 해충과 인공 절단의 차이, 전체 원소 C 검증은 남아 있습니다.

## 후속 확보: USDA LIRF 2008–2011
공식 공개11파일과96포장수량/24처리요약·1,461기상일을 확보해 목록을10연구로 확장했습니다. 기본 작물/수분 반응의 독립 검증 후보로 유지하며 상세 감사는 docs/LIRF_INPUT_QUALIFICATION.md에 기록했습니다.2009T3 요약 평균과 포장 평균 불일치,4개 기상값 결측, 관개수N·초기 토양N·스프링클러/강수 구분, 응애/우박/서리 외란이 확인됐습니다. 보정용으로 전환하거나 정량 준비 완료로 승격하지 않습니다.

2026-11-07 Oliveira 후속: `OLIVEIRA_OVERLAP_UNITS.md`. 14항목 원출처 대조로 보고 설계는 구분했으나 포트·보정계보 독립성 미확정, Dryad 1개체/논문 2개체와 HI 분모·수분 기준 차이 유지. 우선순위3 명세 완료/정량 차단, 다음은 우선순위4 Du Plessis 온도–발육·생존 자료 추출이다.

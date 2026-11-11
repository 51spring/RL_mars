# LIRF 패키지·native·현장 입력 차이 원장

2026-11-06. 입력 차이 19개를 출처·상태·후속 조치로 분리했다. 원장은 모델 보정이나 농학 검증 점수가 아니다. 자동 현장값 대체를 모든 항목에서 금지하며 `research_ready=False`, `main_training_allowed=False`를 유지한다.

근거: `outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5/verification.json`. 같은 폴더의 `input_difference_ledger.json`에 전체 항목, `d22_soil_candidate.json`에 층별 셀 위치, `daily_mean_air_observations.json`에 날짜·기상 출처 셀을 보존했다. 초기 산출물 `20261106T134917Z_lirf_evidence_ledger_4400a2e8`도 보존했으나 파종 출처 행과 비료량 필드 표현을 정정한 위 실행을 사용한다.

## 토양 자료의 적용 범위

`LIRF_Soils.xlsx`의 Moisture Release 10–13행에서 site5–D22 연결을 확인했다. Soil Texture 36–43행의 site5 표본 8층은 0–182.88cm에 걸치며, 기존 포장 수량표의 2008 T1 block2 D22 한 포장과 연결된다. 네 T1 포장의 평균 토양을 대표한다고 확인한 것은 아니다. Moisture Release의 네 행은 8층 전체의 수분 특성 측정을 뜻하지 않는다.

포화반죽 pH는 7.57–8.06이다. 현행 ICASA SLPHW의 물 속 pH와 측정법 등가성이 미확인되어 native 기본값 7을 교체하지 않았다. 층별 pH 평균도 만들지 않았다. native 진단 토양 깊이 200cm 대비 마지막 17.12cm는 미측정 범위로 남긴다. Bulk Density D2 통계는 2008–2015 NMM 보정 코어의 통합 자료이며 2008 D22 층별 값으로 배정하지 않았다.

토성은 최상층 sand/clay/silt 65/19.5/15.5%로 원 패키지 진단의 85/5/10%와 다르다. 개별 포장·층 깊이·수리 특성·초기 상태 대응이 모두 해결되기 전 전체 native 프로필로 승격하지 않는다.

## 기온 자료의 적용 범위

2008–2011년 기록된 일평균 기온 1,461개로 연도별·월별 통계를 계산했다. 일수 가중 전체 평균은 8.575459°C이며, 통합 월평균의 최대–최소 차이는 27.160806°C, 그 절반은 13.580403°C이다. 기록된 일평균을 사용했으며 최고·최저 기온의 평균이나 토양온도가 아니다. 보정 관측소 태그를 보존했고, 2010년 태그 없음도 그대로 기록했다. 네 해를 장기 기후 평년값으로 간주하지 않는다.

공식 DSSAT vol3 PDF 물리 페이지209(인쇄197)의 Climate AMP 정의는 월평균 차이의 절반이다. 반면 현재 고정 소스 `SPAM/STEMP.for` 340/345/352행의 계절항은 TAMP를 2로 나눈다. Climate 파일 AMP에서 현재 WTH/native TAMP로 넘어가는 정의·변환 경로는 아직 미확인이다. 두 기술 통계를 모두 보존하고 적용값을 선택하지 않았다. native TAV20/TAMP5도 변경하지 않았다.

공식 문서: [DSSAT vol3](https://dssat.net/wp-content/uploads/2011/10/DSSAT-vol3.pdf). 고정 사본은 `outputs/runs/20261106T134643Z_lirf_reference_definitions_c197b893/DSSAT-vol3.pdf`, 원장의 렌더링 PNG와 SHA로 근거를 추적한다. 현행 ICASA 사본은 `outputs/runs/20261106T085959Z_icasa_dictionary_8bbb3db6`에 보존했다.

## 남은 입력 차이

원장은 온도2항목, pH·토성·깊이·밀도·증발·비옥도, 파종·재식간격·품종, 초기 수분·N, 관개수N·비료N·강우/관개 일정, 기상 읽기·수확 기준·생물/서리 외란을 구분한다. 파종일은 CropLog A10:D10, 재식 간격76cm는 방법 문서5페이지와 대조했다. field TEW12mm와 native SLU1 6mm는 다른 물리량으로 유지한다.

기존 native 2,364개 기상 값 대조는 기술 경계의 증거다. 품종 동등성·보정 독립성, 초기 상태의 관측 날짜·N 풀, 관개수 N 배분, 강우와 하루 차이 관개 일정, 외란 처리 기준이 해결되지 않아 수량 적합도나 정책 우열로 해석하지 않는다.

다음은 현재 실행 경로에서 Climate AMP/WTH TAMP/토양온도 모듈의 정의와 변환을 확인하고, 적용 여부와 민감도 범위를 사전에 명시하는 것이다. 현장 토양 후보는 미측정 깊이·수리 특성·밀도·측정법 문제를 유지한 채 개별 포장 입력 가능성을 검토한다. 이번 작업의 신규 native 실행·학습·이미지 변경은 0건이다.

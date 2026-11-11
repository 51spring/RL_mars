# Battaglia IPAR 관측과 DSSAT 광 차단량 대조

## 포장 측정

2019년 논문은 맑은 날 11~14시에 LI-191R 선형 센서와 LI-1000 기록계로 광합성광양자속밀도(PPFD)를 측정했다. 시험구 안에서 토양면의 세 판독값을, 이랑 밖 통로에서 입사광 참조값 한 개를 얻었다. 논문 표의 IPAR(%)는 입사광 대비 토양면 투과율을 1에서 뺀 비율이다. 초록의 에너지 단위 표기와 별도로, 여기서는 방법의 계산식과 표 4의 백분율을 사용했다. [논문 방법 및 표 4](https://www.researchgate.net/publication/333626126_Effects_of_Corn_Row_Width_and_Defoliation_Timing_and_Intensity_on_Canopy_Light_Interception)

2013년 표 4에서 두 품종×두 이랑 폭의 무피해 대조와 V7 100% 적엽군을 추출했다. V8·R5의 16개 평균으로 8개 처리−대조 차이를 계산했다. V8에는 적엽군이 대조군보다 36~59%p 낮았고 R5에는 5~8%p 낮았다. 표 평균의 기술 비교이며 반복구별 측정일·시각과 공분산은 미확보다. 2012년 VT와 R2는 일부 처리만 측정됐다. 2013년 V8은 V7 피해 후이며 VT~R1은 V14 피해 후, R2 측정은 R2 피해 직후다. R5에는 새 적엽 처리가 없었다. [논문](https://doi.org/10.2134/cropsci2018.05.0337) · [추출한 처리 대비](../outputs/runs/20261107T065543Z_battaglia_ipar_crosswalk_f020491b/field_ipar_contrasts.csv)

## 모델에서 읽을 수 있는 양

| 항목 | 범위 |
|---|---|
| CERES 내부 차단율 | 성장 계산에 들어가는 LAI와 이랑 폭·밀도로 `1 − exp(−LIFAC × LAI)`를 계산한다. |
| CERES 내부 IPAR | 일사량 SRAD에 품종 공통 종 파일의 PARSR 0.50을 곱해 일별 PAR 에너지를 얻는다. 여기에 차단율을 곱한 후 재식밀도로 나누면 MJ/개체/일이다. |
| 표준 저장 출력 | 확인한 CERES `PlantGro.OUT`에는 `LAID`가 있고 내부 `IPAR`는 없다. `Weather.OUT`의 `PARD`는 기상 PAR의 광자량이며 단위는 mol/m²/일이다. |
| MARS 잎 피해 | 하루 성장 계산 후 녹색 LAI를 바꾸는 경로다. 피해 당일의 종료 LAI를 써도 그날 성장에 이미 사용한 광 차단량은 재현되지 않는다. |

[성장 계산](../vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_GROSUB.for) · [출력 사전](../vendor/dssat-pdi-source/Data/DATA.CDE) · [MARS 잎 피해 통합](../docker/leaf_integration.for)

## 보관된 DSSAT 실행 대조

기존 UFGA의 무피해 및 0.03 피해 실행에서 각각 136일의 `PlantGro.OUT`과 `Weather.OUT`을 날짜별로 연결했다. 출력의 종료 LAI, 일사량, FileX 이랑 폭 61cm·입모밀도 7.2개/m²로 광 차단율을 계산했고 두 최대값은 각각 0.7476·0.7492였다. FileX 밀도를 사용한 종료 상태 진단값이다. 서로 다른 시점·실험을 섞지 않기 위해 이 값과 Battaglia 측정값 사이의 오차나 피해 효과를 계산하지 않았다. [종료 상태 진단](../outputs/runs/20261107T065543Z_battaglia_ipar_crosswalk_f020491b/ufga_close_diagnostics.csv)

같은 날짜의 보관 정책 trace와 출력은 LAI·일사가 인쇄 정밀도 안에서 일치하지 않았다. 다음 날 trace로 옮겨 비교하면 각 실행의 135일에서 LAI가 모두 일치했지만, 일사는 1982191의 차이가 두 실행 모두 남았다. 따라서 날짜 이동을 일반 규칙으로 채택하지 않았다. 다음은 성장 계산 시점의 입력과 차단율·IPAR를 별도 읽기 진단으로 기록하고, 종료 전후 및 마지막 날의 날짜 계약을 실제 DSSAT에서 확인하는 작업이다. 정량 비교 가능 쌍은 현재 0개다. [검증 결과](../outputs/runs/20261107T065543Z_battaglia_ipar_crosswalk_f020491b/verification.json)

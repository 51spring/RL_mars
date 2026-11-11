# Battaglia 시험 토양과 품종 계수 출처 대조

## 시험 포장 토양

논문은 경사 2~6%의 Loradale 미사질 양토에 무경운으로 파종했다고 보고했다. 두 해의 직접 측정은 표 1의 0~20cm 토양화학에 한정된다. 1M KCl pH는 5.26·5.44이고 계산한 물 pH는 6.13·6.29다. 인·칼륨·칼슘·마그네슘·아연도 같은 깊이의 토양검정값이다. 파종 전 층별 수분, 질산태·암모늄태 질소, 뿌리층 수리 특성은 확인되지 않았다. 표층 토양검정이나 연도별 시비량으로 초기 무기태 질소를 채우지 않았다. [Battaglia 논문, 방법 및 표 1](https://www.researchgate.net/publication/321402722_Corn_Yield_Components_and_Yield_Responses_to_Defoliation_at_Different_Row_Widths)

| 조회 지점 | USDA 지도 단위 | 적용 범위 |
|---|---|---|
| 논문 좌표 38°01′47″N, 84°29′41″W | 3347466 UabC, Urban land–Anthroportic Udorthents–Bluegrass | 보고된 Loradale이 구성 목록에 없어 포장 연결 미확인 |
| 농장 CoCoRaHS 참고점 38.12667°N, 84.49627°W | 2482153 uBlmB, Bluegrass–Maury | 논문 좌표에서 10.8km 떨어진 관측점. 시험구 위치 미확인 |

논문에 좌표 기준계가 명시되지 않아 공간 조회에는 WGS84를 가정했다. 지도 단위는 지역 규모의 토양 구성 추정치이며 두 점의 조회만으로 시험구 위치나 토양을 확정할 수 없다. 같은 농장의 NASIS 건초지 단면 08KY067003도 현재 분류가 Bluegrass여서 대상 시험에 연결하지 않았다. [USDA 점 조회 방법](https://nasis.sc.egov.usda.gov/NasisReportsWebSite/limsreport.aspx?report_name=SDA-PointIntersect) · [농장 참고점](https://mesonet1.agron.iastate.edu/sites/site.php?network=KY_COCORAHS&station=KY-FY-22) · [농장 NASIS 단면](https://nasis.sc.egov.usda.gov/NasisReportsWebSite/limsreport.aspx?pedon_id=08KY067003&report_name=Pedon_Site_Description_usepedonid)

USDA Loradale 표준 단면에는 Ap·A·Bt1·Bt2·BC·C의 6개 토양층과 72in 깊이의 암반이 기술돼 있다. Fayette County SSURGO에서 Loradale로 등재된 2개 구성요소는 각 3개 토양층과 암반층으로 구성됐다. 토성 합계, 층 깊이 연속성, 15bar·⅓bar·포화 근처 수분함량의 순서를 검사했다. 이 값은 지도 단위의 대표값이다. 시험 포장과 연결이 확인되기 전까지 토양 파일이나 초기 상태 입력으로 채택하지 않는다. [USDA Loradale 표준 단면](https://soilseries.sc.egov.usda.gov/OSD_Docs/L/LORADALE.html) · [SSURGO 필드 정의](https://sdmdataaccess.sc.egov.usda.gov/documents/TableColumnDescriptionsReport.pdf)

## 품종과 DSSAT

논문 표 1의 P1360HR과 P2088YHR은 각각 상대숙기 113과 120이다. 2018년 방법에는 P2088HYR 표기도 있어 검색에 포함했다. 프로젝트에 포함된 CERES-Maize 품종 파일 167개 행과 DSSAT 공식 공개 커밋의 168개 행에서 두 품종과 표기 변형을 검색했으나 해당 항목을 확인하지 못했다. 기존 기술 환경의 IB0035는 McCurdy 84aa로 식별됐고, 같은 ID도 두 파일에서 계수값이 달랐다. 상대숙기에서 P1·P2·P5·G2·G3·PHINT를 추정하거나 IB0035로 대입하지 않았다. [논문 표 1](https://doi.org/10.2134/agronj2017.06.0322) · [DSSAT 공식 파일](https://github.com/DSSAT/dssat-csm-os/blob/25c93b9a2f73f8ec45bf441b198dac5fb7b22849/Data/Genotype/MZCER048.CUL)

다음은 확보한 일별 기상과 부록의 누적 GDD 42개를 대조하고, 품종·이랑 폭별 무피해 대조의 생육단계를 조사일 구간으로 정리하는 작업이다. 생육 조사 구간은 관측 기준을 검토하는 데 쓰고 피해 시행일이나 독립 품종 보정값으로 간주하지 않는다. 개별 관수일과 투입량, 실제 포장 좌표·수리 특성·초기 상태, 두 품종의 독립 계수는 미확보다. 정량 보정과 본 학습은 보류한다.

[원본 출처·조회 SQL·해시](../outputs/runs/20261107T064354Z_battaglia_soil_cultivar_lineage_40c3b7a3/sources.json) · [검증 결과](../outputs/runs/20261107T064354Z_battaglia_soil_cultivar_lineage_40c3b7a3/verification.json)

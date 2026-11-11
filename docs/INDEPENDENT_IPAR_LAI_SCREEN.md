# 옥수수 군락 광 차단율과 LAI의 독립 공개자료 선별

목표는 시간대별 광 차단율(fIPAR)을 독립적으로 측정한 녹색 LAI에 연결하는 것이다. 정오 관측과 일중 통합을 대조하려면 같은 포장·날짜에서 군락 위·아래 광량이 일조 시간대에 걸쳐 있어야 한다. 일별 비율은 측정 간격을 반영한 차단 광량 합계를 같은 시간대의 입사 광량 합계로 나눈다. LAI가 같은 광량 자료에서 역산됐으면 광 차단 모형의 독립 입력으로 분류하지 않는다.

## 확보한 원자료

MuST-C v3.0의 참조 ZIP을 확보했고 저장소의 MD5와 로컬 SHA-256을 확인했다. 옥수수 SunScan 22행은 7개 날짜, 8개 포장에서 측정됐다. 파괴 표본 30행 중 포장 수준 LAI 값이 있는 5행만 비교에 사용했다. 포장 ID를 맞춘 결과 같은 날 LAI 쌍 2개와 하루 차이 3개가 있었다. 파괴 표본의 시각과 SunScan의 상·하부 PPFD 원값은 제공된 표에서 확인되지 않았다. 별도 기상 PAR는 포장별 하부 투과광을 제공하지 않는다. 이 5쌍은 LAI 측정법 비교 자료로 보존했다. [MuST-C 공개 데이터](https://doi.org/10.60507/FK2/OX9XTM) · [측정 방법](https://pmc.ncbi.nlm.nih.gov/articles/PMC12796333/) · [연결한 LAI 기록](../outputs/runs/20261107T071234Z_independent_ipar_lai_screen_d2bd5770/mustc_lai_pair_candidates.csv)

## 광량 자료와 적용 범위

| 후보 | 확인한 범위 | 남은 조건 |
|---|---|---|
| ORNL DAAC 중서부 자료 | 30분 단위 fPAR. 양자 센서 기반 값과 NDVI 추정값의 출처를 논문에서 구분한다. | 센서 관측 옥수수 사이트·연도를 선별하고 독립 LAI 원자료와 연결해야 한다. [데이터 논문](https://www.nature.com/articles/s41597-024-03004-w) · [저장소](https://doi.org/10.3334/ORNLDAAC/2136) |
| Iowa COBS | 2009·2010년 상·하부 PPFD, 측정 시각, 태양 천정각, 직달광 비율의 메타데이터가 있다. | 목록에 있는 LAI는 IPAR에서 역산했다. EDI 원자료 API 요청은 403이었다. [메타데이터](https://silph.biorenew.iastate.edu/dataset/cobs-plants) |
| Siebers 등 Dryad | 일리노이 옥수수의 여러 LAI 기기 비교이며 옥수수 측정일은 하루다. | API 401, 공개 페이지 파일 링크 403으로 원본 열은 미확인이다. [Dryad 데이터](https://doi.org/10.5061/dryad.h1893201g) |
| CORNIBU | 포장 차단율로 검토한 구조 모형과 코드를 공개했다. | 확인한 저장소 트리에는 포장별 LAI·광량 관측표가 없었다. [논문](https://doi.org/10.1016/j.compag.2024.109694) · [저장소](https://github.com/mserouar/CORNIBU) |
| Lacasa 등 | 맑은 날 정오의 옥수수 fIPAR와 LAI를 함께 분석했다. | 원 관측은 저자 요청 조건이며 공개 저장소에는 분석 코드가 있다. [논문](https://doi.org/10.1186/s13007-021-00753-2) · [저장소](https://github.com/jlacasa/k-estimation) |
| Kukal·Irmak | 옥수수를 포함한 포장 작물의 15분 간격 광량 수지를 측정했다. | 이번 검색에서는 행 단위 공개 파일을 찾지 못했다. [논문](https://doi.org/10.1016/j.agrformet.2019.107887) |

선별한 7개 출처에서 현재 확보해 확인한 **독립 LAI–fIPAR 정량 비교 쌍은 0개**다. 다음은 ORNL DAAC의 센서 기반 fPAR을 옥수수 사이트·연도별로 분리하고, Mead US-Ne2·US-Ne3의 독립 LAI 측정일과 현장 식별자가 일치하는지 대조하는 단계다. 날짜·공간 범위·LAI 측정 방식이 확인되기 전까지 계수 추정과 농학 검증은 보류한다. [US-Ne2 현장 정보](https://ameriflux.lbl.gov/sites/siteinfo/US-Ne2) · [US-Ne3 현장 정보](https://ameriflux.lbl.gov/sites/siteinfo/US-Ne3)

[출처와 해시](../outputs/runs/20261107T071234Z_independent_ipar_lai_screen_d2bd5770/sources.json) · [검증 결과](../outputs/runs/20261107T071234Z_independent_ipar_lai_screen_d2bd5770/verification.json)

# ORNL–Mead 광 흡수율과 독립 LAI 연결 대조

Wu 등의 논문 표 2에서 Mead 옥수수 관측은 세 사이트·연도에 해당한다. 두 사이트의 2018년 기록은 콩이다. 표의 기간은 분광 관측 기간이며 날짜별 센서 fAPAR의 유효 행 수는 원본 CSV로 확인해야 한다. [Wu 등, 표 2 및 방법](https://doi.org/10.1038/s41597-024-03004-w)

| 사이트·연도 | 분광 관측 기간 | 독립 녹색 LAI 근거 |
|---|---|---|
| US-Ne2 2017 관개 옥수수 | 7월 15일~10월 15일 | 2017년 현장·작물은 Miao 등에서 교차 확인. 날짜별 LAI 표 미확보 |
| US-Ne3 2017 천수 옥수수 | 7월 15일~9월 17일 | 2017년 현장·작물은 Miao 등에서 교차 확인. 날짜별 LAI 표 미확보 |
| US-Ne3 2019 천수 옥수수 | 5월 3일~10월 15일 | Johansen 등의 파괴 표본 채취 11회, 5월 29일~9월 18일 |

2019년 US-Ne3에서 동일 사이트·연도와 보고 기간의 겹침을 확인했다. Johansen 등은 20×20m 집중조사구 6곳에서 식물체를 채취하고 녹색 잎의 면적을 LI-3100C로 측정했다. 정확한 LAI 행과 시각별 fAPAR 행은 연결하지 못했다. 두 논문의 해당 포장 파종일도 4월 24일과 4월 27일로 달라 파종 후 일수(DAP)는 합치지 않았다. [Johansen 등, 현장 채취 방법](https://doi.org/10.1038/s41598-022-09376-6) · [Miao 등, 2017년 현장](https://doi.org/10.1029/2019JG005051)

ORNL의 30분 기록에서 `FPAR_measured`는 센서 기반 흡수율이고 `FPAR_VI`는 red-edge NDVI 추정값이다. Mead 센서값은 투과광과 군락 위 반사광을 빼고 토양 반사광을 더해 계산한다. Battaglia의 차단율은 입사광 대비 투과광 비율만 사용한다. 공개 스키마에는 입사 PAR와 계산된 흡수율이 있으나 투과광과 두 반사광의 개별 열은 없다. 차단율을 재구성하려면 투과광 또는 순반사 보정 자료가 추가로 필요하다. [Wu 등, 식 23 및 공개 변수](https://www.nature.com/articles/s41597-024-03004-w) · [Battaglia 광 차단 측정](https://doi.org/10.2134/cropsci2018.05.0337)

Earthdata CMR에서 CSV의 파일 식별자와 SHA-256을 확인했다. 카탈로그의 SHA-256과 공개 체크섬 파일은 일치했다. ZIP과 개별 CSV는 인증 화면으로 연결된 뒤 401이었고, AmeriFlux의 두 BADM 링크도 로그인으로 연결됐다. 데이터 원본 해시 검증과 30분 행 검사는 미수행이며 **실제 날짜별 비교 쌍은 0개**다. [ORNL 데이터](https://doi.org/10.3334/ORNLDAAC/2136) · [AmeriFlux BADM 안내](https://ameriflux.lbl.gov/data/aboutdata/badm-data-product/)

다음은 확보한 LIRF 공개 자료의 군락 피복률·LAI가 같은 포장과 날짜로 연결되는지 확인하는 작업이다. 피복률은 기하학적 면적 비율로 분류하고 광 차단율과 별도로 다룬다. Mead 행 단위 연결과 농학 검증 및 본 학습은 보류 중이다.

[출처·접근 결과](../outputs/runs/20261107T072300Z_ornl_mead_fpar_lai_0eda4047/sources.json) · [검증 결과](../outputs/runs/20261107T072300Z_ornl_mead_fpar_lai_0eda4047/verification.json)

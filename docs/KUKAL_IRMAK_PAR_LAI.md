# Kukal·Irmak 옥수수 PAR–LAI 공개 자료 확인

네브래스카 Clay Center의 SCAL 시험에서 80일형 옥수수는 2016·2017년, 113일형은 2017년에 조사됐다. 각 성숙형·연도 조합은 보고된 관측 계열이다. 연속 센서와 수동 계측은 측정 시간과 공간 범위가 다르다. [광량 연구 §2.2·그림 10](https://doi.org/10.1016/j.agrformet.2019.107887) · [관련 논문 §2.3~2.4](https://doi.org/10.1002/agg2.20110)

| 자료 | 확인한 측정 방식 | MARS 적용 범위 |
|---|---|---|
| 연속 PAR | 고정 센서의 1분 관측을 15분 평균으로 기록했다. 입사광은 시험장 한 지점, 투과광은 군락별 지면 부근의 선형 센서에서 측정했다. | 원본 시각·포장 연결과 유효 구간을 확보하면 같은 시간 구간의 투과광·입사광 합계로 일별 차단율을 계산할 수 있다. |
| 정오 PAR와 LAI | AccuPAR LP-80으로 맑은 날 정오 전후 군락 위·아래 광량을 측정했다. LAI는 이 방식으로 추정한 전체 LAI다. 그림 12는 광량계로 측정한 fIPAR와 LAI를 비교한다. | 광량계 역산 LAI를 독립 녹색 LAI로 분류할 수 없다. 연속 PAR는 별도 센서이므로 두 비교의 관측 의존성은 구분한다. |
| 일별 그래프 | 그림 13은 연속 센서의 일별 광량과 열량 기준으로 보간한 LAI를 사용했다. §3.2는 입사 PAR 결측 일부를 일사량으로 채운 구간을 보고한다. | 보간 LAI와 보충한 입사광을 직접 실측으로 집계할 수 없다. |

논문의 LAI 방법에는 작물별 20개 위치, 그림 6 설명에는 30개 측정값으로 표시돼 있다. 원시 표본 ID 없이 이 차이를 해소할 수 없다. 파괴 표본은 지상부 건물중을 얻는 데 사용됐다. 본문에서 그 표본의 독립 잎 면적을 확인하지 못했다. [광량 연구 §2.3·그림 6·12·13](https://doi.org/10.1016/j.agrformet.2019.107887) · [별도 생육 논문](https://doi.org/10.2134/agronj2019.01.0017)

출판사 웹 페이지의 직접 요청은 403이었다. Crossref에 연결된 Elsevier XML은 서지 정보만 반환했다. Crossref 관계 필드에는 데이터 링크가 없었고, DataCite에서 논문 DOI를 인용한 데이터셋 검색은 0건이었다. OpenAlex에 저장소 전문이 등록돼 있지 않았다. 대학 학위논문 다운로드는 PDF 대신 HTML을 반환했고 공개 서지에는 교내 인증 안내가 있다. 논문 방법은 공개 웹에 노출된 본문 사본에서 확인했다. 이번에 확인한 경로에서는 행 단위 PAR 파일과 독립 LAI 파일을 확보하지 못했다. [Crossref 기록](https://api.crossref.org/works/10.1016/j.agrformet.2019.107887) · [대학 학위논문 서지](https://digitalcommons.unl.edu/dissertations/AAI13861925/) · [논문 사본](https://www.scribd.com/document/468312571/Kukal-et-al-2020-Light-interactions-use-and-efficiency-in-row-crop-canopies-under-optimal)

**검증 가능한 같은 포장·날짜의 독립 LAI–PAR 쌍은 0개다.** 다음은 Zhou 등의 보충 데이터 1에서 포장·조사일·입사·투과광 열과 별도 LAI 측정 여부를 확인한다. 해당 연구의 PAR 채집은 오전 늦게부터 정오 무렵에 집중돼 있어 일별 적분 검증과 구분한다. [Zhou 등, PAR 방법·보충자료](https://academic.oup.com/plcell/article/36/5/1600/7584950)

[검증 결과](../outputs/runs/20261107T075326Z_kukal_irmak_par_lai_ae7ab1c5/verification.json) · [접근 기록 및 원본 해시](../outputs/runs/20261107T075326Z_kukal_irmak_par_lai_ae7ab1c5/access.json)

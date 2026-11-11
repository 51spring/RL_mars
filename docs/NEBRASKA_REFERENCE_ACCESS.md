# Nebraska 부록·참조 원문 공개 접근 점검

2026-11-07. 공식 HTML5개를 보존하고 두 참조 논문의 서지·초록·공개 다운로드 링크를 대조했다. **Schmer2020·Sindelar2019a 전문 PDF와 Li2023 부록은 확보하지 못했다.** 이번 완료 범위는 가용성·부분집합 경계 점검이며 재현입력 확보 완료가 아니다.

취득: `outputs/runs/20261106T234559Z_nebraska_reference_sources_3fd38462/verification.json`.
검사: `outputs/runs/20261106T234731Z_nebraska_reference_access_audit_aa4e4f99/verification.json`.
재현: `scripts/fetch_nebraska_references.py`, `scripts/audit_nebraska_reference_access.py`.

| 자료 | 공식 기록·취득 | 이번에 확정하지 않은 항목 |
|---|---|---|
| Schmer2020, DOI10.1002/agj2.20192 | 대학/USDA HTML200,대학이 연결한 PDF403 | 전체 연도별 파종/밀도/시비/관수·품종·설계 계층 매핑 |
| Sindelar2019a, DOI10.2136/sssaj2018.06.0225 | 대학/USDA HTML200,대학이 연결한 PDF403 | 깊이별 수리 수치·2010 초기상태·처리별 원 관측 |
| Li2023 부록 | 대학 HTML200,본문의 부록 DOI 참조 확인;기존 출판사403 | FigS1/TableS2 등 실제 파일·전체 모형 입력 |

403은 정상 공개 링크를 직접 요청한 결과이며 접근 제어를 우회하지 않았다. 같은 거부 링크를 반복 호출하거나 미발송 자료 요청을 보내지 않았다. 실제 파일 부재나 공개자료 전체 부재로 확대 해석하지 않는다.

## 확인한 적용 범위

Schmer의 공식 초록은2011–2018년 전체 실험에 N125/200kg/ha와 manure/cover/control을 포함한다고 설명한다. 이미 확인한 Li2023은 이 전체 실험의 N200부분집합8처리다. **현재 취득한 Nebraska XLSX로 N시비량에 따른 반응 대비를 확보했다고 판단하지 않는다.** 옥수수 N재고/흡수 관측과 N투입량을 바꾼 실험 대비를 구분한다. 두 논문을 추가 독립 연구로 세거나 전체 실험의 처리 평균을 현재 자료의 누락 셀로 복제하지 않는다.2010행과 Schmer의2011–2018분석 범위 연결도 미확정이다.

Sindelar의 공식 초록은 관리 후5/6년의 토양 수리 연구와 잔사 제거56%를 설명한다. 이 연구 결과를2010파종 전 초기 수리값으로 쓰지 않는다. Li의 약59%와 출처/기간이 달라 수치 하나로 통합하지 않았다. 품종 계수·전체 토양층·일별 관리값은 초록으로 확보할 수 없다.

두 전문을 취득하지 못했으므로 기존 SD/N요약 차이와 관수4회 반복의 실험단위 의미는 해소되지 않았다. 원자료·요약값·공분산·SE·전체 입력을 새로 채운 항목은0개다. 기존17항목 명세와 출처별 원값은 그대로 보존한다.

## 링크 목록의 한정 및 수정

최초 취득 실행의 `linked_resources.json`은 `content`와`href`에서 키워드를 찾으면서 초록의 supplemental이라는 단어도 URL처럼 포함한 문제가 있었다. 그 목록을 통한 추가 다운로드는 없었다. 원 실행을 덮어쓰지 않고 이번 `official_metadata_inventory.json`에서 HTMLParser의 실제`a href`·URL형식·HTML엔티티 해석으로 목록을 다시 검증했다. 수집 스크립트도 URL형식 조건을 보완했다. 실제 부록 payload 링크는 이번 대학 저장소 앵커 범위에서 식별하지 못했다.

## 다음 작업

Nebraska는 **전문·부록 및 불일치 설명 확보 대기**로 유지한다. 같은 접근 실패를 반복하기보다 별도 후보 Iran관수×N DOI10.17632/6zj7pzftwg.1의 공개 파일 목록과 실제 payload 확보를 다음 우선순위로 둔다. 원래 loading상태인 빈 목록을 파일 없음으로 해석하지 않고, 날짜·수량 기준·오차·완전 입력이 실제 파일에 있는지 확인한다.

활성10연구 역할·28처리/16대비·정량 준비0개·연구/본학습false를 유지한다. 새native/학습/모형 입력 할당은0건이다. 이번 변경은 출처 조사 및 다음 작업 설정이며 기존 소프트웨어204검사 결과를 재실행 결과로 표시하지 않는다.

공식 출처: [Schmer 대학 저장소](https://digitalcommons.unl.edu/agronomyfacpub/1425/), [Schmer USDA 기록](https://www.ars.usda.gov/research/publications/publication/?seqNo115=368850), [Sindelar 대학 저장소](https://digitalcommons.unl.edu/agronomyfacpub/1286/), [Sindelar USDA 기록](https://www.ars.usda.gov/research/publications/publication/?seqNo115=354236), [Li 대학 저장소](https://digitalcommons.unl.edu/usdaarsfacpub/2628/).

# Masii 시험 프로토콜과 포장 기록 연결 검토

Mulwa 연구진의 2024년 학회 초록 `NMK_AKE89`(초록집 인쇄 184쪽)를 저장소 설명과 대조했다. 지역·연구진·교미교란 처리별 농장 수·장치 간격과 조사 기간이 일치해 같은 시험일 가능성이 높다. 농장 번호와 초록의 시험 포장을 직접 연결하는 자료는 확인되지 않았다. [학회 초록집](https://www.researchgate.net/publication/383282319_THEME_Utilization_of_Biological_Resources_for_Sustainable_Development_Nature_Conservation_and_Climate_Resilience) · [Kenyatta University 발표 목록](https://agriculture.ku.ac.ke/faculty-profiles-department-of-agricultural-science-and-technology/prof-ruth-kahuthia-gathu) · [Mendeley V1](https://data.mendeley.com/datasets/g8fsd6dpxk/1)

| 항목 | 대조 결과 |
|---|---|
| 재배 기간 | 초록은 2023년 4–8월과 2023년 10월–2024년 3월을 보고한다. 원자료 조사일 28개는 각각 해당 월 범위에 들어간다. |
| 시험 설계 | 두 출처 모두 교미교란 유무별 농장 3곳과 장치 간격 20m를 보고한다. 저장소는 별도로 하위 포장 IPM/대조 배치를 설명한다. |
| 품종 | 초록에 KDH 414-12(Ukamess)가 명시되어 있다. 원자료의 포장별 품종으로 확정하려면 자료 연결표가 필요하다. |
| 배치 반경과 면적 | 초록은 반경 112m와 농장당 약 2,000m², 저장소는 반경 127m와 광역 처리 범위 5ha를 보고한다. 반경 차이는 미해결이다. 농장 면적과 광역 범위는 별도 항목으로 보존했다. |
| 살포 및 조사 순서 | 저장소는 조사 결과에 따른 생물학적 방제와 합성 살충제 사용을 설명한다. 초록은 필요시 다른 해충도 관리했다고 보고한다. 포장별 실제 시행일·약제·용량·조사 전후 순서는 공개 자료에서 연결하지 못했다. |

V1 통합문서 6개의 OOXML을 확인했다. 시트 11개 중 숨김 시트와 주석 파일은 없었다. 시즌 2 곡실 수량 통합문서에 외부 통합문서 참조 1개와 캐시 셀 10개가 포함돼 있다. 외부 원본을 확보하거나 살포·기상 기록으로 확인한 상태는 아니다. 첫 시즌 처리 라벨과 발생률 키 충돌은 원출처에 남아 있다.

## 보정에 필요한 연결

- 조사일은 확인됐으며 같은 포장의 연속 조사 구간은 144개다. 관측소 ID나 포장 좌표를 확인한 기상 매칭, 실제 살포 사건 매칭, 동일 식물·시점의 독립 반복 판독은 모두 0건이다. 해당 수치는 확인된 연결 건수이며 실제 현장에서 사건이 없었다는 뜻으로 사용하지 않는다.
- 케냐 기상청은 관측자료 요청과 관측·위성 결합 격자 자료를 구분해 제공한다. NASA POWER 일별 자료도 좌표와 일 집계 기준을 지정할 수 있다. 연결에는 농장–시즌과 관측소 또는 좌표의 대응, 기상 단위와 일 경계가 필요하다. 지역 대표 좌표를 포장에 부여하지 않았다. [케냐 기상청](https://meteo.go.ke/Services/climate-data-management/) · [NASA POWER 일별 API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- 방제 효과에는 포장별 시행일, 약제·투입량, 조사 전후 순서와 대조구의 무처리 확인이 필요하다. 조사 잡음에는 같은 식물·시점의 독립 판독과 MARS가 관측하는 최근 7일 신생 피해량에 대응하는 기준 측정이 필요하다.
- 다음은 공개 피해 척도 검증 연구에서 동일 식물 독립 판독과 실제 잎 면적 측정을 함께 제공하는지 확인하는 단계다. [Toepfer et al. 피해 척도 검증 연구](https://link.springer.com/article/10.1007/s10340-021-01359-2)

`scripts/audit_masii_faw_protocol.py`에 기존 `field_audit.json` 경로를 인자로 주면 파일 해시, 조사일 범위와 통합문서 구조를 재검사한다. 결과는 `outputs/runs/20261107T025729Z_masii_faw_protocol_linkage_78d174c5/protocol_linkage.json`에 있다.

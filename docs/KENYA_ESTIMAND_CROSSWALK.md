# Kenya 분석대상·불확실성 교차대조와 원논문 연결

2026-11-07. 추정평균/대비/실패자료를모형별로대조했다. **점추정이같아도오차는바꿔쓸수없고,생산시즌조건부수량으로전체시즌실패위험을평가할수없다.** 활성레지스트리추가/모형적합은하지않았다.

근거: `outputs/runs/20261107T012319Z_kenya_estimand_crosswalk_af9712d0/verification.json`.
재현: `scripts/build_kenya_estimand_crosswalk.py`.

## 원논문 연결과 실제 취득 상태

출판사검색색인의Data availability는현재Mendeley자료를직접연결한다. 논문은 **Sowing-time strategies alter maize grain yield, stover production and biomass allocation across contrasting rainfed environments in eastern Kenya**,DOI10.1016/j.eja.2026.128364,PIIS1161030126003837이다. 제목/저자/DOI를Crossref공식응답과대조했다.

공식취득: `outputs/runs/20261107T012059Z_kenya_protocol_sources_72dfbf08/verification.json`.
출판사본문HTML은403이었다. Crossref가직접제공한공식XML경로는HTTP200/2083bytes였지만 **coredata서지정보만있고본문/방법은없었다.** 이응답은 `outputs/runs/20261107T012133Z_kenya_linked_fulltext_e59c8d07/article.xml`에보존했다. 경로명/HTTP성공을전문확보로간주하지않고 `full_protocol_acquired=False`로한정했다.

Crossref권호일은2027년1월,CCBY라이선스시작기재는2026-10-07이다. 두필드를동일한발행일로합치거나라이선스시작을별도확인된온라인게재일로바꾸지않았다. 전문을확보하지못해수분보정률/채취방법/전체입력값은여전히미확정이다.

## 비교 대상과 오차

원07표에서별도cross-site모형30행을분리하면08표와대응하는189행이남는다. site/응답/season/sowing/variety로대응하고productive-season접미사의의미를별도로보존했다. 원평균과원SE/df/CI/행번호는 `EMM_primary_vs_season_specific.json`에보존했다.

| 비교 | 대응 수 | 점추정 검토차이 | SE 차이 | 추가 경계 |
|---|---:|---:|---:|---|
| primary EMM vs season-specific EMM | 189 | 0 | 189 | df도69행에서다름 |
| primary sowing 대비 vs season-specific 대비 | 126 | 0 | 126 | 각대비의자기모형SE를유지 |
| primary 대비 방향 vs 자기모형 EMM차이 | 146 | 0 | 계산안함 | cross-site포함,공분산무시SE생성0 |

검토차이는절대0.0000001출력단위의보고해상도점검이며계측오차나농학합격선이아니다. 두분석의오차차이는동일평균이라고해서자료오류라는뜻이아니라**적합모형/공분산/df가다르다는경계**다. SE/CI를섞거나둘중작은SE를고르지않는다. 원대비SE를두EMM의독립SE공식으로교체하지않았다. 모형재적합이나공분산재현을수행한것은아니다.

07표의7모형은Kiamaogo곡실/잔사/HI, Machang'a잔사/생산시즌곡실/생산시즌HI, Duma cross-site잔사다. cross-site의Variety=NA행은별도모형결과로유지했고새품종/추가독립관측으로세지않았다. 원site/season/model키가다르면평균을단순병합하지않는다.

## 생산시즌 조건과 실패위험

Kiamaogo의곡실추정은5시즌이고,Machang'a의곡실/HI추정은 **SR09/LR10 두생산시즌**이다. 실패요약과교차하면다음과같다.

| Machang'a 시즌 | 요약 포장-시즌 | 곡실 실패 | primary곡실평균에포함 |
|---|---:|---:|---|
| LR09 | 18 | 17 | 아니오 |
| SR09 | 18 | 0 | 예 |
| LR10 | 18 | 0 | 예 |
| SR10 | 18 | 18 | 아니오 |
| LR11 | 18 | 18 | 아니오 |

제외3시즌의54포장-시즌은실패53개와곡실이있던1개를함께포함한다. 이는원모형의정확한적합행수를복구한것이아니라공개실패요약으로확인한**분석대상범위**다. 포함시즌만으로무조건부평균수익/전체실패율을산출하지않는다. 실패를골라빼거나미공개원수량을0으로채우지않는다. 실패요약은실패포장ID/개별수량을제공하지않는다.

기존90행의강우노출/날짜도4site-season만있어전체10site-season프로토콜/기상을완성하지못한다. 수분보정기준·원곡실·전체토양/기상/관리·품종계수·초기상태는미해결이다.

## 다음 출처 경로

Kenyatta대학공식저장소에서Ngetich의 **Enhancing Farmers'Agricultural Productivity Through Improved Field Management Practices in the Central Highlands of Kenya** 기록을찾았다. [공식기록](https://ir-library.ku.ac.ke/items/334fc540-fd9b-4812-9920-6d116dbfe558)은파종시기/AquaCrop관련원프로토콜후보다. 이번웹열람은timeout으로전문을취득하지못했다. 같은지점/저자라도동일실험·전체시즌/품종·관리·보정노출을먼저대조해야하므로해당수치를현재자료에이식하지않았다.

다음은이공식저장소의공개파일확보와원현장프로토콜/수량보정/모형보정이력대조다. 부분실험·과거AquaCrop사용이현재DSSAT계수의독립성을자동증명하지않는다. 기존10연구역할/정량준비0개·연구/본학습false·새native/학습0을유지한다.

주요원출처: [출판사기록](https://www.sciencedirect.com/science/article/pii/S1161030126003837), [Crossref등록정보](https://api.crossref.org/works/10.1016/j.eja.2026.128364), [Mendeley자료](https://data.mendeley.com/datasets/tdw54wgvbf/1).

2026-11-07 공식원현장파일후속: `KENYA_LEGACY_PROTOCOL_AUDIT.md`. 대학PDF2개는3쪽발췌/1쪽초록이며전문미확보. AquaCrop과거보정언급·LR09무곡실vs현재1양성정의차이를미해결보존,입력할당0. 세현장후보의완료요건은미충족/대기이며다음독립작업은우선순위3 Oliveira두연구의중복/단위/수분기준대조다.

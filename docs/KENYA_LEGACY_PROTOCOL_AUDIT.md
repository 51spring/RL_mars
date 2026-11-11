# Kenya 대학 저장소 원현장 문서·과거 모형 이력 감사

2026-11-07. 공식 저장소의 두 PDF를 확보하고 전4쪽을 렌더링 대조했다. **학위논문 파일은3쪽발췌,초기파종논문파일은1쪽초록으로,전체방법/수량보정식/입력표는확보하지못했다.** 다운로드성공을전문확보로승격하지않았다.

학위논문취득: `outputs/runs/20261107T014953Z_kenya_thesis_pdf_5b37285e/verification.json`.
공식파일목록: `outputs/runs/20261107T015050Z_kenya_thesis_bundle_inventory_cdebf755/verification.json`.
초기파종초록취득: `outputs/runs/20261107T015203Z_kenya_early_protocol_source_eb106ea9/verification.json`.
감사/재현: `outputs/runs/20261107T015403Z_kenya_legacy_protocol_audit_337a03f4/verification.json`, `scripts/audit_kenya_legacy_protocol.py`.

## 실제 파일과 공개 범위

학위논문공식기록은 **Enhancing Farmers'Agricultural Productivity Through Improved Field Management Practices in the Central Highlands of Kenya**,Ngetich,KipchirchirFelix이며기록날짜는2013-03-21이다. 취득PDF표지는November2012로서로다른날짜를보존했다.

- 실제PDF3쪽은표지,선언문(인쇄ii),초록(인쇄xvii)이다. 중간방법장/표가있는연속학위논문이아니다.
- 공식API묶음ORIGINAL에는동일한1PDF(1800513bytes)만있다. LICENSE/TEXT/THUMBNAIL에각1파일이있는목록을보존했다. 추가전체본문이이항목의다른ORIGINAL파일에있다고가정하지않는다. 다른공개저장소에없다는주장은아니다.
- PDF의크기·공식MD5·취득SHA256을대조했다. 원문PDF의SHA256은`c068f4682f2e5207c6d9bc750b17c4c38b0ff6f2aab63859acf761a7ba3e82fd`다.

별도 **Effect of Planting Dates on Maize Yield under Rainfed Conditions in the Central Highlands of Kenya** 대학기록의공개PDF도6281bytes/1쪽초록이었다. 본문제목/방법장/데이터부록이포함되지않아해당실험의완전프로토콜로쓰지않는다. 렌더링중대체폰트경고가있었으나출력페이지의텍스트와추출문을대조했고원본을변경하지않았다.

검색색인호스트repository.ku.ac.ke의인증서호스트불일치는실패근거로보존했다. 인증서검증을끄지않고대학공식ARM목록이별도로명시한유효HTTPS호스트ir-library.ku.ac.ke의동일기록링크로취득했다. 학위논문메타데이터의localhost:4000주소도사용하지않고공식rel=item HTTPS링크를사용했다. 추가권한·외부연락·접근우회0이다.

## 보정 이력과 실험 간 연결

학위논문초록은파종시기·경운/지표관리·분할N·유출등여러실험과AquaCrop의매개변수화/보정/검증을설명한다. 현재데이터의같은지점이름/유사파종처리와겹칠가능성이있지만정확한시즌/포장/계수/보정분할은확인되지않았다.

**AquaCrop과거사용을현재DSSAT계수의보정노출또는독립성증명으로대체하지않는다.** 여러생산물/지점의R²를개별처리검증점수로쓰지않는다. 초록의분할시비`70N`결과는다른분할N실험의진술이므로파종시기실험에70kgN/ha를할당하거나미표시단위를추정하지않는다.

초기1쪽초록은Mbeere의3파종×2품종×3반복과LR09/SR09/LR10,AquaCrop현장자료보정을설명한다. 품종이름·전체5시즌·두지점의입력/설계일치와데이터계보는미확정이다. 같은저자/지점이라도이를새독립연구로추가하지않았다.

## LR09 곡실 정의 차이

초기초록은LR09에곡실이없었다고진술한다. 현재CSV18은Machang'a LR09에서18포장-시즌중17실패,1곡실있음(Wet sowing/Duma43)을보고한다. **동일실험/집계/선별/실패정의가확인되지않아미해결차이로보존**한다. 초록으로현재양의관측1개를지우거나실패18/18로변경하지않는다. 현재생산시즌조건부분석과과거전체시즌요약을합치지않는다.

## 완료 범위와 다음 작업

현재완료범위는공식파일취득·발췌범위확인·과거모형이력과정의차이명세다. 원곡실/수분보정·전체토양/기상/초기상태/품종/관리·정확보정분할등8필수영역을미해결계약으로유지했다. 새native입력/학습/보정·독립역할승격0이다.

별도현장보정후보Nebraska/Iran/Kenya는1차파일/명세조사를거쳤으나전체입력/보정요건을충족한후보0개다. 우선순위2의**완료조건은충족하지않았으므로대기**로남긴다. 같은공개파일재시도대신,독립적으로가능한기존우선순위3 **Oliveira architecture/N두연구의실험중복·단위·수분기준대조**를다음작업으로둔다. 새공개근거가확보되면현장후보의명시된공백을다시검토한다.

활성10연구역할·정량준비0개·연구/본학습false를유지한다. 이번출처감사를204개소프트웨어검사의새실행으로보고하지않는다.

공식기록: [학위논문](https://ir-library.ku.ac.ke/items/334fc540-fd9b-4812-9920-6d116dbfe558), [초기파종연구](https://ir-library.ku.ac.ke/items/a8fa524b-35f8-45fd-97ef-d046b26b94ba).

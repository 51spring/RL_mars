# 앞으로의 진행 순서

기준일: 2026-11-07. 기본 작업 폴더는 `C:/Users/WD/Desktop/강화학습_MARS`입니다.

현재 소프트웨어 204개 검사와 동일 이미지 CPU·CUDA 장기 교차 비교 4회를 통과했습니다. 각 실행은 102,400단계, 800갱신, 770완료 시즌입니다. 농학 검증과 본 실험은 아직 완료하지 않았습니다.

| 순서 | 작업 | 완료 조건 |
|---|---|---|
| 1. 입력·모델 경계 검증 | 좌표/표고 전송 오류의 별도 패치·원본 대비 회귀, 다른 작물 실패 경로, 작물 원소 C 측정과 수확 반출·잔사·다음 시즌 경계 감사 | 변경 근거·변경 전후 궤적·항목별 수지 및 허용오차를 기록. 측정 불가능/미검증 항목은 통과 처리하지 않음 |
| 2. 농학 자료 확보·보정 | 공개 10연구에서 처리별 평균·SE·수확 기준·품종/토양/기상을 확인. 온도·신규 피해 조사·피해/회복 반응을 보정하고 다른 연구로 검증 | 보정/독립 검증 연구를 분리하고 재현 가능한 허용범위를 충족. 자료 부족 값은 가정/민감도 대상으로 유지 |
| 3. 기준선·예비 학습 | 규칙 정책 πB의 관수/살포 임계값 튜닝, 같은 시비·방제 규칙을 쓰는 관수 전용 πI와 공동 관리 πJ 예비 학습. GAE 0.95/0.98 및 보상 계수 검토 | validation에서만 선택하고 모든 정책에 같은 제약 적용. 최종 test split 미사용, 제약 위반 0건 |
| 4. 실험 설정 동결 | 완료된 동일 이미지 장치 비교를 바탕으로 본 학습 설정·시드·시험 감축일 달력·조건별 대비·통계 절차 확정 | 연구 진입 조건 충족 후 설정/이미지/자료/정책 버전 고정. 실제 처리량으로 학습·평가 비용 산정 |
| 5. 본 학습·공통 시즌 평가 | πI·πJ 각10시드×500만 단계(총1억 단계). 감축9조건+무감축1조건, 조건별1,000개 공통 외생 시즌 평가 | 대응 관계를 보존한 결과 배열, 체크포인트·실패 기록·원장·최종 raw 수익을 보관 |
| 6. 통계·민감도·결과 정리 | 평균 수익·하위10% 평균·수량·투입량·실패율, 학습 시드/시즌 교차 부트스트랩·Holm 보정·H1/H2 사전 대비, H3 검증 범위 확인 | 효과크기·불확실성·제약 위반과 적용 한계를 보고. 보상·초기화·마스크 기여도 및 단가/예산/해충 등의 민감도 분석 |

v2 N 회계 이후 공개3연구28처리와16원문 대비를 등록했습니다. Santos의 R3 이삭 수량과 native 건조 곡실의 endpoint가 달라 직접 보정에 사용할 수 없고, 독립 연구의 역할은 유지합니다. 현재 정량 가능 시나리오는0개입니다. 다음은 **grain maize 보정 자료와 수치 오차/전체 토양·품종·일별 실험 입력 확보**, 피해/단계 매핑 검토입니다. 상세: `AGRONOMIC_SCENARIOS.md`. 본 실험은 아직 시작하지 않습니다.

온도 기준·조사 잡음은 현재 미보정이며 전체 원소 C·수확 후 수지와 독립적인 회복/물·질소 상호작용 검증도 남아 있습니다. 이 조건을 충족하기 전에는 본 실험을 시작하지 않습니다. 검증 실패로 대체 모형을 택할 경우 연구 범위를 다시 명시하고 H3를 제외합니다.

동일 이미지 장기 비교에서 CPU는 두 대응 쌍에서 CUDA보다 23–34% 빨랐습니다. CPU 기술 기본값을 유지합니다. 본 실험 소요 기간은 동결된 학습 설정의 실측 후 정합니다. 상세는 `CONTROLLED_DEVICE_THROUGHPUT.md`에 있습니다.

작업 시작·완료·실패 시 `PROGRESS.md`를 갱신하고, 각 실행은 `outputs/runs/`의 고유 폴더에 설정·소스 스냅샷·이미지 식별자·검증 근거를 보존합니다.

기본 학습 실행은 보정된 CPU/CUDA 프로필로 전환했고 원본 재현은 -LegacyMetadata로 선택합니다. 상세 변경과 증거는 METADATA_AND_HARVEST_BOUNDARY.md를 참고합니다.

후속 자료 조사: `docs/GRAIN_MAIZE_DATA_SEARCH.md`. Ghana의9개 수량 주변평균과 SEM은 확보했으나 셀값/오차 공분산/전체 재현 입력은 미확보입니다. 기존28시나리오와 분리하며 초기 온실 원자료의 단위 충돌도 해결 전입니다.

독립적으로 진행하는 기준선 기술 경로: `docs/BASELINE_PAIRED_DIAGNOSTIC.md`. 규칙/무투입의validation4쌍을 사용하며 실제 실행 상태는 진행 기록을 확인합니다. 임계값 선택/우열 검정과 분리합니다.

v2 범용 토양/실패 경계 확장(현장·다년 검증과 구분): `docs/ACTUAL_HARVEST_DOMAIN_EXTENSION.md`. 두 범용 토양8쌍 및 깊은 파종 실패까지22회 실행 통과, 유기물 초기화 경고는 유지합니다.

원소 탄소 측정 가능성 감사: `docs/CARBON_MEASUREMENT_AUDIT.md`.16개 보존 출력5,696일의 토양C 산술/잔사 인터페이스 통과, 작물/종자/동화/호흡/수확/피해의6개 원소C 항목 미확인으로 전체C 게이트 유지.

2년Q 잔사 경계/출력 완전성: `docs/MULTIYEAR_RESIDUE_HANDOFF.md`.2개 수확률·4성공 실행에서6개 경계 통과. 기존 탄소 최종 휴경 출력9일 누락을 한정하고 진단 전용 무버퍼 설정으로 보완했습니다. 후속 다년 모형N 원장도 아래 범위에서 완료했습니다.

2년Q 통합 모형N: `docs/MULTIYEAR_MODELED_N.md`. 두 수확률·4RUN1,468재고 관측과8개음성대조 통과. 연도 간 누적·휴경→작물 초기화까지 검증했으며 원소C/농학은 미완료입니다.

후속 범용 토양2종의 다년Q 검증: `MULTIYEAR_GENERIC_SOILS.md`. 8회 실행·2,936개N재고 관측·12개 초기화 및4개 음성 대조 통과. 실제 현장/독립농학과 구분하며 F모드는 미검증입니다.

F모드 지정2년 달력·N 검증: `F_MODE_MULTIYEAR.md`.4회 실행·1,468관측/6초기화와4음성대조 통과. 범용토양F/다른실패/농학으로 일반화하지 않습니다.

수분 부족 발아 실패: `GERMINATION_FAILURE.md`. 대조/후보4회에서 실패·raw회계·관수 출아·프로세스 정리 통과. 경고의 고정15일과 실제DSGT21일을 구분했습니다. 출아 관수 대조도 수량0이므로 수량 회복으로 해석하지 않습니다. 다음 우선순위는 농학 입력의 누락 보완과 검증 가능한 자료 범위 확정입니다. 생육 중 사망/실패는 미검증으로 유지합니다.

USDA LIRF 현장 입력 확보: docs/LIRF_INPUT_QUALIFICATION.md. 공식11파일, 포장수량96개/처리요약24개·일별기상1,461개를 보존했습니다. 전체 연구를 독립 기본 작물/수분 반응 검증 후보로 유지합니다.2009T3 평균 불일치·기상4결측·초기/관개수N·2008관수/강수 구분과 응애/우박/서리 외란이 남아 정량 준비0개를 유지합니다. 다음은 공개DSSAT 품종/모형 패키지·원관측과 토양/초기상태 대응 확인이며 현재 자료를 무피해 대조로 확정하지 않습니다.

LIRF 기상/공개모형 감사: docs/LIRF_WEATHER_MODEL_AUDIT.md. 공개 패키지는2008년100ET 한처리, DEKALB521/MZCER045로 현장52-59와 동등성·계수 보정 이력·048호환성 미확인. 같은 관측소 API에서도4값 결측 유지, 일사 재집계3후보 미적용. 다음은2008 토양·초기상태·관리 대조와 품종 이력/단위 확인입니다.

LIRF2008 토양·초기상태·관리 대조: docs/LIRF2008_INPUT_CROSSWALK.md. 총관수는 일치하지만 강수40.114mm·관수39.5mm의하루차이·시비/관개수N·초기날짜 차이가 남았습니다. SLFC1/입도10개스키마 문제는 자동수정하지 않습니다. 다음은AgMIP→DSSAT 변환기의 과거 단위/기본값과 패키지 재현·현장 검증 계약을 구분해 확인합니다.

AgMIP writer실행검증: docs/AGMIP_DSSAT_TRANSLATION_AUDIT.md.2버전×8조건/32파일통과. PLDP÷10·명시적−99의−9.9변환·입도미보정·SLFC1미출력 확인. configs/lirf_translation_contract.json으로패키지진단과현장검증을구분했습니다. 다음은전체DOME 채움/날짜/품종 계약과 공개패키지 재현용 진단입력입니다.

DOME·입력경계: docs/LIRF_DOME_EXPORT_BOUNDARY.md.7FILL/4조건·12음성대조·진단4파일 생성검증통과. 원본입도차단·명시적fixture27변경으로원본/가정을분리했고176검사통과. 다음은격리native의수용값·품종045/048·날짜/종료검사이며 현장검증/본학습false를유지합니다.

LIRF native수용검사: docs/LIRF_NATIVE_INPUT_QUALIFICATION.md. 원날짜2건거부·원기상헤더2건오독재현·명시적시작일/헤더/계수호환2건수용검증. 기상2,364항목·초기상태·16관수/10시비·실제종료확인. 다음은패키지가정/native기본값/현장실측차이원장과측정가능항목확정이며181소프트웨어검사통과, 독립농학/본학습false유지.

LIRF 입력 차이19항목·D22부분토양8층·일평균 기온1,461일 출처 원장: `LIRF_EVIDENCE_LEDGER.md`. 자동 현장값 대체0, 전체 토양 프로필 미완료. 다음은 Climate AMP에서 실제 WTH/native TAMP까지의 정의·변환 경로 확인과 사전 민감도 기준 지정이다. 연구/본학습false·정량준비0개를 유지한다.

온도 native5조건·기상5,900항목·기본값정확회귀 완료: `LIRF_TEMPERATURE_PATH.md`. WTH전달 배율1/STEMP계절항1/2를 확인했으며 WGEN런타임·과거Climate의미 차이는 미해결이다. 최초구분열오류 실행은withdrawn 보존, 현장값선택0. 다음은D22토양 수분특성·밀도·초기상태 매핑 가능성 검토다.

D22 수리자료 경계 완료: `D22_HYDRAULIC_MAPPING.md`. 압력판4층/24평균/42기술표본,200cm깊이의54.61%만덮음. 밀도통합표·FC기간모호성·6월처리평균/1월초기일차이·하부수분깊이정의충돌을유지. 다음은방법문서/연도별시트깊이및산출식대조이며native수리값선택0·정량준비0개다.

연도별 수분24시트/방법문서 대조 완료: `LIRF_WATER_DEPTH_AUDIT.md`. 전연도 하부깊이충돌유지, 공통상부105/135cm각633후보·SWD599대조중2차이보존. 다음은2010-07-01 T2/T3와포장별FC처리평균대조·비교불확실성계약이다. 후보는현장검증/초기상태로승격하지않으며정량준비0개유지.

포장FC집계/비교계약완료: `LIRF_FC_AGGREGATION.md`.96포장672FC·168평균/SD쌍·48정적FC저장량,2010/11집계정확일치에도7/1 T2/T3차이2건유지. 다음은일별포장SWC/계측오차/보정이력가용성확인이다. 정적FC SD를일별오차로대체하지않고모형오차임계값null·정량준비0개를유지한다.

일별포장수분/계측보정가용성점검완료: `LIRF_DATA_AVAILABILITY.md`,미발송명세 `LIRF_MISSING_DATA_SPEC.json`.공식12자료·60시트/228주석확인범위에서해당원자료/오차공분산미확보.다음은모형패키지·관련논문의품종계수/보정연도/split대조로독립검증역할조건확정.추측보정·본학습진입없음.

품종계수/보정노출감사: `LIRF_CALIBRATION_PROVENANCE.md`.5계수세트·3논문대조,정확패키지계보/독립성미확정.현재역할conditional_candidate_not_qualified,전체연구holdout계획유지·독립검증점수불허.다음은Fang2014등직접계보근거확인이며원계수교체/학습없음.

Fang2014계보추적/근거고정독립성검사완료: `FANG_LINEAGE_FOLLOWUP.md`.원문미취득/계보미확정유지,readiness에SHA·연구ID·실제독립성보고서검사연결.203검사통과,실제LIRF자격거부·전체연구false.다음은10연구의재현입력/오차/역할통합우선순위와실행가능외부검증경로정리다.

통합우선순위: `AGRONOMIC_INPUT_PRIORITIES.md` 및 `configs/agronomic_input_priorities.json`.10연구×8항목/5작업,다음은Oveysi독립입력명세→별도현장건조곡실보정자료선별이다.계보검사는모든independent_역할6종을포괄하며204검사통과.정량준비/본학습게이트는false유지.

Oveysi독립입력명세완료: `OVEYSI2010_INPUT_DOSSIER.md`.17항목/14미확정,FC/WP관수기준·계절량확인,밀도단위/최대N기준·일별기상/일정등제한유지.우선순위1명세완료·정량실행차단,다음은별도현장건조곡실보정자료선별.204검사통과·본학습false.

2026-11-07 별도 보정자료 1차 선별 완료: 외부 후보3건과 기존 LIRF 확장 단서1건을 분리했다. Nebraska 원본1개를 확보했으나 활성 연구 추가/정량 준비 승격은0건이다. 다음은 Nebraska 원자료–요약표·실험단위·날짜/빈값 의미와 원논문의 토양/기상/관리/품종 보정 이력 대조다. Mendeley 파일 목록과 새 LIRF 확장자료 공식 위치는 후속 확보 대상으로 남긴다. 상세: `FIELD_CALIBRATION_CANDIDATE_SCREEN.md`.

2026-11-07 Nebraska 입력감사 완료/정량 차단: `NEBRASKA_INPUT_AUDIT.md`. 수량72평균 대조에서 큰 차이는 없지만 SD9건 차이, N목표값 추가 차이, 관수336조합×4반복을 확인했다. 강수3287일의 날짜 연속성을 확인했으며 완전 기상으로 승격하지 않았다. 다음은 공식 부록과 Schmer2020/Sindelar2019a의 관리·토양·품종 입력 확보 및 원 SD 차이 해석이다.

2026-11-07 후속 공개접근 점검: `NEBRASKA_REFERENCE_ACCESS.md`. 공식HTML5개 확보,참조PDF2건403·부록미확보로 완전 입력/SD차이는 계속 미확정이다. 현재 Nebraska부분집합은N200단일수준이므로N투입량반응대비를 확보한 것으로 세지 않는다. 다음 작업은 Iran관수×N후보의공개파일목록/실제payload확보다. Nebraska전문/부록후속은 유지한다.

2026-11-07 Iran후속완료: `IRAN_WATER_N_INPUT_AUDIT.md`. 공식익명API에서원파일1개/7시트·36수확행·12그룹확보,관수4합계/건물36항등식/IWP72캐시산술대조. 날짜/요일/DAP충돌및전체토양/기상/관리/품종미확정으로정량준비승격0.다음은원논문/프로토콜연결및출처별입력공백명세다.

2026-11-07 후속명세: `IRAN_PROTOCOL_DOSSIER.md`. 셀주석16개에서파종2/관비11/수확2관리행을회수했다. 이전파종일미확정은보고일출처확보로보완하되2014수확DAP충돌과비료회차량/전체입력미확정은유지한다. 100숫자관수행은검출된요일충돌구간밖이지만일정/효율자격을부여하지않는다. 정확한원논문연결은미해결,다음은Kenya공개파일확보다.

2026-11-07 Kenya후속: `KENYA_INPUT_AUDIT.md`. CSV20개확보·90강우노출/날짜행및기존분석출력범위구분. 강우48/실패75/t602/공분산18선택산술검토차이0이나원포장곡실/일별기상미확보로정량준비승격0. 다음은응답대상/오차범위대조와원프로토콜/누락원자료연결이다.

2026-11-07 Kenya분석대상후속: `KENYA_ESTIMAND_CROSSWALK.md`. EMM189/대비126점추정일치하나SE각189/126차이유지. Machanga생산시즌조건부곡실과제외3시즌54포장-시즌(실패53)분리. 원논문DOI연결확인,API200은coredata만으로전문미확보. 다음은공식Kenyatta저장소원프로토콜파일확보/동일성·보정이력대조다.

2026-11-07 공식원현장파일후속: `KENYA_LEGACY_PROTOCOL_AUDIT.md`. 대학PDF2개는3쪽발췌/1쪽초록이며전문미확보. AquaCrop과거보정언급·LR09무곡실vs현재1양성정의차이를미해결보존,입력할당0. 세현장후보의완료요건은미충족/대기이며다음독립작업은우선순위3 Oliveira두연구의중복/단위/수분기준대조다.

2026-11-07 Oliveira 후속: `OLIVEIRA_OVERLAP_UNITS.md`. 14항목 원출처 대조로 보고 설계는 구분했으나 포트·보정계보 독립성 미확정, Dryad 1개체/논문 2개체와 HI 분모·수분 기준 차이 유지. 우선순위3 명세 완료/정량 차단, 다음은 우선순위4 Du Plessis 온도–발육·생존 자료 추출이다.

2026-11-07 Du Plessis 온도별 발육·생존 자료 추출을 완료했다. 일정 온도 실험의 발육 기간, 사망률과 회귀 적산온도를 기록했다. 다음은 온도별 번식과 개체군 증가율을 보고한 생명표의 적용 범위 확인이다. 상세 근거는 `DUPLESSIS_THERMAL_CONSTRAINTS.md`에 있다.

2026-11-07 온도별 번식·생명표 비교를 완료했다. 다음은 같은 포장의 반복 유충수·엽피해 관측과 기상·방제 이력을 결합할 수 있는 공개 자료 탐색이다. 관측오차를 따로 추정할 수 있도록 같은 시점의 반복 판독 여부도 확인한다. 상세 근거는 `FAW_THERMAL_DEMOGRAPHY.md`에 있다.

2026-11-07 Masii 반복조사 원자료 6개를 확보했다. 두 시즌에서 동일 방문의 유충 수·피해 점수 6,717행을 확인했다. 다음은 공개 프로토콜·기상·실제 살포 기록 연결과 관측오차 판독 자료 확인이다. 상세는 `FAW_FIELD_SURVEILLANCE.md`에 있다.

2026-11-07 Masii 학회 초록과 저장소의 시험 설계를 대조했다. 반경 차이와 포장별 기상·살포 연결은 미해결이다. 다음은 피해 척도 연구의 독립 반복 판독·잎 면적 기준값 확인이다. 상세는 `MASII_PROTOCOL_LINKAGE.md`에 있다.

2026-11-07 피해 척도 원문과 Soujanya 공개 보충표 9시트를 확인했다. MARS 신규 잎 손실 기준과 독립 반복 판독을 함께 충족한 공개 자료는 확인하지 못했다. 다음은 토고 Koffi 반복조사의 날짜·기상·방제 연결 검토다. 상세는 `FAW_SURVEY_MEASUREMENT_ERROR.md`에 있다.

2026-11-07 토고 Koffi 연구의 조사 설계와 공개 메타데이터를 확인했다. 원본 다운로드 403과 논문 상관표 두 행 불일치를 기록했다. 다음은 Varella 공개 자료의 포장 알·초기 유충 생존과 소실을 대조하는 단계다. 상세는 `TOGO_FAW_FIELD_LINKAGE.md`에 있다.

2026-11-07 Varella 보충표의 알·초기 유충 16코호트를 본문과 대조했다. 다음은 계수별 보정 가능 범위와 기술 민감도 시나리오 정리다. 상세는 `VARELLA_FIELD_STAGE_SURVIVAL.md`에 있다.

2026-11-07 해충 계수별 보정 요건과 기술 민감도 가정을 분리했다. 합성 408개 궤적을 검증했다. 다음은 제약을 만족하는 고정 행동과 공통 DSSAT 시즌을 사용한 선택 시나리오의 전달 검사다. 상세는 `FAW_PARAMETER_SENSITIVITY.md`에 있다.

2026-11-07 DSSAT 공통 두 시즌의 기술 민감도 전달 검사 8회를 완료했다. 다음은 고정 행동의 보상 계수 η 민감도 검사다. 상세는 `FAW_DSSAT_SENSITIVITY_PAIRING.md`에 있다.

2026-11-07 공통 DSSAT 시즌 η 민감도 검사에서 12회 실행했다. 다음은 동일 롤아웃에 GAE λ=0.95·0.98을 적용하고 수확·시간제한 처리를 대조하는 기술 검사다. 상세는 `REWARD_ETA_SENSITIVITY.md`에 있다.

2026-11-07 실제 DSSAT GAE 공통 롤아웃에서 두 λ와 종료 처리를 검증했다. 다음은 장기 CPU·CUDA 기록의 비교 조건 점검이다. 상세는 `GAE_COMMON_ROLLOUT.md`에 있다.

2026-11-07 기존 장기 CPU·CUDA 기록을 감사하고 동일 이미지 교차 순서의 1,024단계 예비 비교 4회를 통과했다. 다음은 같은 조건의 102,400단계 장기 반복이다. 상세는 `CONTROLLED_DEVICE_THROUGHPUT.md`에 있다.

2026-11-07 동일 이미지 장기 CPU·CUDA 교차 비교를 완료했다. 다음은 농학 보정·독립 회복·물×질소 검증에 필요한 입력과 사전 기준을 재점검한다.

2026-11-07 농학 검증 진입 조건을 재점검했다. 28개 시나리오 중 정량 검증 가능 0개이며, Oveysi 물×피해 기술 대비 4개를 분리했다. 다음은 Battaglia 포장 회복 자료의 원문·학위논문 및 실험 입력 대조다. 상세는 `AGRONOMIC_REENTRY_AUDIT.md`에 있다.

2026-11-07 Battaglia의 수량·IPAR 논문은 동일 포장 시험으로 확인했다. 생육 조사 날짜·GDD 헤더 42쌍을 기록했다. 다음은 Spindletop 일별 기상과 실제 관수일의 분리 연결 검토다. 상세는 `BATTAGLIA_RECOVERY_INPUT_AUDIT.md`에 있다.

2026-11-07 Battaglia의 시험장 일별 기상 366행과 생육 조사일 42개를 대조했다. 관수 이벤트는 미확보다. 다음은 Loradale 토양층·초기 상태와 두 품종의 DSSAT 계수 출처 대조다. 상세는 `BATTAGLIA_SPINDLETOP_WEATHER.md`에 있다.

2026-11-07 Battaglia 토양·품종 출처를 대조했다. 포장 토양과 품종 계수는 미확보다. 다음은 농장 기상으로 논문 누적 GDD 42개를 대조하고 무피해 대조의 생육 관측 구간을 정리하는 작업이다. 상세는 `BATTAGLIA_SOIL_CULTIVAR_LINEAGE.md`에 있다.

2026-11-07 Battaglia 부록의 누적 GDD 42개를 재현하고 무피해 대조 생육 도달 구간 48개를 정리했다. 다음은 IPAR 관측과 DSSAT 군락 광 차단 출력의 대조다. 상세는 `BATTAGLIA_GDD_PHENOLOGY.md`에 있다.

2026-11-07 Battaglia IPAR의 측정 조건과 CERES 내부 광 차단량을 대조했다. 다음은 성장 계산 시점의 광 차단 진단과 피해·종료일 날짜 계약 검사다. 상세는 `BATTAGLIA_IPAR_CROSSWALK.md`에 있다.

2026-11-07 CERES 성장 시점 IPAR 진단과 피해·수확일의 날짜 계약을 실제 DSSAT 4시즌에서 확인했다. 다음은 시간대별 IPAR와 LAI를 함께 제공하는 독립 공개자료 검토다. 상세는 `NATIVE_CERES_IPAR.md`에 있다.

2026-11-07 독립 광 차단율·LAI 후보 7개를 검토했다. 다음은 ORNL DAAC 센서 관측 fPAR과 Mead 독립 LAI의 현장·날짜 대조다. 상세는 `INDEPENDENT_IPAR_LAI_SCREEN.md`에 있다.

2026-11-07 ORNL–Mead의 흡수율과 독립 LAI를 대조했다. 2019 US-Ne3의 보고 기간은 겹치며 원본 행 연결은 미완료다. 다음은 LIRF 군락 피복률과 LAI의 포장·날짜 대조다. 상세는 `ORNL_MEAD_FPAR_LAI.md`에 있다.

2026-11-07 USDA LIRF에서 피복률·LAI 포장·날짜 180쌍을 연결했다. 다음은 2012년 개발·2013년 보류 평가의 기하학적 피복률 진단이다. 상세는 `LIRF_CANOPY_COVER_LAI.md`에 있다.

2026-11-07 2012년 LIRF 피복률 곡선의 2013년 MAE는 7.93%p, 평균 오차는 −5.62%p였다. 다음은 Kukal·Irmak의 공개 원자료·부록에서 시간대별 PAR와 독립 LAI의 포장·날짜 연결을 확인하는 단계다. 상세는 `LIRF_COVER_LAI_HELDOUT.md`에 있다.

2026-11-07 Kukal·Irmak 광량 연구에서 연속 PAR와 광량계 추정 LAI의 측정 경로를 분리했다. 공개 원자료에서 확인한 독립 LAI–PAR 쌍은 0개다. 다음은 Zhou 등의 보충 데이터 1의 포장·조사일·PAR와 독립 LAI 여부 확인이다. 상세는 `KUKAL_IRMAK_PAR_LAI.md`에 있다.

2026-11-07 Zhou 공식 보충자료에서 PAR 유전자형 효과와 포장 센서 원값을 구분했다. 독립 LAI 연결 쌍은 0개다. 다음은 옥수수 군락 층별 광 차단 연구의 원자료·포장·날짜 연결 점검이다. 상세는 `ZHOU_MAIZE_PAR_SUPPLEMENT.md`에 있다.

2026-11-07 Duan 두 논문의 8개 연도·밀도 조합에서 수확 지표 32개가 일치했다. 독립 LAI–PAR 원자료 연결은 0개다. 다음은 누적 광학 근거의 적용 범위와 Battaglia 무피해 대조의 비교 범위 확정이다. 상세는 `DUAN_MAIZE_CANOPY_LAYER_PAR_LAI.md`에 있다.

2026-11-07 광학 자료의 비교 조건과 Battaglia 무피해 평균 8개를 정리했다. 현장–DSSAT 직접 광학 비교 쌍은 0개다. 다음은 같은 UFGA 무피해 조건에서 38·76cm 이랑 폭의 기술 민감도 검사다. 상세는 `OPTICAL_EVIDENCE_BATTAGLIA_CONTROL.md`에 있다.

2026-11-07 CERES 38·76cm 이랑 폭을 보관 성장일 124개에서 LAI를 고정해 계산했다. Docker Linux 엔진이 시작되지 않아 두 폭의 실제 시뮬레이션과 LAI 반응은 실행 대기다. 상세는 `NATIVE_CERES_IPAR_ROW_WIDTH.md`에 있다.

2026-11-07 Docker 엔진 복구 후 38·76cm 실제 DSSAT 두 시즌을 완료했다. 124일 평균 차단율 차이는 +5.023%p였다. 다음은 복수 공통 기상 시드에서 폭 민감도 범위를 확인하는 기술 검사다. 상세는 `NATIVE_CERES_IPAR_ROW_WIDTH.md`에 있다.

2026-11-07 4개 UFGA 기상 시드의 38·76cm 무피해 8시즌을 완료했다. 다음은 실험용 해충 환경의 공통 validation 시즌에서 고정 규칙·무투입 기준선의 제약과 수익 원장을 확인하는 기술 검사다. 폭 민감도 상세는 `NATIVE_CERES_IPAR_ROW_WIDTH.md`에 있다.

2026-11-07 실험용 해충 검증 4쌍에서 고정 규칙과 무투입 대조의 마스크·감축 공지·수익 원장을 확인했다. 다음은 관수 전용 정책의 시비·방제 규칙 공유 검사다. 상세는 `BASELINE_PAIRED_DIAGNOSTIC.md`에 있다.

2026-11-07 관수 전용 규칙 공유를 실제 DSSAT 12시즌과 별도 예산 0 검사에서 확인했다. 다음은 최신 근거로 연구 진입 요건을 재점검하고 미확보 현장 입력의 우선순위를 확정하는 단계다. 상세는 `BASELINE_PAIRED_DIAGNOSTIC.md`에 있다.

2026-11-07 연구 진입을 재점검했다. 등록 28개 시나리오에서 정량 검증 가능은 0개다. 다음은 LIRF 2012–2013 통합 파일의 무피해·수분 반응 재현 입력 감사다. 상세는 `RESEARCH_GATE_RECHECK.md`에 있다.

2026-11-07 LIRF 2012–2013 입력 명세에서 건조 수량 94개, 처리·날짜 4,248행, 강수 불일치 7일을 확인했다. 다음은 GLY04와 Crop Log의 기상·관리 날짜 및 관개수 N 대조다. 상세는 `LIRF_2012_2013_BASELINE_INPUT_DOSSIER.md`에 있다.

2026-11-07 LIRF 강수 불일치 7일을 GLY04와 대조하고 작업일지의 관수·시비 날짜 및 관개수 N 범위를 정리했다. 다음은 블록·처리별 토양층과 파종 전 수분·무기태 N, DK 52-04 품종 계수 계보 확인이다. 상세는 `LIRF_2012_2013_WEATHER_MANAGEMENT.md`에 있다.

2026-11-07 LIRF 공식 배치도와 옥수수 96개 포장을 대조해 16개 블록 코어에 연결했다. 다음은 DayCent 보충자료와 LIRF 2008–2024 확장 파일에서 파종 초기값과 포장 관측의 출처를 찾는 작업이다. 상세는 `LIRF_2012_2013_INITIAL_SOIL_CULTIVAR.md`에 있다.

2026-11-07 DayCent 분석의 기간과 USDA 기존 파일 목록을 확인했다. 2012–2013 파종 초기 수분·무기태 N 신규 확보는 0건이다. 다음은 건조 곡실 수량의 연도·블록 짝대조와 결측에 따른 오차 정리다. 상세는 `LIRF_INITIAL_OBSERVATION_SOURCE_FOLLOWUP.md`에 있다.

2026-11-07 LIRF 건조 곡실 수량의 연도별 블록 짝대조 28개와 결측의 영향을 정리했다. 다음은 같은 대비의 기간별 ET·총관수 노출 대조다. 상세는 `LIRF_2012_2013_BLOCK_PAIRED_YIELD.md`에 있다.

2026-11-07 LIRF 관수 목표·기간별 ET·총관수 대조를 완료했다. 다음은 처리별 생육 달력과 0–105 cm 관측·예측 수분 결핍 대조다. 상세는 `LIRF_2012_2013_ACHIEVED_WATER_EXPOSURE.md`에 있다.

2026-11-07 LIRF 생육일과 0–105 cm 수분 결핍 909쌍을 대조했다. 다음은 누적 증거의 활용 범위와 정량 진입 요건 정리다. 상세는 `LIRF_2012_2013_STAGE_SOIL_WATER_DEFICIT.md`에 있다.

2026-11-08 LIRF 증거 9건을 통합하고 현장 재현·정량 검증 요건을 확정했다. 다음은 Battaglia 피해 시행일·실제 손실량·회복 관측의 포장별 연결이다. 상세는 `LIRF_2012_2013_EVIDENCE_QUALIFICATION.md`에 있다.

2026-11-08 Battaglia R2 적엽 시행일 두 날짜를 확인했다. 포장별 실제 피해량·회복 연결은 미확보다. 다음은 별도 포장 적엽 시험의 대응 원자료 선별이다. 상세는 `BATTAGLIA_PLOT_DAMAGE_RECOVERY_LINKAGE.md`에 있다.

2026-11-08 포장 적엽 자료 5개를 선별했다. 실제 손실량–회복 연결은 0개이며 LeafScan 모의 면적 94쌍은 조사오차 자료 후보로 남겼다. 상세는 `INDEPENDENT_FIELD_DEFOLIATION_RECOVERY_SOURCE_SCREEN.md`에 있다.

2026-11-08 LeafScan 모의 면적 94쌍의 손실률을 재현했다. 독립 판독 확인은 0쌍이다. 다음은 실제 FAW 피해 면적과 독립 판독의 동일 시점 자료 탐색이다. 상세는 `LEAFSCAN_LEAF_LOSS_MEASUREMENT_QUALIFICATION.md`에 있다.

2026-11-08 실제 FAW 피해 공개자료에서 7일 신규 잎 손실과 독립 판독의 연결은 0쌍이었다. 다음은 물×질소×잎 피해 공동 처리 자료 선별이다. 상세는 `FAW_PHYSICAL_LOSS_INDEPENDENT_RATING_SOURCE_SCREEN.md`에 있다.

2026-11-08 물×질소×잎 피해 공동 처리를 검토한 7개 자료에서 적격 포장 설계는 0개였다. 다음은 KBS033의 물×질소 원자료와 재현 입력 감사다. 상세는 `FIELD_WATER_NITROGEN_DAMAGE_JOINT_DESIGN_SCREEN.md`에 있다.

2026-11-08 KBS033 현재 시험지의 7개 옥수수 시즌과 2023년 관리 일지 연결을 확인했다. 다음은 2023년 기온 결측과 층별 토양·품종 입력의 출처 감사다. 상세는 `KBS033_FIELD_DATA_AUDIT.md`에 있다.

2026-11-08 KBS033 기온 결측·토양·품종 입력 감사를 마쳤다. 다음은 물 처리군 내부의 질소 반응을 시즌별로 대조하는 작업이다. 상세는 `KBS033_2023_WEATHER_SOIL_LINEAGE.md`에 있다.

2026-11-08 KBS033 질소–수량 대비를 정리했다. 다음은 2020·2023년 같은 추비량에서 수량이 달랐던 F1·F2의 처리 이력과 시비표 확인이다. 상세는 `KBS033_WATER_NITROGEN_DESCRIPTIVE_CONTRASTS.md`에 있다.

2026-11-08 F1·F2의 과거 시비 이력과 2023년 시비표를 대조했다. 다음은 2014년 KBS033의 DSSAT 재현 입력 감사다. 상세는 `KBS033_F1_F2_NITROGEN_HISTORY_AUDIT.md`에 있다.

2026-11-08 KBS033 2014년의 기상·시비·관수 입력을 대조했다. 다음은 DKC52-59 독립 생육 자료와 CERES 계수 연결 가능성 확인이다. 상세는 `KBS033_2014_REPLAY_INPUT_SCREEN.md`에 있다.

2026-11-08 DKC52-59 독립 생육 근거를 선별했다. 다음은 미네소타 동일 품종 밀도 시험의 반복·수량 구성 자료 감사다. 상세는 `DKC52_59_INDEPENDENT_PHENOLOGY_SCREEN.md`에 있다.

2026-11-08 미네소타 DKC52-59 밀도별 관측 평균을 확인했다. 다음은 KBS033 2014년 최종 개체밀도 자료의 출처 확인이다. 상세는 `DKC52_59_MINNESOTA_DENSITY_COMPONENT_AUDIT.md`에 있다.

2026-11-08 KBS033 2014년 72포장에 직접 연결된 실측 개체수는 0개다. 다음은 KBS033 재현 범위 종합 판정이다. 상세는 `KBS033_2014_FINAL_STAND_LINEAGE.md`에 있다.

2026-11-08 KBS033은 기술적 수량 대비로 보관한다. 다음은 FACETS Live Oak의 옥수수 포장 원자료와 독립성 감사다. 상세는 `KBS033_REPLAY_READINESS_DISPOSITION.md`에 있다.

2026-11-08 FACETS 옥수수 포장·수확 키를 대조했다. 다음은 실제 관수·시비·수확 환산과 DSSAT 보정 계보 점검이다. 상세는 `FACETS_LIVE_OAK_CORN_INPUT_AUDIT.md`에 있다.

2026-11-08 FACETS 시장수량 환산 180개와 FDACS 시비 23행을 확인했다. 다음은 HydroShare SWAT 관리 입력에서 실측 일별 관수·시비 출처를 확인하는 작업이다. 상세는 `FACETS_LIVE_OAK_OPERATIONS_AND_CALIBRATION_LINEAGE.md`에 있다.

2026-11-08 HydroShare의 현장시험 기반 관리 입력을 장기 시나리오와 분리했다. 다음은 FDACS 계약 21894 최종보고서와 부록의 관측 기록 대조다. 상세는 `FACETS_LIVE_OAK_DAILY_OPERATIONS_SOURCE_AUDIT.md`에 있다.

2026-11-08 FDACS 최종보고서의 관수·시비·수확 절차를 SWAT과 대조했다. 다음은 탈곡 표본 180개의 수량 환산과 보고서 처리 평균 확인이다. 상세는 `FDACS_21894_MEASURED_OPERATIONS_CROSSWALK.md`에 있다.

2026-11-08 FDACS 수량 180개를 환산해 본문 평균을 대조했다. 다음은 분할구 설계를 반영한 블록별 수량 대비다. 상세는 `FDACS_21894_GRAIN_YIELD_RECONSTRUCTION.md`에 있다.

2026-11-08 FDACS 분할구에서 시즌별 수량 대비를 계산했다. 다음은 FACETS/FDACS의 재현·독립 검증 가능 범위를 판정하는 작업이다. 상세는 `FDACS_21894_SPLIT_PLOT_YIELD_CONTRASTS.md`에 있다.

2026-11-08 FACETS/FDACS의 밭–시즌별 재현·독립 검증 가능 범위를 판정했다. 다음은 Ransom 공개 자료의 질소 반응 재현 입력을 선별하는 작업이다. 상세는 `FACETS_FDACS_REPLAY_READINESS_DISPOSITION.md`에 있다.

2026-11-08 Ransom 49개 지점–연도의 수량·기상·관수·토양 입력을 연결했다. 다음은 관수 지점–연도 8개의 질소 반응 재현 후보 선별이다. 상세는 `RANSOM_CORN_N_2014_2016_INPUT_SCREEN.md`에 있다.

2026-11-08 Ransom 관수 지점 8개의 재현 후보를 선별했다. 다음은 Becker 2016 DSSAT 입력 명세다. 상세는 `RANSOM_IRRIGATED_SITE_REPLAY_SHORTLIST.md`에 있다.

2026-11-08 Becker 2016 DSSAT 입력 명세와 관수수 질소 소스를 대조했다. 다음은 관수수 N의 네이티브 질량·정밀도 검사다. 상세는 `RANSOM_BECKER_2016_DSSAT_INPUT_DOSSIER.md`에 있다.

2026-11-08 네이티브 AP005 비교에서 질소 투입량의 정밀도 손실을 확인했다. 다음은 격리 진단 빌드의 두 작성 경로와 정밀 출력 대조다. 상세는 `RANSOM_BECKER_IRRIGATION_N_NATIVE_MASS_PROBE.md`에 있다.

2026-11-08 Becker 기술 입력의 DSSAT 투입량 소수점 보존을 확인했다. 다음은 초기 토양 프로필 검증이다. 상세는 `RANSOM_BECKER_NATIVE_SERIALIZATION_PRECISION.md`에 있다.

2026-11-08 Becker 4블록의 수분과 무기질소를 깊이별로 대조했다. 채취일이 달라 단일 초기일을 확정하지 않았다. 다음은 포장 위치와 SSURGO 구성 토양·층별 수리값 대조다. 상세는 `RANSOM_BECKER_2016_INITIAL_SOIL_PROFILE.md`에 있다.

2026-11-08 Becker 시험구 64개를 SSURGO D62A에 연결했다. 다음은 Hubbard·Mosford 기술 시나리오의 DSSAT 초기 수분·무기질소 재고 대조다. 상세는 `RANSOM_BECKER_2016_SSURGO_HYDRAULIC_CROSSWALK.md`에 있다.

2026-11-08 Becker 1블록 기술 시나리오 4개의 초기 수분·무기질소 재고가 DSSAT 출력과 일치했다. 다음은 4월 21–26일 모의 경로와 4월 26일 수분 코어 대조다. 상세는 `RANSOM_BECKER_2016_NATIVE_INITIAL_STOCK_PROBE.md`에 있다.

2026-11-08 Becker 파종 전 수분 경로를 4월 26일 코어와 대조했고 무기질소 장부 잔차를 확인했다. 다음은 유기탄소·잔사·토양온도 조건과 순무기화 및 무기질소 잔차 원인 검토다. 상세는 `RANSOM_BECKER_2016_PREPLANT_WATER_N_BRIDGE.md`에 있다.

2026-11-08 Becker 10개 조건에서 순무기화 민감도를 대조하고 상세 무기질소 장부를 검산했다. 다음은 공개 자료에서 토양온도·잔사량·하부 유기탄소의 근거를 확인하고 4블록 초기화 후보를 구성하는 작업이다. 상세는 `RANSOM_BECKER_2016_PREPLANT_MINERALIZATION_PROBE.md`에 있다.

2026-11-08 Becker 4블록×2개 대표층 후보와 입력 불확실성을 정리했다. 다음은 고정한 비교 조건의 네이티브 초기 재고 및 4월 26일 코어 대조다. 상세는 `RANSOM_BECKER_2016_FOUR_BLOCK_INITIALIZATION_EVIDENCE.md`에 있다.

2026-11-08 Becker의 고정 16조건에서 초기 재고와 4월 26일 수분 코어를 대조했다. 다음은 P0157AMX 생태형·품종 연결 및 수량을 가린 관리 입력 검토다. 상세는 `RANSOM_BECKER_2016_FOUR_BLOCK_NATIVE_INITIALIZATION_MATRIX.md`에 있다.

2026-11-08 Becker 두 P0157AMX 계수와 두 관리 일정의 네이티브 전달을 확인했다. 다음은 수량을 가린 64시험구 기술 재현 조건과 평가 항목 사전 고정이다. 상세는 `RANSOM_BECKER_2016_CULTIVAR_MANAGEMENT_REPLAY_GATE.md`에 있다.

2026-11-08 Becker 64시험구 기술 재현 256개가 입력·생육 점검을 통과했다. 다음은 건조수량 단위와 블록 내 처리 대비를 고정한 뒤 관측 수량을 대조하는 작업이다. 상세는 `RANSOM_BECKER_2016_YIELD_MASKED_TECHNICAL_REPLAY.md`에 있다.

2026-11-08 Becker 관측 수량 64개와 모의 256개를 대조했다. 네 조합 모두 수량이 과대였고 같은 총량의 분시 반응이 관측보다 작았다. 다음은 생육 중 질소·물 경로의 시점별 진단이다. 상세는 `RANSOM_BECKER_2016_FROZEN_YIELD_N_CONTRAST_AUDIT.md`에 있다.

2026-11-08 Becker 추비 전 표층 질산 과대와 7월 단회·분시의 모의 질소 흡수 수렴을 확인했다. 다음은 초기 유기물 풀·무기화와 깊이별 질산 이동 가정의 민감도 대조다. 상세는 `RANSOM_BECKER_2016_INSEASON_N_RESPONSE_DIAGNOSIS.md`에 있다.

2026-11-08 Becker 조기 질소 공급 경로 8개를 기술 대조했다. 다음은 코어 총질소의 입력 자격과 유기물 풀 배분·초기 질소 재고의 분리다. 상세는 `RANSOM_BECKER_2016_EARLY_N_SUPPLY_MECHANISM_PROBE.md`에 있다.

2026-11-08 Becker 코어 총질소의 환산과 CENTURY 기본값 대체를 확인했다. 다음은 4블록의 측정 C:N 호환 범위와 심층 결측 처리 검토다. 상세는 `RANSOM_BECKER_2016_TOTAL_N_POOL_INITIALIZATION_QUALIFICATION.md`에 있다.

2026-11-08 Becker 4블록의 총질소 입력 24개에서 전층 기본값 대체를 확인했다. 다음은 호환 관측층을 보존하는 층별 초기화의 기술 대조다. 상세는 `RANSOM_BECKER_2016_FOUR_BLOCK_JOINT_CN_SUPPORT.md`에 있다.

2026-11-08 Becker 호환 층 24개를 보존하는 기술 조건을 확인했다. 다음은 현장 재현 자격 종합 판정과 독립 자료 후보의 초기 토양·관리 입력 검토다. 상세는 `RANSOM_BECKER_2016_LAYERWISE_CN_INITIALIZATION_PROBE.md`에 있다.

2026-11-08 Becker를 기술 재현으로 분류하고 후속 3개 지점을 선별했다. 다음은 Waseca 2016 무관수 질소 전이의 입력 명세다. 상세는 [후속 후보 선별](RANSOM_BECKER_REPLAY_DISPOSITION_AND_FOLLOWUP_SITE_SCREEN.md)에 있다.

2026-11-08 Waseca 2016 무관수 입력 명세를 작성했다. 다음은 채취일 사이 강수와 코어 수분·수리값 차이를 반영한 날짜별 초기 수분·무기질소 자격 검토다. [Waseca 입력 명세](RANSOM_WASECA_2016_RAINFED_INPUT_DOSSIER.md)

2026-11-08 Waseca의 날짜별 강수와 포화수분 범위를 대조했다. 다음은 깊이별 질량 대응과 심층 결측, 하부 배수 조건을 고정하는 DSSAT 파종 전 기술 대조 설계다. [날짜별 초기화 판정](RANSOM_WASECA_2016_DATED_WATER_N_INITIALIZATION_QUALIFICATION.md)

2026-11-08 Waseca 파종 전 기술 조건 32개를 고정하고 초기 무기질소 질량을 검산했다. 다음은 격리 DSSAT에서 초기 재고와 4월 26일 수분을 대조하는 작업이다. [기술 대조 설계](RANSOM_WASECA_2016_PREPLANT_WATER_N_TECHNICAL_PROBE_DESIGN.md)

2026-11-08 격리 DSSAT Waseca 기술 조건 32개를 검산했다. 4월 26일 전 조건의 모의 수분이 코어보다 낮았다. 다음은 배수·지하수위·코어 근거와 현장 재현 활용 범위 판정이다. [네이티브 기술 대조](RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_TECHNICAL_PROBE.md)

2026-11-08 Waseca를 기술 진단으로 분류하고 Wisconsin 두 후보를 Dryad에 연결했다. 다음은 Plano 우선의 Plano·Lorenzo 2016 무관수 입력 명세다. [Waseca 활용 판정](RANSOM_WASECA_2016_PREPLANT_WATER_N_NATIVE_DISPOSITION.md)

2026-11-08 Plano·Lorenzo 무관수 입력 명세를 작성했다. 다음은 Plano 초기화 날짜와 SSURGO 수리값 검토다. [위스콘신 입력 명세](RANSOM_WISCONSIN_PLANO_LORENZO_2016_RAINFED_INPUT_DOSSIER.md)

2026-11-09 Plano 초기화 시점과 수리값을 검토했다. 다음은 4월 13일 수분과 독립된 초기 질소 가정을 적용할 무시비 기술 대조 설계다. [초기화 자격](RANSOM_WISCONSIN_PLANO_2016_INITIALIZATION_TIMING_AND_SOIL_HYDRAULICS.md)

2026-11-09 Plano 무시비 기술 조건 16개를 고정했다. 다음은 격리 DSSAT 실행과 날짜별 상태·물질수지 대조다. [기술 설계](RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_TECHNICAL_PROBE_DESIGN.md)

2026-11-09 Plano 네이티브 기술 조건 16개를 검산했다. 다음은 질소 과소의 초기값·순무기화·흡수·용탈 경로와 재현 활용 범위 대조다. [Plano 네이티브 대조](RANSOM_WISCONSIN_PLANO_2016_DATED_INITIALIZATION_NATIVE_TECHNICAL_PROBE.md)

2026-11-09 Plano 초기 재고·순무기화·작물 흡수·하단 용탈을 분리해 저장 출력 16조건을 검산했다. 현장 오차를 흐름별로 배분하려면 같은 시험구의 시작·종료 재고와 기간별 흡수·이동 근거가 필요하다. Plano는 기술 진단으로 보존하고 현장 재현 등록을 보류했다. [질소 경로와 활용 판정](RANSOM_WISCONSIN_PLANO_2016_DATED_N_RESPONSE_DISPOSITION.md)

2026-11-09 Lorenzo의 지도 포화값과 코어 수분을 대조하고 Plano와 예정 무시비 6월 시료를 연결했다. Lorenzo 초기 재고와 하부 경계의 근거가 부족해 현장 재현은 보류했다. [Lorenzo 초기화 자격](RANSOM_WISCONSIN_LORENZO_2016_INITIALIZATION_QUALIFICATION.md)

2026-11-09 Ransom 49개 시험에서 Lewis 2015와 Shumway 2016의 동일일 초기 수분·질소 근거를 확인했다. 다음은 Lewis의 현장 수리값과 P1498AM 외부 보정 자료의 완전성·계수 이력 검토다. [독립 현장 후보 선별](RANSOM_INDEPENDENT_BASELINE_SCREEN.md)

2026-11-09 Lewis의 4블록 코어 수분과 Marshall 수리값을 대조했다. Shelby 2015의 외부 P1498AM 원자료를 연결했고 파종 전 초기 토양과 관수·생육 자료 공백을 확인했다. P1498AM의 정확한 계수·생태형 및 보정 이력이 다음 정량 진입 조건이다. [Lewis 수리값과 보정 자료](RANSOM_LEWIS_2015_HYDRAULICS_AND_CULTIVAR.md)

2026-11-09 Novelty P1498AM의 공개 기상·관리 및 2015년 수량 주변평균을 대조했다. 품종별 무침수 보정에 필요한 공동 수량과 계수·생태형은 미확보 상태다. Lewis를 검증 후보로 유지하고 계수 근거가 있는 별도 후보를 병행 검토할 수 있다. [Novelty 보정 자료 감사](P1498AM_NOVELTY_CALIBRATION_EVIDENCE.md)

2026-11-09 Ohio P1197AM 출아·기상을 대조했다. Shumway에는 출처가 명확한 CERES 계수·생태형과 별도 보정 근거가 필요하다. [Ohio 출아 관측 감사](P1197AM_OHIO_EMERGENCE_EVIDENCE.md)

2026-11-09 Adnan 2019년 질소 처리별 관측과 2020년 공개 시트의 역할을 검토했다. Ordos 공개 후보의 토양 의존성과 평균 기상을 확인했다. 다음은 PREPCLIM 공개 예제에서 실행 입력과 독립 실측 계보를 분리해 확인하는 작업이다. [Adnan 자료 감사](ADNAN_CERES_CALIBRATION_EVALUATION_AUDIT.md)

2026-11-09 PREPCLIM 예제의 실험·품종·생태형·토양 연결을 확인했다. 재실행 기술 후보로 보존하고, 독립 평가용으로는 시험구 실측과 입력이 함께 공개된 자료를 별도로 선별한다. [PREPCLIM 감사](PREPCLIM_NATIVE_INPUT_AND_EVALUATION_AUDIT.md)

2026-11-09 출아 후 저온 실패와 브라질 2002년 기본 생육·수량 8처리 재실행을 완료했다. 생육 중 수분 스트레스 종료도 저온 배제 조건에서 확인했다. 다음은 브라질 입력과 논문 관리 기록의 차이 및 독립 수량 판정 기준을 확정하는 작업이다. [환경 검증](ENVIRONMENT_VALIDATION_SWEEP.md)

2026-11-09 BRPI0202 배포 기상과 자동관측소의 일사 차이를 대조했다. 다음은 261 mm 현장 관수 일정과 일사 원본 계보를 확인하거나, 별도로 보정·평가 연도가 분리된 SIAZ 자료의 재현 자격을 점검하는 작업이다. [BRPI0202 입력 검증](BRPI2002_MANAGEMENT_AND_WEATHER_QUALIFICATION.md)

2026-11-09 SIAZ 1996년 보정과 1995년 평가를 재실행하고 75 cm 줄 간격의 영향을 분리했다. 다음은 Zaragoza 배포 WTH의 좌표와 일자료, 80 cm 토양 프로필의 현장 계보를 대조하는 작업이다. [SIAZ 검증](SIAZ1995_1996_FROZEN_CULTIVAR_REPLAY.md)

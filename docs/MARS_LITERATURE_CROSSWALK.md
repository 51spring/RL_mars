# MARS 문헌 활용과 46편 비교표 대조

개정 제안서 14–16쪽의 참고문헌을 팀 검토 문서의 46개 제목과 대조했다. 대소문자·공백·문장부호를 정규화한 제목을 비교하고 저자·연도 및 원문 링크를 확인했다. 번호는 팀 검토 문서의 배열 순서다.

| 분류 | 편수 |
|---|---:|
| 두 목록에 모두 수록 | 29 |
| 46편 비교표에만 수록 | 17 |
| 개정 제안서 참고문헌에만 수록 | 0 |

같은 저자의 다른 논문은 따로 집계했다. Gautron 2022의 gym-DSSAT 보고서는 두 목록에 있고, 같은 해 작물 관리 강화학습 리뷰는 46편 비교표에만 있다. Baja 2025의 질소 제약 연구와 관측 비용 연구는 서로 다른 두 편이며 두 목록에 각각 수록됐다.

아래 표에서 구현·기술 검증, 설계 배경, 보정·독립 검증 후보를 구분했다. 보정·독립 검증 후보는 정량 판정이 완료되지 않았다. 46편에만 있는 문헌에는 팀 문서에서 확인한 검토 주제를 기록했다.

## 두 목록에 모두 있는 29편

| 번호와 팀 | 문헌 | 구분 | MARS에 가져온 내용 |
|---:|---|---|---|
| 1 (A) | Gautron 외 2022 · [gym-DSSAT: a crop model turned into a Reinforcement Learning environment](https://publications.cirad.fr/une_notice.php?dk=601356) | 구현 기반 | DSSAT를 일별 의사결정 환경으로 쓰는 구조를 채택했다. 실제 연결은 Gym/PDI 워커로 검증했다. |
| 2 (A) | Tao 외 2023 · [Optimizing Crop Management with Reinforcement Learning and Imitation Learning](https://www.ijcai.org/proceedings/2023/691) | 구현·비교 설계 | 관수·시비 공동 관리와 부분관측 비교를 참고했다. 곡실 단가 0.158 USD/kg을 초기 경제 설정에 반영했다. |
| 5 (A) | Baja 외 2025 · [Adaptive fertilizer management for optimizing nitrogen use efficiency with constrained reinforcement learning](https://doi.org/10.1016/j.compag.2025.110554) | 비교 배경 | 제약하 질소 관리의 선행 사례로 참고했다. MARS에서는 시비와 비용 제약을 자원 원장과 행동 마스크로 집행한다. |
| 6 (A) | Jones 외 2003 · [The DSSAT cropping system model](https://www.sciencedirect.com/science/article/pii/S1161030102001077) | 구현 기반 | 작물·토양·기상·관리 입력이 연결되는 DSSAT를 기본 작물 모형으로 사용했다. |
| 8 (A) | Saseendran 외 2014 · [Enhancing the Water Stress Factors for Simulation of Corn in RZWQM2](https://doi.org/10.2134/agronj2013.0300) | 검증 배경 | 수분 스트레스 계산이 옥수수 생육에 미치는 영향을 참고했다. RZWQM2 계수를 DSSAT에 옮기지 않았다. |
| 10 (A) | Batchelor 외 2020 · [Simulation of Maize Lethal Necrosis (MLN) Damage Using the CERES-Maize Model](https://doi.org/10.3390/agronomy10050710) | 피해 모형 배경 | 손상을 CERES-Maize 생장·수량에 전달한 사례를 검토했다. 실제 잎 가해 쓰기와 반출 회계는 MARS에서 구현했다. |
| 11 (A) | Blanco 외 2023 · [Severe Defoliation of Vegetative Maize Plants Does Not Reduce Grain Yield: Further Implications with Action Thresholds](https://www.ars.usda.gov/research/publications/publication/?seqNo115=405843) | 독립 검증 후보 | 강한 반복 적엽의 수량 반응을 검증 조건으로 참고했다. 인공 적엽 결과를 해충 피해량으로 환산하지 않았다. |
| 12 (A) | de Oliveira Jr. 외 2026 · [Early defoliation and nitrogen fertilization: effects on maize morphophysiology and production](https://doi.org/10.1007/s11738-026-03963-0) | 독립 검증 후보 | V4 절단과 질소 추비 시점에 따른 회복을 검증 후보로 등록했다. 온실 처리량을 포장 시비·피해율로 대입하지 않았다. |
| 14 (A) | Overton 외 2021 · [Global crop impacts, yield losses and action thresholds for fall armyworm (Spodoptera frugiperda): A review](https://doi.org/10.1016/j.cropro.2021.105641) | 해석 배경 | 피해와 방제 기준의 조건별 차이를 정리했다. MARS의 방제 임계값은 미확정이다. |
| 16 (A) | Schulman 외 2017 · [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) | 구현 | PPO를 학습 알고리즘으로 채택하고 MaskablePPO에서 마스킹된 행동을 처리했다. |
| 17 (A) | Schulman 외 2016 · [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) | 구현·기술 검증 | GAE를 채택하고 실제 공통 롤아웃에서 λ 0.95·0.98과 수확·시간제한 처리를 확인했다. 최종 λ 선택은 남아 있다. |
| 18 (A) | Huang 및 Ontañón 2022 · [A Closer Look at Invalid Action Masking in Policy Gradient Algorithms](https://doi.org/10.32473/flairs.v35i.130584) | 구현 | 무효 행동 마스킹의 근거로 사용했다. 물·질소·살포 선택지는 자원 원장이 계산한 실행 가능 집합을 따른다. |
| 19 (A) | Carrara 외 2019 · [Budgeted Reinforcement Learning in Continuous State Space](https://papers.nips.cc/paper_files/paper/2019/hash/4fe5149039b52765bde64beb9f674940-Abstract.html) | 제약 설계 배경 | 비용과 보상을 함께 다루는 예산형 정책을 참고했다. MARS는 일별 행동과 시즌 지출을 원장에서 검사한다. |
| 20 (A) | Agarwal 외 2021 · [Deep Reinforcement Learning at the Edge of the Statistical Precipice](https://papers.neurips.cc/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html) | 평가 계획 | 여러 시드와 효과크기·불확실성을 함께 보고하도록 설계했다. 10시드의 충분성은 예비 분산으로 재검토할 계획이다. |
| 22 (B) | Kelly 외 2024 · [Assessing the value of deep reinforcement learning for irrigation scheduling](https://doi.org/10.1016/j.atech.2024.100403) | 비교 설계 | 관수 정책의 경제적 가치가 강수·제약·기준선에 의존할 수 있어 관수 전용과 공동 관리를 공통 외생 시즌에서 비교하도록 설계했다. |
| 23 (B) | Baja 외 2025 · [To Measure or Not: A Cost-Sensitive, Selective Measuring Environment for Agricultural Management Decisions with Reinforcement Learning](https://doi.org/10.1609/aaai.v39i27.34999) | 관측 설계 배경 | 관측 정보의 가치를 참고해 제한된 조사와 잡음의 검증을 설계했다. 측정 구매 행동은 도입하지 않았다. |
| 27 (B) | Abang 외 2024 · [Maize plants can recover from fall armyworm damage under optimum crop production conditions in humid tropical agro-ecologies](https://doi.org/10.1093/jee/toae235) | 독립 검증 후보 | 자연 해충 피해의 주별 추적과 회복·수량을 검증 후보로 등록했다. 피해 등급과 집계 SE는 조사 잡음으로 사용하지 않았다. |
| 28 (B) | Santos 외 2018 · [Irrigation as an alternative to reduce damages caused by defoliation of sweet corn](https://www.scielo.br/j/hb/a/nLvnyKQ3FXHH9dCpGBkzNxw/) | 보정 후보 | 관수×적엽 처리 대비를 정리했다. 단옥수수 이삭 수량과 DSSAT 건조 곡실의 측정 대상 차이를 기록했다. |
| 29 (B) | Du Plessis 외 2020 · [The Effect of Temperature on the Development of Spodoptera frugiperda (Lepidoptera: Noctuidae)](https://doi.org/10.3390/insects11040228) | 생물학적 범위 | 온도별 발육 기간, 유충 생존, 발육 회귀를 추출했다. 포장 개체군 성장률이나 온도 기준으로 대입하지 않았다. |
| 30 (B) | Kaelbling 외 1998 · [Planning and acting in partially observable stochastic domains](https://www.sciencedirect.com/science/article/pii/S000437029800023X) | 관측 설계 | 직접 볼 수 없는 해충압과 관측 가능한 조사값을 분리하는 부분관측 설계에 참고했다. |
| 31 (B) | Stolz 외 2024 · [Excluding the Irrelevant: Focusing Reinforcement Learning through Continuous Action Masking](https://papers.nips.cc/paper_files/paper/2024/hash/acf4a08f67724e9d2de34099f57a9c25-Abstract-Conference.html) | 후속 비교 | 연속 행동 마스킹을 후속 비교 근거로 인용했다. 현재 구현은 이산 행동을 사용한다. |
| 33 (B) | Holm 1979 · [A Simple Sequentially Rejective Multiple Test Procedure](https://www.jstor.org/stable/4615733) | 통계 계획 | 감축 9조건의 사전 정의 대비에서 Holm 다중검정 보정을 계획했다. 본 실험 통계는 미실행이다. |
| 34 (C) | Balderas 외 2025 · [A comparative study of deep reinforcement learning for crop production management](https://doi.org/10.1016/j.atech.2025.100853) | 비교 배경 | 작물 관리 과제에 따라 PPO·DQN의 상대 성능이 달라질 수 있음을 연구 동기로 사용했다. |
| 36 (C) | Wang 외 2026 · [Learning-based agricultural management in partially observable environments subject to climate variability](https://doi.org/10.1038/s41598-026-57117-w) | 관측 설계 배경 | 기후 변동과 부분관측하 농업 관리의 선행 사례로 참고했다. MARS의 관측과 외생 시나리오는 별도로 구성했다. |
| 40 (C) | Blanco 외 2022 · [Grain Yield is Not Impacted by Early Defoliation of Maize: Implications for Fall Armyworm Action Thresholds](https://doi.org/10.3958/059.047.0209) | 독립 검증 후보 | 초기 적엽 시점과 강도별 수량 반응을 정리했다. 초기 피해가 항상 0이라는 통과 조건은 두지 않았다. |
| 41 (C) | Oveysi 외 2010 · [The impact of source restriction on yield formation of corn (Zea mays L.) due to water deficiency](https://doi.org/10.17221/86/2010-PSE) | 독립 검증 후보 | 수분 조건×생육단계별 잎 제거의 곡실 수량을 검증 대상으로 정리했다. 일별 기상·토양·품종 계보는 미확정이다. |
| 43 (C) | Real-Santillán 외 2024 · [Water stress decreases the biocontrol efficacy of a nucleopolyhedrovirus against the fall armyworm on maize](https://doi.org/10.1007/s10340-023-01700-x) | 해석 배경 | 수분 스트레스가 방제 효능에 영향을 줄 수 있음을 검토했다. 바이러스 방제 효능을 화학 살충제 계수로 옮기지 않았다. |
| 44 (C) | Ng 외 1999 · [Policy Invariance Under Reward Transformations: Theory and Application to Reward Shaping](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf) | 구현·기술 검증 | 잠재함수 차이를 학습 보상에 더하는 방식을 구현했다. 수확·시간제한과 η 변형에서 원수익과 학습 신호를 구분했다. |
| 45 (C) | Achiam 외 2017 · [Constrained Policy Optimization](https://proceedings.mlr.press/v70/achiam17a.html) | 제약 설계 배경 | 기대 비용 제약과 매 시즌 지켜야 하는 물리적 재고 제한의 차이를 설계에 반영했다. 학습 알고리즘은 MaskablePPO다. |

## 46편 비교표에만 있는 17편

| 번호와 팀 | 문헌 | 비교표에서 검토한 주제 |
|---:|---|---|
| 3 (A) | Kallenberg 외 2023 · [Nitrogen management with reinforcement learning and crop growth models](https://doi.org/10.1017/eds.2023.28) | 작물모형 기반 질소 시비 정책 학습과 일반화 |
| 4 (A) | Chen 외 2021 · [A reinforcement learning approach to irrigation decision-making for rice using weather forecasts](https://www.sciencedirect.com/science/article/pii/S0378377421001037) | 기상예보와 DQN을 활용한 벼 관수 결정 |
| 7 (A) | Sadras 외 2016 · [Interactions between water and nitrogen in Australian cropping systems: physiological, agronomic, economic, breeding and modelling perspectives](https://doi.org/10.1071/CP16027) | 물·질소 상호작용의 생리·농학·경제·모형 종합 |
| 9 (A) | English 1990 · [Deficit Irrigation. I: Analytical Framework](https://doi.org/10.1061/(ASCE)0733-9437(1990)116:3(399)) | 경제적으로 최적인 부족 관수량의 수학적 분석 |
| 13 (A) | Baudron 외 2019 · [Understanding the factors influencing fall armyworm (Spodoptera frugiperda J.E. Smith) damage in African smallholder maize fields and quantifying its impact on yield. A case study in Eastern Zimbabwe](https://www.sciencedirect.com/science/article/pii/S0261219419300304) | 소농 포장의 해충 피해 요인과 수량 손실 추정 |
| 15 (A) | Marenco 외 1992 · [Sweet Corn Response to Fall Armyworm (Lepidoptera: Noctuidae) Damage During Vegetative Growth](https://doi.org/10.1093/jee/85.4.1285) | 단옥수수 생육기별 해충 피해와 수량 반응 |
| 21 (B) | Wu 외 2022 · [Optimizing Nitrogen Management with Deep Reinforcement Learning and Crop Simulations](https://openaccess.thecvf.com/content/CVPR2022W/AgriVision/html/Wu_Optimizing_Nitrogen_Management_With_Deep_Reinforcement_Learning_and_Crop_Simulations_CVPRW_2022_paper.html) | DSSAT와 강화학습을 결합한 질소 관리 |
| 24 (B) | Gautron 외 2022 · [Reinforcement learning for crop management support: Review, prospects and challenges](https://doi.org/10.1016/j.compag.2022.107182) | 작물 관리 강화학습의 문헌·가능성·과제 종합 |
| 25 (B) | Malik 외 2019 · [DSSAT-CERES-maize modelling to improve irrigation and nitrogen management practices under Mediterranean conditions](https://www.sciencedirect.com/science/article/pii/S0378377418316263) | 지중해 옥수수 재배의 관수·질소 관리 개선 |
| 26 (B) | Fereres 및 Soriano 2007 · [Deficit irrigation for reducing agricultural water use](https://doi.org/10.1093/jxb/erl165) | 부족 관수의 절수 효과와 적용 조건 |
| 32 (B) | Hausknecht 및 Stone 2015 · [Deep Recurrent Q-Learning for Partially Observable MDPs](https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-SDMIA15-Hausknecht.html) | 순환신경망을 통한 부분 관측 이력 통합 |
| 35 (C) | Saikai 외 2023 · [Deep reinforcement learning for irrigation scheduling using high-dimensional sensor feedback](https://doi.org/10.1371/journal.pwat.0000169) | 다차원 센서 기반 관수 정책과 경제성 |
| 37 (C) | Sadras 2004 · [Yield and water-use efficiency of water- and nitrogen-stressed wheat crops increase with degree of co-limitation](https://www.sciencedirect.com/science/article/abs/pii/S1161030104000632) | 물·질소 공동 제한과 밀 수량·물 이용 효율 |
| 38 (C) | Kadiyala 외 2015 · [Identifying irrigation and nitrogen best management practices for aerobic rice–maize cropping system for semi-arid tropics using CERES-rice and maize models](https://doi.org/10.1016/j.agwat.2014.10.019) | 반건조 열대 밭벼–옥수수의 물·질소 관리 |
| 39 (C) | Geerts 및 Raes 2009 · [Deficit irrigation as an on-farm strategy to maximize crop water productivity in dry areas](https://doi.org/10.1016/j.agwat.2009.04.009) | 건조 지역 부족 관수와 물 생산성 |
| 42 (C) | Hruska 및 Gould 1997 · [Fall Armyworm (Lepidoptera: Noctuidae) and Diatraea lineolata (Lepidoptera: Pyralidae): Impact of Larval Population Level and Temporal Occurrence on Maize Yield in Nicaragua](https://doi.org/10.1093/jee/90.2.611) | 두 해충의 밀도·발생 시기에 따른 옥수수 수량 |
| 46 (C) | Ross 외 2011 · [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning](https://proceedings.mlr.press/v15/ross11a.html) | DAgger와 순차 모방학습의 오차 누적 완화 |

## 46편 밖에서 후속 검증에 참고한 주요 문헌

| 문헌 | MARS에서 확인한 내용 |
|---|---|
| Chen et al. (2022) | 온도별 사육 코호트의 번식과 개체군 증가를 확인했다. 20°C 산란수 표기 오류는 결측 처리했다. [논문](https://doi.org/10.3390/insects13020211) |
| Adan et al. (2024) | ILCYM 모의 생명표에서 28°C 이후 증가율 하강을 확인했다. Chen 연구와 반응 방향이 달라 민감도 근거로 분리했다. [논문](https://doi.org/10.1371/journal.pone.0299154) |
| Varella et al. (2015) | 포장 알·유충의 보충표를 본문과 대조했다. 유충 손실에 유실·이동·미발견이 섞여 있어 실제 사망률은 분리할 수 없었다. [논문](https://doi.org/10.1371/journal.pone.0130437) |
| Koffi et al. (2025) | 토고 시험장의 주간 조사와 포장 무방제 조건을 확인했다. 공개 파일 접근이 제한돼 조사일별 기상 연결은 미검증이다. [논문](https://doi.org/10.1111/afe.12693) |
| Ajam et al. (2024) | 우간다 69포장 반복조사의 설계와 유충·피해 기록 방법을 검토했다. 원자료는 저자 요청 방식으로 표시됐다. [논문](https://doi.org/10.3390/insects15050301) |
| Toepfer et al. (2021) | 피해 척도와 조사 부위를 대조했다. 같은 식물·시점·척도의 독립 반복 판독과 면적 기준값을 확인하지 못했다. [논문](https://doi.org/10.1007/s10340-021-01359-2) |
| Soujanya et al. (2022) | 접종 후 7·14·21일 피해 점수를 확인했다. 보충표의 실험 반복은 판독자 반복과 구분했다. [논문](https://doi.org/10.3389/fpls.2022.906207) |
| 옥수수 질소 공급과 유충 섭식 실험 (2022) | 스캔한 잎 조각의 섭식 면적 측정 방법을 확인했다. [논문](https://doi.org/10.3390/ijms231810457) |
| de Oliveira et al. (2026) | 품종별 초기 절단 후 회복을 보정 후보로 검토했다. 위 12번 질소 연구와 DOI가 다르며 실험 중복은 미확정이다. [논문](https://doi.org/10.1002/agg2.70295) |
| Abdul Rahman et al. (2022) | 가나 후기 하엽 제거와 곡실 수량을 검토했다. 처리 주변평균과 원처리 반복을 구분했다. [논문](https://doi.org/10.3390/agriculture12020275) |
| Li et al. (2023) | Nebraska 관개 옥수수 잔사 연구를 별도 현장 보정 후보로 점검했다. [논문](https://doi.org/10.1016/j.eja.2023.126807) |
| 동부 Kenya 파종 시기 연구 (2026) | 포장 수량과 생육·관리 입력의 연결 가능성을 확인했다. [논문](https://doi.org/10.1016/j.eja.2026.128364) |

공개 자료는 논문 수에 따로 넣지 않았다. Masii는 같은 조사일의 유충 수와 피해 점수, FAMEWS는 감염 식물 비율, USDA LIRF와 Iran 관수×질소 자료는 기상·토양·관수·수량 입력, LeafByte는 면적 측정의 정확도와 반복성 검토에 참고했다. [Masii](https://doi.org/10.17632/g8fsd6dpxk.1) · [FAMEWS](https://doi.org/10.5061/dryad.9kd51c5gg) · [USDA LIRF](https://doi.org/10.15482/USDA.ADC/1254006) · [Iran](https://doi.org/10.17632/6zj7pzftwg.1) · [LeafByte](https://doi.org/10.5061/dryad.jdfn2z377)

## 대조 원본과 검증 기록

- [팀 검토 문서](<C:/Users/WD/Downloads/papers_46_team_review.docx>)
- [개정 제안서](proposal_revised.pdf) 14–16쪽과 [추출 텍스트](proposal_revised.txt)
- [농학 문헌 등록부](../configs/agronomic_sources.json) · [자료별 검증 현황](AGRONOMIC_INPUT_PRIORITIES.md)
- [해충 계수 근거](FAW_PARAMETER_SENSITIVITY.md) · [실제 DSSAT 잎 피해](FAW_DSSAT_SENSITIVITY_PAIRING.md) · [η 보상](REWARD_ETA_SENSITIVITY.md) · [GAE](GAE_COMMON_ROLLOUT.md)

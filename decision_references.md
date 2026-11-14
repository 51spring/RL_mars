# decision_project.md 문헌 근거 — 논문별 정리

`decision_project.md`에서 논문을 근거로 든 곳을 논문별로 모았다. **2026-11-14 확장:** 값 근거가 아니어도 이 프로젝트에서 쓴 모든 논문(구현 기반·설계 배경·검증 후보·검토 후 미채택)을 7절에 모았다. 출처는 `decision_project.md`와 `docs/MARS_LITERATURE_CROSSWALK.md`(제안서 참고문헌·46편 비교표 대조)다. 이 파일만 보면 논문마다 어디에·어떻게 쓰였는지 확인할 수 있다. 각 행은 **어디(절)**, **어떤 값**, **어떻게 썼는지**, **왜**를 적는다. 절 번호는 `decision_project.md` 기준이다. 정리일 2026-11-12.

사용 방식 표기:
- **채택**: 논문 값을 그대로 썼다.
- **범위 맞춤**: 논문이 보고한 범위·현상에 맞도록 값을 골랐다.
- **비교**: 현재 값이 논문 값과 같은 규모인지 대조만 했다(값은 다른 근거로 정함).
- **해석**: 결과나 설계를 설명할 때 방향만 빌렸다.
- **반대·한계**: 논문이 현재 설계의 한계를 보여 준다.
- **구현 기반**: 코드·모형·알고리즘 자체로 썼다(논문 필수 인용).
- **설계 배경**: 설계 방향을 정할 때 참고했다(값은 가져오지 않음).
- **검증 후보**: 독립 검증·보정 자료로 검토했다(정량 판정 미완료 포함).
- **검토만**: 46편 비교표에서 검토했고 프로젝트 값·설계에는 쓰지 않았다.

## 요약

| 논문 | 분야 | 쓰인 절 | 주요 사용 |
|---|---|---|---|
| Gautron et al. 2022 (gym-DSSAT) | 시뮬레이터·RL | 9, 12, 15 | 이전 공급량 264 mm, 입력 상한 50 mm, 전문가 시비 116 kg |
| Tao et al. 2023 | 작물 RL | 1, 9, 12, 15, 18 | 곡실·물·질소 단가 **채택**, 무투입 수렴 사례 |
| Kelly 2024 | 관수 RL | 9, 12, 14 | 감축 수준·공급량 민감도, 관수 격자, 결정 주기 |
| Saikai 2023 | 관수 RL | 9 | 물 단가·격자 비교 |
| Balderas et al. 2025 | 작물 RL | 3, 9, 12, 18 | 평가 행동 방식, PPO 기본값, 무관수 수렴 사례 |
| Kallenberg et al. 2023 | 질소 RL | 3, 15 | 시비 격자 비교, PPO 기본값·tanh |
| Wu et al. 2022 | 질소 RL | 15 | 시비 격자·시기 비교 |
| Baja | 질소 RL | 15 | 시비 격자 비교 |
| Wang 2026 | 질소 경제 | 15 | 곡실·질소 가격비 비교 |
| Saseendran et al. 2014 | 작물 모형(물 스트레스) | 9 | 관수 규칙의 스트레스 지표 해석 |
| Fereres & Soriano 2007 | 부족 관수 | 9, 17 | b0′ 보호 구간, 적엽–증발 해석 |
| Santos et al. 2018 | 적엽×관수 | 9, 17, 19 | 민감 생육기, 관수 효율, 적엽 손실 |
| Oveysi et al. 2010 | 적엽×관수 | 17, 19 | 물 부족 시 적엽 손실 방향 |
| Blanco et al. 2022·2023 | 적엽 | 16, 17 | 초기 적엽 무손실 → 단계 가중치 불필요 |
| Abang et al. 2024 | FAW 피해 | 16, 17 | **α = 0.01 결정** 근거 |
| Hruska 2019 (Abang 인용) | FAW 피해 | 17 | α 사전 규칙의 목표 적엽 범위 |
| Du Plessis et al. 2020 | FAW 온도 | 2, 16, 28 | 해충 온도 하한 **13.1 °C 채택** |
| Adan et al. 2024 | FAW 개체군 증가 | 28 | 증식률 0.211·온도 상한 28 °C **채택** |
| Overton et al. 2021 | FAW 임계 | 16 | 방제 임계 척도 불일치 |
| Real-Santillán et al. 2024 | 물×해충 | 16 | 물×방제 상호작용 부재의 한계 |
| Sisay et al. 2019 외 | 살포 효능 | 17 | 효능·잔효 근거 탐색 실패 기록 |
| Ng, Harada, Russell 1999 | 보상 설계 | 18 | 잠재함수 보정 → η 유지 |
| Schulman et al. 2017 (PPO) | RL 알고리즘 | 3, 25, 30 | PPO 기본값, 엔트로피 0.01 기각, n_epochs 4 참고 |
| Huang et al. 2022 (PPO 구현 세부) | RL 구현 | 25 | 문헌 PPO 설정 대조 |
| Holm 1979 | 통계 | 5 | 다중검정 보정 |
| Agarwal et al. 2021 | 통계 | 5 | 적은 실행 수에서 부트스트랩 구간 보고 |
| Ma et al. 2006, Bennett et al. 1986 | 원 실험 | 21 | UFGA8201 입력·관측 대조, 초기 무기질소 |
| Bowen 1994 (DSSAT 품종 파일 주석) | 모형 계보 | 1 | 품종 계수가 UFGA8201로 보정됨 |
| SIAZ 1995 (실험 자료) | 검증 | 19 | 독립 연도 물 반응 단 A |
| Rahman 2022 | 검증 자료 | 19 | 기록용 JSON (비교 실험 미사용) |
| **7절 기반·배경·검증·검토 문헌** | 구현·설계·검증·검토 | 1, 3, 16~23, 28, 32, 34 등 | DSSAT·CERES-Maize·WGEN·SB3·GAE·행동 마스킹 등 논문 필수 인용 포함 |

---

## 1. 시뮬레이터·작물 RL

### Gautron et al. 2022 — gym-DSSAT: a crop model turned into a Reinforcement Learning environment
`MARS_reference/gym-DSSAT a crop model turned into a Reinforcement Learning environment.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | 시즌 물 공급 **264 mm (이전 값)** | 채택 → 이후 200 mm로 변경 | 표 6·9의 UFGA8201 처리 3 전문가 관수 16회 합계가 264 mm. 같은 시나리오 PPO 사용량 133.8 mm도 비교. 264 mm에서는 감축이 거의 구속하지 않아 200 mm로 바꿨다(D12) |
| 9 | 관수 입력 상한 50 mm | 채택 | 논문의 관수 행동 범위 [0, 50] |
| 9 | 규칙 관수 기준선 | 해석 | DSSAT 자동관수를 기준선으로 제안 → 단계별 규칙 탐색의 출발점 |
| 9 | b0′ 보호 구간 istage 4·5 | 비교 | PPO 관수가 모의 80~120일(파종 후 약 53~93일)에 집중 |
| 9 | 표 10 단계 설명 | 해석 | 단계 이름은 끝나는 사건 기준으로 읽어야 함(시작 기준이면 출아 2일·출사 42일로 맞지 않음) |
| 12 | 공급량 민감도 264 mm | 비교 | 대안 값으로 제시 |
| 15 | 이전 질소 예산 116 kg (91.64 USD) | 채택 → 이후 폐기 | 전문가 일정 27+35+54 = 116 kg. 수익 최적보다 낮아 탐색으로 161 kg 일정 채택 |
| 15 | 시비 시기 | 비교 | PPO가 화서 분화 시작(istage 2, 평균 37일) 무렵에 시비 집중 |

### Tao et al. 2023 — Optimizing Crop Management with Reinforcement Learning and Imitation Learning (IJCAI)
`MARS_reference/Optimizing Crop Management with Reinforcement Learning and Imitation Learning.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 1, 2 | 곡실 단가 **0.158 USD/kg** | 채택 | 초기 경제 설정(`MARS_LITERATURE_CROSSWALK.md`). 1절 점검에서 DSSAT 수량이 건물 기준임을 확인해 수분 15.5 % 환산을 결정(2026-11-11) |
| 9 | 물 단가 ~~1.1 USD/mm/ha~~ | 이전 채택 → 2026-11-13 교체(27절, 6절 Alabama 예산서) | 표 1 RF1 |
| 15 | 질소 단가 ~~0.79 USD/kg~~ | 이전 채택 → 2026-11-13 교체(27절, 6절 USDA AMS) | 표 1 RF1 |
| 9 | 플로리다 DQN 관수 120 mm | 비교 | 공급량 200 mm가 학습 정책 사용량보다 충분히 큼을 확인 |
| 9 | 관수 격자 0~24 mm 6 간격 | 비교 | 현재 0~25 mm 5 간격과 같은 규모 |
| 15 | 학습 정책 질소 200 kg, 지침 기준선 360 kg; 격자 0~160 kg 40 간격 | 비교 | 질소 예산·격자의 규모 대조 |
| 9, 18 | 부분관측 DQN이 무투입으로 수렴 | 해석 | 희소 초기 확률(관수 0.13)로 탐색 여유를 둔 이유 |
| 32 | 같은 현상 | 재현 | B7 시험 학습에서 b3(방제) 초반 40만 단계 무살포 고착, b4(동시) 초반 10만 단계 무투입. 행동 복제 초기화(34절)를 시험한 이유 |
| 12 | 물 단가 민감도 0·1.0·2.2 | 비교 | 대안 값 |

### Kelly 2024 — Assessing the value of deep reinforcement learning for irrigation scheduling (SSRN 프리프린트)
`MARS_reference/Assessing the value of deep reinforcement learning for irrigation scheduling.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | 감축률 20·40·60 % | 범위 맞춤 | 물 상한 75·100·125 mm에서 DRL 이득 +12.2·+7.1·+4.3, 상한 없음 −1.3 USD/ha. 200 mm에서 감축 후 160·120·80 mm가 이 구간에 걸친다. 세 수준 자체의 문헌 근거는 없다 |
| 9, 14 | 공급량 민감도 120·160 mm | 범위 맞춤 | 같은 상한 실험 |
| 9 | 관수 격자 0~25 mm | 채택 | 최적 행동이 0~25 mm 2.5 간격 |
| 9, 12 | 물 단가 1 USD/mm, 곡실 0.18 USD/kg | 비교 | 단가 민감도 대안 |
| 9 | 규칙 기준선 | 해석 | 생육단계별 토양수분 임계 4개를 최적화한 기준선 → 단계별 규칙 채택(11절) |
| 9, 12 | 결정 주기 3일 | 반대·한계 | 3일 주기 수익이 가장 높았다. 본 연구는 매일 결정, 후속 연구로 둠 |
| 9, 12 | 감축 계약 | 비교 | 시즌 총량 상한 방식. 본 연구는 남은 물 비례, 총량 방식은 민감도 후보 |

### Saikai et al. 2023 — Deep reinforcement learning for irrigation scheduling using high-dimensional sensor feedback
`MARS_reference/Deep reinforcement learning for irrigation scheduling using high-dimensional sensor feedback.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | 물 단가 0.6 AUD/mm(저비용), 관수 격자 0~40 mm 10 간격 | 비교 | 물 단가·격자 규모 대조 |

### Balderas et al. 2025 — A comparative study of deep reinforcement learning for crop production management (Smart Agricultural Technology 10:100853)
`MARS_reference/A comparative study of deep reinforcement learning for crop production management.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9, 12 | 평가 행동 방식 | 비교 | 단일 관수 과제는 확률 행동, 혼합 과제는 최대확률. 본 연구는 최대확률로 결정(D9) |
| 9, 18 | 혼합 과제 PPO가 물을 전혀 주지 않음 | 해석 | 희소 초기 확률로 탐색 여유를 둔 이유 |
| 32 | 같은 현상 | 재현 | b4(동시 학습) 초반 물·질소·살포 모두 0. 혼합 과제가 단일 과제보다 어렵다는 보고와 맞음 |
| 9 | PPO 관수 시기 모의 80~120일, 격자 0~24 mm 6 간격 | 비교 | b0′ 보호 구간·격자 대조 |
| 3 | SB3 PPO 기본 하이퍼파라미터, γ = 1, 10⁶단계 | 비교 | PPO 기본값 유지의 근거 |

### Kallenberg et al. 2023 — Nitrogen management with reinforcement learning and crop growth models (Environmental Data Science)
`MARS_reference/nitrogen-management-with-reinforcement-learning-and-crop-growth-models.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 15 | 시비 격자 0·20·40 kg | 비교 | 문헌 격자 3~21단계 중 하나. 9단계 유지 결정 |
| 3 | SB3 PPO 기본값, tanh, 128×128 | 비교 | 기본값·활성함수 유지 근거 |
| 3 | VecNormalize 사용 | 비교 | 본 연구는 고정 척도만 사용(차이 기록) |

### Wu et al. 2022 — Optimizing Nitrogen Management With Deep Reinforcement Learning and Crop Simulations (CVPRW)
`MARS_reference/Wu_Optimizing_Nitrogen_Management_..._CVPRW_2022_paper.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 15 | 시비 격자 0~160 kg 40 간격 | 비교 | 격자 단계 수 대조 |
| 15 | 기준선 V5 1회 시비 | 비교 | 시비 시기 대조 |

### Baja et al. 2025 — Adaptive fertilizer management for optimizing nitrogen use efficiency with constrained reinforcement learning (Comput. Electron. Agric., doi:10.1016/j.compag.2025.110554)
`MARS_reference/Adaptive fertilizer management for optimizing nitrogen use efficiency with constrained reinforcement learning.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 15 | 시비 격자 0~80 kg 10 간격 | 비교 | 현재 격자(0~80 kg, 9단계)와 범위 같음 |
| 25 | 엔트로피 0.01 | 비교 | 문헌 PPO 설정 대조표. 25절에서 시험 후 기각 |
| 23 | 제약하 질소 관리 | 설계 배경 | 시비·비용 제약을 자원 원장과 행동 마스크로 집행 (CROSSWALK) |

### Wang et al. 2026 — Learning-based agricultural management in partially observable environments subject to climate variability (Sci. Rep., doi:10.1038/s41598-026-57117-w)
`MARS_reference/Learning-based agricultural management in partially observable environments subject to climate variability.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 15 | 곡실 0.071, 질소 0.39 USD/kg (가격비 5.5), 격자 0~200 kg 10 간격 | 비교 | 현재 질소/곡실 가격비 5.0(0.79/0.158)과 비슷함을 확인. 15.5 % 환산 후에는 건물 기준 가격비가 4.2(0.79/0.187)로 바뀐다 |
| 22 | 기후 변동·부분관측 농업 관리 | 설계 배경 | 관측과 외생 시나리오는 별도 구성 (CROSSWALK) |

## 2. 작물 생리·관수

### Saseendran et al. 2014 — Enhancing the Water Stress Factors for Simulation of Corn in RZWQM2
`MARS_reference/Enhancing the Water Stress Factors for Simulation of Corn in RZWQM2.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | 규칙 관수 트리거 1 − SWFAC | 해석 | SWFAC는 공급 < 수요일 때 작동하고 잎 신장 스트레스(TURFAC)는 더 일찍 시작 → 단일 임계보다 단계별 임계를 탐색한 이유 |

### Fereres & Soriano 2007 — Deficit irrigation for reducing agricultural water use
`MARS_reference/Deficit irrigation for reducing agricultural water use.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | b0′ 보호 구간 istage 4·5 | 해석 | 개화 후 스트레스는 피하고, 개화 전 부족은 수확지수를 높일 수 있다 |
| 17 | 해충 적엽과 물 절약 경로 | 해석 | 엽면적 감소가 증발 비중을 키워 절약을 상쇄한다는 지적과 같은 방향 |

### Santos et al. 2018 — Irrigation as an alternative to reduce damages caused by defoliation of sweet corn
`MARS_reference/Irrigation as an alternative to reduce damages caused by defoliation of sweet corn.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 9 | b0′ 보호 구간 | 비교 | 인용된 민감기: 추대~등숙 시작 |
| 9 | 관수 효율 100 % | 반대·한계 | 점적 관수 효율로 관수량 보정(CUC 96.2 %). 스프링클러 수치 없음 → 100 % 유지, 한계로 명시 |
| 9 | 관수량 105.7·158.5·211.5·264.2 mm | 사용 안 함 | 264 mm의 감축 후 물과 비슷하지만 단옥수수·다른 지역의 ETc 비율이라 근거로 쓰지 않음 |
| 17 | 물 부족에서도 적엽이 수량을 줄임 | 반대·한계 | 극심한 감축에서 무방제가 이득인 모의 결과는 모형이 과장할 수 있음 |
| 19 | 표 1 생산성 | 기록 | `santos2018_table1_productivity.json`, 비교 실험 미사용 |

### Oveysi et al. 2010 — The impact of source restriction on yield formation of corn due to water deficiency (Plant Soil Environ., doi:10.17221/86/2010-PSE)
`MARS_reference/The impact of source restriction on yield formation of corn  due to water deficiency.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 17 | V8 적엽 손실: 완전 관수 19.2 %, 물 부족 14.8 % | 해석 | 모의에서 물이 부족할수록 피해 영향이 작아진 방향(5.0 → 2.4 → 1.5 %)과 같음 |
| 17 | 물 부족에서도 적엽 손실 존재 | 반대·한계 | 무방제 이득 모의 결과의 과장 가능성 |
| 19 | 표 4 곡실, 입력 명세 | 기록 | `oveysi2010_*.json`, 비교 실험 미사용 |

## 3. 해충(FAW)·방제

### Blanco et al. 2022·2023 — 초기 적엽과 수량
`MARS_reference/Severe Defoliation of Vegetative Maize Plants Does Not Reduce Grain Yield Further Implications with Action Thresholds.pdf`, `Implications for Fall Armyworm Action Thresholds.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 16 | 피해 시기 | 반대·한계 | V7 이전 적엽(66 %, 반복)에서 수량 감소 없음 → 모든 단계에서 잎을 제거하는 모형의 한계 |
| 17 | V1-V2·V3-V4 33·66 % 적엽 무손실 | 범위 맞춤(검증) | DSSAT 수량비 0.999~1.004로 이미 재현 → 단계별 피해 가중치를 넣지 않음 |

### Abang et al. 2024 — Maize plants can recover from fall armyworm damage under optimum crop production conditions in humid tropical agro-ecologies (J. Econ. Entomol. 117(6))
`MARS_reference/Maize plants can recover from fall armyworm damage ....pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 17 | **피해 계수 α = 0.01** | 범위 맞춤 | 우기 수량 손실 4.5~11.7 %(표 2), 현장 시험 대부분 20 % 미만. α 0.01의 손실 중앙값 4.9 %·상위 10 % 11.9 %가 우기 범위와 일치 |
| 17 | 적엽 "보통 25 %" (Hruska 2019 인용) | 범위 맞춤 | 평균 적엽으로 읽으면 α 0.01(평균 21 %)이 가깝다 |
| 16 | 약 50 % 적엽부터 건기에만 유의한 손실 | 반대·한계 | 피해 시기·조건을 구분하지 않는 모형의 한계 |
| 28 | 우기 수량 손실 4.5~11.7 % | 재보정 목표 | 새 증식률에서 유입 확률 재보정 기준(수량 손실 중앙값). 0.03 유지(4.4 %, 사전 규칙 이탈) |

### Hruska 2019 (Abang 2024를 통한 인용)

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 17 | FAW 적엽은 50 %를 넘는 경우가 드물고 보통 25 % | 범위 맞춤 | α 사전 규칙(최대 강도 중앙값 25 %, 50 % 초과 시즌 10 % 이하)의 목표. 사전 규칙은 0.005를 골랐지만 사용자 결정으로 0.01 채택(사전 규칙 이탈로 기록) |
| 28 | 같은 기준(평균 적엽 21 %, 50 % 초과 ≤ 13 %) | 재보정 목표 | 새 증식률에서 유입 확률 재보정. 0.03 유지(평균 20.9 %, 50 % 초과 17.5 %) |

### Du Plessis et al. 2020 — The Effect of Temperature on the Development of Spodoptera frugiperda
`MARS_reference/The Effect of Temperature on the Development of Spodoptera frugiperda Lepidoptera Noctuidae.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 28 | **해충 온도 하한 13.1 °C** (증식률 0) | 채택 (2026-11-13) | 알~성충 발육 하한 13.1 °C. 이전 10 °C(가정)를 교체 |
| 2, 16, 28 | 해충 온도 상한 ~~30 °C~~ | 이전 비교 → 28 °C로 교체(Adan 2024) | 발육 최적 26~30 °C는 발육률이라 개체군 증가율(rm) 기준으로 바꿈 |

### Adan et al. 2024 — Combining temperature-dependent life table data into Insect Life Cycle Model to forecast fall armyworm distribution in maize agro-ecological zones in Africa (PLoS One 19(5):e0299154)
https://pmc.ncbi.nlm.nih.gov/articles/PMC11073722/

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 28 | **증식률 상한 0.211/일, 온도 상한 28 °C** | 채택 (2026-11-13) | 표 8 옥수수 FAW 내재 증가율 rm: 20·25·28·30·32 °C = 0.121·0.189·0.211·0.157·0.109. 모형 g(T)는 개체군 증가율이라 발육률보다 rm이 맞는 기준 |

### Overton et al. 2021 — Global crop impacts, yield losses and action thresholds for fall armyworm: A review
`MARS_reference/Global crop impacts, yield losses and action thresholds for fall armyworm ....pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 16 | 방제 임계 | 반대·한계 | 경제적 임계는 문헌에 없고 행동 임계는 감염주율(예: 15 %)로 보고 → 모형의 0~1 밀도 지수와 척도가 달라 직접 쓸 수 없음. 임계는 검증 시즌 탐색으로 0.7 채택(17절) |

### Real-Santillán et al. 2024 — Water stress decreases the biocontrol efficacy of a nucleopolyhedrovirus against the fall armyworm on maize
`MARS_reference/Water stress decreases the biocontrol efficacy ....pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 16 | 물×해충 상호작용 없음 | 반대·한계 | 수분 스트레스가 바이러스 방제 효능을 낮춤. 화학 약제에 적용할 근거가 없어 상호작용을 넣지 않고 한계로 기록 |

### Sisay et al. 2019 외 (살포 효능·잔효 탐색)

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 17 | 효능 0.8, 잔효 5일 | 근거 없음(가정 유지) | Sisay 2019(Insects 10(2):45)와 Florida Entomologist 103(2) 인도 포장 시험은 원문을 읽지 못함. 이전 조사의 Masii는 처리 배정만, Varella는 무살충 시험. 종자 처리 잔효 자료는 방식이 달라 사용 불가 |

## 4. 강화학습·통계

### Ng, Harada, Russell 1999 — Policy Invariance Under Reward Transformations
`MARS_reference/Policy Invariance Under Reward Transformations Theory and Application to Reward Shaping.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 18 | 잠재함수 Φ = 곡실 단가 × η × topwt, γ = 1 | 채택(이론) | 잠재함수 보정은 최적 정책을 바꾸지 않는다 → η는 학습 신호 모양만 바꿈. 측정 수확지수 0.514에도 η 0.45 유지(D8) |

### Schulman et al. 2017 — Proximal Policy Optimization Algorithms
`MARS_reference/Proximal Policy Optimization Algorithms.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 3 | 학습률 3e-4, clip 0.2, 엔트로피 0, tanh, 정책·가치망 분리, Adam | 채택(기본값) | MuJoCo 표 3e-4·ε 0.2(0.1·0.3보다 좋음), 엔트로피 보너스 없음, tanh MLP. SB3 기본값과 같다 |
| 25 | Atari 설정 엔트로피 계수 0.01 | 시험 후 기각 | 시드 0·2에서 하락이 더 커짐. 엔트로피 0 유지 |
| 30 | Atari 에폭 3 (MuJoCo 10) | 참고 | 갱신 크기를 줄이는 n_epochs 4 채택. 급락 제거는 시험 학습으로 확인(기준 곡선 n_epochs 10은 급락) |

### Huang et al. 2022 — The 37 Implementation Details of Proximal Policy Optimization (ICLR Blog Track)
https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 25 | 학습률 선형 감쇠, 엔트로피 0.01, 에폭 10, 행동 마스킹 | 비교 | 문헌 PPO 설정 대조표. 감쇠(분리 실험 ②)·엔트로피 0.01(25절)을 시험했으나 채택하지 않음 |

### Holm 1979 — A Simple Sequentially Rejective Multiple Test Procedure
`MARS_reference/a-simple-sequentially-rejective-multiple-test-procedure-458rh2uo9s.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 5 | 검정군별 Holm 보정 (가설 2, 조건별 9, 대비 비용 4, 대비 이득 4, 감축 손실 5, 효과 5) | 채택 | 대비가 많아 검정군마다 다중검정 보정 |

### Agarwal et al. 2021 — Deep Reinforcement Learning at the Edge of the Statistical Precipice (NeurIPS 2021)
`MARS_reference/deep-reinforcement-learning-at-the-edge-of-the-statistical-precipice-Paper.pdf`

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 5 | 시드·시즌 교차 부트스트랩, 95 % 백분위 구간 | 비교(방법 근거) | 심층 RL에서는 3~10회 실행이 흔하므로 점추정 대신 부트스트랩 구간을 보고하라고 권한다. 이 연구는 시즌 1,000개도 함께 다시 뽑는다 |
| 5, D10 | 시드 수 5 또는 10 | 해석 | 실행 수가 적으면 추정의 불확실성이 커진다. 시드 5개 안에서 구간이 거칠어지는 한계의 근거 |
| — | 사분위 평균(IQM), 성능 분포 | 사용 안 함 | 여러 과제를 합치는 지표라 이 연구(단일 과제, 시즌 평균 순수익)에는 쓰지 않음 |

## 5. UFGA8201 원 실험·모형 계보

### Ma et al. 2006 — Evaluation of the RZWQM-CERES-Maize hybrid model for maize production (Agricultural Systems 87:274–295); Bennett, Jones, Zur, Hammond 1986 (Agronomy Journal 78:273–280)

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 21 | 파종일 1982-02-26, 이랑 61 cm, 품종 McCurdy 84AA | 비교 | 템플릿과 일치 |
| 21 | 재식밀도 7.1 주/m² | 비교 | 템플릿 7.2, 거의 일치 |
| 21 | 생리적 성숙 7월 4일 | 비교 | 모의 평균 파종 후 130.4일(7월 6일경)과 일치 |
| 21 | 토양 수분 한계·초기 수분 | 비교 | 템플릿과 같은 값 |
| 21 | 초기 무기질소 NO3 0.6, NH4 1.5 µg/g | 비교 → 현재 값 유지 | 템플릿(0.1·0.5)과 다르지만 1982년 실측 기상 6처리 재현에서 수량 차이 25 kg/ha 이내 |
| 21 | 저질소 처리 시비 62 kg (FileX는 116 kg) | 비교 | FileX에 논문에 없는 5월 17일 54 kg 포함 → 이전 질소 예산 근거의 문제 확인 |
| 21 | 관측 곡실 수량 6처리 | 비교 | 모의 RMSE 813~1104 kg/ha. UFGA8201은 품종 보정에 쓰여 독립 검증이 아니다 |

### Bowen 1994 (DSSAT `MZCER048.CUL` 머리 주석)

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 1 | 품종 IB0035 P1, G2 | 반대·한계 | UFGA8201 품종의 P1을 이 실험으로 다시 보정, G2는 1.1배. 독립 매개변수 계보 한계(20절)의 직접 근거 |

### SIAZ 1995 (실험 자료)

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 19 | 독립 연도 물 반응 | 검증 | 진입 조건 단 A 충족 근거 |

### Rahman 2022

| 절 | 값 | 사용 방식 | 왜 |
|---|---|---|---|
| 19 | 주변평균 곡실 | 기록 | `rahman2022_marginal_grain.json`, 비교 실험 미사용 |

## 7. 기반·설계 배경·검증 후보·검토 문헌 (값 근거 외)

### 7.1 구현 기반 — 논문 필수 인용

| 논문 | 파일 | 쓰인 곳 | 어떻게 |
|---|---|---|---|
| Jones et al. 2003 — The DSSAT cropping system model (Eur. J. Agron. 18:235–265) | `Jones_2003_The_DSSAT_cropping_system_model.pdf` | 전체(1절 시뮬레이터, 21절 원 실험) | 작물·토양·기상·관리 입력을 잇는 기본 작물 모형. 설정 대조는 DSSAT 파일(`MZCER048.CUL`, `SOIL.SOL`, `DATA.CDE`)로 했다 |
| Jones & Kiniry 1986 — CERES-Maize: A simulation model of maize growth and development (Texas A&M Univ. Press) | 없음(원전 미확보) | 전체 | DSSAT 안의 옥수수 모형. 생육 단계(istage)·수분 스트레스(SWFAC)·수량 계산의 원전 |
| Richardson & Wright 1984 — WGEN: A model for generating daily weather variables (USDA-ARS ARS-8) | 없음(원전 미확보) | 1절, 3절(시즌 구간), 모든 학습·평가 | 확률 기상 생성. 월 통계 `UFGA.CLI`, 학습·검증·시험 시즌마다 다른 WGEN 시드 |
| Gautron et al. 2022 (gym-DSSAT) | 1절 항목 참조 | 1절 | DSSAT를 일별 의사결정 환경으로 쓰는 구조 채택 |
| Schulman et al. 2016 — High-Dimensional Continuous Control Using Generalized Advantage Estimation (ICLR) | `High-Dimensional Continuous Control Using Generalized Advantage Estimation.pdf` | 3절, D7, 18절 | GAE 채택. λ 0.95·0.98을 실제 공통 롤아웃으로 비교, 0.98은 무관수 붕괴가 잦아 **λ 0.95 결정**(D7) |
| Huang & Ontañón 2022 — A Closer Look at Invalid Action Masking in Policy Gradient Algorithms (FLAIRS-35) | `A Closer Look at Invalid Action Masking in Policy Gradient Algorithms.pdf` | 3절, 23절 | MaskablePPO 무효 행동 마스킹의 이론 근거. 물·질소·살포 선택지는 자원 원장이 계산한 실행 가능 집합 |
| Raffin et al. 2021 — Stable-Baselines3: Reliable Reinforcement Learning Implementations (JMLR 22:268) + sb3-contrib | 없음(소프트웨어) | 3절 | 학습 구현체(SB3 2.7.1, MaskablePPO). 하이퍼파라미터 기본값의 출처 |

### 7.2 설계 배경

| 논문 | 파일 | 쓰인 곳 | 어떻게 |
|---|---|---|---|
| Ross et al. 2011 — A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning (AISTATS, DAgger) | `A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning.pdf` | 제안서 10쪽 대안, 32·34절 | 행동 복제 후 PPO 미세조정의 배경. 34절은 DAgger가 아닌 단순 행동 복제(규칙 궤적 모방) + 라벨 스무딩·드문 행동 가중치 |
| Kaelbling et al. 1998 — Planning and acting in partially observable stochastic domains (Artif. Intell.) | `Planning and acting in partially observable stochastic domains.pdf` | 22절 관측 설계 | 볼 수 없는 해충 밀도와 관측 가능한 조사값을 분리한 부분관측 설계 |
| Hausknecht & Stone 2015 — Deep Recurrent Q-Learning for Partially Observable MDPs | `Deep Recurrent Q-Learning for Partially Observable MDPs.pdf` | 22절 | 순환망 대신 7일 관측 이력(196개 입력)을 쌓는 방식의 대조 (검토) |
| Achiam et al. 2017 — Constrained Policy Optimization (ICML) | `Constrained Policy Optimization.pdf` | 23절 | 기대 비용 제약과 매 시즌 지켜야 하는 물리 재고 제한의 차이 → 제약을 마스크로 집행 |
| Carrara et al. 2019 — Budgeted Reinforcement Learning in Continuous State Space (NeurIPS) | `budgeted-reinforcement-learning-in-continuous-state-space-Paper.pdf` | 23절 | 비용·보상을 함께 다루는 예산형 정책 참고. 시즌 지출은 원장에서 검사 |
| Stolz et al. 2024 — Excluding the Irrelevant: Focusing RL through Continuous Action Masking (NeurIPS) | `NeurIPS-2024-excluding-the-irrelevant-focusing-reinforcement-learning-through-continuous-action-masking-Paper-Conference.pdf` | 후속 비교 | 연속 행동 마스킹을 후속 연구로 인용. 현재는 이산 행동 |
| Baja et al. 2025 — To Measure or Not: A Cost-Sensitive, Selective Measuring Environment (AAAI) | `To Measure or Not A Cost-Sensitive, Selective Measuring Environment for Agricultural Management Decisions with Reinforcement Learning.pdf` | 16절 조사 설계 | 관측 정보의 가치 → 7일 주기 조사와 잡음 검증 설계. 측정 구매 행동은 도입 안 함 |
| Chen et al. 2021 — A reinforcement learning approach to irrigation decision-making for rice using weather forecasts (Agric. Water Manag.) | `A reinforcement learning approach to irrigation decision-making for rice using weather forecasts.pdf` | 46편 비교표, 고찰 | 예보를 쓰는 관수 RL. 본 연구 관측에는 예보가 없어 규칙 대비 정보 이점이 작다는 해석의 대조 |
| Gautron et al. 2022 — Reinforcement learning for crop management support: Review, prospects and challenges (Comput. Electron. Agric.) | 없음 | 서론 | 작물 관리 RL 리뷰 (46편 비교표) |

### 7.3 검증 후보·피해 모형 배경

| 논문 | 파일 | 쓰인 곳 | 어떻게 |
|---|---|---|---|
| Batchelor et al. 2020 — Simulation of Maize Lethal Necrosis Damage Using the CERES-Maize Model (Agronomy 10:710) | `Simulation of Maize Lethal Necrosis (MLN) Damage Using the CERES-Maize Model.pdf` | 16절 피해 전달 | 손상을 CERES-Maize 생장에 전달한 선례. 실제 잎 가해 쓰기와 반출 회계는 자체 구현 |
| de Oliveira Jr. et al. 2026 — Early defoliation and nitrogen fertilization effects on maize morphophysiology and production (Acta Physiol. Plant.) | `Early defoliation and nitrogen fertilization effects on maize morphophysiology and production.pdf` | 17절 | V4 절단·추비 시점별 회복을 검증 후보로 등록. 온실 처리량을 포장 값으로 대입 안 함 |
| de Oliveira et al. 2026 (Agrosyst. Geosci. Environ., doi:10.1002/agg2.70295) | 없음 | 17절 | 품종별 초기 절단 후 회복, 보정 후보 |
| Hruska & Gould 1997 — Fall Armyworm and Diatraea lineolata: Larval Population Level and Temporal Occurrence on Maize Yield in Nicaragua (J. Econ. Entomol.) | `Fall Armyworm (Lepidoptera Noctuidae) and Diatraea lineolata Impact of Larval Population Level and Temporal Occurrence on Maize Yield in Nicaragua.pdf` | 16·17절 | 유충 밀도·발생 시기별 수량 (검토). 피해 시기 한계 서술 |
| Baudron et al. 2019 — Factors influencing FAW damage in African smallholder maize, Eastern Zimbabwe (Crop Prot.) | `Understanding the factors influencing fall armyworm ... Eastern Zimbabwe.pdf` | 46편 비교표, 28절 맥락 | 포장 피해 요인·수량 손실 (검토) |
| Chen et al. 2022 (Insects 13:211) | 없음 | 28절 민감도 | 온도별 번식·개체군 증가. Adan 2024와 반응 방향이 달라 민감도 근거로 분리 |
| Varella et al. 2015 (PLoS One) | 없음 | 16절 | 포장 알·유충 생존. 실제 사망률 분리 불가 |
| Koffi et al. 2025, Ajam et al. 2024, Toepfer et al. 2021, Soujanya et al. 2022, 질소×섭식 실험 2022 | 없음 | 16절 조사 잡음 | 피해 척도·반복 판독 자료 탐색. 반복 판독 오차를 확보하지 못해 조사 잡음 0.01은 가정으로 남음 |
| Li et al. 2023 (Nebraska), 동부 Kenya 파종 시기 연구 2026 | 없음 | 19절 | 현장 보정 후보 점검 (미채택) |
| Marenco et al. 1992 — Sweet Corn Response to FAW Damage During Vegetative Growth (J. Econ. Entomol.) | 없음 | 46편 비교표 | 생육기별 피해·수량 (검토) |

### 7.4 46편 비교표에서 검토만 한 문헌 (값·설계에 미사용)

| 논문 | 검토 주제 |
|---|---|
| Sadras et al. 2016 (Crop Pasture Sci.) | 물·질소 상호작용 종합 |
| Sadras 2004 (Eur. J. Agron.) | 물·질소 공동 제한과 물 이용 효율 |
| English 1990 (J. Irrig. Drain. Eng.) | 경제적 최적 부족 관수량 |
| Geerts & Raes 2009 (Agric. Water Manag.) | 건조 지역 부족 관수와 물 생산성 |
| Malik et al. 2019 (Agric. Water Manag.) | DSSAT-CERES-Maize 관수·질소 관리 |
| Kadiyala et al. 2015 (Agric. Water Manag.) | CERES-rice·maize 물·질소 관리 |

### 7.5 공개 자료 (논문 수 제외)

Masii(유충 수·피해 점수), FAMEWS(감염 식물 비율), USDA LIRF·Iran 관수×질소(기상·토양·관수·수량 입력), LeafByte(면적 측정 정확도) — 16·19절 검증 자료 탐색. 링크는 `docs/MARS_LITERATURE_CROSSWALK.md`.

## 6. 논문이 아닌 근거 (참고)

| 출처 | 절 | 값 |
|---|---|---|
| 제안서 `docs/proposal_revised.pdf` 6쪽 | 2 | 관수·시비 격자 |
| 제안서 8쪽 | 2, 17 | 살포 효능 0.8, 잔효 5일 초기값 |
| 제안서 10쪽 | 18, 32, 34 | 무투입 수렴 시 대안(행동 복제 후 PPO 미세조정). B7 실패(32절) 뒤 구현·시험(34절) |
| 제안서 11쪽 | 0, 17 | 상태 읽기 검증, 살포 순이익 양·음 조건 확인 |
| DSSAT `DATA.CDE` | 1 | HWAH = 건물 기준 수확량 → 15.5 % 환산 |
| `UFGA.CLI` | 1 | WGEN 월 통계(1958년부터 49년) |
| 프로젝트 측정 실행 | 9~33 | 근거 열의 `outputs/runs/...` 경로 |
| Alabama Extension ANR-2852 관개 옥수수 예산서 2026 (aces.edu, 2026년 2월 개정) | 27 | **물 1.17 USD/mm/ha** ($12/acre-inch), **살포 자재비 24.7** (살충제 $10/acre), **살포 작업비 24.7** (항공 살포 $10/acre) |
| USDA AMS Alabama Production Cost Report (주간, 3051) 공식 데이터 | 27 | **질소 1.83 USD/kg N**: 질산암모늄 2025년 48주 평균 565.2 USD/톤 ÷ (907.2 kg × 0.34) |
| LSU AgCenter 2025 고구마 예산서 부록 표 2 (이동식 관 고랑 관수) | 27 | **관수 작업비 2.04 USD/회**: 노동 0.223 h/acre × $14.83 ÷ 4회 |
| Iowa State 2026 Farm Custom Rate Survey (A3-10, 2026년 3월 개정) | 27, 31 | **시비 작업비 34.8 USD/회**: 액비 곁거름 $14.10/acre(응답 38) |
| UF/IFAS 플로리다 옥수수 시비 지침 (bmp.ifas.ufl.edu, 2025년 9월 승인 잠정 권고) | 31 | 질소 7회 이상 분할, 대부분 관수 주입(관비), VT까지 완료. 관비 작업비 2.04·5회 분할을 검토했으나 확인 시즌 비열등 미통과로 **2회 유지, 작업비 34.8로 되돌림** |

## 근거가 없거나 약한 값

| 값 | 상태 |
|---|---|
| 감축률 20·40·60 %의 세 수준 자체 | 제안서 설정에서 이어짐. Kelly 2024 상한 구간에 걸치는 것만 확인 |
| 살포 효능 0.8, 잔효 5일 | 가정 (포장 자료 미확보) |
| 해충 유입 확률·크기, 조사 잡음 0.01 | 가정 (유입 확률은 피해 수준 재보정 후 유지, 28절). 증식률은 2026-11-13 문헌 기준(Adan 2024, Du Plessis 2020) |
| 관수 효율 100 % | 근거 없음, 한계 |
| 피해 계수 α 0.01 | 보정값이 아니라 문헌 범위 맞춤 |
| η 0.45 | 구현 가정(정책 불변이라 결과에 영향 없음) |
| 희소 초기 확률 0.13·0.03·0.03 | 규칙 정책 빈도 기준, 문헌은 수렴 위험만 근거 |

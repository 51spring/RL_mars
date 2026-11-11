# 독립 N 재고 기반 수확 잔사 후보

후속 범위 확대에서 무투입32조건의 실제 반출 경계가 실패했습니다. 기존 관리 조건 통과를 일반화하지 않습니다. 현재 판정은 `HARVEST_N_SCOPE.md`와 `configs/harvest_n_candidate_domain.json`을 참고합니다.

2026-11-06. 기본 학습 이미지는 그대로이며 `mars-dssat:harvest-n-candidate`에서만 시험했습니다. 이전에 철회한 ×10 단위 후보와 별개입니다.

## 변경과 독립 기준

원본은 STOVN에 포함된 낙엽 N을 수확 잔사에 다시 더합니다. 후보는 MZ_CERES에서 HRes_Ceres에 넘길 지역 SENESCE 복사본의 `ResE(0,N)`만0으로 둡니다. 원래 SENESCE, 건물중·리그닌·P·뿌리, STOVN·생육·수량 보고와 다른 작물 함수는 바꾸지 않습니다. 잔사 결과에서 임의 오차를 빼는 방식은 사용하지 않습니다.

검사 기준은 다음과 같이 분리합니다.

- 종자 N·흡수·뿌리 고사·피해 반출과 실제 식물체 N 재고의 일별 원장.
- 실제 곡실 N 반출 + 명시적인 부산물 N 배분 + 실제 HARVRES와 수확 직전 식물 N/미전송 뿌리 N 재고 비교. 부산물 N은 네이티브 측정이 아닌 배분이라는 제한을 기록.
- 실제 다음 휴경 SoilOrg_init 전후 뿌리→FOM/FON·표면→mulch 전달.
- 원본/후보의 첫 작물 일별 궤적과 Summary/PlantGro/PlantN 수치 출력 정확 대조. 휴경 토양 출력은 잔사 N 변화로 달라질 수 있음.

## 실제 결과

Q/F × 곡실100/50% × 줄기0/50/100% × 무피해/5회3% 피해의24쌍과 C 모드4쌍, 총56실행을 통과했습니다. Q/F는 관리 조건의 UFGA8201·시드123456 한 토양/품종이며, C 대조에는 무투입 시드456789도 포함합니다. 지정 HARVFRAC와 실제 값도 일치했습니다.

무피해·곡실 전량 수확·줄기 미수확 기준 잔사 N은 원본61.001656 → 후보59.588055kg N/ha입니다. 건물중은 유지됩니다. 후보의 최대 N 분배/실제 곡실 반출 경계 잔차0.00001145kg N/ha, 일별 식물체 N 원장 잔차0.00002701kg N/ha입니다. 경계의 허용오차는 기존 binary32 합산 한계를 사용합니다.

근거: `outputs/runs/20261106T025157Z_harvest_n_candidate_8f5f18e3/verification.json`.
이미지: `sha256:370968c24053c98cb519386186bdfe4c2da5678293a06ef02f61b34f8a7265c4`.
원본/후보 바이너리·빌드 소스 SHA, 설정·이미지 manifest, 일별 자료·네이티브 출력을 보존합니다.

```powershell
.\scripts\verify_harvest_n_candidate.ps1
```

`experimental_harvest_n_candidate=true`는 위 범위의 기술 검사만 의미합니다. 기본 원본의 N 보존 게이트는 계속 false이며 후보를 기본 PPO 이미지에 승격하지 않았습니다. 다른 시드/토양·불량 출아·EARS/PLTPOP 차이가 있는 Q/F 조건, 다년 회전, 장기 토양 분해, 원소 C/P와 독립 농학 검증은 남아 있습니다. 전체 작물·토양 수지나 농학적 타당성을 통과한 것으로 간주하지 않습니다.

## 공개 검증자료 확보

Oveysi2010의 교차 처리 수량 평균10개를 Table4에서 전사하고 PDF 렌더링과 대조했습니다. Table3의 주변평균은 구분했습니다. 자료와 출처는 `configs/oveysi2010_table4_grain.json`에 기록했습니다. 출판사 원문: https://www.agriculturejournals.cz/publicFiles/86_2010-PSE.pdf

SE·원자료·일별 실험 입력은 미확보여서 연구 단위의 독립 검증 후보로만 유지합니다. Duncan 문자로 SE를 추정하거나 수량 반응의 부호를 강제하지 않습니다. D2 주변평균과 교차 평균 재계산의 차이는0.1t/ha로 반올림 경계에 있어 별도 확인 대상으로 기록했습니다.

PDF·표 이미지·지문: `outputs/runs/20261106T025347Z_oveysi2010_source_1697e26e`.
자료 자격 검사: `outputs/runs/20261106T025626Z_public_factorial_means_8dc9ccd5/verification.json`.
`quantitative_fit_ready=false`, `research_ready=false`를 유지합니다.

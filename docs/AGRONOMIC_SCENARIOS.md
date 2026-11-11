# 공개 농학자료의 시나리오 대응

2026-11-06. 3연구의28처리와16개 원문 평균 대비를 등록했습니다. 새 시뮬레이션·보정·독립 농학 통과 판정은 실행하지 않았습니다. 공개 목록은 후속 조사에서9연구로 확장됐습니다. 추가 현장9개 주변평균은 factorial 시나리오와 분리하며 [후속 자료 조사](GRAIN_MAIZE_DATA_SEARCH.md)에 근거·접근 제한을 기록했습니다.

| 연구 | 등록 처리 | 확인한 대응과 제한 |
|---|---:|---|
| Santos2018 | 12 | R3의 수확 이삭 무게. native 건조 곡실 HWAH로 대체 불가. 기비·추비 분할량/일별 입력·SE 미확보 |
| Oveysi2010 | 10 | 건조 곡실 kg/ha 단위 변환 가능. SC704/토양/기상·관수 재현과 blade clipping 매핑·수치 SE 미확보 |
| Oliveira2026 | 6 | 무추비도 기비 N40 포함, N 추비 처리의 총량은120kg/ha 상당. 포트 단위와5cm 절단을 field/leaf-fraction으로 대체 불가 |

출처: [Santos 기관 원문](https://repositorio.unesp.br/bitstreams/0bc71673-864b-4f76-a7d3-b4ebedc0401a/download), [Oveysi 출판사 원문](https://www.agriculturejournals.cz/publicFiles/86_2010-PSE.pdf), [Oliveira 출판사 원문](https://link.springer.com/article/10.1007/s11738-026-03963-0).

Santos의 원래 보정 후보 역할은 유지하되, 현재 native 건조 곡실 수량과의 정량 비교/보정은 허용하지 않습니다. 독립 검증용 Oveysi·Oliveira를 보정 데이터로 옮기지 않습니다. 같은 연구 안의 처리 행을 학습/검증으로 나눠 독립성을 주장하지 않습니다.

## 생성물과 코드

- `configs/agronomic_protocols.json`: 출처, 처리, N/물/피해 정의, 누락 입력.
- `agronomic_scenarios.py`: 시나리오·같은 조건의 대조군 대비·단위 비교·역할/준비 상태 검사.
- 실행 폴더의 `scenarios.json`, `observed_contrasts.json`, `readiness_by_scenario.json`:28처리,16대비와 개별 차단 사유.
- Santos PDF·시각 대조 페이지와 Oliveira HTML/DOCX: `outputs/runs/20261106T042630Z_agronomic_source_refresh_14759c5a`. 원문 자산 SHA256을 보존함.

```powershell
.\.venv\Scripts\python.exe scripts/build_agronomic_scenarios.py
```

현재16대비는 같은 연구·물 조건의 처리/대조 평균 비율입니다. 모형 예측과의 검증 점수가 아니며 신뢰구간과 통과 여부는 null입니다. 반응 부호를 제한하지 않고, 유의하지 않다는 결과를 정확한0으로 바꾸지 않습니다.

## 오역·누출 방지

1. R3 이삭 무게, 건조 곡실 수량, 포트 곡실 무게는 다른 endpoint로 저장합니다. t/ha→kg/ha 변환이 가능해도 다른 생물학적 endpoint끼리 비교하지 않습니다.
2. `W/N`은 무추비이며 N0 처리로 만들지 않습니다. V4/V6 추비는 별도 선택이고, 둘 다 더하거나 제안서 예산에 맞춰 자동 절삭하지 않습니다. 이 자료의 재현은 정책 훈련과 별도 검증 작업입니다.
3. 5cm shoot 절단이나 특정 blade 제거를 현재의 균일 잎 건물중 제거로 간주하지 않습니다. 피해 매핑은 확인 전 false입니다.
4. n=3/8, Tukey/Duncan 문자, 보충자료의 F/p 값에서 SE를 만들지 않습니다. 방법에 SE가 보고됐다는 설명도 수치 SE 확보와 구분합니다.
5. 독립 연구는 입력이 완비돼도 보정/임계값 선택에 사용하지 못하게 합니다. 평균이 예측과 정확히 같아도 통계 검증 통과로 표시하지 않습니다.

Oliveira 보충자료는 확보했지만 grain mean/SE는 그림에 제시돼 있고 수치로 추출하지 않았습니다. 그림을 추후 수치화하면 추출 오차·실험 단위·반복 구조를 함께 검증해야 합니다. IITA는 메타데이터의 Open Access와 CSV embargo 표시가 충돌하는 상태로 보이며 원자료는 여전히 미확보입니다. [저장소 표시](https://data.iita.org/dataset/maize-plants-can-compensate-significant-damage-by-the-fall-armyworm-and-recover).

## 다음 완료 조건

정량 검증 가능 시나리오는 현재0개입니다. 우선 grain maize 보정 자료와 numeric mean/SE 또는 사전 허용범위, 전체 토양층/품종 계수·기상·관수 입력, 단계/피해 매핑을 확보합니다. 독립 시나리오에는 정해진 역할을 유지하고 무피해 생육/수량 대조부터 진행합니다. 누락 입력을 WGEN·UFGA·기본 품종으로 대체한 실행은 전이 진단으로 별도 표시해야 합니다.

해충 온도/조사 잡음·피해 계수·보상 eta는 이번 작업에서 변경하지 않았습니다. 연구 준비·본 학습·기본 작물 이미지 승격은 계속 보류합니다.

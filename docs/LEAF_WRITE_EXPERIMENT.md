# 실제 잎 피해 쓰기: 실험용 경로

이 문서는 연구용 해충 실행 승인이나 농학 검증 통과를 뜻하지 않습니다.
구현은 별도 이미지 `mars-dssat:leaf-experimental`에서만 사용합니다.
기본 무해충 바이너리와 vendor 소스는 유지합니다.

## 시점과 범위

원본 MZ_GROSUB의 WLIDOT 피해 블록은 질소 흡수 전입니다.
제안서의 하루 말기 피해와 구분하기 위해 새 블록은 INTEGR의 마지막,
원래 성장·질소 흡수·누적 고사 계산 이후, OUTPUT 이전에 삽입합니다.
MDATE가 도달한 성숙/실패 당일에는 적용하지 않습니다.
이 문서의 펄스 검증은 아침에 지정한 잎 손실 비율의 실제 상태 반영을 검사합니다.
후속 실험용 온라인 연결은 SEASON_BALANCE_AND_ONLINE.md에 구분해 기록합니다.

## 상태와 단위

Fortran/PDI에서 쓰기 전후의 LFWT, PLA, SENLA, STOVN, STMWT,
XLAI, TOPWT, WTNCAN, GRAINN, 누적 고사 건물중/질소를 읽습니다.

- LFWT: g/plant, PLA/SENLA: cm²/plant, PLTPOP: plants/m²
- TOPWT: g/m², STOVN: g N/plant, WTNCAN: g N/m²
- XLAI: m² leaf/m² ground
- 별도 제거 원장: g dry matter/m² 및 g N/m²

PLA에는 이미 고사한 면적 SENLA가 포함되므로 녹색 면적을 PLA−SENLA로 구분합니다.
손실 비율 delta에 대해 녹색 면적과 LFWT를 (1−delta)배로 줄이고 SENLA는 유지합니다.
이 구현의 PLA 식은 SENLA+(PLA−SENLA)×(1−delta)입니다.
제안서의 단순 PLA 배율을 고사 면적에까지 적용하면 생존 면적 비율이 맞지 않으므로
백엔드의 실제 변수 의미를 따로 명시한 것입니다. 이 해석은 회복 자료로 검증해야 합니다.

STOVN에서는 기존 모형의 잎/줄기 비례 질소 배분을 사용해 제거된 잎의 질소를 차감합니다.
LAI/XLAI/XHLAI, AREALF, WTLF, STOVWT, BIOMAS/TOPWT, PTF, SLA,
HI/HIP, WTNCAN, WTNLF/WTNST/WTNVEG, 관련 질소 농도를 다시 계산합니다.
새 고사엽이나 토양 잔사로 추가하지 않고 별도 제거량으로 기록합니다.

## 구현 파일

- `docker/leaf_integration.for`: 말기 INTEGR 쓰기 및 PDI 전후 읽기
- `docker/patch_leaf_source.py`: 컨테이너 복사본에만 적용하는 위치 고정 패치
- `docker/Dockerfile.leaf`: 동일 컴파일러/설정의 무수정 대조와 수정 바이너리 생성
- `src/mars_env/leaf_diagnostics.py`: 실험용 프로토콜 및 회계 항등식 검사
- `scripts/verify_native_leaf.py`: 실제 상태 전후 검사, 무피해 회귀, V7 전 피해 검사

`LeafDiagnosticBackend.step_damage(water_mm, nitrogen_kg_ha, fraction)`은 실험 전용입니다.
`supports_leaf_damage`는 계속 False이고 연구용 pest_enabled 실행은 거부합니다.
입력 비율 0일 때 기존 상태 계산을 다시 하지 않아 무피해 회귀를 보존하도록 설계했습니다.

```powershell
docker build -f docker/Dockerfile.leaf -t mars-dssat:leaf-experimental .
.\scripts\verify_native_leaf.ps1
```

빌드 로그: `outputs/leaf_build.log`.
실제 검증에 성공한 경우에만 `outputs/native_leaf_verification.json`이 생성됩니다.
결과 파일 없이 구현만으로 완료 판정하지 않습니다.

## 실제 검증 결과

`outputs/native_leaf_verification.json`의 passed=True를 확인했습니다.

- 배포 바이너리, 동일 소스/컴파일러 대조, 수정 바이너리의 무피해 전체 궤적이 정확히 일치했습니다.
- 세 무피해 경로의 최종 수확량은 모두 4707kg/ha로 일치했습니다.
- 무피해 경로의 122개 활성일에 쓰기 전후 항등식을 검사했습니다.
- DAP15(V3)와 DAP50(V12)에 25% 잎 손실을 적용했습니다.
- 첫 피해 직전의 당일 생육 값은 무피해와 동일했고 다음 관측에는 실제 감소가 반영됐습니다.
- 두 펄스의 건물중/질소 제거량은 각각 약 0.36g/m²·0.01584g N/m²,
  21.78049g/m²·0.747117g N/m²입니다. 고사 잔사와 곡실 질소는 순간적으로 바뀌지 않았습니다.
- 펄스 사례의 수확량 4657kg/ha는 연결 진단값이며 보정된 피해 효과나 H3의 증거가 아닙니다.

초기 DAP10은 출아 전이어서 잎 쓰기 이벤트가 없었습니다. 실제 잎이 있는 DAP15로
검증 날짜를 바꿨습니다. V7 이전 손실을 억제하는 조건을 추가한 것은 아닙니다.
런타임 로그는 개발 중 시도의 오류를 포함하여 누적되며 최종 판정 근거는 구조화된 결과 JSON입니다.
원본 vendor 소스는 바꾸지 않았고 컨테이너 복사본만 패치했습니다.

## 남은 검증

국소적인 생체량·질소 감소와 제거량의 항등식은 전체 생태계 수지 검증과 다릅니다.
후속 검증에서 종자·흡수·식물체·뿌리 고사·제거 N 재고 수지는 실제 8개 조건에서 닫혔습니다.
원소 탄소 및 토양/잔사 전체 수지는 남아 있습니다.
원본의 호흡·노화·고사 잔사·재이동 경로 및 일별 전체 탄소/질소 수지를 추가 확인해야 합니다.
현재 제거 건물중을 원소 탄소량으로 간주하지 않습니다. 조직별 탄소 조성이 필요합니다.
인/칼륨 활성 조건의 회계는 이 경로의 검증 범위가 아닙니다(기본 시나리오에서는 비활성).
회복·수량 반응, 물×질소×피해의 농학적 타당성도 별도 검증합니다.
출력 궤적·국소 회계가 통과해도 H3 또는 실제 재배 효과가 검증된 것은 아닙니다.

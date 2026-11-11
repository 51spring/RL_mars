# Q/F 수확 잔사 감사: 단위 판정 정정

2026-11-06 후속 감사에서 이전 g/m² 판정과 ×10 후보를 철회했습니다.
원본 CumLeafSenes 생성식에는 PLTPOP×10이 이미 포함되며 단위는 kg/ha입니다.

원본 Q/F24조건의 건물중 분배·실제 토양 전달은 확인했습니다. 그러나 낙엽 N이 이미 canopy N에 포함된 상태에서 잔사에 다시 더해져16조건에서 독립 N 재고 보존이 실패했습니다. 전체 물리 수지 통과로 해석하지 않습니다.

현재 설명·단위·수지·측정 범위는 [C 모드 반출과 C/N 감사](C_HARVEST_AND_OBSERVABILITY.md)를 참고합니다.
재감사 근거는 `outputs/runs/20261106T023809Z_sequence_inventory_reaudit_76087465/verification.json`입니다.
이전020048 보고서는 보존하되 검증 판정에서 철회했습니다. 기본 PPO 이미지는 영향을 받지 않았습니다.

```powershell
.\scripts\verify_sequence_handoff.ps1
```

위 명령은 원본 계측 전용 `mars-dssat:sequence-native`를 빌드하고 `verify_sequence_inventory.py --matrix`를 실행합니다. 철회된 단위 후보는 빌드하지 않습니다.

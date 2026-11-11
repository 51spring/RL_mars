# Becker 2016 P0157AMX와 관리 입력 전달 검사

2026-11-08 한국 시간. Zhen 등의 보충표 S1에서 P0157AMX 수동·자동 보정 계수 6개씩을 다시 읽고, 각각 별도 CERES 품종 ID로 기록했다. 공개 본문·보충표와 프로젝트의 CERES 파일에서 원 연구의 생태형 연결은 확인하지 못했다. 실행 검사는 현재 이미지의 `IB0001 GENERIC MIDWEST1`을 두 계수 세트에 공통으로 사용했다. 격리 이미지의 ECO·SPE와 입력 CUL 해시를 보존했다. 두 계수 세트의 값은 네이티브 INP에서 모두 원문과 일치했다. [Zhen 등 원문](https://www.nass.usda.gov/Research_and_Science/Cropland/docs/2025_DISSAT%20Auto%20Cal.pdf) · [보충표 S1](https://ars.els-cdn.com/content/image/1-s2.0-S1161030125003661-mmc1.docx)

## 관리 기록과 네이티브 전달

- 64시험구의 블록·처리 ID와 질소 시비량을 정리했다. 기술 실행은 1블록의 포장 109(처리 시비 0)와 포장 104(45 + 270 kg N/ha)에 두 계수 세트를 교차한 4조건이다. 토양은 앞선 초기화 검사의 1블록 Hubbard 배수상한 조건으로 고정했다.
- 4월 27일 파종, 76 cm 이랑과 87,720립/ha를 입력했다. 파종량을 모델 개체밀도의 대리값으로 적용했으며 FileX의 8.772/m²가 두 내부 파일에서 8.8/m²로 반올림됐다. 파종 깊이 5 cm는 기술 가정이다. 질산암모늄은 5월 2일·6월 22일 기록과 표면 살포 규약을 적용해 `FE001/AP001`로 입력했다. [Dryad](https://doi.org/10.5061/dryad.66t1g1k2g) · [시험 관리 규약](https://doi.org/10.2134/agronj2017.04.0207)
- 스프링클러 20건을 `IR004`로, 관수수 질산태 N을 `FE008/AP005`로 넣었다. 관수와 강수가 겹친 6일은 MRMS 강수와 관수 기록을 각각 보존했다. 관수수 질소의 깊이별 수송은 표층 배치 가정에 따른다.
- 4조건의 177일씩 총 708개 일별 기록에서 투입일과 누적량이 입력과 일치했다. 물은 모두 245.11 mm, 총 투입 질소는 포장 109에서 27.66, 포장 104에서 342.66 kg N/ha였다. [검산 결과](../outputs/runs/20261108T093207Z_ransom_becker_2016_cultivar_and_management_replay_gate_cbd8adb3/verification.json)

관리표에는 별도 비료 P₂O₅ 67.3, K₂O 183.8 kg/ha와 추가 N 0이 기록돼 있다. 기술 검사에서는 N 경로만 활성화했다. 원 연구 생태형, 실측 입모·파종 깊이, 관수수 질소의 수직 배치 및 다른 양분의 모형화가 재현 범위를 제한한다. 관측 수량 파일은 사용하지 않았고 정량 등록은 0건이다. 소프트웨어 검사 204개가 통과했다.

다음은 64시험구 기술 재현에서 사용할 품종·토양 가정과 평가 항목을 수량 공개 전에 고정하고, 생육·관리 출력의 누락과 실패를 먼저 확인하는 작업이다. [고정 입력](../outputs/runs/20261108T093207Z_ransom_becker_2016_cultivar_and_management_replay_gate_cbd8adb3/frozen.json) · [재현 코드](../outputs/runs/20261108T093207Z_ransom_becker_2016_cultivar_and_management_replay_gate_cbd8adb3/probe.py) · [소프트웨어 검사](../outputs/runs/20261108T093207Z_ransom_becker_2016_cultivar_and_management_replay_gate_cbd8adb3/unit_tests.json)

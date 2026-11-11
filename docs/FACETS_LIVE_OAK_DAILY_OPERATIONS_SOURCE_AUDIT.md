# FACETS Live Oak HydroShare 일별 관리 입력 감사

2026-11-08 한국 시간. Rath 아카이브의 파일 목록 802개를 모두 확인하고, 포장시험 자료 중 README, 관리 입력, 설정, 비료 정의 및 비교용 모형 출력 등 39개 파일을 공개 MD5와 대조했다. Lee 아카이브는 파일 목록 12개와 현장시험 TAR 및 두 README를 확인했다. 대용량 유역 시나리오는 논문 방법과 README로 범위를 판정했다. [Rath 아카이브](https://doi.org/10.4211/hs.0a7735b121f845f7ab0d1ac6348d9980) · [Lee 아카이브](https://doi.org/10.4211/hs.e992c4484f864ef8bccdc2924ed6e9ba)

## FDACS 2015–2017

Rath 현장시험 입력은 남쪽 2015·2017년과 북쪽 2016년 옥수수의 관수 3종×질소 3수준을 다룬다. 포장시험 전체의 관수 5종 중 Calendar·SMS·Rainfed만 포함한다. 수문반응단위(HRU)당 처리 하나를 지정했고, 각 반복구의 현장 기록 키는 없다. `file.cio`의 시작 연도와 `.mgt`의 연도 구분자를 연결하여 18개 파일의 옥수수 **처리–시즌 27개**를 재현했다. 파종일부터 수확일까지 **관수 입력 631행, 비료 입력 207행**이다. 같은 관수일과 수량이 질소 처리별 파일에 반복되므로 행 수는 고유 관측 건수와 구분한다. `fert.dat`의 무기·유기 N 비율을 제품 kg/ha에 곱해 N kg/ha로 합산했다. [Rath 논문 §2.1·2.4–2.6 및 Table 1](https://www.watershedecology.org/uploads/1/2/7/3/12731039/rath_et_al._2021.pdf) · [SWAT 관리 입력 정의](https://swat.tamu.edu/media/69359/ch20_input_mgt.pdf)

| 옥수수 연도 | Calendar 입력 / 논문 | SMS 입력 / 논문 | Rainfed 입력 / 논문 |
|---|---:|---:|---:|
| 2015 | 330.20 / 330 | 151.05–151.45 / 151 | 15.24 / 15 |
| 2016 | 479.53 / 490 | 269.45–289.77 / 291 | 22.86 / 25 |
| 2017 | 546.10 / 546 | 302.26 / 302 | 48.26 / 48 |

단위는 mm다. 2016년 SMS에는 6월 1일과 3일 10.16 mm 입력이 각각 일부 파일에만 있다. 저·고질소 폴더 설명도 값과 반대다. 예를 들어 2015년 폴더 `Rate_1`의 총 N은 약 336, `Rate_3`는 약 157 kg/ha다. 입력 행과 README 표기를 그대로 남겼다. 2016년 4월 19일에도 개별 비료 행에서 약 33.63 kg N/ha가 확인되지만 처리 전체의 보충 시비 기록과 직접 연결되지는 않는다. 따라서 학위논문의 30/34 kg N/ha 충돌을 해소하지 않았다.

현장시험 재현용 일정은 논문의 처리별 현장 시행 정보를 담고 있으나 일부 합계 차이와 반복구 연결 공백이 있다. 장기 시나리오에서는 과거 강수로 달력 관수를 구성하고 작물 수분 스트레스로 자동 관수를 작동시켰다. 이 자료를 각각 **현장시험 기반 처리별 모형 입력**과 **장기 시나리오 입력**으로 분리했다. `output.mgt`는 SWAT 출력으로 구분했다. [Rath 논문 §2.4·2.6](https://www.watershedecology.org/uploads/1/2/7/3/12731039/rath_et_al._2021.pdf)

## FACETS 2018

Lee의 남쪽 현장시험 TAR에서 작물 코드 19의 2018년 3월 8일 파종과 8월 15일 수확 구간을 분리했다. HRU 9개에 **관수 236행, 비료 64행**이 있으며 HRU 8의 처리 라벨은 README에 비어 있다. 2018년 북쪽과 2020년 옥수수에 대응하는 현장시험 일정은 이 TAR의 범위 밖이다. 별도의 Santa Fe 유역 모형에는 1980–2018년 고정 관리 일정 및 자동 관수 규칙이 들어간다. [Lee 아카이브](https://doi.org/10.4211/hs.e992c4484f864ef8bccdc2924ed6e9ba) · [Lee 논문 §2.3](https://www.watershedecology.org/uploads/1/2/7/3/12731039/lee_et_al._2024.pdf)

두 아카이브에서 옥수수 **입력 1,138행**을 출처 파일과 줄 번호로 추적할 수 있다. 반복구별 관수·시비 원장과 원장의 처리 키가 미확보라 정량 등록은 0건이다. 다음은 공개된 FDACS 계약 21894 최종보고서와 부록에서 유량계 측정과 일별 적용량의 처리·반복구 연결을 대조하는 작업이다. [FDACS 최종보고서](https://ccmedia.fdacs.gov/content/download/113761/file/Final-report_21894.pdf)

[검산 결과](../outputs/runs/20261108T042622Z_facets_live_oak_daily_operations_source_audit_b0ccf1d7/verification.json) · [Rath 입력 행](../outputs/runs/20261108T042622Z_facets_live_oak_daily_operations_source_audit_b0ccf1d7/corn_operations.json) · [Lee 입력 행](../outputs/runs/20261108T042622Z_facets_live_oak_daily_operations_source_audit_b0ccf1d7/lee_corn_operations.json) · [재현 코드](../outputs/runs/20261108T042622Z_facets_live_oak_daily_operations_source_audit_b0ccf1d7/audit.py)
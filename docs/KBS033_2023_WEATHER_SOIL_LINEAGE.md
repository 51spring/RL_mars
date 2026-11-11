# KBS033 2023년 기온·토양·품종 입력 감사

2026-11-08 한국 시간. 2023년 파종일부터 수확일까지 190일을 대조했다. 원본을 수정하거나 DSSAT 입력을 생성하지 않았다.

| 자료 | 최고·최저기온 결측일 28일의 확인 결과 |
|---|---|
| KBS 일별 강수·기온, SALUS용 일별 기상, 3 m 센서 일별 극값 | 3개 표 모두 결측일에 사용할 수 있는 극값 0개. 3 m 센서 표에서 같은 날짜에 값이 다른 2일은 비교에서 제외했다. [일별 기온](https://lter.kbs.msu.edu/datatables/7) · [SALUS](https://lter.kbs.msu.edu/datatables/143) · [3 m 센서](https://lter.kbs.msu.edu/datatables/561) |
| KBS 시간별 센서 | 결측일 중 25일은 UTC 날짜에 유효한 시간평균 24개가 있다. 시간평균의 최대·최소는 일별 관측 극값과 구분했다. [시간별 표](https://lter.kbs.msu.edu/datatables/13) |
| Gull Lake COOP | 같은 표기일에서 최고 18일, 최저 16일, 둘 다 15일을 확보했다. COOP는 현지 오후 4시 종료의 24시간을 집계한다. 주 관측표와 공통값의 평균 절대 차이는 최고 2.89°C, 최저 2.16°C다. 날짜 이동도 진단했으나 보충 입력에 사용하지 않았다. [COOP 기상](https://lter.kbs.msu.edu/datatables/31) |

2016년 탄소·총질소 자료는 2023년 시험지의 포장 12개와 처리번호·물 처리까지 연결됐다. 시료 깊이는 0–10 cm와 10–25 cm다. 2007·2016년 용적밀도 표는 포장번호 13개가 일치하고 깊이는 최대 25 cm다. KBS의 Kalamazoo·Oshtemo 토양층 참고자료도 확인했으나 시험지 D의 개별 포장에 어느 토양층을 적용할지 확인되지 않았다. 2023년 파종 전 심도별 수분·무기질소 자료는 여전히 미확보다. [탄소·총질소](https://lter.kbs.msu.edu/datatables/566) · [용적밀도](https://lter.kbs.msu.edu/datatables/503) · [KBS 토양층 연구](https://lter.kbs.msu.edu/docs/robertson/Syswerda_et_al_2012_AGEE.pdf)

Pioneer P0306Q는 농작업 기록과 품종 자료에서 확인했다. 상대숙기 103은 확인됐으나 로컬 CERES-Maize 품종 파일에 일치 항목이 없고, P1·P2·P5·G2·G3·PHINT의 독립 계수도 확보하지 못했다. [KBS 품종 기록](https://aglog.kbs.msu.edu/materials/392) · [Pioneer 품종 자료](https://www.pioneer.com/content/dam/dpagco/pioneer/na/ca/en/files/articles/DF-Tar-Spot-of-Corn-in-the-U.S.-and-Canada-NA_CA_EN_V1.pdf)

재현에 필요한 초기 토양과 품종계수가 미확보이므로 2023년 정량 검증 등록은 보류했다. 다음은 유효 수량의 질소 반응을 시즌별·물 처리군별로 산출하는 작업이다. 각 물 처리군 내부의 블록을 유지하고, 관수와 천수의 반응 차이는 기술적 비교로 구분한다. 소프트웨어 검사 204개가 통과했다.

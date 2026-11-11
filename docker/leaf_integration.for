C     MARS experimental day-end live leaf removal, after native N uptake.
C     Green leaf area is removed; pre-existing senesced area is retained.
C     Exported dry matter and N are diagnostic sinks, not soil litter.
      IF (YRDOY.GE.YRPLT .AND. PLTPOP.GT.0.0 .AND.
     &    (MDATE.LE.0 .OR. YRDOY.LT.MDATE)) THEN
        MARS_DELTA = 0.0
        CALL pdi_transaction_begin("mars_leaf_before")
        CALL pdi_expose("MARS_DELTA", MARS_DELTA, pdi_in)
        CALL pdi_expose("MARS_LFWT", LFWT, pdi_out)
        CALL pdi_expose("MARS_PLA", PLA, pdi_out)
        CALL pdi_expose("MARS_SENLA", SENLA, pdi_out)
        CALL pdi_expose("MARS_STOVN", STOVN, pdi_out)
        CALL pdi_expose("MARS_STMWT", STMWT, pdi_out)
        CALL pdi_expose("MARS_XLAI", XLAI, pdi_out)
        CALL pdi_expose("MARS_TOPWT", TOPWT, pdi_out)
        CALL pdi_expose("MARS_WTNCAN", WTNCAN, pdi_out)
        CALL pdi_expose("MARS_GRAINN", GRAINN, pdi_out)
        CALL pdi_expose("MARS_CLS", CumLeafSenes, pdi_out)
        CALL pdi_expose("MARS_CNS", CumLfNSenes, pdi_out)
        CALL pdi_transaction_end()
        MARS_DELTA = MIN(1.0,MAX(0.0,MARS_DELTA))
        MARS_DM = 0.0
        MARS_N = 0.0
        IF (MARS_DELTA.GT.0.0 .AND. LFWT.GT.0.0) THEN
          MARS_DM = MARS_DELTA * LFWT
          IF (STOVWT.GT.0.0)
     &      MARS_N = STOVN * MARS_DM / STOVWT
          LFWT = MAX(0.0,LFWT - MARS_DM)
          PLA = MAX(SENLA,PLA-MARS_DELTA*MAX(0.0,PLA-SENLA))
          STOVN = MAX(0.0,STOVN-MARS_N)
          STOVWT = LFWT+STMWT
          LAI = MAX(0.0,(PLA-SENLA)*PLTPOP*0.0001)
          XLAI = LAI
          XHLAI = LAI
          AREALF = LAI*10000.0
          WTLF = LFWT*PLTPOP
          BIOMAS = (LFWT+STMWT+EARWT)*PLTPOP
          TOPWT = BIOMAS
          PTF = 0.0
          IF ((RTWT+LFWT+STMWT+EARWT).GT.0.0)
     &      PTF = (LFWT+STMWT+EARWT)/(RTWT+LFWT+STMWT+EARWT)
          SLA = 0.0
          IF (WTLF.GT.0.0) SLA = LAI*10000.0/WTLF
          HI = 0.0
          HIP = 0.0
          IF (TOPWT.GT.0.0) THEN
            HI = SDWT/TOPWT
            HIP = PODWT/TOPWT
          ENDIF
          WTNCAN = (STOVN+GRAINN)*PLTPOP
          WTNLF = 0.0
          WTNST = 0.0
          IF (STOVWT.GT.0.0) THEN
            WTNLF = STOVN*LFWT/STOVWT*PLTPOP
            WTNST = STOVN*STMWT/STOVWT*PLTPOP
          ENDIF
          WTNVEG = WTNLF+WTNST
          PCNL = 0.0
          PCNST = 0.0
          PCNVEG = 0.0
          IF (WTLF.GT.0.0) PCNL = WTNLF/WTLF*100.0
          IF (STMWT.GT.0.0)
     &      PCNST = WTNST/(STMWT*PLTPOP)*100.0
          IF (STOVWT.GT.0.0)
     &      PCNVEG = WTNVEG/(STOVWT*PLTPOP)*100.0
        ENDIF
        MARS_DM = MARS_DM*PLTPOP
        MARS_N = MARS_N*PLTPOP
        MARS_CUM_DM = MARS_CUM_DM+MARS_DM
        MARS_CUM_N = MARS_CUM_N+MARS_N
        CALL pdi_transaction_begin("mars_leaf_after")
        CALL pdi_expose("MARS_LFWT", LFWT, pdi_out)
        CALL pdi_expose("MARS_PLA", PLA, pdi_out)
        CALL pdi_expose("MARS_SENLA", SENLA, pdi_out)
        CALL pdi_expose("MARS_STOVN", STOVN, pdi_out)
        CALL pdi_expose("MARS_STMWT", STMWT, pdi_out)
        CALL pdi_expose("MARS_XLAI", XLAI, pdi_out)
        CALL pdi_expose("MARS_TOPWT", TOPWT, pdi_out)
        CALL pdi_expose("MARS_WTNCAN", WTNCAN, pdi_out)
        CALL pdi_expose("MARS_GRAINN", GRAINN, pdi_out)
        CALL pdi_expose("MARS_CLS", CumLeafSenes, pdi_out)
        CALL pdi_expose("MARS_CNS", CumLfNSenes, pdi_out)
        CALL pdi_expose("MARS_DM", MARS_DM, pdi_out)
        CALL pdi_expose("MARS_N", MARS_N, pdi_out)
        CALL pdi_expose("MARS_CUM_DM", MARS_CUM_DM, pdi_out)
        CALL pdi_expose("MARS_CUM_N", MARS_CUM_N, pdi_out)
        CALL pdi_transaction_end()
      ENDIF

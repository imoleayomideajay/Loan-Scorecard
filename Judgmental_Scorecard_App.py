WITH LoanSnapshot AS (
    SELECT
        C.ccodcta                           AS LoanCode,
        CONVERT(DATE, C.dfecvig)            AS DisbursementDate,
        @dfecsis                            AS ReportDate,
        L.OustandingPrincipal               AS OutstandingPrincipal,
        OverdueData.CurrentOverdueDays      AS CurrentOverdueDays,

        -- MOB
        DATEDIFF(MONTH, C.dfecvig, @dfecsis)
        - CASE 
            WHEN DAY(@dfecsis) < DAY(C.dfecvig) THEN 1 
            ELSE 0 
          END                               AS MOB

    FROM Loans L
    INNER JOIN lfsbaku..cremcre C
        ON C.ccodcta = L.LoanCode
    OUTER APPLY (
        SELECT 
            MAX(CASE 
                WHEN credppg.cestado = 'E'
                     AND credppg.dfecven < @dfecsis
                THEN DATEDIFF(DAY, credppg.dfecven, @dfecsis)
                ELSE 0
            END) AS CurrentOverdueDays
        FROM credppg
        WHERE credppg.ccodcta = L.LoanCode
          AND credppg.ctipope <> 'D'
    ) OverdueData
)

SELECT
    FORMAT(DisbursementDate, 'yyyy-MM') AS DisbursementMonth,
    MOB,

    SUM(OutstandingPrincipal) AS TotalOutstanding,

    SUM(CASE WHEN CurrentOverdueDays = 0 THEN OutstandingPrincipal ELSE 0 END) AS PAR_0,
    SUM(CASE WHEN CurrentOverdueDays > 0 THEN OutstandingPrincipal ELSE 0 END) AS PAR_1_PLUS,
    SUM(CASE WHEN CurrentOverdueDays > 30 THEN OutstandingPrincipal ELSE 0 END) AS PAR_30_PLUS,
    SUM(CASE WHEN CurrentOverdueDays > 90 THEN OutstandingPrincipal ELSE 0 END) AS PAR_90_PLUS

FROM LoanSnapshot
GROUP BY
    FORMAT(DisbursementDate, 'yyyy-MM'),
    MOB
ORDER BY
    DisbursementMonth,
    MOB;
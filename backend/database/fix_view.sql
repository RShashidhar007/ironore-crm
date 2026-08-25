-- Fix the ORDER BY error in vw_ComplaintsReadyForSolution view
-- Run this in MSSQL to fix the view

IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_ComplaintsReadyForSolution')
    DROP VIEW vw_ComplaintsReadyForSolution;
GO

CREATE VIEW vw_ComplaintsReadyForSolution AS
SELECT TOP 10000
    ComplaintID,
    CategoryType,
    ComplaintDescription,
    MarketingReview,
    PlantHeadReview,
    RootCauseAnalysis,
    CorrectivePreventiveAction,
    Solution,
    Status,
    CASE 
        WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != '' THEN 'YES'
        ELSE 'NO'
    END AS HasMarketingReview,
    CASE 
        WHEN PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != '' THEN 'YES'
        ELSE 'NO'
    END AS HasPlantReview,
    CASE 
        WHEN RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != '' THEN 'YES'
        ELSE 'NO'
    END AS HasRCA,
    CASE 
        WHEN CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != '' THEN 'YES'
        ELSE 'NO'
    END AS HasCPA,
    CASE 
        WHEN Solution IS NOT NULL AND LTRIM(RTRIM(Solution)) != '' THEN 'YES'
        ELSE 'NO'
    END AS HasSolution,
    CASE 
        WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != ''
             AND PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != ''
             AND RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != ''
             AND CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != ''
             AND (Solution IS NULL OR LTRIM(RTRIM(Solution)) = '')
        THEN 'READY_FOR_GENERATION'
        ELSE 'WAITING'
    END AS ReadyStatus,
    UpdatedDate
FROM Complaints_Master
ORDER BY UpdatedDate DESC;
GO

-- Test the view
SELECT TOP 10 * FROM vw_ComplaintsReadyForSolution;
GO

PRINT 'View fixed successfully!';

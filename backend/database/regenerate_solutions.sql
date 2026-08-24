-- Regenerate solutions for all complaints that have:
-- 1. Both Marketing and Plant Head approvals set to 'approved'
-- 2. Root Cause Analysis
-- 3. Corrective Preventive Action
-- 4. No existing solution yet

-- This is a data update script - run this to update existing complaints in MSSQL
-- Note: This marks which complaints SHOULD have solutions generated.
-- The actual AI generation happens via the API endpoint.

-- First, let's see which complaints meet all criteria
SELECT 
    ComplaintID,
    MarketingReview,
    PlantHeadReview,
    RootCauseAnalysis,
    CorrectivePreventiveAction,
    Solution,
    Status
FROM Complaints_Master
WHERE 
    LOWER(RTRIM(LTRIM(MarketingReview))) = 'approved'
    AND LOWER(RTRIM(LTRIM(PlantHeadReview))) = 'approved'
    AND RootCauseAnalysis IS NOT NULL
    AND RootCauseAnalysis != ''
    AND CorrectivePreventiveAction IS NOT NULL
    AND CorrectivePreventiveAction != ''
    AND (Solution IS NULL OR Solution = '')
ORDER BY ComplaintID;

-- To mark these as needing solution generation, you can:
-- 1. Call the API endpoint: POST /api/complaints/{complaint_id}/trigger-solution
-- 2. Or run the review update endpoints with "approved" status to trigger auto-generation

-- If you want to auto-set status to 'Resolved' for these complaints (optional):
-- UPDATE Complaints_Master
-- SET Status = 'Pending_Solution_Generation'
-- WHERE 
--     LOWER(RTRIM(LTRIM(MarketingReview))) = 'approved'
--     AND LOWER(RTRIM(LTRIM(PlantHeadReview))) = 'approved'
--     AND RootCauseAnalysis IS NOT NULL
--     AND RootCauseAnalysis != ''
--     AND CorrectivePreventiveAction IS NOT NULL
--     AND CorrectivePreventiveAction != ''
--     AND (Solution IS NULL OR Solution = '');

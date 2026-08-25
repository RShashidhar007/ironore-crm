-- MSSQL Database Trigger for INSTANT Automatic Solution Generation
-- This trigger fires immediately when you edit the complaint in SSMS
-- No waiting for scheduler - solution updates in real-time

-- IMPORTANT: Run this script in MSSQL to enable instant generation on edits

-- ============================================================================
-- STEP 1: Create a stored procedure that marks complaints ready for generation
-- ============================================================================

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_MarkComplaintReadyForSolution')
    DROP PROCEDURE sp_MarkComplaintReadyForSolution;
GO

CREATE PROCEDURE sp_MarkComplaintReadyForSolution
    @ComplaintID NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @HasMarketingReview BIT = 0;
    DECLARE @HasPlantReview BIT = 0;
    DECLARE @HasRCA BIT = 0;
    DECLARE @HasCPA BIT = 0;
    
    -- Check if all conditions are met
    SELECT 
        @HasMarketingReview = CASE WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != '' THEN 1 ELSE 0 END,
        @HasPlantReview = CASE WHEN PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != '' THEN 1 ELSE 0 END,
        @HasRCA = CASE WHEN RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != '' THEN 1 ELSE 0 END,
        @HasCPA = CASE WHEN CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != '' THEN 1 ELSE 0 END
    FROM Complaints_Master
    WHERE ComplaintID = @ComplaintID;
    
    -- If all conditions are met, clear solution so scheduler will regenerate it
    IF (@HasMarketingReview = 1 AND @HasPlantReview = 1 AND @HasRCA = 1 AND @HasCPA = 1)
    BEGIN
        -- Clear the solution to trigger regeneration
        UPDATE Complaints_Master
        SET 
            Solution = NULL,
            UpdatedDate = GETDATE(),
            Status = 'Ready_For_Solution_Generation'
        WHERE 
            ComplaintID = @ComplaintID;
        
        -- Log this event
        IF EXISTS (SELECT * FROM sys.objects WHERE type = 'U' AND name = 'SolutionGenerationLog')
        BEGIN
            INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
            VALUES (@ComplaintID, GETDATE(), 'Trigger: All conditions met - marked for regeneration');
        END
        
        PRINT 'Complaint ' + @ComplaintID + ' marked for solution regeneration';
    END
END;
GO

-- ============================================================================
-- STEP 2: Create the trigger that fires on UPDATE
-- This runs INSTANTLY when you edit a row in SSMS
-- ============================================================================

IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_Complaints_TriggerSolutionGeneration')
    DROP TRIGGER TR_Complaints_TriggerSolutionGeneration;
GO

CREATE TRIGGER TR_Complaints_TriggerSolutionGeneration
ON Complaints_Master
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- For each row that was updated
    DECLARE @ComplaintID NVARCHAR(50);
    DECLARE complaint_cursor CURSOR FOR
        SELECT DISTINCT ComplaintID FROM inserted;
    
    OPEN complaint_cursor;
    FETCH NEXT FROM complaint_cursor INTO @ComplaintID;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Call the stored procedure to check and mark for regeneration
        EXEC sp_MarkComplaintReadyForSolution @ComplaintID;
        FETCH NEXT FROM complaint_cursor INTO @ComplaintID;
    END;
    
    CLOSE complaint_cursor;
    DEALLOCATE complaint_cursor;
END;
GO

-- ============================================================================
-- STEP 3: Create logging table (if it doesn't exist)
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE type = 'U' AND name = 'SolutionGenerationLog')
BEGIN
    CREATE TABLE SolutionGenerationLog (
        LogID INT PRIMARY KEY IDENTITY(1,1),
        ComplaintID NVARCHAR(50),
        TriggerTime DATETIME,
        Action NVARCHAR(500),
        CreatedAt DATETIME DEFAULT GETDATE()
    );
    PRINT 'Created SolutionGenerationLog table';
END;
GO

-- ============================================================================
-- STEP 4: View to check which complaints are ready for solution
-- ============================================================================

CREATE OR ALTER VIEW vw_ComplaintsReadyForSolution AS
SELECT 
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

-- ============================================================================
-- USAGE INSTRUCTIONS
-- ============================================================================

/*
HOW TO USE:

1. Run this entire script in MSSQL once to set up the trigger

2. Edit a complaint in SSMS:
   - Right-click Complaints_Master
   - Click "Edit Top 200 Rows"
   - Edit the columns (MarketingReview, PlantHeadReview, RootCauseAnalysis, CorrectivePreventiveAction)
   - Click "Update" or press Ctrl+Enter

3. The trigger fires INSTANTLY:
   - Checks if all 4 fields are filled
   - If yes: Clears the Solution field (sets to NULL)
   - Backend scheduler picks it up within 30 seconds and regenerates

4. Check the log:
   SELECT * FROM SolutionGenerationLog ORDER BY CreatedAt DESC;

5. Check ready complaints:
   SELECT * FROM vw_ComplaintsReadyForSolution WHERE ReadyStatus = 'READY_FOR_GENERATION';

HOW IT WORKS:

When you edit a row in SSMS and update:
  ↓
Trigger fires automatically
  ↓
Checks if all 4 fields are filled
  ↓
If yes: Clears Solution field + Marks as Ready_For_Solution_Generation
  ↓
Backend scheduler (runs every 30 sec) detects the ready complaint
  ↓
Scheduler calls AI to generate solution
  ↓
Solution is updated in database
  ↓
You can see it immediately in SSMS (refresh the view)

TIMING:
- Trigger fire: INSTANT (when you click Update in SSMS)
- Solution generation: Within 30 seconds (scheduler cycle)
- Visible in SSMS: Refresh F5 to see the updated solution

*/

-- ============================================================================
-- TEST THE TRIGGER
-- ============================================================================

-- Uncomment below to test manually:
/*
-- First, check current state
SELECT ComplaintID, MarketingReview, PlantHeadReview, RootCauseAnalysis, CorrectivePreventiveAction, Solution, Status
FROM Complaints_Master
WHERE ComplaintID = 'CMP-20260824-0001';

-- This simulates editing in SSMS - trigger will fire automatically
UPDATE Complaints_Master
SET 
    MarketingReview = 'Approved by marketing',
    PlantHeadReview = 'Plant head approved this',
    UpdatedDate = GETDATE()
WHERE ComplaintID = 'CMP-20260824-0001';

-- Check the log to see trigger fired
SELECT * FROM SolutionGenerationLog WHERE ComplaintID = 'CMP-20260824-0001' ORDER BY CreatedAt DESC;

-- Check if solution was cleared (ready for generation)
SELECT ComplaintID, Solution, Status FROM Complaints_Master WHERE ComplaintID = 'CMP-20260824-0001';

-- Solution should be regenerated within 30 seconds by the backend scheduler
-- Refresh after 30 seconds to see the new solution
*/

-- SIMPLIFIED TRIGGER - Fix for MSSQL hanging
-- This version is simpler and won't cause locks

-- Drop old trigger and stored procedure
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_Complaints_TriggerSolutionGeneration')
    DROP TRIGGER TR_Complaints_TriggerSolutionGeneration;
GO

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_MarkComplaintReadyForSolution')
    DROP PROCEDURE sp_MarkComplaintReadyForSolution;
GO

-- Create SIMPLE stored procedure (no cursor, minimal logic)
CREATE PROCEDURE sp_MarkComplaintReadyForSolution
    @ComplaintID NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Simply mark as ready if all 4 fields exist
    -- The backend will do the AI generation
    UPDATE Complaints_Master
    SET 
        Solution = NULL,
        Status = 'Ready_For_Solution_Generation',
        UpdatedDate = GETDATE()
    WHERE 
        ComplaintID = @ComplaintID
        AND MarketingReview IS NOT NULL
        AND MarketingReview != ''
        AND PlantHeadReview IS NOT NULL
        AND PlantHeadReview != ''
        AND RootCauseAnalysis IS NOT NULL
        AND RootCauseAnalysis != ''
        AND CorrectivePreventiveAction IS NOT NULL
        AND CorrectivePreventiveAction != '';
        
    -- Log the event
    IF @@ROWCOUNT > 0
    BEGIN
        INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
        VALUES (@ComplaintID, GETDATE(), 'Trigger fired: marked for regeneration');
    END
END;
GO

-- Create SIMPLE trigger (no cursor, direct call)
CREATE TRIGGER TR_Complaints_TriggerSolutionGeneration
ON Complaints_Master
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Get the first/only updated complaint ID
    DECLARE @ComplaintID NVARCHAR(50);
    SELECT TOP 1 @ComplaintID = ComplaintID FROM inserted;
    
    -- Call procedure directly (no cursor)
    IF @ComplaintID IS NOT NULL
    BEGIN
        EXEC sp_MarkComplaintReadyForSolution @ComplaintID;
    END
END;
GO

PRINT 'Simple trigger created successfully!';
GO

-- Test
SELECT * FROM SolutionGenerationLog ORDER BY CreatedAt DESC;

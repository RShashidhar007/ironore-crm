-- MSSQL Database Trigger for Automatic Solution Generation
-- This trigger automatically regenerates solutions whenever complaint data is updated
-- No API call needed - solutions update instantly when you edit the database

-- First, create a stored procedure that will be called by the trigger
-- This procedure checks all conditions and updates the solution

IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_RegenerateSolution')
    DROP PROCEDURE sp_RegenerateSolution;
GO

CREATE PROCEDURE sp_RegenerateSolution
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
    
    -- If all conditions are met, generate solution
    IF (@HasMarketingReview = 1 AND @HasPlantReview = 1 AND @HasRCA = 1 AND @HasCPA = 1)
    BEGIN
        -- Update solution status - the API will fetch and generate on next read
        -- Or you can call your API endpoint here if you have HTTP capability
        
        UPDATE Complaints_Master
        SET 
            Status = 'Ready_For_Solution_Generation',
            UpdatedDate = GETDATE()
        WHERE 
            ComplaintID = @ComplaintID 
            AND (Solution IS NULL OR LTRIM(RTRIM(Solution)) = '');
        
        -- Log this event (optional)
        IF EXISTS (SELECT * FROM sys.objects WHERE type = 'U' AND name = 'SolutionGenerationLog')
        BEGIN
            INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
            VALUES (@ComplaintID, GETDATE(), 'Auto-trigger: All conditions met');
        END
    END
END;
GO

-- Now create the trigger that fires on UPDATE
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_Complaints_AutoGenerateSolution')
    DROP TRIGGER TR_Complaints_AutoGenerateSolution;
GO

CREATE TRIGGER TR_Complaints_AutoGenerateSolution
ON Complaints_Master
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Get the list of updated complaints
    DECLARE @ComplaintID NVARCHAR(50);
    
    -- Cursor through updated complaints
    DECLARE complaint_cursor CURSOR FOR
        SELECT DISTINCT ComplaintID FROM inserted;
    
    OPEN complaint_cursor;
    FETCH NEXT FROM complaint_cursor INTO @ComplaintID;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Call the stored procedure for each updated complaint
        EXEC sp_RegenerateSolution @ComplaintID;
        
        FETCH NEXT FROM complaint_cursor INTO @ComplaintID;
    END;
    
    CLOSE complaint_cursor;
    DEALLOCATE complaint_cursor;
END;
GO

-- Optional: Create a logging table to track when solutions are triggered
IF NOT EXISTS (SELECT * FROM sys.objects WHERE type = 'U' AND name = 'SolutionGenerationLog')
BEGIN
    CREATE TABLE SolutionGenerationLog (
        LogID INT PRIMARY KEY IDENTITY(1,1),
        ComplaintID NVARCHAR(50),
        TriggerTime DATETIME,
        Action NVARCHAR(500),
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END;
GO

-- Alternative: If you have HTTP capability in MSSQL 2016+, you can make API calls
-- Uncomment below if your SQL Server supports sp_OACreate (requires enabling)
/*
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_RegenerateSolutionViaAPI')
    DROP PROCEDURE sp_RegenerateSolutionViaAPI;
GO

CREATE PROCEDURE sp_RegenerateSolutionViaAPI
    @ComplaintID NVARCHAR(50),
    @APIEndpoint NVARCHAR(MAX) = 'http://localhost:8000/api/complaints'
AS
BEGIN
    DECLARE @url NVARCHAR(MAX);
    DECLARE @response NVARCHAR(MAX);
    DECLARE @objHTTP INT;
    
    SET @url = @APIEndpoint + '/' + @ComplaintID + '/trigger-solution';
    
    BEGIN TRY
        EXEC sp_OACreate 'MSXML2.XMLHttp.6.0', @objHTTP OUT;
        EXEC sp_OAMethod @objHTTP, 'open', NULL, 'POST', @url, 'false';
        EXEC sp_OAMethod @objHTTP, 'setRequestHeader', NULL, 'Content-Type', 'application/json';
        EXEC sp_OAMethod @objHTTP, 'send', NULL, '';
        EXEC sp_OAGetProperty @objHTTP, 'responseText', @response OUT;
        EXEC sp_OADestroy @objHTTP;
        
        -- Log the API call
        INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
        VALUES (@ComplaintID, GETDATE(), 'API Call: ' + @response);
    END TRY
    BEGIN CATCH
        INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
        VALUES (@ComplaintID, GETDATE(), 'API Call Failed: ' + ERROR_MESSAGE());
    END CATCH;
END;
GO
*/

-- View to see which complaints are ready for solution generation
CREATE OR ALTER VIEW vw_ComplaintsReadyForSolution AS
SELECT 
    ComplaintID,
    CategoryType,
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
        WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != ''
             AND PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != ''
             AND RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != ''
             AND CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != ''
             AND (Solution IS NULL OR LTRIM(RTRIM(Solution)) = '')
        THEN 'READY'
        ELSE 'WAITING'
    END AS ReadyStatus
FROM Complaints_Master
ORDER BY UpdatedDate DESC;
GO

-- Example Usage:
-- After running the trigger setup, whenever you UPDATE the Complaints_Master table,
-- the trigger will automatically check conditions and mark as 'Ready_For_Solution_Generation'

-- View the status
-- SELECT * FROM vw_ComplaintsReadyForSolution;

-- Check the log of triggered solutions
-- SELECT * FROM SolutionGenerationLog ORDER BY CreatedAt DESC;

-- Test the trigger manually by updating a complaint
-- UPDATE Complaints_Master
-- SET MarketingReview = 'approved', PlantHeadReview = 'approved'
-- WHERE ComplaintID = 'CMP-20260824-0001';

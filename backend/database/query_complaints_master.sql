-- Query Complaints Master Table
-- Retrieves top 1000 records from the Complaints_Master table

SELECT TOP (1000) 
    [CID],
    [ComplaintID],
    [CategoryType],
    [ComplaintDescription],
    [RootCauseAnalysis],
    [RootCauseAnalysisDate],
    [CorrectivePreventiveAction],
    [CorrectivePreventiveActionDate],
    [MarketingReview],
    [MarketingReviewDate],
    [PlantHeadReview],
    [PlantHeadReviewDate],
    [HODReview],
    [HODReviewDate],
    [CreatedBy],
    [CreatedDate],
    [Solution],
    [PONumber],
    [DispatchDate],
    [Progress],
    [Status],
    [UpdatedBy],
    [UpdatedDate]
FROM [Customer_DB].[dbo].[Complaints_Master]

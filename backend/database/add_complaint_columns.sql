-- SQL Script to add new columns to Complaints_Master table
-- Run this in SQL Server Management Studio or Azure Data Studio

USE [Customer_DB];
GO

-- Check if columns already exist before adding them
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'PONumber')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [PONumber] NVARCHAR(100) NULL;
    PRINT 'Added PONumber column';
END
ELSE
BEGIN
    PRINT 'PONumber column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'DispatchDate')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [DispatchDate] DATE NULL;
    PRINT 'Added DispatchDate column';
END
ELSE
BEGIN
    PRINT 'DispatchDate column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'Summary')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [Summary] NVARCHAR(2000) NULL;
    PRINT 'Added Summary column';
END
ELSE
BEGIN
    PRINT 'Summary column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'Solution')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [Solution] NVARCHAR(2000) NULL;
    PRINT 'Added Solution column';
END
ELSE
BEGIN
    PRINT 'Solution column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'Progress')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [Progress] NVARCHAR(2000) NULL;
    PRINT 'Added Progress column';
END
ELSE
BEGIN
    PRINT 'Progress column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'Status')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [Status] NVARCHAR(50) NULL DEFAULT 'Under Review';
    PRINT 'Added Status column';
END
ELSE
BEGIN
    PRINT 'Status column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'UpdatedBy')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [UpdatedBy] NVARCHAR(100) NULL;
    PRINT 'Added UpdatedBy column';
END
ELSE
BEGIN
    PRINT 'UpdatedBy column already exists';
END
GO

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[Complaints_Master]') AND name = 'UpdatedDate')
BEGIN
    ALTER TABLE [dbo].[Complaints_Master]
    ADD [UpdatedDate] DATETIME NULL;
    PRINT 'Added UpdatedDate column';
END
ELSE
BEGIN
    PRINT 'UpdatedDate column already exists';
END
GO

-- Verify the changes
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Complaints_Master'
ORDER BY ORDINAL_POSITION;
GO

PRINT 'All columns added successfully!';

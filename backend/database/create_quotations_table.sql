-- Create Quotations_Master table for tracking quotation requests
-- This table stores customer quotation requests with pricing and PDF documentation

CREATE TABLE [dbo].[Quotations_Master] (
    [QuotationID] INT PRIMARY KEY IDENTITY(1,1),
    [QuotationNumber] VARCHAR(50) UNIQUE NOT NULL,  -- e.g., QT-2026-08-001
    [CID] VARCHAR(50) FOREIGN KEY REFERENCES [Customer_Detail]([CID]),
    [PID] VARCHAR(50) FOREIGN KEY REFERENCES [Product_Master]([PID]),
    [ProductName] VARCHAR(250) NOT NULL,
    [QuantityMT] DECIMAL(10,2) NOT NULL,  -- Quantity requested in Metric Tons
    [PricePerMT] DECIMAL(10,2) NOT NULL,  -- Quoted price per Metric Ton
    [TotalAmount] DECIMAL(12,2) NOT NULL,  -- QuantityMT * PricePerMT
    [ValidityDays] INT DEFAULT 7,  -- Quote validity period in days
    [Notes] TEXT,  -- Additional notes/terms
    [Status] VARCHAR(50) DEFAULT 'Generated',  -- Generated, Accepted, Rejected, Expired
    [CreatedBy] VARCHAR(100) NOT NULL,
    [CreatedDate] DATETIME NOT NULL,
    [ExpiryDate] DATETIME NOT NULL,
    [AcceptedDate] DATETIME,
    [PDFFilePath] VARCHAR(500),  -- Path to generated PDF
    [UpdatedBy] VARCHAR(100),
    [UpdatedDate] DATETIME
);

-- Create indexes for common queries
CREATE INDEX idx_quotation_cid ON [dbo].[Quotations_Master]([CID]);
CREATE INDEX idx_quotation_pid ON [dbo].[Quotations_Master]([PID]);
CREATE INDEX idx_quotation_created ON [dbo].[Quotations_Master]([CreatedDate]);
CREATE INDEX idx_quotation_status ON [dbo].[Quotations_Master]([Status]);

-- Example insert
INSERT INTO [dbo].[Quotations_Master] (
    [QuotationNumber], [CID], [PID], [ProductName], [QuantityMT], 
    [PricePerMT], [TotalAmount], [ValidityDays], [Status], 
    [CreatedBy], [CreatedDate], [ExpiryDate]
)
VALUES (
    'QT-2026-08-001',
    'CUST001',
    '13000000',
    'LOW CCS IRON ORE PELLET',
    100.00,
    5200.00,
    520000.00,
    7,
    'Generated',
    'admin',
    GETDATE(),
    DATEADD(DAY, 7, GETDATE())
);

-- Verify table creation
SELECT * FROM [dbo].[Quotations_Master];

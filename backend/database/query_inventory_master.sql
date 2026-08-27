-- Query Inventory Master Table
-- Retrieves top 1000 records from the Inventory_Master table

SELECT TOP (1000) 
    [InventoryID],
    [PID],
    [Category],
    [QuantityMT],
    [ProducedDate],
    [InitialPrice],
    [SellingPrice]
FROM [Customer_DB].[dbo].[Inventory_Master]

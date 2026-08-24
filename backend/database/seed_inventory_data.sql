-- Seed Inventory Master with sample data
-- Format: Produced entries show available stock, Sold entries track orders

INSERT INTO [dbo].[Inventory_Master] ([PID], [Category], [QuantityMT], [ProducedDate], [InitialPrice], [SellingPrice])
VALUES
-- Product 13000000
(13000000, 'Produced', 500.00, '2026-08-01', 4500.00, NULL),
(13000000, 'Sold', 150.00, '2026-08-01', 4500.00, 5200.00),

-- Product 13000001
(13000001, 'Produced', 300.00, '2026-08-03', 4300.00, NULL),
(13000001, 'Sold', 80.00, '2026-08-03', 4300.00, 5000.00),

-- Product 13000002
(13000002, 'Produced', 450.00, '2026-08-05', 8500.00, NULL),
(13000002, 'Sold', 200.00, '2026-08-05', 8500.00, 9500.00),

-- Product 13000003
(13000003, 'Produced', 300.00, '2026-08-08', 8600.00, NULL),
(13000003, 'Sold', 250.00, '2026-08-08', 8600.00, 9700.00),

-- Product 13000004
(13000004, 'Produced', 400.00, '2026-08-10', 8400.00, NULL),
(13000004, 'Sold', 125.00, '2026-08-10', 8400.00, 9400.00);

-- View available stock by product (Produced - Sold)
SELECT 
    PID,
    SUM(CASE WHEN Category = 'Produced' THEN QuantityMT ELSE 0 END) as TotalProduced,
    SUM(CASE WHEN Category = 'Sold' THEN QuantityMT ELSE 0 END) as TotalSold,
    SUM(CASE WHEN Category = 'Produced' THEN QuantityMT ELSE -QuantityMT END) as AvailableStock
FROM [dbo].[Inventory_Master]
GROUP BY PID
ORDER BY PID;

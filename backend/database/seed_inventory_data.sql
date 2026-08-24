-- Seed Inventory Master with sample data
-- Format: Produced entries show available stock, Sold entries track orders
-- 
-- PRICING NOTE: 
-- - InitialPrice: Base/cost price per Metric Ton (MT) - e.g., 4500 means 4500 INR/MT
-- - SellingPrice: Sales price per Metric Ton (MT) - e.g., 5200 means 5200 INR/MT
-- - NULL SellingPrice for Produced entries means the product hasn't been sold yet (no market price recorded)

INSERT INTO [dbo].[Inventory_Master] ([PID], [Category], [QuantityMT], [ProducedDate], [InitialPrice], [SellingPrice])
VALUES
-- Product 13000000: LOW CCS IRON ORE PELLET
-- 500 MT produced at 4500 INR/MT, 150 MT sold at 5200 INR/MT = 350 MT available
(13000000, 'Produced', 500.00, '2026-08-01', 4500, NULL),
(13000000, 'Sold', 150.00, '2026-08-01', 4500, 5200),

-- Product 13000001: Unscreened Accretion
-- 300 MT produced at 4300 INR/MT, 80 MT sold at 5000 INR/MT = 220 MT available
(13000001, 'Produced', 300.00, '2026-08-03', 4300, NULL),
(13000001, 'Sold', 80.00, '2026-08-03', 4300, 5000),

-- Product 13000002: IRON ORE PELLET FE 63
-- 450 MT produced at 8500 INR/MT, 200 MT sold at 9500 INR/MT = 250 MT available
(13000002, 'Produced', 450.00, '2026-08-05', 8500, NULL),
(13000002, 'Sold', 200.00, '2026-08-05', 8500, 9500),

-- Product 13000003: IRON ORE PELLET FE 65
-- 300 MT produced at 8600 INR/MT, 250 MT sold at 9700 INR/MT = 50 MT available
(13000003, 'Produced', 300.00, '2026-08-08', 8600, NULL),
(13000003, 'Sold', 250.00, '2026-08-08', 8600, 9700),

-- Product 13000004: Iron Ore Pellet chips 3-8 mm Fe 60-65%
-- 400 MT produced at 8400 INR/MT, 125 MT sold at 9400 INR/MT = 275 MT available
(13000004, 'Produced', 400.00, '2026-08-10', 8400, NULL),
(13000004, 'Sold', 125.00, '2026-08-10', 8400, 9400);

-- View available stock by product (Produced - Sold) with pricing
SELECT 
    im.PID,
    pm.ProductName,
    SUM(CASE WHEN im.Category = 'Produced' THEN im.QuantityMT ELSE 0 END) as TotalProducedMT,
    SUM(CASE WHEN im.Category = 'Sold' THEN im.QuantityMT ELSE 0 END) as TotalSoldMT,
    SUM(CASE WHEN im.Category = 'Produced' THEN im.QuantityMT ELSE -im.QuantityMT END) as AvailableStockMT,
    MAX(im.InitialPrice) as InitialPricePerMT,
    MAX(im.SellingPrice) as SellingPricePerMT
FROM [dbo].[Inventory_Master] im
LEFT JOIN [dbo].[Product_Master] pm ON im.PID = pm.PID
GROUP BY im.PID, pm.ProductName
ORDER BY im.PID;

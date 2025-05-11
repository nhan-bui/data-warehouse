SELECT 
    i.KichCo,
    g.Bang,
    
CASE
    WHEN i.TrongLuong >= 0 AND i.TrongLuong < 3 THEN '0-3'
    WHEN i.TrongLuong >= 3 AND i.TrongLuong < 5 THEN '3-5'
    WHEN i.TrongLuong >= 5 AND i.TrongLuong < 8 THEN '5-8'
    WHEN i.TrongLuong >= 8 THEN '8+'
    ELSE 'Unknown'
END AS WeightRange
,
    
    SUM(f.SoLuongTonKho) AS TotalInventory


FROM fact_inventory f
JOIN dim_time t ON f.MaThoiGian = t.MaThoiGian
JOIN dim_item i ON f.MaMH = i.MaMH
join dim_store s on f.MaCuaHang = s.MaCuaHang
join dim_geo g on s.MaThanhPho = g.MaThanhPho

GROUP BY i.KichCo, WeightRange, g.Bang
SELECT 
    
    
CASE
    WHEN i.TrongLuong >= 0 AND i.TrongLuong < 3 THEN '0-3'
    WHEN i.TrongLuong >= 3 AND i.TrongLuong < 5 THEN '3-5'
    WHEN i.TrongLuong >= 5 AND i.TrongLuong < 8 THEN '5-8'
    WHEN i.TrongLuong >= 8 THEN '8+'
    ELSE 'Unknown'
END AS WeightRange
,
    
    SUM(f.SoLuongBan) AS TotalQuantity,
    SUM(f.DoanhThu) AS TotalRevenue


FROM fact_sales f
JOIN dim_time t ON f.MaThoiGian = t.MaThoiGian
JOIN dim_item i ON f.MaMH = i.MaMH
JOIN dim_customer c ON f.MaKH = c.MaKH
join dim_geo g on f.MaThanhPho = g.MaThanhPho

GROUP BY t.Nam, t.Quy, c.LoaiKH, WeightRange, g.Bang
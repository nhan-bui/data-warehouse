SELECT 
    c.LoaiKH,
    i.KichCo,
    
    SUM(f.SoLuongBan) AS TotalQuantity,
    SUM(f.DoanhThu) AS TotalRevenue


FROM fact_sales f
JOIN dim_time t ON f.MaThoiGian = t.MaThoiGian
JOIN dim_item i ON f.MaMH = i.MaMH
JOIN dim_customer c ON f.MaKH = c.MaKH
join dim_geo g on f.MaThanhPho = g.MaThanhPho

GROUP BY c.LoaiKH, i.KichCo
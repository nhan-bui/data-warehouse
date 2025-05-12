SELECT 
    t.Nam,
    t.Thang,
    t.Quy,
    i.MaMH,
    g.Bang,
    s.MaCuaHang,
    s.SoDienThoai,
    i.MoTa,
    
    SUM(f.SoLuongTonKho) AS TotalInventory


FROM fact_inventory f
JOIN dim_time t ON f.MaThoiGian = t.MaThoiGian
JOIN dim_item i ON f.MaMH = i.MaMH
join dim_store s on f.MaCuaHang = s.MaCuaHang
join dim_geo g on s.MaThanhPho = g.MaThanhPho

GROUP BY t.Nam, t.Quy, t.Thang, s.MaCuaHang, i.MaMH, g.Bang
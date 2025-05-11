import pandas as pd
from sqlalchemy import create_engine, Integer, String, Date
from tqdm import tqdm
# Kết nối đến CSDL tích hợp
engine_integrated = create_engine("mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/intergrated_db")

def import_csv_to_db(csv_file, table_name, column_mapping=None, target_dtype=None):
    # Đọc dữ liệu từ CSV
    df = pd.read_csv(csv_file)

    # Đổi tên cột theo mapping (nếu có)
    if column_mapping:
        df = df.rename(columns=column_mapping)

    # Tự động chuyển các cột datetime sang Date
    datetime_keywords = ['thoi_gian', 'ngay', 'date', 'time']
    for col in df.columns:
        # Chỉ xử lý các cột có tên chứa từ khóa thời gian
        if any(keyword in col.lower() for keyword in datetime_keywords):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            except:
                continue

    # Import vào CSDL
    df.to_sql(
        name=table_name,
        con=engine_integrated,
        if_exists='append',
        index=False,
        dtype=target_dtype if target_dtype else {}
    )


column_mapping_cua_hang = {
    'ma_cua_hang': 'MaCuaHang',
    'ma_thanh_pho': 'MaThanhPho',
    'so_dien_thoai': 'SoDienThoai',
    'thoi_gian': 'ThoiDiemThanhLap'
}


target_dtype_store = {
    'MaCuaHang': Integer(),
    'MaThanhPho': Integer(),
    'SoDienThoai': String(15),
    'ThoiDiemThanhLap': Date()
}

column_mapping_mat_hang = {
    'ma_mh': 'MaMH',
    'mo_ta': 'MoTa',
    'kich_co': 'KichCo',
    'trong_luong': 'TrongLuong',
    'gia': 'Gia',
    'thoi_gian': 'ThoiDiemSanXuat'
}

from sqlalchemy import DECIMAL

target_dtype_item = {
    'MaMH': Integer(),
    'MoTa': String(100),
    'KichCo': String(20),
    'TrongLuong': DECIMAL(10, 2),
    'Gia': DECIMAL(15, 2),
    'ThoiDiemSanXuat': Date()
}


column_mapping_luu_tru = {
    'ma_cua_hang': 'MaCuaHang',
    'ma_mh': 'MaMH',
    'so_luong_trong_kho': 'SoLuongTrongKho',
    'thoi_gian': 'ThoiGianNhapHang'
}


target_dtype_stored_item = {
    'MaCuaHang': Integer(),
    'MaMH': Integer(),
    'SoLuongTrongKho': Integer(),
    'ThoiGianNhapHang': Date()
}

column_mapping_don_hang = {
    'ma_don': 'MaDon',
    'ngay_dat_hang': 'NgayDatHang',
    'ma_khach_hang': 'MaKH'
}

target_dtype_order = {
    'MaDon': Integer(),
    'NgayDatHang': Date(),
    'MaKH': Integer()
}

column_mapping_dat_hang = {
    'ma_don': 'MaDon',
    'ma_mh': 'MaMH',
    'so_luong_dat': 'SoLuongDat',
    'gia_dat': 'GiaDat',
    'thoi_gian': 'ThoiDiemDatHang'
}

target_dtype_ordered_item = {
    'MaDon': Integer(),
    'MaMH': Integer(),
    'SoLuongDat': Integer(),
    'GiaDat': DECIMAL(15, 2),
    'ThoiDiemDatHang': Date()
}


# Import cho bảng Store (Cửa hàng)
import_csv_to_db(
    csv_file='exported_data/ban_hang/cua_hang.csv',
    table_name='store',
    column_mapping=column_mapping_cua_hang,
    target_dtype=target_dtype_store
)

# Import cho bảng Item (Mặt hàng)
import_csv_to_db(
    csv_file='exported_data/ban_hang/mat_hang.csv',
    table_name='item',
    column_mapping=column_mapping_mat_hang,
    target_dtype=target_dtype_item
)

# Import cho bảng StoredItem (Lưu trữ)
import_csv_to_db(
    csv_file='exported_data/ban_hang/mat_hang_duoc_luu_tru.csv',
    table_name='stored_item',
    column_mapping=column_mapping_luu_tru,
    target_dtype=target_dtype_stored_item
)

# Import cho bảng Order (Đơn hàng)
import_csv_to_db(
    csv_file='exported_data/ban_hang/don_dat_hang.csv',
    table_name='order',
    column_mapping=column_mapping_don_hang,
    target_dtype=target_dtype_order
)

# Import cho bảng OrderedItem (Đặt hàng)
import_csv_to_db(
    csv_file='exported_data/ban_hang/mat_hang_duoc_dat.csv',
    table_name='ordered_item',
    column_mapping=column_mapping_dat_hang,
    target_dtype=target_dtype_ordered_item
)
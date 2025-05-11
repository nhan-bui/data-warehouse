from sqlalchemy import create_engine, Column, String, ForeignKey, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
Base = declarative_base()

class VanPhongDaiDien(Base):
    __tablename__ = 'van_phong_dai_dien'
    ma_thanh_pho = Column(Integer, primary_key=True)  # Chuyển sang Integer
    ten_thanh_pho = Column(String(100), nullable=False)
    dia_chi_vp = Column(String(255), nullable=False)
    bang = Column(String(50), nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

class CuaHang(Base):
    __tablename__ = 'cua_hang'
    ma_cua_hang = Column(Integer, primary_key=True)  # Chuyển sang Integer
    ma_thanh_pho = Column(Integer, ForeignKey('van_phong_dai_dien.ma_thanh_pho'), nullable=False)  # Chuyển sang Integer
    so_dien_thoai = Column(String(15), nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

    # Mối quan hệ với Văn phòng đại diện
    van_phong = relationship("VanPhongDaiDien", backref="cua_hang")

class MatHang(Base):
    __tablename__ = 'mat_hang'
    ma_mh = Column(Integer, primary_key=True)  # Chuyển sang Integer
    mo_ta = Column(String(255), nullable=False)
    kich_co = Column(String(50), nullable=False)
    trong_luong = Column(Float, nullable=False)
    gia = Column(Float, nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

class MatHangDuocLuuTru(Base):
    __tablename__ = 'mat_hang_duoc_luu_tru'
    # ma = Column(Integer, primary_key=True)
    ma_cua_hang = Column(Integer, ForeignKey('cua_hang.ma_cua_hang'), primary_key=True)  # Chuyển sang Integer
    ma_mh = Column(Integer, ForeignKey('mat_hang.ma_mh'), primary_key=True)  # Chuyển sang Integer
    so_luong_trong_kho = Column(Integer, nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

    # Mối quan hệ với Cửa hàng và Mặt hàng
    cua_hang = relationship("CuaHang", backref="mat_hang_luu_tru")
    mat_hang = relationship("MatHang", backref="luu_tru")

class DonDatHang(Base):
    __tablename__ = 'don_dat_hang'
    ma_don = Column(Integer, primary_key=True)  # Chuyển sang Integer
    ngay_dat_hang = Column(DateTime, default=datetime.utcnow)
    ma_khach_hang = Column(Integer, nullable=False)  # Giả sử mã khách hàng là số nguyên

class MatHangDuocDat(Base):
    __tablename__ = 'mat_hang_duoc_dat'
    # ma = Column(Integer, primary_key=True)
    ma_don = Column(Integer, ForeignKey('don_dat_hang.ma_don'), primary_key=True)  # Chuyển sang Integer
    ma_mh = Column(Integer, ForeignKey('mat_hang.ma_mh'), primary_key=True)  # Chuyển sang Integer
    so_luong_dat = Column(Integer, nullable=False)
    gia_dat = Column(Float, nullable=False)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

    # Mối quan hệ với Đơn đặt hàng và Mặt hàng
    don_dat_hang = relationship("DonDatHang", backref="mat_hang_dat")
    mat_hang = relationship("MatHang", backref="dat_hang")

# Cấu hình kết nối database
DATABASE_URI = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/ban_hang"

def create_database():
    # Tạo engine kết nối
    engine = create_engine(DATABASE_URI, echo=True)

    try:
        # Tạo tất cả bảng từ các model đã định nghĩa
        Base.metadata.create_all(engine)
        print("✅ Đã tạo bảng thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi tạo bảng: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    create_database()
from sqlalchemy import create_engine, Column, String, Date, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class KhachHang(Base):
    __tablename__ = 'khach_hang'

    ma_kh = Column(Integer, primary_key=True)
    ten_kh = Column(String(50), nullable=False, default="")
    ma_tp = Column(Integer)
    ngay_dat_hang_dau_tien = Column(Date)

    # Quan hệ 1-1 với các loại khách hàng
    khach_hang_du_lich = relationship("KhachHangDuLich", back_populates="khach_hang", uselist=False)
    khach_hang_buu_dien = relationship("KhachHangBuuDien", back_populates="khach_hang", uselist=False)

class KhachHangDuLich(Base):
    __tablename__ = 'khach_hang_du_lich'

    ma_kh = Column(Integer, ForeignKey('khach_hang.ma_kh'), primary_key=True)
    huong_dan_vien_du_lich = Column(String(50))
    thoi_gian = Column(Date)

    # Quan hệ ngược
    khach_hang = relationship("KhachHang", back_populates="khach_hang_du_lich")

class KhachHangBuuDien(Base):
    __tablename__ = 'khach_hang_buu_dien'

    ma_kh = Column(Integer, ForeignKey('khach_hang.ma_kh'), primary_key=True)
    dia_chi_buu_dien = Column(String(100))
    thoi_gian = Column(Date)

    # Quan hệ ngược
    khach_hang = relationship("KhachHang", back_populates="khach_hang_buu_dien")



# Cấu hình kết nối database
DATABASE_URI = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/vpdd"

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
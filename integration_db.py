from sqlalchemy import create_engine, Column, String, Date, ForeignKey, DECIMAL, Integer
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.mysql import DECIMAL

Base = declarative_base()

# ---------- Văn phòng đại diện ----------
class Customer(Base):
    __tablename__ = 'customer'

    MaKH = Column(Integer, primary_key=True)
    TenKH = Column(String(50), nullable=False)
    MaThanhPho = Column(Integer, ForeignKey('representative_office.MaThanhPho'))
    NgayDatHangDauTien = Column(Date)

    # Relationships
    tourist_info = relationship("TouristCustomer", back_populates="customer", uselist=False)
    postal_info = relationship("PostalCustomer", back_populates="customer", uselist=False)
    orders = relationship("Order", back_populates="customer")

class TouristCustomer(Base):
    __tablename__ = 'tourist_customer'

    MaKH = Column(Integer, ForeignKey('customer.MaKH'), primary_key=True)
    HuongDanVienDuLich = Column(String(50))
    ThoiDiemDuLich = Column(Date)

    customer = relationship("Customer", back_populates="tourist_info")

class PostalCustomer(Base):
    __tablename__ = 'postal_customer'

    MaKH = Column(Integer, ForeignKey('customer.MaKH'), primary_key=True)
    DiaChiBuuDien = Column(String(100))
    ThoiDiemDangKy = Column(Date)

    customer = relationship("Customer", back_populates="postal_info")

class RepresentativeOffice(Base):
    __tablename__ = 'representative_office'

    MaThanhPho = Column(Integer, primary_key=True)
    TenThanhPho = Column(String(50), nullable=False)
    DiaChiVP = Column(String(100))
    Bang = Column(String(50))
    ThoiDiemThanhLap = Column(Date)

    stores = relationship("Store", back_populates="office")

# ---------- Bán hàng ----------
class Store(Base):
    __tablename__ = 'store'

    MaCuaHang = Column(Integer, primary_key=True)
    MaThanhPho = Column(Integer, ForeignKey('representative_office.MaThanhPho'))
    SoDienThoai = Column(String(15))
    ThoiDiemThanhLap = Column(Date)

    office = relationship("RepresentativeOffice", back_populates="stores")
    stored_items = relationship("StoredItem", back_populates="store")

class Item(Base):
    __tablename__ = 'item'

    MaMH = Column(Integer, primary_key=True)
    MoTa = Column(String(100))
    KichCo = Column(String(20))
    TrongLuong = Column(DECIMAL(10, 2))
    Gia = Column(DECIMAL(15, 2))
    ThoiDiemSanXuat = Column(Date)

    stored_in = relationship("StoredItem", back_populates="item")
    ordered_in = relationship("OrderedItem", back_populates="item")

class Order(Base):
    __tablename__ = 'order'

    MaDon = Column(Integer, primary_key=True)
    NgayDatHang = Column(Date)
    MaKH = Column(Integer, ForeignKey('customer.MaKH'))

    customer = relationship("Customer", back_populates="orders")
    ordered_items = relationship("OrderedItem", back_populates="order")

# ---------- Bảng liên kết ----------
class StoredItem(Base):
    __tablename__ = 'stored_item'

    MaCuaHang = Column(Integer, ForeignKey('store.MaCuaHang'), primary_key=True)
    MaMH = Column(Integer, ForeignKey('item.MaMH'), primary_key=True)
    SoLuongTrongKho = Column(Integer)
    ThoiGianNhapHang = Column(Date)

    store = relationship("Store", back_populates="stored_items")
    item = relationship("Item", back_populates="stored_in")

class OrderedItem(Base):
    __tablename__ = 'ordered_item'

    MaDon = Column(Integer, ForeignKey('order.MaDon'), primary_key=True)
    MaMH = Column(Integer, ForeignKey('item.MaMH'), primary_key=True)
    SoLuongDat = Column(Integer)
    GiaDat = Column(DECIMAL(15, 2))
    # ThoiDiemDatHang = Column(Date)

    order = relationship("Order", back_populates="ordered_items")
    item = relationship("Item", back_populates="ordered_in")

# ---------- Tạo database ----------
def create_database():
    DATABASE_URI = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/intergrated_db"
    engine = create_engine(DATABASE_URI, echo=True)

    try:
        Base.metadata.create_all(engine)
        print("✅ Tạo bảng thành công!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        engine.dispose()

def clone_data():
    pass

if __name__ == "__main__":
    create_database()
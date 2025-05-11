import random

from faker import Faker
from customers import KhachHang, KhachHangDuLich, KhachHangBuuDien
from sales import DonDatHang, VanPhongDaiDien
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# --- Database Connection (Use the same details as your generation script) ---
DATABASE = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/vpdd"
# echo=False is usually better here unless you need to debug the SQL query
engine = create_engine(DATABASE, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker('vi_VN')
def get_all_customer_and_city_ids():
    """
    Fetches all distinct customer IDs (ma_khach_hang) from the DonDatHang table.

    Returns:
        list: A list of unique customer IDs, or an empty list if none are found or an error occurs.
    """

# --- Database Connection (Use the same details as your generation script) ---
    SALE_DATABASE = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/ban_hang"
    # echo=False is usually better here unless you need to debug the SQL query
    engine = create_engine(SALE_DATABASE, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    customer_ids = []
    city_ids = []
    try:
        print("Fetching distinct customer IDs (ma_khach_hang) from DonDatHang table...")

        # 1. Create the query: Select the ma_khach_hang column from DonDatHang
        # 2. Apply .distinct(): Ensures only unique values are returned by the database
        query = session.query(DonDatHang.ma_khach_hang).distinct()

        # 3. Execute the query and get results:
        #    - .all() would return a list of tuples: [(id1,), (id2,), ...]
        #    - .scalars().all() conveniently extracts the first element of each tuple,
        #      giving a direct list of values: [id1, id2, ...]
        customer_ids = [id[0] for id in query]
        query = session.query(VanPhongDaiDien.ma_thanh_pho).distinct()
        city_ids = [city_id[0] for city_id in query]
        print(f"Successfully fetched {len(customer_ids)} unique customer IDs.")
        print(f"Successfully fetched {len(city_ids)} unique city IDs.")
    except Exception as e:
        print(f"An error occurred while fetching customer IDs: {e}")
        # Optionally, you might want to handle the error more gracefully
        # or re-raise it depending on your application's needs.
    finally:
        # It's good practice to close the session when you're done with it.
        if session:
            session.close()
            print("Session closed.")

    return customer_ids, city_ids

def generate_khach_hang(id_list, city_ids):

    for id_kh in id_list:
        kh = KhachHang(
            ma_kh=id_kh,
            ten_kh=fake.name(),
            ma_tp=random.choice(city_ids),
            ngay_dat_hang_dau_tien=fake.date_between(start_date='-5y', end_date='today')
        )
        session.add(kh)
    session.commit()
    print(f"Đã tạo {len(id_list)} khách hàng")


def generate_khach_hang_du_lich(num_records=20):
    """Tạo dữ liệu khách hàng du lịch"""
    khach_hangs = session.query(KhachHang).all()
    selected_kh = random.sample(khach_hangs, num_records)

    for kh in selected_kh:
        khdl = KhachHangDuLich(
            ma_kh=kh.ma_kh,
            huong_dan_vien_du_lich=fake.name(),
            thoi_gian=fake.date_between(start_date=kh.ngay_dat_hang_dau_tien, end_date='today')
        )
        session.add(khdl)
    session.commit()
    print(f"Đã tạo {num_records} khách hàng du lịch")

def generate_khach_hang_buu_dien(num_records=20):
    """Tạo dữ liệu khách hàng bưu điện"""
    khach_hangs = session.query(KhachHang).all()

    selected_kh = random.sample(khach_hangs, min(num_records, len(khach_hangs)))

    for kh in selected_kh:
        khbd = KhachHangBuuDien(
            ma_kh=kh.ma_kh,
            dia_chi_buu_dien=fake.address(),
            thoi_gian=fake.date_between(start_date=kh.ngay_dat_hang_dau_tien, end_date='today')
        )
        session.add(khbd)
    session.commit()
    print(f"Đã tạo {len(selected_kh)} khách hàng bưu điện")

def clear_data():
    """Xóa toàn bộ dữ liệu trong các bảng"""
    session.query(KhachHangDuLich).delete()
    session.query(KhachHangBuuDien).delete()
    session.query(KhachHang).delete()
    session.commit()
    print("Đã xóa toàn bộ dữ liệu cũ")

if __name__ == "__main__":
    # Xóa dữ liệu cũ nếu cần
    clear_data()

    ids_kh, ids_city = get_all_customer_and_city_ids()
    generate_khach_hang(ids_kh, ids_city)
    generate_khach_hang_du_lich(3000)
    generate_khach_hang_buu_dien(4000)

    session.close()
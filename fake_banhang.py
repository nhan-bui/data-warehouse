from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
from datetime import datetime, timedelta
import logging # Import logging

# Import các lớp bảng từ file trước đó
from sales import (
    VanPhongDaiDien,
    CuaHang,
    MatHang,
    MatHangDuocLuuTru,
    DonDatHang,
    MatHangDuocDat,
)

# Configure logging to see SQL and other info
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) # Set to INFO or DEBUG

# Khởi tạo Faker
fake = Faker('vi_VN')

# Kết nối tới cơ sở dữ liệu
DATABASE_URL = "mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/ban_hang"
# Set echo=False if you don't want to see every SQL command during generation
engine = create_engine(DATABASE_URL, echo=False) # Changed echo to False for less output
Session = sessionmaker(bind=engine)
session = Session()

# Số lượng bản ghi cần tạo
NUM_VAN_PHONG = 39
NUM_CUA_HANG = 39*20
NUM_MAT_HANG = 1000
NUM_LUU_TRU = 125*NUM_CUA_HANG
NUM_DON_DAT_HANG = 10000
NUM_MAT_HANG_DAT = 500000 # Reduced for faster testing if needed

# Hàm tạo dữ liệu giả lập
def generate_fake_data():
    print("Generating Van Phong Dai Dien...")
    office_ids = set() # Use set for faster lookups
    van_phong_list = []
    attempts = 0
    max_attempts = NUM_VAN_PHONG * 5 # Avoid infinite loop if collisions are too frequent
    while len(van_phong_list) < NUM_VAN_PHONG and attempts < max_attempts:
        attempts += 1
        ma_tp = random.randint(1, 9999)
        if ma_tp not in office_ids: # Correct check for uniqueness
            van_phong = VanPhongDaiDien(
                ma_thanh_pho=ma_tp,
                ten_thanh_pho=fake.city(),
                dia_chi_vp=fake.address(),
                bang=fake.state(),
                thoi_gian=fake.date_time_between(start_date="-5y", end_date="now"),
            )
            van_phong_list.append(van_phong)
            office_ids.add(ma_tp) # Add to set
    if not van_phong_list:
         print("Error: Could not generate any VanPhongDaiDien records. Check constraints or random range.")
         return # Stop if no offices were created

    session.add_all(van_phong_list)
    session.commit()
    print(f"Added {len(van_phong_list)} Van Phong Dai Dien.")

    # Tạo Cửa hàng
    print("Generating Cua Hang...")
    cua_hang_list = []
    stored_ids = set() # Use set
    attempts = 0
    max_attempts = NUM_CUA_HANG * 5
    van_phong_ma_thanh_pho_list = [vp.ma_thanh_pho for vp in van_phong_list] # Get list of valid IDs

    while len(cua_hang_list) < NUM_CUA_HANG and attempts < max_attempts:
        attempts += 1
        ma_ch = random.randint(1, 50000)
        if ma_ch not in stored_ids: # Correct check
            # Ensure we pick a valid ma_thanh_pho from the ones we created
            ma_tp = random.choice(van_phong_ma_thanh_pho_list)
            cua_hang = CuaHang(
                ma_cua_hang=ma_ch,
                ma_thanh_pho=ma_tp,
                so_dien_thoai=fake.phone_number()[:15],
                thoi_gian=fake.date_time_between(start_date="-5y", end_date="now"),
            )
            cua_hang_list.append(cua_hang)
            stored_ids.add(ma_ch) # Add to set
    if not cua_hang_list:
         print("Error: Could not generate any CuaHang records.")
         return

    session.add_all(cua_hang_list)
    session.commit()
    print(f"Added {len(cua_hang_list)} Cua Hang.")

    # Tạo Mặt hàng
    print("Generating Mat Hang...")
    mat_hang_list = []
    items_ids = set() # Use set
    attempts = 0
    max_attempts = NUM_MAT_HANG * 5
    while len(mat_hang_list) < NUM_MAT_HANG and attempts < max_attempts:
        attempts += 1
        ma_mh_gen = random.randint(1, 999999)
        if ma_mh_gen not in items_ids: # Correct check
            mat_hang = MatHang(
                ma_mh=ma_mh_gen,
                mo_ta=fake.sentence(),
                kich_co=fake.random_element(elements=("S", "M", "L", "XL")),
                trong_luong=round(random.uniform(0.1, 10.0), 2),
                gia=round(random.uniform(10.0, 1000.0), 2),
                thoi_gian=fake.date_time_between(start_date="-5y", end_date="now"),
            )
            items_ids.add(ma_mh_gen) # Add to set
            mat_hang_list.append(mat_hang)
    if not mat_hang_list:
         print("Error: Could not generate any MatHang records.")
         return

    session.add_all(mat_hang_list)
    session.commit()
    print(f"Added {len(mat_hang_list)} Mat Hang.")

    # Tạo Mặt hàng được lưu trữ
    print("Generating Mat Hang Duoc Luu Tru...")
    luu_tru_list = []
    used_combinations_luutru = set()
    # Pre-fetch IDs to avoid accessing objects in loop repeatedly
    cua_hang_ids = [ch.ma_cua_hang for ch in cua_hang_list]
    mat_hang_ids = [mh.ma_mh for mh in mat_hang_list]

    # Check if source lists are populated
    if not cua_hang_ids or not mat_hang_ids:
        print("Error: Cannot generate MatHangDuocLuuTru because CuaHang or MatHang list is empty.")
        return

    # Calculate max possible combinations to prevent infinite loop
    max_possible_luutru = len(cua_hang_ids) * len(mat_hang_ids)
    target_num_luutru = min(NUM_LUU_TRU, max_possible_luutru) # Don't try to create more than possible
    print(f"Targeting {target_num_luutru} unique Mat Hang Duoc Luu Tru entries.")

    attempts = 0
    # Add a safety break condition
    max_attempts_luutru = target_num_luutru * 5

    while len(luu_tru_list) < target_num_luutru and attempts < max_attempts_luutru:
        attempts += 1
        ma_cua_hang = random.choice(cua_hang_ids)
        ma_mh = random.choice(mat_hang_ids)
        if (ma_cua_hang, ma_mh) not in used_combinations_luutru:
            luu_tru = MatHangDuocLuuTru(
                ma_cua_hang=ma_cua_hang,
                ma_mh=ma_mh,
                so_luong_trong_kho=random.randint(1, 100),
                thoi_gian=fake.date_time_between(start_date="-5y", end_date="now"),
            )
            luu_tru_list.append(luu_tru)
            used_combinations_luutru.add((ma_cua_hang, ma_mh))

    session.add_all(luu_tru_list)
    session.commit()
    print(f"Added {len(luu_tru_list)} Mat Hang Duoc Luu Tru.")

    # Tạo Đơn đặt hàng
    print("Generating Don Dat Hang...")
    don_dat_hang_list = []
    order_ids = set() # Use set
    attempts = 0
    max_attempts = NUM_DON_DAT_HANG * 5
    while len(don_dat_hang_list) < NUM_DON_DAT_HANG and attempts < max_attempts:
        attempts += 1
        ma_don_gen = random.randint(1, 9999999)
        if ma_don_gen not in order_ids: # Corrected logic: add if NOT present
            don_dat_hang = DonDatHang(
                ma_don=ma_don_gen,
                ngay_dat_hang=fake.date_time_between(start_date="-5y", end_date="now"),
                ma_khach_hang=random.randint(1, 9999), # Assuming customer IDs don't need prior creation
            )
            order_ids.add(ma_don_gen) # Add to set
            don_dat_hang_list.append(don_dat_hang)
    if not don_dat_hang_list:
         print("Error: Could not generate any DonDatHang records.")
         return

    session.add_all(don_dat_hang_list)
    session.commit()
    print(f"Added {len(don_dat_hang_list)} Don Dat Hang.")

    # Tạo Mặt hàng được đặt
    print("Generating Mat Hang Duoc Dat...")
    mat_hang_dat_list = []
    used_combinations_dat = set()
    # Pre-fetch IDs
    don_dat_hang_ids = [ddh.ma_don for ddh in don_dat_hang_list]
    # mat_hang_ids is already available from before

    # Check if source lists are populated
    if not don_dat_hang_ids or not mat_hang_ids:
        print("Error: Cannot generate MatHangDuocDat because DonDatHang or MatHang list is empty.")
        return

    # Calculate max possible combinations
    max_possible_dat = len(don_dat_hang_ids) * len(mat_hang_ids)
    target_num_dat = min(NUM_MAT_HANG_DAT, max_possible_dat)
    print(f"Targeting {target_num_dat} unique Mat Hang Duoc Dat entries.")

    attempts = 0
    max_attempts_dat = target_num_dat * 2 # Allow more attempts for larger sets

    # Use bulk insert for performance if NUM_MAT_HANG_DAT is large
    BATCH_SIZE = 10000 # Adjust as needed
    temp_batch = []

    while len(mat_hang_dat_list) + len(temp_batch) < target_num_dat and attempts < max_attempts_dat:
        attempts += 1
        ma_don = random.choice(don_dat_hang_ids)
        ma_mh = random.choice(mat_hang_ids)
        if (ma_don, ma_mh) not in used_combinations_dat:
            mat_hang_dat = MatHangDuocDat(
                ma_don=ma_don,
                ma_mh=ma_mh,
                so_luong_dat=random.randint(1, 10),
                gia_dat=round(random.uniform(10.0, 5000.0), 2), # Consider basing this on MatHang.gia
                thoi_gian=fake.date_time_between(start_date="-5y", end_date="now"),
            )
            temp_batch.append(mat_hang_dat.__dict__) # Prepare for bulk insert
            used_combinations_dat.add((ma_don, ma_mh))

            if len(temp_batch) >= BATCH_SIZE:
                print(f"Inserting batch of {len(temp_batch)} Mat Hang Duoc Dat...")
                session.bulk_insert_mappings(MatHangDuocDat, temp_batch)
                session.commit()
                mat_hang_dat_list.extend(temp_batch) # Keep track conceptually, list not used directly
                temp_batch = []


    # Insert any remaining items in the last batch
    if temp_batch:
        print(f"Inserting final batch of {len(temp_batch)} Mat Hang Duoc Dat...")
        session.bulk_insert_mappings(MatHangDuocDat, temp_batch)
        session.commit()
        mat_hang_dat_list.extend(temp_batch)

    print(f"Added {len(mat_hang_dat_list)} Mat Hang Duoc Dat.") # This count might be slightly off if bulk used, better count from DB if needed.

if __name__ == "__main__":
    print("Deleting existing data...")
    # Delete in reverse order of dependency
    session.query(MatHangDuocDat).delete()
    session.query(DonDatHang).delete()
    session.query(MatHangDuocLuuTru).delete()
    session.query(MatHang).delete()
    session.query(CuaHang).delete()
    session.query(VanPhongDaiDien).delete()
    session.commit()
    print("Existing data deleted.")

    # Tạo dữ liệu giả lập và chèn vào cơ sở dữ liệu
    generate_fake_data()
    print("Data generation and insertion complete!")

    session.close() # Close the session when done
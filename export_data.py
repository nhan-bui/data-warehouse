import pandas as pd
from sqlalchemy import create_engine

# Kết nối đến DB vpdd
engine_vpdd = create_engine("mysql+pymysql://nhanadmin:nhandeptrai191@localhost:3306/vpdd")

tables_vpdd = ['khach_hang', 'khach_hang_du_lich', 'khach_hang_buu_dien']

for table in tables_vpdd:
    df = pd.read_sql_table(table, engine_vpdd)
    df.to_csv(f'exported_data/vpdd/{table}.csv', index=False)
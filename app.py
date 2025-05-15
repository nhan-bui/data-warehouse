from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import clickhouse_connect
import pyarrow

client_sales = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',  # nếu chưa set mật khẩu
    database='sale_cube'
)

client_sales = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',  # nếu chưa set mật khẩu
    database='inventory_cube'
)
class SaleCube(BaseModel):
    dim_time: int
    dim_geo: int
    dim_item: int
    dim_customer: int

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/sales")
def create_item(item: SaleCube):
    dim_time = item.dim_time
    dim_item = item.dim_item
    dim_geo = item.dim_geo
    dim_customer = item.dim_customer

    table_name = f"time{dim_time}_customer{dim_customer}_item{dim_item}_geo{dim_geo}"
    result = client_sales.query_arrow(f"SELECT * FROM {table_name}").to_pandas()


    
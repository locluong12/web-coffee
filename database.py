import streamlit as st
import pyodbc
from dotenv import load_dotenv
import os 

load_dotenv()
# Cấu hình thông tin kết nối
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")

CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

def get_connection():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    return conn, cursor


def get_table_info(query):
    conn, cursor = get_connection()

    cursor.execute(f"{query}")

    # Lấy tên các cột
    columns = [column[0] for column in cursor.description]

    # Lấy dữ liệu và chuyển đổi thành list of dictionaries
    rows = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in rows]

    # In dữ liệu dưới dạng dictionaries
    print(data)

    cursor.close()
    conn.close()

    return data


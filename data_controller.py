from model.database import get_table_info, get_connection
import streamlit as st
from time import sleep
import pandas as pd
from collections import defaultdict
from datetime import datetime


def kho_data():
    query = "SELECT * FROM TonKho"
    return get_table_info(query)

def thuc_don_data():
    query = ''' 
        SELECT *
        FROM ThucDon AS td
        INNER JOIN LoaiHangHoa AS lhh ON td.MaLoaiHH = lhh.MaLoaiHH
    '''
    return get_table_info(query)

def Ton_kho_data():
    query = "SELECT * FROM TonKho"
    return get_table_info(query)

def cong_thuc_data():
    query = "SELECT * FROM CongThuc"
    return get_table_info(query)

def tat_ca_chi_tiet_hoa_don_data():
    query = '''
        SELECT *
        FROM ChiTietHoaDon AS ct
        INNER JOIN HoaDonBanHang AS hd ON ct.MaHD = hd.MaHD
        ORDER BY hd.NgayLap
    '''

    return get_table_info(query)

def tru_ton_kho(required_ingredients):
    conn, cursor = get_connection()
    try:
        for ma_nl, req_qty in required_ingredients.items():
            cursor.execute("""
                UPDATE TonKho
                SET SoLuong = SoLuong - ?
                WHERE MaNL = ?
            """, (req_qty, ma_nl))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Lỗi cập nhật database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def group_hoa_don(tat_ca_hoa_don):
    grouped = defaultdict(lambda: {
        "MaKhachHang": "",
        "NgayLap": "",
        "items": [],
        "tong_tien": 0
    })

    for row in tat_ca_hoa_don:
        ma_hd = row["MaHD"]
        grouped[ma_hd]["MaKhachHang"] = row["MaKhachHang"]
        grouped[ma_hd]["NgayLap"] = row["NgayLap"]
        grouped[ma_hd]["items"].append({
            "MaHH": row["MaHH"],
            "SoLuong": row["SoLuongBan"],
            "DonGia": row["DonGia"],
            "ThanhTien": row["ThanhTien"]
        })
        grouped[ma_hd]["tong_tien"] += row["ThanhTien"]

    # Chuyển thành list để hiển thị
    data = []
    for ma_hd, info in grouped.items():
        product_list = [
            f"{item['MaHH']}" for item in info["items"]
        ]
        don_gia_list = [
            f"{item['DonGia']:,} VND" for item in info["items"]
        ]

        thanh_tien_list = [
            f"{item['ThanhTien']:,} VND" for item in info["items"]
        ]

        quantity_list = [str(item["SoLuong"]) for item in info["items"]]

        data.append({
            "Mã hóa đơn": ma_hd,
            "Mã KH": info["MaKhachHang"],
            "NgayLap_raw": info["NgayLap"],  # giữ lại ngày dạng datetime để sort
            "Ngày lập": info["NgayLap"].strftime("%d-%m-%Y"),
            "Sản phẩm": "<br>".join(product_list),
            "Đơn giá": "<br>".join(don_gia_list),
            "Số lượng": "<br>".join(quantity_list),
            "Thành tiền": "<br>".join(thanh_tien_list),
            "Tổng tiền": f"{info['tong_tien']:,} VND"
        })

    # Sắp xếp theo Ngày lập giảm dần
    data.sort(key=lambda x: x["NgayLap_raw"], reverse=True)

    return data

def bo_loc_du_lieu(df, start_date, end_date, selected_kh, selected_nv, search_ma_hd):
   # Áp dụng bộ lọc
    df_filtered = df.copy()
    df_filtered = df_filtered[
        (df_filtered["NgayLap_raw"].dt.date >= start_date) &
        (df_filtered["NgayLap_raw"].dt.date <= end_date)
    ]
    if selected_kh != '':
        df_filtered = df_filtered[df_filtered["Mã KH"] == selected_kh]
    
    if selected_kh != '':
        df_filtered = df_filtered[df_filtered["Mã hóa đơn"] == selected_nv]

    return df_filtered

def get_next_mahd_and_id():
    conn, cursor = get_connection()

    cursor.execute("SELECT MAX(MaHD) FROM HoaDonBanHang")
    last_mahd = cursor.fetchone()[0] or "HD00000"
    new_mahd = f"HD{int(last_mahd[2:]) + 1:05d}"

    cursor.execute("SELECT MAX(ID) FROM ChiTietHoaDon")
    last_id = cursor.fetchone()[0] or 0
    next_id = last_id + 1

    cursor.close()
    conn.close()

    return new_mahd, next_id

def cap_nhap_du_lieu_hoa_don():
    # Gọi hàm để lấy mã hóa đơn mới (tăng dần theo thứ tự) và ID mới bắt đầu cho ChiTietHoaDon
    new_mahd, next_id = get_next_mahd_and_id()

    # Lấy một sản phẩm bất kỳ từ giỏ hàng (st.session_state.cart) để truy xuất thông tin khách hàng và nhân viên
    any_item = next(iter(st.session_state.cart.values()))
    ma_kh = any_item.get('MaKhachHang', None)     # Mã khách hàng (giả sử giống nhau cho toàn bộ sản phẩm trong giỏ)
         

    # Kết nối tới database và tạo cursor để thực hiện các câu lệnh SQL
    conn, cursor = get_connection()

    # Tính tổng tiền của hóa đơn bằng cách cộng tiền từng món hàng trong giỏ
    tong_tien = sum(item['DonGia'] * item['SoLuong'] for item in st.session_state.cart.values())
    # Kiểm tra khách hàng đã tồn tại chưa
    cursor.execute("SELECT COUNT(*) FROM KhachHang WHERE MaKhachHang = ?", (ma_kh,))
    khach_ton_tai = cursor.fetchone()[0]

    if khach_ton_tai == 0:
        # Nếu khách chưa tồn tại, thêm vào
        cursor.execute("INSERT INTO KhachHang (MaKhachHang) VALUES (?)", (ma_kh,))
        conn.commit()

    # Chèn dữ liệu vào bảng HoaDonBanHang
    cursor.execute(
        "INSERT INTO HoaDonBanHang (MaHD, MaKhachHang, NgayLap, TongTien) VALUES (?, ?, ?, ?)",
        (new_mahd, ma_kh, datetime.now(), tong_tien)  # datetime.now() lấy ngày giờ hiện tại làm NgayLap
    )

    # Tạo danh sách các bản ghi sẽ chèn vào bảng ChiTietHoaDon
    chi_tiet_data = []
    for item in st.session_state.cart.values():
        chi_tiet_data.append((
            next_id,                            # ID tăng dần, không trùng
            new_mahd,                           # Liên kết với hóa đơn vừa tạo
            item['MaHH'],                       # Mã hàng hóa
            item['SoLuong'],                    # Số lượng bán
            item['DonGia'],                     # Đơn giá
            item['SoLuong'] * item['DonGia']    # Thành tiền = Số lượng * Đơn giá
        ))
        next_id += 1  # Tăng ID sau mỗi bản ghi

    # Chèn nhiều dòng dữ liệu chi tiết hóa đơn vào cùng lúc để tăng tốc độ
    cursor.executemany(
        "INSERT INTO ChiTietHoaDon (ID, MaHD, MaHH, SoLuongBan, DonGia, ThanhTien) VALUES (?, ?, ?, ?, ?, ?)",
        chi_tiet_data
    )

    conn.commit()     # Lưu các thay đổi vào database
    cursor.close()    # Đóng cursor
    conn.close()      # Đóng kết nối database


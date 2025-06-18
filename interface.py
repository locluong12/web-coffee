import streamlit as st 
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from model.qr_code import generate_vietqr

from controller.data_controller import (
    kho_data, 
    thuc_don_data, 
    cong_thuc_data, 
    tat_ca_chi_tiet_hoa_don_data, 
    group_hoa_don, 
    bo_loc_du_lieu
)
from controller.interface_controller import chon_thanh_toan, show_centered_image

def setup_page():
    """
    Cấu hình trang web cơ bản:
    - Đặt tiêu đề trang, icon và layout (wide).
    """
    st.set_page_config(
        page_title="Cafe",   # Tiêu đề hiển thị trên tab trình duyệt
        page_icon="https://th.bing.com/th/id/R.283c1ca1b7db46617327cde50b2dcfbd?rik=Z7BUVWHh2nnnCw&pid=ImgRaw&r=0", # Icon trên tab
        layout="wide", # Giao diện rộng
        initial_sidebar_state="auto" # ("auto", "expanded", or "collapsed")
    )

def setup_sidebar():
    # --- Sidebar menu ---
    with st.sidebar:
        st.markdown("")
        if st.button("Kho nguyên liệu"):
            st.session_state.menu = "Kho nguyên liệu"
        if st.button("Thực đơn"):
            st.session_state.menu = "Đặt món"
        if st.button("Hoá đơn"):
            st.session_state.menu = "Hoá đơn"
        if st.button("Thống kê"):
            st.session_state.menu = "Thống kê"

def chon_kho_ton_kho():
    st.subheader("📦 Kho nguyên liệu")
    data = kho_data()

    df = pd.DataFrame(data) 

    st.table(df)

import uuid
import streamlit as st

# --- Hàm sinh mã khách hàng --- 
def sinh_ma_khach_hang(ten_khach):
    ten_khach_chuan = ten_khach.strip().title()  # Đảm bảo tên khách là chuẩn

    # Khởi tạo session_state nếu chưa có
    if "ds_ma_khach_hang" not in st.session_state:
        st.session_state.ds_ma_khach_hang = []  # Danh sách mã khách hàng đã có
    if "ten_to_ma_khach" not in st.session_state:
        st.session_state.ten_to_ma_khach = {}  # Tên khách hàng với mã tương ứng

    # Kiểm tra nếu tên khách hàng đã có mã
    if ten_khach_chuan in st.session_state.ten_to_ma_khach:
        # Nếu tên khách hàng đã có mã, trả về mã cũ
        ma_khach_hang = st.session_state.ten_to_ma_khach[ten_khach_chuan]
        st.write(f"[DEBUG] Khách hàng '{ten_khach_chuan}' đã có mã {ma_khach_hang}.")
        return ma_khach_hang

    # Nếu tên khách hàng chưa có mã, tạo mã mới theo định dạng KH00000001
    ma_moi = f"KH{len(st.session_state.ds_ma_khach_hang)+1:08d}"

    # Thêm mã mới vào danh sách mã khách hàng và gán cho tên khách
    st.session_state.ds_ma_khach_hang.append(ma_moi)
    st.session_state.ten_to_ma_khach[ten_khach_chuan] = ma_moi
    st.write(f"[DEBUG] Đã gán mã mới cho khách hàng '{ten_khach_chuan}': {ma_moi}")
    return ma_moi


# --- Hàm chọn và đặt món --- 
def chon_dat_mon():
    # Khởi tạo dữ liệu nếu chưa có
    st.session_state.setdefault("products", thuc_don_data())
    st.session_state.setdefault("cong_thuc", cong_thuc_data())
    st.session_state.setdefault("selected_category", "Cà phê")
    st.session_state.setdefault("cart", {})
    st.session_state.setdefault("customer_name", "")
    st.session_state.setdefault("ma_khach_hang", "")
    st.session_state.setdefault("ds_ma_khach_hang", [])
    st.session_state.setdefault("ten_to_ma_khach", {})
    st.session_state.setdefault("da_thanh_toan", False)

    col1, _, col2 = st.columns([1.9, 0.05, 1.05])

    # --- Cột trái: Danh mục sản phẩm --- 
    with col1:
        categories = sorted({p["TenLoaiHH"] for p in st.session_state.products})
        cols = st.columns(len(categories))
        for col, category in zip(cols, categories):
            if col.button(category, key=f"cat_{category}") :
                st.session_state.selected_category = category

        st.subheader(f"{st.session_state.selected_category}")
        filtered_products = [
            p for p in st.session_state.products
            if p["TenLoaiHH"] == st.session_state.selected_category
        ]

        if filtered_products:
            for i in range(0, len(filtered_products), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(filtered_products):
                        product = filtered_products[i + j]
                        with cols[j]:
                            show_centered_image(product["Link"])
                            st.markdown(f"**{product['TenHH'].strip()}**")
                            st.markdown(f"{product['DonGia']:,} VND")
                            if st.button("➕", key=f"add_{product['MaHH']}"):
                                st.session_state.da_thanh_toan = False
                                if product["TenHH"] in st.session_state.cart:
                                    st.session_state.cart[product["TenHH"]]["SoLuong"] += 1
                                else:
                                    st.session_state.cart[product["TenHH"]] = {
                                        "DonGia": product["DonGia"],
                                        "SoLuong": 1,
                                        "MaHH": product["MaHH"],
                                        "Link": product["Link"],
                                        "MaKhachHang": None,
                                    }
                                st.rerun()
        else:
            st.write("❌ Không có sản phẩm nào.")

    # --- Cột phải: Giỏ hàng & thanh toán --- 
    with col2:
        st.subheader("🛒 Giỏ hàng")
        st.write("---")

        customer_name = st.text_input(
            "👤 Tên khách hàng",
            placeholder="Nhập tên khách...",
            label_visibility="visible",
            value=st.session_state.get("customer_name", "")
        )

        if customer_name != st.session_state.get("customer_name", ""):
            st.session_state.customer_name = customer_name

        if st.session_state.cart:
            total_price = sum(
                item["DonGia"] * item["SoLuong"]
                for item in st.session_state.cart.values()
            )

            for item_name, details in st.session_state.cart.items():
                c1, c2, c3, c4 = st.columns([0.8, 1.15, 0.3, 0.55])
                with c1:
                    show_centered_image(details["Link"], height=80)
                with c2:
                    st.write(item_name)
                    st.caption(f'{details["DonGia"]:,} VND')
                with c3:
                    st.write(f"X{details['SoLuong']}")
                with c4:
                    st.write(f"{(details['DonGia'] * details['SoLuong']):,} VND")

            st.write("---")
            c1, _, c2 = st.columns([1.2, 0.85, 1.25])
            with c1:
                st.subheader("**Tổng tiền**")
            with c2:
                st.subheader(f"**{total_price:,} VND**")

            # Nút tạo mã QR
            if st.button("✅ Mã QR"):
                st.session_state.qr_image = generate_vietqr(total_price)
                st.image(st.session_state.qr_image, caption="📷 Quét mã QR để thanh toán qua Techcombank")

            # Nút thanh toán
            if st.button("✅ Thanh Toán"):
                if not st.session_state.customer_name.strip():
                    st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi thanh toán.")
                else:
                    ma_kh = sinh_ma_khach_hang(st.session_state.customer_name.strip())
                    st.session_state.ma_khach_hang = ma_kh

                    for item in st.session_state.cart.values():
                        item["MaKhachHang"] = ma_kh

                    # Thực hiện thanh toán
                    chon_thanh_toan()

                    st.success("✅ Thanh toán thành công!")
                    st.session_state.cart = {}
                    st.session_state.qr_image = None
                    st.session_state.da_thanh_toan = True
                    st.session_state.customer_name = ""

        elif st.session_state.get("da_thanh_toan", False):
            st.success("✅ Thanh toán thành công!")
            st.session_state.da_thanh_toan = False
        else:
            st.subheader("🛒 Giỏ hàng trống.")
            st.session_state.qr_image = None  # Reset hình ảnh mã QR khi giỏ hàng trống
# Hàm lọc dữ liệu
def bo_loc_du_lieu(df, start_date, end_date, selected_kh, search_ma_hd=""):
    # Đảm bảo Ngày không chứa NaT
    df['NgayLap_raw'] = pd.to_datetime(df['NgayLap_raw'], errors='coerce')
    df = df.dropna(subset=['NgayLap_raw'])

    # Lọc theo ngày
    df_filtered = df[(df['NgayLap_raw'] >= start_date) & (df['NgayLap_raw'] <= end_date)]
    
    # Lọc theo Mã KH
    if selected_kh:
        df_filtered = df_filtered[df_filtered['Mã KH'] == selected_kh]
    
    # Lọc theo Mã hóa đơn (nếu có)
    if search_ma_hd:
        df_filtered = df_filtered[df_filtered['Mã hóa đơn'].str.contains(search_ma_hd, na=False)]
    
    return df_filtered


# Hiển thị tất cả hóa đơn
def chon_tat_ca_hoa_don():
    st.subheader("📜 Hóa đơn")

    # Lấy dữ liệu hóa đơn (dữ liệu gốc không thay đổi)
    tat_ca_hoa_don = tat_ca_chi_tiet_hoa_don_data()  # Lấy tất cả hóa đơn

    if tat_ca_hoa_don:
        # Nhóm hóa đơn (hoặc xử lý thêm nếu cần)
        data = group_hoa_don(tat_ca_hoa_don)  # Nhóm theo cách cần thiết
        df = pd.DataFrame(data)

        # Chuyển "Ngày lập" về kiểu datetime đúng định dạng dd-mm-yyyy
        df["NgayLap_raw"] = pd.to_datetime(df["Ngày lập"], format="%d-%m-%Y", errors="coerce")

        # Bộ lọc
        with st.expander("🔍 Bộ lọc hóa đơn", expanded=True):
            col1, col2 = st.columns(2)

            # Lọc theo khoảng thời gian
            min_date = df["NgayLap_raw"].min().date()
            max_date = df["NgayLap_raw"].max().date()

            start_date = col1.date_input("Từ ngày", min_value=min_date, max_value=max_date, value=min_date)
            end_date = col2.date_input("Đến ngày", min_value=min_date, max_value=max_date, value=max_date)

            # Chuyển đổi sang datetime
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            co1, co2, co3 = st.columns(3)

            # Lọc theo Mã KH
            ma_kh_list = sorted(df["Mã KH"].dropna().unique().tolist())
            selected_kh = co1.selectbox(
                "Lọc theo Mã KH", 
                options=[""] + ma_kh_list,
                index=0,
                help="Chọn Mã KH từ danh sách để lọc."
            )

            # Lọc theo Mã hóa đơn
            ma_hd_list = sorted(df["Mã hóa đơn"].dropna().unique().tolist())
            search_ma_hd = co3.selectbox(
                "Lọc theo Mã hóa đơn",
                options=[""] + ma_hd_list,
                index=0,
                help="Chọn Mã hóa đơn để lọc."
            )

            # Áp dụng bộ lọc
            df_filtered = bo_loc_du_lieu(df, start_date, end_date, selected_kh, search_ma_hd)

        # Hiển thị kết quả
        if not df_filtered.empty:
            # Ẩn các cột không cần hiển thị
            if 'Mã NV' in df_filtered.columns:
                df_display = df_filtered.drop(columns=["Mã NV", "NgayLap_raw"])
            else:
                df_display = df_filtered.drop(columns=["NgayLap_raw"])

            # Hiển thị bảng HTML có chứa liên kết
            st.markdown(df_display.to_html(index=False, escape=False), unsafe_allow_html=True)
        else:
            st.info("Không tìm thấy hóa đơn nào theo bộ lọc.")


def chon_thong_ke():
    # Tải dữ liệu tất cả các hóa đơn chi tiết
    tat_ca_hoa_don = tat_ca_chi_tiet_hoa_don_data()

    # Hiển thị tiêu đề con cho phần thống kê
    st.subheader("📊 Thống kê doanh thu và sản phẩm bán chạy nhất")
    
    if tat_ca_hoa_don:
        hoa_don_data = []  # Danh sách lưu trữ thông tin mỗi hóa đơn để phân tích doanh thu
        product_sales = {}  # Dictionary lưu trữ số lượng bán của từng sản phẩm
        
        # Duyệt qua tất cả các hóa đơn
        for hoa_don in tat_ca_hoa_don:
            timestamp = pd.to_datetime(hoa_don['timestamp'])  # Chuyển đổi timestamp thành datetime
            day = timestamp.date()  # Lấy ngày từ timestamp
            month = timestamp.strftime("%Y-%m")  # Lấy tháng theo định dạng "YYYY-MM"
            
            # Thêm dữ liệu cho doanh thu theo ngày và tháng
            hoa_don_data.append({"Ngày": day, "Tháng": month, "Doanh thu": hoa_don['total_price']})
            
            # Duyệt qua từng sản phẩm trong hóa đơn
            for item, details in hoa_don["items"].items():
                if item not in product_sales:
                    product_sales[item] = 0  # Khởi tạo số lượng bán cho sản phẩm nếu chưa có
                product_sales[item] += details['quantity']  # Cộng dồn số lượng bán của sản phẩm
        
       

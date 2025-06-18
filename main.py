import streamlit as st
from login import login_page  # File login.py cần nằm cùng thư mục hoặc là module hợp lệ
from view.css import custom_css
from view.dashboard import dashboard
from interface import (
    chon_tat_ca_hoa_don,
    chon_dat_mon,
    chon_kho_ton_kho,
    setup_sidebar,
    setup_page
)

# 🟢 BẮT BUỘC: Gọi set_page_config đầu tiên
setup_page()

# --- Kiểm tra trạng thái đăng nhập ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- Nếu chưa đăng nhập, hiển thị trang login rồi dừng ---
if not st.session_state["authenticated"]:
    login_page()
    st.stop()

# --- Đã đăng nhập, hiển thị giao diện chính ---
# 🟢 Giao diện cơ bản
setup_sidebar()
custom_css()

# 🟢 Nút logout
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

# 🟢 Tiêu đề trang
st.markdown("<h1 style='text-align: center;'>Warehouse Inventory Management</h1>", unsafe_allow_html=True)

# --- Giao diện chính ---
if "menu" not in st.session_state:
    st.session_state.menu = "Đặt món"

if st.session_state.menu == "Đặt món":
    chon_dat_mon()

elif st.session_state.menu == "Kho nguyên liệu":
    chon_kho_ton_kho()

elif st.session_state.menu == "Hoá đơn":
    chon_tat_ca_hoa_don()

elif st.session_state.menu == "Thống kê":
    dashboard()

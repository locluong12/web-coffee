from model.database import get_connection
import streamlit as st
from controller.data_controller import tru_ton_kho, cap_nhap_du_lieu_hoa_don
from datetime import datetime
from time import sleep

def chon_thanh_toan():
    error_flag = False
    required_ingredients = {}
    
    # Xác định nguyên liệu cần thiết từ giỏ hàng
    for item, details in st.session_state.cart.items():
        mahh = details.get("MaHH")
        soluong_mua = details.get("SoLuong", 0)
        
        # Tìm công thức tương ứng với mã hàng hóa
        for cf in st.session_state.cong_thuc:
            if cf['MaHH'] == mahh:
                ma_nl = cf['MaNL']
                soluong_don_vi = cf['SoLuong']
                st.write(cf)
                st.write(soluong_mua)

                soluong_don_vi = int(soluong_don_vi)
                soluong_mua = int(soluong_mua)
                required_ingredients[ma_nl] = required_ingredients.get(ma_nl, 0) + soluong_don_vi * soluong_mua
    
    # Kiểm tra tồn kho nguyên liệu
    conn, cursor = get_connection()
    try:
        for ma_nl, soluong_can in required_ingredients.items():
            cursor.execute("SELECT TenNL, SoLuong, DonViTinh FROM TonKho WHERE MaNL = ?", (ma_nl,))
            nl = cursor.fetchone()
            
            if not nl:
                st.error(f"❌ Không tìm thấy nguyên liệu mã: {ma_nl} trong kho.")
                error_flag = True
                continue
                
            ten_nl, soluong_kho, don_vi = nl
            if soluong_can > soluong_kho:
                st.error(f"❌ Không đủ nguyên liệu: {ten_nl}. Cần {soluong_can} {don_vi}, còn {soluong_kho} {don_vi}.")
                error_flag = True
    except Exception as e:
        st.error(f"Lỗi kiểm tra tồn kho: {e}")
        error_flag = True
    finally:
        cursor.close()
        conn.close()
    
    # Nếu đủ nguyên liệu, tiến hành thanh toán
    if not error_flag:
        if tru_ton_kho(required_ingredients):
            cap_nhap_du_lieu_hoa_don()
            st.session_state.da_thanh_toan = True
            
            st.session_state.cart = {}
            st.session_state.qr_image = None
            st.rerun()

def show_centered_image(url, height: str = '100'):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src="{url}" style="height: {height}px;" />
        </div>
        """,
        unsafe_allow_html=True
    )
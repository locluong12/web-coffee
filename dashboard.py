import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards

from controller.dashboard_controller import (
    kho_data,    
    hoa_don_data,
    thuc_don_data, 
    khach_hang_data, 
    chi_tiet_hoa_don_data
)

# --- Hàm Sidebar ---
def add_filter_sidebar():
    """Tạo sidebar và quản lý trạng thái bộ lọc."""
    st.subheader("⚙️ Bộ lọc")

    today = datetime.now().date()
    # Lấy giá trị mặc định hoặc giá trị đã lưu trong session state
    default_start = st.session_state.get('date_range_start', today - timedelta(days=30))
    default_end = st.session_state.get('date_range_end', today)
    default_nhan_vien = st.session_state.get('selected_nhan_vien', ["Tất cả"])
    default_loai_hh = st.session_state.get('selected_loai_hh', ["Tất cả"])
    default_loai_kh = st.session_state.get('selected_loai_kh', ["Tất cả"])


    # --- Bộ lọc thời gian ---
    with st.expander("🗓️ Thời gian", expanded=True):
        date_range_tuple = st.date_input(
            "Chọn khoảng thời gian",
            value=(default_start, default_end),
            min_value=datetime(2020, 1, 1).date(), # Giới hạn ngày bắt đầu tối thiểu
            max_value=today,
            key='date_selector' # Key để truy cập giá trị nếu cần
        )

        # Nút tắt - Cập nhật trực tiếp session state và rerun
        st.markdown("**Hoặc trong:**")
        cols_time = st.columns(2)
        if cols_time[0].button("Hôm nay", use_container_width=True):
            st.session_state['date_range_start'] = today
            st.session_state['date_range_end'] = today
            st.rerun()
        if cols_time[1].button("7 ngày", use_container_width=True):
            st.session_state['date_range_start'] = today - timedelta(days=7)
            st.session_state['date_range_end'] = today
            st.rerun()
        cols_time2 = st.columns(2)
        if cols_time2[0].button("30 ngày", use_container_width=True):
            st.session_state['date_range_start'] = today - timedelta(days=30)
            st.session_state['date_range_end'] = today
            st.rerun()
        if cols_time2[1].button("Năm nay", use_container_width=True):
            st.session_state['date_range_start'] = datetime(today.year, 1, 1).date()
            st.session_state['date_range_end'] = today
            st.rerun()

        # Lưu giá trị từ date_input vào state khi thay đổi (nếu không dùng nút tắt)
        # Cần nút "Áp dụng" nếu muốn xác nhận thay đổi từ date_input
        if 'date_selector' in st.session_state:
             current_start, current_end = st.session_state['date_selector']
             # Chỉ cập nhật nếu khác giá trị đang lưu để tránh rerun không cần thiết khi dùng nút tắt
             if current_start != st.session_state.get('date_range_start') or current_end != st.session_state.get('date_range_end'):
                 st.session_state['pending_date_range_start'] = current_start
                 st.session_state['pending_date_range_end'] = current_end


    # --- Bộ lọc khác ---
    selected_nhan_vien_current = default_nhan_vien
    selected_loai_hh_current = default_loai_hh
    selected_loai_kh_current = default_loai_kh

    

    with st.expander("🏷️ Loại hàng hóa", expanded=False):
        try:
            df_thuc_don = pd.DataFrame(thuc_don_data())
            if not df_thuc_don.empty and 'TenLoaiHH' in df_thuc_don.columns:
                loai_hh_options = ["Tất cả"] + sorted(df_thuc_don["TenLoaiHH"].unique().tolist())
                selected_loai_hh_current = st.multiselect("Chọn loại hàng hóa", loai_hh_options, default=default_loai_hh, key='ms_loaihh')
            else:
                st.warning("Không có dữ liệu loại hàng hóa.")
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu loại hàng hóa: {e}")

    with st.expander("👥 Loại khách hàng", expanded=False):
        try:
            df_khach_hang = pd.DataFrame(khach_hang_data())
            if not df_khach_hang.empty and 'TenLoaiKH' in df_khach_hang.columns:
                # Đảm bảo xử lý NaN thành 'Chưa phân loại' hoặc loại bỏ nếu cần
                df_khach_hang['TenLoaiKH'] = df_khach_hang['TenLoaiKH'].fillna('Chưa phân loại')
                loai_kh_options = ["Tất cả"] + sorted(df_khach_hang["TenLoaiKH"].unique().tolist())
                selected_loai_kh_current = st.multiselect("Chọn loại khách hàng", loai_kh_options, default=default_loai_kh, key='ms_loaikh')
            else:
                st.warning("Không có dữ liệu loại khách hàng.")
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu loại khách hàng: {e}")

    # --- Nút Áp dụng và Xóa ---
    col_apply, col_clear = st.columns(2)

    apply_pressed = col_apply.button("✅ Áp dụng", type="primary", use_container_width=True)
    clear_pressed = col_clear.button("❌ Xóa", use_container_width=True)

    if apply_pressed:
        # Lưu các giá trị đang chờ (nếu có) hoặc giá trị hiện tại của multiselect
        st.session_state['date_range_start'] = st.session_state.get('pending_date_range_start', default_start)
        st.session_state['date_range_end'] = st.session_state.get('pending_date_range_end', default_end)
        st.session_state['selected_nhan_vien'] = selected_nhan_vien_current
        st.session_state['selected_loai_hh'] = selected_loai_hh_current
        st.session_state['selected_loai_kh'] = selected_loai_kh_current
        # Xóa giá trị pending sau khi áp dụng
        if 'pending_date_range_start' in st.session_state: del st.session_state['pending_date_range_start']
        if 'pending_date_range_end' in st.session_state: del st.session_state['pending_date_range_end']
        st.success("Đã áp dụng bộ lọc!")
        st.rerun() # Rerun để dashboard cập nhật

    if clear_pressed:
        keys_to_delete = ['date_range_start', 'date_range_end',
                          'selected_nhan_vien', 'selected_loai_hh', 'selected_loai_kh',
                          'pending_date_range_start', 'pending_date_range_end']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.info("Đã xóa tất cả bộ lọc!")
        st.rerun() # Rerun để reset về mặc định

    # Trả về các giá trị bộ lọc đang được áp dụng từ session_state
    filters = {
        'date_range': (
            st.session_state.get('date_range_start', today - timedelta(days=30)),
            st.session_state.get('date_range_end', today)
        ),
        'selected_nhan_vien': st.session_state.get('selected_nhan_vien', ["Tất cả"]),
        'selected_loai_hh': st.session_state.get('selected_loai_hh', ["Tất cả"]),
        'selected_loai_kh': st.session_state.get('selected_loai_kh', ["Tất cả"])
    }
    return filters

# --- Hàm Dashboard Chính ---
def dashboard():
    col1, col2 = st.columns([5, 1])
    with col2:
        # Thêm sidebar bộ lọc và lấy giá trị lọc đã áp dụng
        filters = add_filter_sidebar()

    with col1:
        st.subheader("📊 Tổng quan hoạt động bán hàng")

        # Sử dụng các bộ lọc đã chọn từ session_state
        start_date, end_date = filters['date_range']
        selected_nhan_vien = filters['selected_nhan_vien']
        selected_loai_hh = filters['selected_loai_hh']
        selected_loai_kh = filters['selected_loai_kh']

        # Hiển thị thông tin bộ lọc đang áp dụng
        filter_info = f"Dữ liệu từ **{start_date.strftime('%d/%m/%Y')}** đến **{end_date.strftime('%d/%m/%Y')}**"
        active_filters = []
        if selected_nhan_vien != ["Tất cả"]: active_filters.append(f"NV: {', '.join(selected_nhan_vien)}")
        if selected_loai_hh != ["Tất cả"]: active_filters.append(f"Loại HH: {', '.join(selected_loai_hh)}")
        if selected_loai_kh != ["Tất cả"]: active_filters.append(f"Loại KH: {', '.join(selected_loai_kh)}")

        if active_filters:
            filter_info += " | Lọc theo: " + " | ".join(active_filters)
        st.info(filter_info)

        # --- Tải và chuẩn bị dữ liệu ---
        try:
            # Tải dữ liệu gốc
            df_hoa_don_raw = pd.DataFrame(hoa_don_data())
            df_chi_tiet_raw = pd.DataFrame(chi_tiet_hoa_don_data())
            df_thuc_don_raw = pd.DataFrame(thuc_don_data()) # Đã có TenLoaiHH
            df_khach_hang_raw = pd.DataFrame(khach_hang_data()) # Đã có TenLoaiKH
            df_kho_raw = pd.DataFrame(kho_data())

            # Kiểm tra dữ liệu hóa đơn cơ bản
            if df_hoa_don_raw.empty:
                st.warning("Không có dữ liệu hóa đơn để hiển thị.")
                return # Dừng thực thi nếu không có hóa đơn

            # --- Chuyển đổi kiểu dữ liệu quan trọng ---
            df_hoa_don_raw['NgayLap'] = pd.to_datetime(df_hoa_don_raw['NgayLap']).dt.date
            df_hoa_don_raw['TongTien'] = pd.to_numeric(df_hoa_don_raw['TongTien'], errors='coerce').fillna(0)
            if not df_chi_tiet_raw.empty:
                df_chi_tiet_raw['ThanhTien'] = pd.to_numeric(df_chi_tiet_raw['ThanhTien'], errors='coerce').fillna(0)
                df_chi_tiet_raw['SoLuongBan'] = pd.to_numeric(df_chi_tiet_raw['SoLuongBan'], errors='coerce').fillna(0)

            # --- Áp dụng bộ lọc ---
            # Bắt đầu với bản sao của dữ liệu gốc
            df_hoa_don_filtered = df_hoa_don_raw.copy()

            # Chuyển đổi cột 'NgayLap' sang kiểu datetime, xử lý lỗi nếu có
            df_hoa_don_filtered["NgayLap"] = pd.to_datetime(df_hoa_don_filtered["NgayLap"], errors='raise')

            # Chuyển đổi start_date và end_date sang kiểu datetime nếu cần
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            # Tạo mask lọc theo ngày
            mask_date = (df_hoa_don_filtered['NgayLap'] >= start_date) & (df_hoa_don_filtered['NgayLap'] <= end_date)
            df_hoa_don_filtered = df_hoa_don_filtered[mask_date]

            # Kiểm tra nếu còn dữ liệu sau lọc ngày
            if df_hoa_don_filtered.empty:
                st.warning(f"Không có dữ liệu hóa đơn trong khoảng thời gian đã chọn.")
                return

            

            # 3. Lọc theo loại khách hàng (trên df_hoa_don_filtered)
            if selected_loai_kh != ["Tất cả"]:
                # Dữ liệu hoa_don_data đã join sẵn TenLoaiKH (đã được chuẩn hóa NaN thành 'Chưa phân loại')
                if 'TenLoaiKH' in df_hoa_don_filtered.columns:
                    df_hoa_don_filtered['TenLoaiKH'] = df_hoa_don_filtered['TenLoaiKH'].fillna('Chưa phân loại')
                    df_hoa_don_filtered = df_hoa_don_filtered[df_hoa_don_filtered['TenLoaiKH'].isin(selected_loai_kh)]
                else:
                    st.error("Thiếu cột 'TenLoaiKH' trong dữ liệu hóa đơn để lọc.")


            # 4. Lọc theo loại hàng hóa (ảnh hưởng đến hóa đơn nào được giữ lại)
            if selected_loai_hh != ["Tất cả"]:
                if not df_chi_tiet_raw.empty and 'MaHH' in df_chi_tiet_raw.columns and 'MaHD' in df_chi_tiet_raw.columns and not df_thuc_don_raw.empty and 'MaHH' in df_thuc_don_raw.columns and 'TenLoaiHH' in df_thuc_don_raw.columns:
                    # Lấy MaHH tương ứng với TenLoaiHH đã chọn
                    selected_mahh = df_thuc_don_raw[df_thuc_don_raw['TenLoaiHH'].isin(selected_loai_hh)]['MaHH'].unique()
                    # Lấy MaHD chứa các MaHH này từ chi tiết hóa đơn gốc
                    hd_ids_contain_selected_hh = df_chi_tiet_raw[df_chi_tiet_raw['MaHH'].isin(selected_mahh)]['MaHD'].unique()
                    # Lọc df_hoa_don_filtered để chỉ giữ lại các hóa đơn thỏa mãn
                    df_hoa_don_filtered = df_hoa_don_filtered[df_hoa_don_filtered['MaHD'].isin(hd_ids_contain_selected_hh)]
                else:
                    st.error("Thiếu dữ liệu hoặc cột cần thiết (Chi tiết HĐ, Thực đơn) để lọc theo Loại hàng hóa.")


            # --- Tạo df_merged_final SAU KHI đã lọc df_hoa_don_filtered ---
            # df_merged_final chỉ chứa các chi tiết thuộc các hóa đơn đã được lọc hoàn chỉnh
            if not df_chi_tiet_raw.empty and not df_hoa_don_filtered.empty:
                df_merged_final = pd.merge(
                    df_chi_tiet_raw,
                    df_hoa_don_filtered[['MaHD']], # Chỉ cần merge theo MaHD của các hóa đơn đã lọc
                    on='MaHD',
                    how='inner' # Chỉ giữ lại chi tiết của hóa đơn đã lọc
                )
                # Merge thêm thông tin cần thiết từ df_thuc_don_raw nếu chưa có trong df_chi_tiet_raw
                if 'TenHH' not in df_merged_final.columns or 'TenLoaiHH' not in df_merged_final.columns:
                    df_merged_final = pd.merge(df_merged_final, df_thuc_don_raw[['MaHH', 'TenHH', 'TenLoaiHH']], on='MaHH', how='left')
            else:
                df_merged_final = pd.DataFrame() # Tạo DataFrame rỗng nếu không có dữ liệu

            # Kiểm tra lần cuối nếu df_hoa_don_filtered còn dữ liệu sau tất cả bộ lọc
            if df_hoa_don_filtered.empty:
                st.warning("Không có dữ liệu phù hợp với tất cả các bộ lọc đã chọn.")
                return

            # --- Tính toán KPIs ---
            total_revenue = df_hoa_don_filtered['TongTien'].sum()
            total_orders = len(df_hoa_don_filtered)
            # Đếm khách hàng duy nhất từ hóa đơn đã lọc, loại bỏ khách lẻ nếu có mã KH null/rỗng
            unique_customers = df_hoa_don_filtered['MaKhachHang'].nunique() if 'MaKhachHang' in df_hoa_don_filtered.columns else 0


            # Tìm sản phẩm bán chạy nhất (dựa trên df_merged_final)
            best_product = "Không có dữ liệu"
            if not df_merged_final.empty and 'SoLuongBan' in df_merged_final.columns and 'TenHH' in df_merged_final.columns:
                product_sales = df_merged_final.groupby(['MaHH', 'TenHH'])['SoLuongBan'].sum().reset_index()
                if not product_sales.empty:
                    best_selling_item = product_sales.loc[product_sales['SoLuongBan'].idxmax()]
                    best_product = f"{best_selling_item['TenHH']} ({int(best_selling_item['SoLuongBan'])} SP)"


            # --- HÀNG 1: KPI Cards ---
            kpi_cols = st.columns(4)
            kpi_cols[0].metric("Tổng doanh thu", f"{total_revenue:,.0f} đ")
            kpi_cols[1].metric("Số hóa đơn", f"{total_orders}")
            kpi_cols[2].metric("Số khách hàng", f"{unique_customers}")
            kpi_cols[3].metric("SP bán chạy nhất", best_product)
            style_metric_cards(border_left_color="#1976D2") # Thêm style cho đẹp
            
            import plotly.graph_objects as go
            import plotly.express as px
            

            # Giả sử bạn đã xử lý dữ liệu như trước
            df_hoa_don_filtered['NgayLap'] = pd.to_datetime(df_hoa_don_filtered['NgayLap']).dt.date

            daily_revenue = df_hoa_don_filtered.groupby('NgayLap').agg(
                DoanhThu=('TongTien', 'sum')
            ).reset_index()

            if 'df_merged_final' in locals() and not df_merged_final.empty:

                # Đổi tên các cột để đồng bộ hóa dữ liệu
                df_temp = df_merged_final.rename(columns={'Sản phẩm': 'MaHH', 'Số lượng': 'SoLuongBan'})

               # ===================== BIỂU ĐỒ 1: Doanh thu theo ngày =====================
            if 'daily_revenue' in locals() and not daily_revenue.empty:
                # Lọc những ngày có doanh thu khác 0
                daily_revenue = daily_revenue[daily_revenue['DoanhThu'] > 0]

                if not daily_revenue.empty:
                    fig_revenue_day = go.Figure()

                    fig_revenue_day.add_trace(go.Bar(
                        x=daily_revenue['NgayLap'],
                        y=daily_revenue['DoanhThu'],
                        marker=dict(color='#023468'),
                        hovertemplate='<b>Ngày:</b> %{x|%d/%m/%Y}<br><b>Doanh thu:</b> %{y:,.0f} đ<extra></extra>',
                    ))

                    fig_revenue_day.update_layout(
                        title={
                            'text': 'Doanh thu bán hàng theo ngày',
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        title_font=dict(size=20, color='black', family='Arial'),
                        xaxis=dict(
                            title='Ngày',
                            tickformat='%d/%m/%Y',
                            tickangle=45,
                            type='category',  # Đảm bảo hiển thị toàn bộ các ngày theo thứ tự
                            tickmode='linear',
                            tickfont=dict(size=10),
                        ),
                        yaxis=dict(title='Doanh thu (VNĐ)', tickformat=',.0f'),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black', family='Arial'),
                        height=500,
                        bargap=0.6,
                        showlegend=False
                    )

                    st.plotly_chart(fig_revenue_day, use_container_width=True)
                else:
                    st.info("Không có doanh thu nào để hiển thị.")


                      
                # ===================== CHIA GIAO DIỆN LÀM 2 CỘT NGANG =====================
                col1, spacer, col2 = st.columns([1, 0.1, 1])  # Cột giữa để tạo khoảng cách

                # Tạo 2 cột ngang
            col1, col2 = st.columns(2)

            # ===================== BIỂU ĐỒ 1: TOP 10 sản phẩm bán chạy =====================
            with col1:
                tenhh_col = 'TenHH_x' if 'TenHH_x' in df_temp.columns else 'TenHH_y' if 'TenHH_y' in df_temp.columns else None
                if tenhh_col and {'SoLuongBan', tenhh_col}.issubset(df_temp.columns):
                    top10 = df_temp.groupby(tenhh_col)['SoLuongBan'].sum().reset_index()
                    top10 = top10.sort_values(by='SoLuongBan', ascending=False).head(10)

                    fig_top10 = px.bar(
                        top10.sort_values('SoLuongBan'),
                        x='SoLuongBan',
                        y=tenhh_col,
                        orientation='h',
                        text='SoLuongBan',
                        labels={tenhh_col: 'Tên hàng hóa', 'SoLuongBan': 'Số lượng bán'},
                        height=500,  # ✅ Chiều cao bằng với pie chart
                        color_discrete_sequence=['#023468']
                    )

                    fig_top10.update_traces(
                        texttemplate='%{text}',
                        textposition='outside',
                        marker=dict(line=dict(color='black', width=1)),
                        opacity=0.9
                    )

                    fig_top10.update_layout(
                        title={
                            'text': 'TOP 10 SẢN PHẨM BÁN CHẠY NHẤT',
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        title_font=dict(size=18, color='black', family='Arial'),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='black', family='Arial', size=10),
                        showlegend=False,
                        margin=dict(t=60, b=30, l=30, r=30)  # ✅ Khoảng cách đều
                    )

                    st.plotly_chart(fig_top10, use_container_width=True)
                else:
                    st.info("Không có dữ liệu để hiển thị biểu đồ.")

            # ===================== BIỂU ĐỒ 2: Doanh thu theo loại hàng hóa =====================
            with col2:
                if {'TenLoaiHH', 'ThanhTien'}.issubset(df_merged_final.columns):
                    df_temp_doanhthu = df_merged_final[['TenLoaiHH', 'ThanhTien']]
                    doanh_thu_loai = df_temp_doanhthu.groupby('TenLoaiHH')['ThanhTien'].sum().reset_index()
                    doanh_thu_loai = doanh_thu_loai.sort_values(by='ThanhTien', ascending=False)

                    fig_pie = px.pie(
                        doanh_thu_loai,
                        names='TenLoaiHH',
                        values='ThanhTien',
                        height=500,  # ✅ Chiều cao bằng bar chart
                        color_discrete_sequence=px.colors.sequential.Blues[::-1]
                    )

                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                    )

                    fig_pie.update_layout(
                        title={
                            'text': 'DOANH THU BÁN HÀNG THEO LOẠI HÀNG HOÁ',
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        title_font=dict(size=18, color='black', family='Arial'),
                        font=dict(color='black', family='Arial', size=10),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        showlegend=True,
                        margin=dict(t=60, b=30, l=30, r=30)  # ✅ Khoảng cách đều
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Không có đủ dữ liệu để hiển thị doanh thu theo loại hàng hóa.")




            import plotly.express as px

            # Giả sử df_kho_raw đã được load trước đó
            if not df_kho_raw.empty:
                st.markdown(
                    "<h3 style='text-align: center; color: Black; font-weight: bold;'>BIỂU ĐỒ TIÊU THỤ VÀ TỒN KHO NGUYÊN LIỆU ĐÃ BÁN</h3>",
                    unsafe_allow_html=True
                )

                # Tính toán
                stock_items = df_kho_raw[['MaNL', 'TenNL', 'SoLuongBanDau', 'SoLuong', 'DonViTinh']].copy()
                stock_items['SoLuongBanDau'] = pd.to_numeric(stock_items['SoLuongBanDau'], errors='coerce').fillna(0)
                stock_items['SoLuong'] = pd.to_numeric(stock_items['SoLuong'], errors='coerce').fillna(0)
                stock_items['TieuThu'] = stock_items['SoLuongBanDau'] - stock_items['SoLuong']
                stock_items_sold = stock_items[stock_items['TieuThu'] > 0]

                if not stock_items_sold.empty:
                    # Tìm nguyên liệu có lượng tiêu thụ và tồn kho lớn nhất và nhỏ nhất
                    min_tieuthu = stock_items_sold['TieuThu'].min()
                    min_tonkho = stock_items_sold['SoLuong'].min()

                    # Lấy danh sách màu sắc từ px.colors.sequential.Blues
                    color_scale = px.colors.sequential.Blues[::-1]
                    num_colors = len(color_scale)

                    # Biểu đồ 1: Tiêu thụ
                    fig_consumption = px.bar(
                        stock_items_sold,
                        x='TieuThu',
                        y='TenNL',
                        orientation='h',
                        text=stock_items_sold.apply(lambda row: f"{row['TieuThu']:.0f} {row['DonViTinh']}", axis=1),
                        color='TieuThu',
                        color_continuous_scale=color_scale,
                        height=500,  # Tăng chiều cao biểu đồ
                        labels={'TieuThu': 'Lượng tiêu thụ', 'TenNL': 'Nguyên liệu'},
                        template='plotly_white'
                    )

                    # Thay đổi màu thanh có lượng tiêu thụ nhỏ nhất thành màu xanh lá
                    fig_consumption.data[0].marker.color = [
                        'green' if x == min_tieuthu else color_scale[min(int((x / stock_items_sold['TieuThu'].max()) * (num_colors - 1)), num_colors - 1)]
                        for x in stock_items_sold['TieuThu']
                    ]

                    # Đảm bảo văn bản nằm ngoài thanh để hiển thị đầy đủ
                    fig_consumption.update_traces(textposition='outside', textangle=0)

                    # Tăng kích thước và các margin để văn bản có đủ không gian
                    fig_consumption.update_layout(
                        yaxis_title=None,
                        xaxis_title='Lượng tiêu thụ',
                        coloraxis_showscale=False,
                        margin=dict(l=10, r=10, t=30, b=50),
                        bargap=0.1,  # Giảm khoảng cách giữa các thanh để chúng dài hơn
                        showlegend=False,  # Tắt legend nếu không cần thiết
                        autosize=True,  # Tự động điều chỉnh kích thước biểu đồ
                        xaxis=dict(tickangle=45),  # Quay nhãn trục x nếu cần thiết
                    )

                    # Biểu đồ 2: Tồn kho
                    fig_stock = px.bar(
                        stock_items_sold,
                        x='SoLuong',
                        y='TenNL',
                        orientation='h',
                        text=stock_items_sold.apply(lambda row: f"{row['SoLuong']:.0f} {row['DonViTinh']}", axis=1),
                        color='SoLuong',
                        color_continuous_scale=color_scale,
                        height=500,  # Tăng chiều cao biểu đồ
                        labels={'SoLuong': 'Số lượng tồn', 'TenNL': 'Nguyên liệu'},
                        template='plotly_white'
                    )

                    # Thay đổi màu thanh có số lượng tồn kho nhỏ nhất thành màu xanh lá
                    fig_stock.data[0].marker.color = [
                        'green' if x == min_tonkho else color_scale[min(int((x / stock_items_sold['SoLuong'].max()) * (num_colors - 1)), num_colors - 1)]
                        for x in stock_items_sold['SoLuong']
                    ]

                    # Đảm bảo văn bản nằm ngoài thanh để hiển thị đầy đủ
                    fig_stock.update_traces(textposition='outside', textangle=0)

                    # Tăng chiều rộng các cột và giảm khoảng cách giữa các cột
                    fig_stock.update_layout(
                        yaxis_title=None,
                        xaxis_title='Số lượng tồn',
                        coloraxis_showscale=False,
                        margin=dict(l=10, r=10, t=30, b=50),
                        bargap=0.1,  # Giảm khoảng cách giữa các thanh để chúng dài hơn
                        bargroupgap=0.1,  # Tạo khoảng cách nhỏ giữa các nhóm cột
                        showlegend=False,
                        autosize=True,  # Tự động điều chỉnh kích thước biểu đồ
                        xaxis=dict(tickangle=45),  # Quay nhãn trục x nếu cần thiết
                    )

                    # Hiển thị biểu đồ tiêu thụ
                    st.markdown("<h4 style='text-align: center; color: black; font-weight: bold;'>Số lượng tiêu thụ</h4>", unsafe_allow_html=True)
                    st.plotly_chart(fig_consumption, use_container_width=True)

                    # Hiển thị biểu đồ tồn kho
                    st.markdown("<h4 style='text-align: center; color: black; font-weight: bold;'>Số lượng tồn kho</h4>", unsafe_allow_html=True)
                    st.plotly_chart(fig_stock, use_container_width=True)

                else:
                    st.info("Không có nguyên liệu đã được bán.")
            else:
                st.info("Không có dữ liệu nguyên liệu.")

            # --- HÀNG 6: Quản lý kho ---
            
            if not df_kho_raw.empty:
                

                # Cảnh báo nguyên liệu sắp hết
                st.markdown("##### ⚠️ Cảnh báo Nguyên liệu sắp hết (<= 10 đơn vị)")
                low_stock_threshold = 10
                low_stock = df_kho_raw[pd.to_numeric(df_kho_raw['SoLuong'], errors='coerce').fillna(0) <= low_stock_threshold].copy()

                if not low_stock.empty:
                    low_stock = low_stock.sort_values('SoLuong')
                    low_stock_display = low_stock[['MaNL', 'TenNL', 'SoLuong', 'DonViTinh']]
                    low_stock_display.columns = ['Mã NL', 'Tên nguyên liệu', 'Số lượng tồn', 'Đơn vị']
                    st.dataframe(low_stock_display, use_container_width=True, hide_index=True)
                else:
                    st.success(f"✅ Không có nguyên liệu nào có số lượng tồn từ {low_stock_threshold} trở xuống.")
            else:
                st.info("Không có dữ liệu kho để hiển thị.")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình xử lý hoặc hiển thị dashboard: {str(e)}")
            st.exception(e) # In chi tiết lỗi ra console/log nếu cần debug
            st.info("Vui lòng kiểm tra lại bộ lọc hoặc kết nối cơ sở dữ liệu.")
            import matplotlib.pyplot as plt
            # Lọc các sản phẩm có số lượng tồn kho dưới 10
            low_stock_threshold = 10
            low_stock = df_kho_raw[df_kho_raw['SoLuong'] <= low_stock_threshold]

            # Vẽ biểu đồ cảnh báo hàng tồn kho
            if not low_stock.empty:
                # Vẽ biểu đồ cột
                plt.figure(figsize=(10, 6))
                plt.bar(low_stock['TenNL'], low_stock['SoLuong'], color='orange')
                
                # Thêm tiêu đề và nhãn cho biểu đồ
                plt.title('Cảnh báo Nguyên liệu Sắp Hết (Tồn kho <= 10)', fontsize=14)
                plt.xlabel('Tên Nguyên Liệu', fontsize=12)
                plt.ylabel('Số Lượng Tồn Kho', fontsize=12)
                plt.xticks(rotation=45, ha='right')  # Quay tên sản phẩm để dễ đọc

                # Hiển thị biểu đồ trong Streamlit
                st.pyplot(plt)

            else:
                st.success(f"✅ Không có nguyên liệu nào có số lượng tồn dưới {low_stock_threshold}.")
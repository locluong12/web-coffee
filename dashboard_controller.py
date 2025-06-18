from model.database import get_table_info

# Các hàm lấy dữ liệu
def kho_data():
    query = "SELECT * FROM TonKho"
    return get_table_info(query)

def hoa_don_data():
    query = """
    SELECT hd.*
    FROM HoaDonBanHang hd
    LEFT JOIN KhachHang kh ON hd.MaKhachHang = kh.MaKhachHang
    """
    return get_table_info(query)

def chi_tiet_hoa_don_data():
    query = """
    SELECT ct.*, td.TenHH 
    FROM ChiTietHoaDon ct
    JOIN ThucDon td ON ct.MaHH = td.MaHH
    """
    return get_table_info(query)

def thuc_don_data():
    query = """
    SELECT td.*, lhh.TenLoaiHH
    FROM ThucDon td
    JOIN LoaiHangHoa lhh ON td.MaLoaiHH = lhh.MaLoaiHH
    """
    return get_table_info(query)

def khach_hang_data():
    query = """
    SELECT kh.*, lkh.TenLoaiKH
    FROM KhachHang kh
    LEFT JOIN LoaiKhachHang lkh ON kh.MaLoaiKH = lkh.MaLoaiKH
    """
    return get_table_info(query)

def nhan_vien_data():
    query = """
    SELECT *
    FROM NhanVien 
    """
    return get_table_info(query)

from dotenv import load_dotenv
import os 

load_dotenv()

# Cấu hình thông tin kết nối
TECHCOMBANK_ACCOUNT = os.getenv("TECHCOMBANK_ACCOUNT")
TECHCOMBANK_BANK_ID = os.getenv("TECHCOMBANK_BANK_ID")
PAYMENT_DESCRIPTION = os.getenv("PAYMENT_DESCRIPTION")

# --- Hàm tạo mã QR VietQR ---
def generate_vietqr(amount):
    return f"https://img.vietqr.io/image/{TECHCOMBANK_BANK_ID}-{TECHCOMBANK_ACCOUNT}-compact.png?amount={amount}&addInfo={PAYMENT_DESCRIPTION}"


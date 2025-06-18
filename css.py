import streamlit as st 

def custom_css():
    st.markdown("""
        <style>
            :root {
                --gold: #FFECB3;
                --dark-brown: #4E342E;
                --choco: #795548;
                --coffee: #6D4C41;
                --caramel: #8D6E63;
                --milk: #A1887F;
            }

            [data-testid="stMainBlockContainer"] {
                padding: 16px;
            }
                
            [data-testid="stHeader"] {
                background-color: transparent;
            }

            /* Sidebar */
            section[data-testid="stSidebar"] {
                background: linear-gradient(135deg, #5D4037, var(--dark-brown));
                padding: 0px;
                border-radius: 15px;
                box-shadow: 2px 2px 20px rgba(0, 0, 0, 0.3);
            }

            /* Tiêu đề Sidebar */
            .sidebar-title {
                text-align: center;
                font-size: 26px;
                font-weight: bold;
                color: var(--gold);
                text-shadow: 2px 2px 8px rgba(200, 215, 0, 0.5);
            }
                
            

            /* Nút bấm */
            div.stButton > button {
                width: 100%;
                height: 55px;
                margin-bottom: 12px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: 0.3s;
                box-shadow: 4px 6px 10px rgba(0, 0, 0, 0.2);

            }

            /* Màu nền nút */
            div.stButton:nth-child(1) > button { background: linear-gradient(135deg, var(--choco), #6F4E37); }
            div.stButton:nth-child(2) > button { background: linear-gradient(135deg, var(--coffee), #4E342E); }
            div.stButton:nth-child(3) > button { background: linear-gradient(135deg, var(--caramel), #6D4C41); }
            div.stButton:nth-child(4) > button { background: linear-gradient(135deg, var(--milk), #8D6E63); }

            /* Hiệu ứng Hover */
            div.stButton > button:hover {
                transform: scale(1.07);
                box-shadow: 6px 8px 14px rgba(255, 215, 0, 0.3);
            }

            /* Hiệu ứng Click */
            div.stButton > button:active {
                transform: scale(0.98);
                box-shadow: 2px 4px 6px rgba(0, 0, 0, 0.3);
            }
            
            /* Khoảng cách danh mục */
            div[data-testid="stHorizontalBlock"] { margin-bottom: 20px; }
                
            h3 {
                text-align: center;
            }

            table {
                width: 100%;
            }
            th, td {
                text-align: center !important;
                vertical-align: middle !important;
            }

            [data-testid="stHorizontalBlock"] {
                margin-bottom : 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)
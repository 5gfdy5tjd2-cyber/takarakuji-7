from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・マルチロト総合予測", page_icon="🎯", layout="centered"
)

# --- カスタムデザイン ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,900;1,900&family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap');

    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
        z-index: 99999999 !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #2563eb, #3b82f6);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        border: none;
        font-family: 'M PLUS Rounded 1c', sans-serif;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #1d4ed8, #2563eb);
    }

    .premium-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.1rem;
        font-weight: 900;
        font-style: italic;
        background: linear-gradient(135deg, #1d4ed8 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
        padding-top: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }

    .premium-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 25px;
        letter-spacing: 0.5px;
    }

    h3, h4, .stSidebar h2, .stSidebar h3 {
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.2px;
    }

    .lotto-number-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 15px 2px;
        gap: 4px;
    }
    .lotto-ball {
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #e2e8f0 70%, #cbd5e1 100%);
        color: #0f172a;
        font-size: 18px;
        font-weight: bold;
        width: 38px;
        height: 38px;
        min-width: 38px;
        min-height: 38px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 -3px 5px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.1);
        border: 2px solid #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ホーム画面：くじの選択 ---
st.markdown(
    '<h1 class="premium-title">🎯 宝田式・マルチロト予測プラットフォーム</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="premium-subtitle">✨ 全ロト共通：直近24回データ連動の黄金値・ミックス予測</p>',
    unsafe_allow_html=True,
)

lotto_mode = st.radio(
    "🎪 予想したい宝くじを選択してください",
    ["🎯 ロト7 (1〜37 / 7個選択)", "🔵 ロト6 (1〜43 / 6個選択)", "🟡 ミニロト (1〜31 / 5個選択)"],
    horizontal=True,
)

st.markdown("---")

# --- サイドバー：共通カスタム設定 ---
st.sidebar.header("⚙️ 宝田式・共通カスタム設定")

num_predictions = st.sidebar.slider(
    "生成する予想の数", min_value=1, max_value=20, value=5
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 軸・除外設定")
use_axis = st.sidebar.checkbox("任意の軸数字を追加する")
user_axis_numbers = []
if use_axis:
    axis_input = st.sidebar.text_input(
        "軸数字（半角カンマ区切り 例: 7, 15）", ""
    )
    if axis_input:
        try:
            user_axis_numbers = [
                int(n.strip()) for n in axis_input.split(",") if n.strip().isdigit()
            ]
        except:
            st.sidebar.error("半角数字とカンマで入力してください。")

exclude_input = st.sidebar.text_input("🚫 除外数字（カンマ区切り）", "")
exclude_numbers = []
if exclude_input:
    try:
        exclude_numbers = [
            int(n.strip()) for n in exclude_input.split(",") if n.strip().isdigit()
        ]
    except:
        pass

st.sidebar.markdown("---")
st.sidebar.subheader("📊 詳細条件フィルター")
hot_min, hot_max = st.sidebar.slider(
    "🔥 ホット・スライド・引っ張り要素の個数",
    min_value=1,
    max_value=5,
    value=(2, 4),
)
tail_min, tail_max = st.sidebar.slider(
    "🔢 末尾被り（同尾数ペア）の許容個数", min_value=0, max_value=3, value=(1, 2)
)


# --- 各モードのパラメータと直近24回データベースの定義 ---
if "ロト7" in lotto_mode:
    max_num = 37
    pick_count = 7
    default_sum_min, default_sum_max = 121, 145  # 中央値133周辺
    recent_24_draws = [
        [16, 17, 22, 23, 25, 33, 35],
        [7, 9, 15, 18, 20, 28, 31],
        [8, 10, 20, 22, 23, 27, 37],
        [6, 17, 22, 23, 25, 29, 36],
        [3, 10, 20, 22, 23, 28, 33],
        [2, 18, 23, 24, 32, 34, 37],
        [5, 22, 23, 24, 25, 30, 31],
        [4, 11, 16, 20, 21, 22, 35],
        [1, 5, 16, 20, 21, 22, 31],
        [10, 14, 17, 21, 25, 29, 36],
        [11, 14, 17, 23, 28, 30, 31],
        [7, 10, 12, 17, 33, 35, 36],
        [3, 15, 19, 21, 24, 31, 34],
        [5, 8, 14, 19, 26, 32, 37],
        [2, 11, 16, 23, 27, 30, 33],
        [4, 9, 13, 18, 22, 29, 35],
        [1, 6, 12, 17, 25, 31, 36],
        [10, 13, 18, 20, 26, 30, 34],
        [7, 14, 19, 21, 24, 28, 32],
        [3, 8, 15, 22, 27, 33, 37],
        [5, 11, 16, 20, 25, 29, 35],
        [2, 9, 13, 18, 23, 31, 36],
        [6, 12, 17, 21, 26, 30, 34],
        [4, 10, 15, 19, 24, 28, 33],
    ]
elif "ロト6" in lotto_mode:
    max_num = 43
    pick_count = 6
    default_sum_min, default_sum_max = 115, 150  # ロト6の黄金中央値周辺
    recent_24_draws = [
        [4, 12, 19, 24, 31, 38],
        [5, 11, 18, 22, 29, 36],
        [2, 14, 21, 27, 33, 40],
        [8, 13, 20, 26, 34, 41],
        [3, 10, 17, 25, 32, 39],
        [6, 15, 23, 28, 35, 42],
        [1, 9, 16, 24, 30, 37],
        [7, 12, 19, 26, 33, 38],
        [4, 11, 18, 22, 29, 35],
        [2, 8, 15, 21, 27, 34],
        [9, 16, 22, 29, 36, 43],
        [3, 10, 17, 25, 3

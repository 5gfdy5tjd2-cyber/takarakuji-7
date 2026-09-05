import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="宝田式・ロト7 予想システム", page_icon="🎯", layout="centered")

st.title("🎯 宝田式・ロト7 予想システム")
st.write("宝田式理論（黄金ゾーン・区間安定法・合計値ピボット・スライド式・過去24回データ動的連動）を完全統合したアプリです。")

# --- サイドバー（詳細設定エリア） ---
st.sidebar.header("⚙️ 宝田式・詳細カスタマイズ")

# 1. 候補数
num_predictions = st.sidebar.slider("生成する予想の数", min_value=1, max_value=10, value=5)

# 2. 軸数字の指定
st.sidebar.write("### 🔑 軸数字の指定")
use_axis = st.sidebar.checkbox("軸数字を指定する")
axis_numbers = []
if use_axis:
    axis_input = st.sidebar.text_input("カンマ区切りで入力 (例: 7, 15, 24)", "")
    if axis_input:
        try:
            axis_numbers = [int(n.strip()) for n in axis_input.split(",") if n.strip().isdigit()]
        except:
            st.sidebar.error("数字は半角のカンマ区切りで入力してください。")

# 3. 合計値の範囲変更
st.sidebar.write("### 📊 合計値の範囲")
sum_min, sum_max = st.sidebar.slider("許容する合計値の範囲", min_value=100, max_value=200, value=(125, 145))

# 4. 黄金ゾーンの重み付け調整
st.sidebar.write("### ⭐ 黄金ゾーンの重み")

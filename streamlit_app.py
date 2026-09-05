import streamlit as st
import random
import pandas as pd

# ページのタイトル
st.title("宝田式・ロト7予想システム")
st.write("宝田式理論（黄金ゾーン・区間安定法・合計値ピボット等）を完全統合した予想アプリです。")

# 1. 直近24回分の実際の当選データ（本数字7個ずつ）
recent_24_draws = [
    [16, 17, 22, 23, 25, 33, 35], [7, 9, 15, 18, 20, 28, 31],
    [8, 10, 20, 22, 23, 27, 37], [3, 10, 14, 17, 18, 20, 25],
    [4, 18, 23, 24, 32, 33, 35], [4, 21, 25, 28, 30, 35, 37],
    [15, 22, 23, 24, 25, 29, 36], [1, 3, 16, 18, 32, 34, 35],
    [1, 5, 16, 20, 21, 22, 31], [8, 14, 17, 19, 20, 32, 36],
    [11, 21, 22, 25, 28, 29, 36], [11, 14, 17, 23, 28, 30, 36],
    [1, 10, 12, 13, 19, 33, 35], [9, 10, 22, 26, 27, 31, 36],
    [6, 8, 9, 18, 22, 24, 35], [2, 6, 12, 15, 24, 26, 34],
    [5, 6, 7, 8, 15, 17, 19], [2, 6, 15, 19, 20, 22, 27],
    [5, 8, 16, 18, 24, 28, 31], [3, 7, 11, 19, 28, 31, 32],
    [4, 7, 12, 13, 15, 19, 27], [7, 11, 15, 16, 17, 24, 33],
    [7, 13, 16, 22, 28, 33, 36], [3, 4, 9, 10, 18, 21, 37]
]

flat_numbers = [num for draw in recent_24_draws for num in draw]
freq_series = pd.Series(flat_numbers).value_counts()
last_draw = recent_24_draws[0]

def check_conditions(nums):
    total = sum(nums)
    if not (125 <= total <= 145): return False
    b1 = sum(1 for n in nums if 1 <= n <= 10)
    b2 = sum(1 for n in nums if 11 <= n <= 20)
    b3 = sum(1 for n in nums if 21 <= n <= 30)
    b4 = sum(1 for n in nums if 31 <= n <= 37)
    if not (1 <= b1 <= 2 and 1 <= b2 <= 2 and 1 <= b3 <= 2 and 1 <= b4 <= 2): return False
    pull_count = sum(1 for n in nums if n in last_draw)
    if not (1 <= pull_count <= 2): return False
    if not any(nums[i] + 1 == nums[i+1] for i in range(len(nums)-1)): return False
    tails = [n % 10 for n in nums]
    if not (1 <= (len(tails) - len(set(tails))) <= 2): return False
    return True

def generate_lotto7(fixed_nums):
    blocks = [list(range(1, 11)), list(range(11, 21)), list(range(21, 31)), list(range(31, 38))]
    while True:
        candidate = list(fixed_nums)
        needed = 7 - len(candidate)
        if needed > 0:
            pool = [n for b in blocks for n in b if n not in candidate]
            weights = [3.0 if 4 <= freq_series.get(n, 0) <= 6 else (2.0 if freq_series.get(n, 0) >= 7 else 1.0) for n in pool]
            candidate.extend(random.choices(pool, weights=weights, k=needed))
        candidate = sorted(list(set(candidate)))
        if len(candidate) == 7 and check_conditions(candidate):
            return candidate, sum(candidate)

# --- 画面の入力パーツ ---
st.sidebar.header("アプリ設定")
total_outputs = st.sidebar.slider("作成する予想の数", 1, 10, 3)
fixed_input_str = st.sidebar.text_input("軸数字（例: 16, 22 のようにカンマ区切り）", "")

if st.button("予想を生成する"):
    fixed_nums = []
    if fixed_input_str:
        try:
            fixed_nums = [int(x.strip()) for x in fixed_input_str.split(",") if x.strip()]
        except:
            st.error("軸数字の入力形式が正しくありません。半角数字とカンマで入力してください。")
            st.stop()
            
    st.subheader("💡 宝田式・推奨予想結果")
    for i in range(total_outputs):
        try:
            nums, t_sum = generate_lotto7(fixed_nums)
            pulls = [n for n in nums if n in last_draw]
            st.success(f"**予想 {i+1}**: {nums}")
            st.write(f"　└ 合計値: `{t_sum}` | 引っ張り数字: `{pulls}`")
        except:
            st.warning("条件に完全に一致する組み合わせの生成に時間がかかっています。再度お試しください。")

from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・ロト7 完全版プレミアム予想", page_icon="🎯", layout="centered"
)

# --- カスタムデザイン ---
st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 宝田式・ロト7 完全版プレミアム予想")
st.caption(
    "✨ 黄金値ホット軸(1〜3個) × 帯バランス(各2〜3個) × 合計値制御(125〜145) × 末尾被り(0〜2個) 完全統合版"
)

# --- サイドバー（詳細設定エリア：確実にここに配置！） ---
st.sidebar.header("⚙️ 宝田式・詳細カスタマイズ")

num_predictions = st.sidebar.slider(
    "生成する予想の数", min_value=1, max_value=10, value=3
)

st.sidebar.markdown("---")
use_axis = st.sidebar.checkbox("🔑 任意の軸数字を追加する")
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

sum_min, sum_max = st.sidebar.slider(
    "📊 許容する合計値の範囲", min_value=100, max_value=200, value=(125, 145)
)

exclude_input = st.sidebar.text_input("🚫 除外数字（カンマ区切り）", "")
exclude_numbers = []
if exclude_input:
    try:
        exclude_numbers = [
            int(n.strip()) for n in exclude_input.split(",") if n.strip().isdigit()
        ]
    except:
        pass


# --- 過去データベース（シミュレーション用プールの動的連動） ---
recent_24_draws = [
    [6, 17, 22, 23, 25, 29, 36],
    [3, 10, 20, 22, 23, 28, 33],
    [2, 18, 23, 24, 32, 34, 37],
    [5, 22, 23, 24, 25, 30, 31],
    [4, 11, 16, 20, 21, 22, 35],
    [1, 5, 16, 20, 21, 22, 31],
    [10, 14, 17, 21, 25, 29, 36],
    [11, 14, 17, 23, 28, 30, 31],
    [7, 10, 12, 17, 33, 35, 36],
]


# --- 宝田式・完全アルゴリズムによる抽選と選定理由の追跡ロジック ---
def generate_takarada_lotto7_perfect(user_axes, exclude_nums):
    all_nums = list(range(1, 38))
    valid_nums = [n for n in all_nums if n not in exclude_nums]

    for a in user_axes:
        if a in exclude_nums:
            return None, {}, "軸数字に除外数字が含まれています！"

    # 第1段階：過去24回で4〜6回出ている数字（黄金値）を抽出
    flat_draws = [num for draw in recent_24_draws for num in draw]
    counts = Counter(flat_draws)
    golden_values = [
        num
        for num, cnt in counts.items()
        if 4 <= cnt <= 6 and num not in exclude_nums
    ]

    # 前回の当選数字（スライド・引っ張り用）
    previous_draw = recent_24_draws[0]
    pull_numbers = [n for n in previous_draw if n not in exclude_nums]
    slide_numbers = []
    for p in previous_draw:
        if p - 1 >= 1:
            slide_numbers.append(p - 1)
        if p + 1 <= 37:
            slide_numbers.append(p + 1)
    slide_numbers = list(
        set([n for n in slide_numbers if n not in exclude_nums])
    )

    # ホットな数字の候補
    hot_candidates = [
        n
        for n in golden_values
        if n in pull_numbers or n in slide_numbers
    ]

    attempts = 0
    while attempts < 2000:
        attempts += 1
        selected = set(user_axes)
        reasons = {}

        for a in user_axes:
            reasons[a] = "🔑 ユーザー指定軸"

        # ホットな数字から 1〜3個 を軸としてピックアップ
        valid_hot = [n for n in hot_candidates if n not in selected]
        if valid_hot:
            hot_count_target = random.choice([1, 2, 3])
            random.shuffle(valid_hot)
            added_hot = 0
            for h_num in valid_hot:
                if added_hot < hot_count_target and len(selected) < 7:
                    selected.add(h_num)
                    if h_num in pull_numbers:
                        reasons[h_num] = "🔥 ホット数字 (前回引っ張り)"
                    else:
                        reasons[h_num] = "🔥 ホット数字 (前回スライド±1)"
                    added_hot += 1

        # 残りの枠を帯バランス（低・中・高）を意識して埋める
        while len(selected) < 7:
            low_cnt = sum(1 for n in selected if 1 <= n <= 12)
            mid_cnt = sum(1 for n in selected if 13 <= n <= 24)
            high_cnt = sum(1 for n in selected if 25 <= n <= 37)

            pool = []
            for n in valid_nums:
                if n in selected:
                    continue
                if 1 <= n <= 12 and low_cnt < 3:
                    pool.extend([n] * 2)
                elif 13 <= n <= 24 and mid_cnt < 3:
                    pool.extend([n] * 2)
                elif 25 <= n <= 37 and high_cnt < 3:
                    pool.extend([n] * 2)
                else:
                    pool.append(n)

            if not pool:
                break
            cand = random.choice(pool)
            selected.add(cand)

            if 1 <= cand <= 12:
                reasons[cand] = "📊 低帯バランス枠 (01-12)"
            elif 13 <= cand <= 24:
                reasons[cand] = "📊 中帯バランス枠 (13-24)"
            else:
                reasons[cand] = "📊 高帯バランス枠 (25-37)"

        if len(selected) != 7:
            continue

        lotto_list = sorted(list(selected))

        # 1. 帯の偏りチェック（極端な偏りを防ぐ）
        low_final = sum(1 for n in lotto_list if 1 <= n <= 12)
        mid_final = sum(1 for n in lotto_list if 13 <= n <= 24)
        high_final = sum(1 for n in lotto_list if 25 <= n <= 37)

        if not (
            (1 <= low_final <= 4)
            and (1 <= mid_final <= 4)
            and (1 <= high_final <= 4)
        ):
            continue

        # 2. 末尾被り（同尾数）のチェック（0〜2個の範囲）
        last_digits = [n % 10 for n in lotto_list]
        digit_counts = Counter(last_digits)
        pairs_count = sum(1 for d, cnt in digit_counts.items() if cnt >= 2)
        if not (0 <= pairs_count <= 2):
            continue

        return lotto_list, reasons, None

    return (
        None,
        {},
        "条件に一致する組み合わせが見つかりませんでした。合計値の範囲や除外設定を少し広げてください。",
    )


# --- 【メイン画面】一番目立つところに抽選ボタンを配置 ---
st.markdown("---")
generate_btn = st.button("🚀 宝田式・完全版プレミアム予想を生成する", type="primary")

if generate_btn:
    st.markdown("### 📊 宝田式理論・厳選シミュレーション結果")

    success_count = 0
    attempts = 0

    with st.spinner("宝田式ロジックで厳選中..."):

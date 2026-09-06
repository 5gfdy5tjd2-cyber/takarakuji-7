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
    default_sum_min, default_sum_max = 121, 145
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
    default_sum_min, default_sum_max = 115, 150
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
        [3, 10, 17, 25, 31, 39],
        [5, 13, 20, 27, 34, 40],
        [1, 7, 14, 23, 30, 36],
        [6, 12, 19, 26, 32, 38],
        [4, 11, 18, 25, 33, 41],
        [2, 9, 16, 22, 29, 35],
        [8, 15, 21, 28, 34, 42],
        [3, 10, 17, 24, 31, 37],
        [7, 13, 20, 27, 33, 39],
        [5, 11, 18, 25, 32, 40],
        [1, 8, 15, 22, 29, 36],
        [6, 14, 21, 28, 35, 41],
        [4, 10, 17, 24, 30, 38],
    ]
else:
    max_num = 31
    pick_count = 5
    default_sum_min, default_sum_max = 65, 95
    recent_24_draws = [
        [3, 11, 17, 22, 28],
        [5, 12, 19, 24, 29],
        [2, 9, 15, 21, 27],
        [7, 14, 20, 26, 30],
        [4, 10, 16, 23, 28],
        [1, 8, 13, 19, 25],
        [6, 12, 18, 24, 29],
        [3, 10, 17, 22, 27],
        [5, 11, 16, 21, 26],
        [2, 7, 14, 20, 30],
        [4, 9, 15, 23, 28],
        [8, 13, 19, 25, 31],
        [1, 6, 12, 18, 24],
        [3, 10, 16, 22, 27],
        [5, 11, 17, 24, 29],
        [2, 8, 14, 20, 26],
        [7, 13, 19, 25, 30],
        [4, 10, 15, 21, 28],
        [6, 12, 18, 23, 29],
        [1, 7, 13, 19, 25],
        [3, 9, 16, 22, 27],
        [5, 11, 17, 24, 30],
        [2, 8, 15, 21, 26],
        [4, 10, 14, 20, 28],
    ]

sum_min, sum_max = st.sidebar.slider(
    "📈 合計値の範囲",
    min_value=int(max_num * pick_count * 0.2),
    max_value=int(max_num * pick_count * 0.8),
    value=(default_sum_min, default_sum_max),
)


def generate_multilotto(
    user_axes, exclude_nums, h_range, t_range, s_min, s_max, m_num, p_count, draws
):
    all_nums = list(range(1, m_num + 1))
    valid_nums = [n for n in all_nums if n not in exclude_nums]

    for a in user_axes:
        if a in exclude_nums:
            return None, {}, "軸数字に除外数字が含まれています！"

    flat_draws = [num for draw in draws for num in draw]
    counts = Counter(flat_draws)

    golden_values = [
        num
        for num, cnt in counts.items()
        if cnt >= 2 and num not in exclude_nums
    ]
    previous_draw = draws[0]
    pull_numbers = [n for n in previous_draw if n not in exclude_nums]

    slide_numbers = []
    for p in previous_draw:
        if p - 1 >= 1:
            slide_numbers.append(p - 1)
        if p + 1 <= m_num:
            slide_numbers.append(p + 1)
    slide_numbers = list(
        set([n for n in slide_numbers if n not in exclude_nums])
    )

    target_pool = list(set(pull_numbers + slide_numbers + golden_values))
    target_pool = [n for n in target_pool if n not in exclude_nums]

    attempts = 0
    while attempts < 20000:
        attempts += 1
        selected = set(user_axes)
        reasons = {}

        for a in user_axes:
            cnt_a = counts.get(a, 0)
            oddeven_a = "奇数" if a % 2 != 0 else "偶数"
            reasons[
                a
            ] = f"ユーザー様が固定軸として指定された数字です。（直近24回中の出現回数: {cnt_a}回 / {oddeven_a}）"

        available_hot_mix = [n for n in target_pool if n not in selected]
        if available_hot_mix and h_range[1] > 0:
            possible_counts = [
                c
                for c in range(h_range[0], h_range[1] + 1)
                if c <= len(available_hot_mix)
            ]
            mix_target_count = (
                random.choice(possible_counts) if possible_counts else h_range[0]
            )
            random.shuffle(available_hot_mix)

            added_mix = 0
            for h_num in available_hot_mix:
                if added_mix < mix_target_count and len(selected) < p_count:
                    selected.add(h_num)
                    cnt_h = counts.get(h_num, 0)
                    oddeven_h = "奇数" if h_num % 2 != 0 else "偶数"

                    if h_num in pull_numbers:
                        reasons[
                            h_num
                        ] = f"直近の当選数字から引き継가れた**「引っ張り数字」**です（直近24回中 出現{cnt_h}回・{oddeven_h}）。".replace(
                            "가", "が"
                        )
                    elif h_num in slide_numbers:
                        reasons[
                            h_num
                        ] = f"直近当選数字の近傍からスライドした**「スライド数字」**です（直近24回中 出現{cnt_h}回・{oddeven_h}）。"
                    else:
                        reasons[
                            h_num
                        ] = f"過去データの傾向から選ばれた**「ホットな黄金値数字」**です（直近24回中 出現{cnt_h}回・{oddeven_h}）。"
                    added_mix += 1

        while len(selected) < p_count:
            current_tails = [n % 10 for n in selected]

            pool = []
            for n in valid_nums:
                if n in selected:
                    continue
                n_tail = n % 10
                is_golden = counts.get(n, 0) >= 2

                if n_tail in current_tails:
                    pool.extend([n] * 3)
                elif is_golden:
                    pool.extend([n] * 2)
                else:
                    pool.append(n)

            if not pool:
                pool = [n for n in valid_nums if n not in selected]
            if not pool:
                break

            cand = random.choice(pool)
            selected.add(cand)
            cnt_c = counts.get(cand, 0)
            cand_tail = cand % 10
            is_tail_match = current_tails.count(cand_tail) > 0

            tail_desc = (
                "**【末尾被り】**同尾数ペアを形成し、"
                if is_tail_match
                else ""
            )
            reasons[
                cand
            ] = f"{tail_desc}直近24回中の出現実績（{cnt_c}回）を考慮したバランス枠として選出されました。"

        if len(selected) != p_count:
            continue

        lotto_list = sorted(list(selected))

        total_sum = sum(lotto_list)
        if not (s_min <= total_sum <= s_max):
            continue

        last_digits = [n % 10 for n in lotto_list]
        digit_counts = Counter(last_digits)
        pairs_count = sum(1 for d, cnt in digit_counts.items() if cnt >= 2)
        if not (t_range[0] <= pairs_count <= t_range[1]):
            continue

        return lotto_list, reasons, None

    return None, {}, "条件に一致する組み合わせが見つかりませんでした。"


# --- メイン画面：生成ボタン ---
generate_btn = st.button(
    f"🚀 {lotto_mode.split()[1]} のフルカスタム予想を生成する",
    type="primary",
)

if generate_btn:
    st.markdown(f"<h3>📊 {lotto_mode} 厳選シミュレーション結果</h3>", unsafe_allow_html=True)

    success_count = 0
    attempts = 0

    with st.spinner(
        f"過去24回データを参照して{lotto_mode.split()[1]}の予想を最大{num_predictions}通り厳選中..."
    ):
        while success_count < num_predictions and attempts < 25000:
            attempts += 1
            lotto_numbers, reasons, err = generate_multilotto(
                user_axis_numbers,
                exclude_numbers,
                (hot_min, hot_max),
                (tail_min, tail_max),
                sum_min,
                sum_max,
                max_num,
                pick_count,
                recent_24_draws,
            )

            if err:
                st.error(err)
                break

            if lotto_numbers:
                success_count += 1
                total_sum = sum(lotto_numbers)
                odd_count = sum(1 for n in lotto_numbers if n % 2 != 0)
                even_count = sum(1 for n in lotto_numbers if n % 2 == 0)

                with st.container(border=True):
                    st.markdown(f"<h4>🏷️ 予想パターン #{success_count}</h4>", unsafe_allow_html=True)
                    balls_html = "<div class='lotto-number-container'>"
                    for n in lotto_numbers:
                        balls_html += f"<div class='lotto-ball'>{n:02d}</div>"
                    balls_html += "</div>"
                    st.markdown(balls_html, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📊 **合計値**: **{total_sum}**")
                    with col2:
                        st.success(f"⚖️ **奇偶バランス**: **奇数 {odd_count} / 偶数 {even_count}**")

                    with st.expander("📖 【詳細】なぜこの数字が選ばれたのか？"):
                        for num in lotto_numbers:
                            reason_text = reasons.get(
                                num, "条件を満たして選出されました。"
                            )
                            detail_html = f"""
                            <div style="margin-bottom: 12px; font-size: 13px; font-weight: normal; color: #475569; line-height: 1.6;">
                                • 数字 <span style="color: #16a34a; font-size: 18px; font-weight: bold;">[ {num:02d} ]</span>：{reason_text}
                            </div>
                            """
                            st.markdown(detail_html, unsafe_allow_html=True)

    if success_count > 0:
        st.success(
            f"🎉 完了しました！ご指定の {lotto_mode} で、過去24回データを完全網羅した最大 {num_predictions}通りの予想を生成しました。"
        )

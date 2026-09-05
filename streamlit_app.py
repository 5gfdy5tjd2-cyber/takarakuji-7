from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・ロト7 フルカスタム予想", page_icon="🎯", layout="centered"
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
    
    .absolute-fixed-header {
        position: fixed !important;
        top: 60px !important;
        left: 0 !important;
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(8px);
        z-index: 99999 !important;
        padding: 8px 15px !important;
        border-bottom: 2px solid #3b82f6 !important;
        border-top: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        text-align: center;
    }

    .prev-ball-container-fixed {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 4px 0;
    }
    .prev-ball-fixed {
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #cbd5e1 70%, #94a3b8 100%);
        color: #1e293b;
        font-size: 14px;
        font-weight: bold;
        width: 30px;
        height: 30px;
        min-width: 30px;
        min-height: 30px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 -2px 4px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.08);
        border: 1px solid #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- サイドバー：詳細カスタマイズ項目 ---
st.sidebar.header("⚙️ 宝田式・フルカスタム設定")

num_predictions = st.sidebar.slider(
    "生成する予想の数", min_value=1, max_value=10, value=3
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
st.sidebar.subheader("📊 条件フィルター調整（ミックス強化版）")

# デフォルトでホットや末尾被りをしっかり混ぜやすい範囲に調整
hot_min, hot_max = st.sidebar.slider(
    "🔥 ホット・スライド・引っ張り要素の個数",
    min_value=1,
    max_value=5,
    value=(2, 4),
)
zone_min, zone_max = st.sidebar.slider(
    "📦 各帯（低・中・高）の許容個数範囲", min_value=1, max_value=5, value=(1, 4)
)
sum_min, sum_max = st.sidebar.slider(
    "📈 7個の合計値の範囲", min_value=100, max_value=200, value=(115, 155)
)
tail_min, tail_max = st.sidebar.slider(
    "🔢 末尾被り（同尾数ペア）の許容個数", min_value=1, max_value=4, value=(1, 3)
)
renban_min, renban_max = st.sidebar.slider(
    "🔗 連番ペアの許容個数", min_value=0, max_value=3, value=(0, 2)
)


# --- メイン画面のタイトル ---
st.markdown(
    '<h1 class="premium-title">🎯 宝田式・ロト7 フルカスタム予想</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="premium-subtitle">✨ 黄金値・引っ張り・スライド・末尾被りを強力ミックスした次世代予測プラットフォーム</p>',
    unsafe_allow_html=True,
)

# --- 過去データベース（最新 第693回反映） ---
recent_24_draws = [
    [16, 17, 22, 23, 25, 33, 35],  # 第693回 (最新)
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


def generate_takarada_custom(
    user_axes, exclude_nums, h_range, z_range, t_range, r_range
):
    all_nums = list(range(1, 38))
    valid_nums = [n for n in all_nums if n not in exclude_nums]

    for a in user_axes:
        if a in exclude_nums:
            return None, {}, "軸数字に除外数字が含まれています！"

    flat_draws = [num for draw in recent_24_draws for num in draw]
    counts = Counter(flat_draws)

    # 黄金値（出現4〜6回）
    golden_values = [
        num
        for num, cnt in counts.items()
        if 4 <= cnt <= 6 and num not in exclude_nums
    ]
    previous_draw = recent_24_draws[0]
    pull_numbers = [n for n in previous_draw if n not in exclude_nums]

    # スライド数字（前回数字の±1）
    slide_numbers = []
    for p in previous_draw:
        if p - 1 >= 1:
            slide_numbers.append(p - 1)
        if p + 1 <= 37:
            slide_numbers.append(p + 1)
    slide_numbers = list(
        set([n for n in slide_numbers if n not in exclude_nums])
    )

    # 狙い目候補（引っ張り・スライド・黄金値を統合）
    target_pool = list(set(pull_numbers + slide_numbers + golden_values))
    target_pool = [n for n in target_pool if n not in exclude_nums]

    attempts = 0
    while attempts < 10000:
        attempts += 1
        selected = set(user_axes)
        reasons = {}

        # 1. ユーザー指定の軸
        for a in user_axes:
            cnt_a = counts.get(a, 0)
            oddeven_a = "奇数" if a % 2 != 0 else "偶数"
            reasons[
                a
            ] = f"ユーザー様が固定軸として指定された数字です。直近24回中の出現回数は{cnt_a}回（{oddeven_a}）です。"

        # 2. 引っ張り・スライド・ホット数字のミックス枠を積極的に取り込む
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
                if added_mix < mix_target_count and len(selected) < 7:
                    selected.add(h_num)
                    cnt_h = counts.get(h_num, 0)
                    oddeven_h = "奇数" if h_num % 2 != 0 else "偶数"

                    # どの性質に強く該当するかを判定して理由を生成
                    if h_num in pull_numbers:
                        reasons[
                            h_num
                        ] = f"前回（第693回）からそのまま引き継がれた**「引っ張り数字」**です（出現{cnt_h}回・{oddeven_h}）。"
                    elif h_num in slide_numbers:
                        reasons[
                            h_num
                        ] = f"前回当選数字の近傍からスライドしてきた**「スライド数字」**です（出現{cnt_h}回・{oddeven_h}）。"
                    else:
                        reasons[
                            h_num
                        ] = f"出現回数が理想的な帯にある**「ホットな黄金値数字」**です（出現{cnt_h}回・{oddeven_h}）。"
                    added_mix += 1

        # 3. 残りの枠を埋めつつ、末尾被り（同尾数）を意識的に発生させるロジック
        while len(selected) < 7:
            # 現在选ばれている数字の末尾をチェック
            current_tails = [n % 10 for n in selected]

            pool = []
            for n in valid_nums:
                if n in selected:
                    continue
                n_tail = n % 10
                is_golden = 4 <= counts.get(n, 0) <= 6

                # すでに選ばれている数字と同じ末尾（同尾数）なら、末尾被りを作るために優先度を上げる
                if n_tail in current_tails:
                    pool.extend([n] * 4)  # 強く末尾被りを誘発
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
                "**【末尾被り】**同じ下二桁（同尾数）のペアを形成し、"
                if is_tail_match
                else ""
            )
            is_golden_cand = 4 <= cnt_c <= 6
            golden_desc = (
                f"出現回数{cnt_c}回の黄金値"
                if is_golden_cand
                else f"出現回数{cnt_c}回の実績枠"
            )

            reasons[
                cand
            ] = f"{tail_desc}{golden_desc}として全体のバランスを補正するために選出されました。"

        if len(selected) != 7:
            continue

        lotto_list = sorted(list(selected))

        # 4. 各種バリデーション（フィルター）
        odd_final = sum(1 for n in lotto_list if n % 2 != 0)
        if not (2 <= odd_final <= 5):
            continue

        low_final = sum(1 for n in lotto_list if 1 <= n <= 12)
        mid_final = sum(1 for n in lotto_list if 13 <= n <= 24)
        high_final = sum(1 for n in lotto_list if 25 <= n <= 37)
        if not (
            (z_range[0] <= low_final <= z_range[1])
            and (z_range[0] <= mid_final <= z_range[1])
            and (z_range[0] <= high_final <= z_range[1])
        ):
            continue

        last_digits = [n % 10 for n in lotto_list]
        digit_counts = Counter(last_digits)
        pairs_count = sum(1 for d, cnt in digit_counts.items() if cnt >= 2)
        if not (t_range[0] <= pairs_count <= t_range[1]):
            continue

        consecutive_count = 0
        for i in range(len(lotto_list) - 1):
            if lotto_list[i + 1] - lotto_list[i] == 1:
                consecutive_count += 1
        if not (r_range[0] <= consecutive_count <= r_range[1]):
            continue

        return lotto_list, reasons, None

    return None, {}, "条件に一致する組み合わせが見つかりませんでした。"


# --- メイン画面：生成ボタン ---
st.markdown("---")
generate_btn = st.button("🚀 宝田式・フルカスタム予想を生成する", type="primary")

if generate_btn:
    latest_draw = recent_24_draws[0]
    fixed_header_html = """
    <div class="absolute-fixed-header">
        <div style="font-size: 11px; font-weight: bold; color: #475569; margin-bottom: 3px;">
            📌 【追従中】前回（第693回）の当選数字
        </div>
        <div class="prev-ball-container-fixed">
    """
    for p_num in latest_draw:
        fixed_header_html += f'<div class="prev-ball-fixed">{p_num:02d}</div>'
    fixed_header_html += """
        </div>
    </div>
    """
    st.markdown(fixed_header_html, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 75px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3>📊 フルカスタム・厳選シミュレーション結果</h3>", unsafe_allow_html=True)

    success_count = 0
    attempts = 0

    with st.spinner("スライド・引っ張り・末尾被りをミックスして厳選中..."):
        while success_count < num_predictions and attempts < 15000:
            attempts += 1
            lotto_numbers, reasons, err = generate_takarada_custom(
                user_axis_numbers,
                exclude_numbers,
                (hot_min, hot_max),
                (zone_min, zone_max),
                (tail_min, tail_max),
                (renban_min, renban_max),
            )

            if err:
                st.error(err)
                break

            if lotto_numbers:
                total_sum = sum(lotto_numbers)
                if sum_min <= total_sum <= sum_max:
                    success_count += 1
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

                        with st.expander("📖 【詳細】なぜこの7つの数字が選ばれたのか？"):
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
            "🎉 完了しました！引っ張り・スライド・黄金値・末尾被りの要素が1つのパターンの中にバランスよく高密度で混ざり合っています。"
        )

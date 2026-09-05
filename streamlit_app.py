from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・ロト7 フルカスタム予想", page_icon="🎯", layout="centered"
)

# --- カスタムデザイン（迫力のタイトル ＆ 丸みのある見出し ＆ 正円立体ボール） ---
st.markdown(
    """
    <style>
    /* 1. フォントのインポート（迫力用 Montserrat & 丸み用 M PLUS Rounded 1c） */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,900;1,900&family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@500;700&display=swap');

    /* 全体の背景と文字色を明るく爽やかに */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    /* サイドバーも明るく */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #2563eb, #3b82f6);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.7rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        border: none;
        font-family: 'M PLUS Rounded 1c', sans-serif;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #1d4ed8, #2563eb);
    }

    /* 🔥 タイトル：圧倒的な迫力と重厚感のあるフォント */
    .premium-title {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 2.3rem;
        font-weight: 900;
        font-style: italic;
        background: linear-gradient(135deg, #1d4ed8 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
        padding-top: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }

    /* ✨ サブタイトルの洗練されたデザイン */
    .premium-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 25px;
        letter-spacing: 0.5px;
    }

    /* 🍩 見出し全般（h3, h4, サイドバー見出し）：丸みを帯びたポップで優しいフォント */
    h3, h4, .stSidebar h2, .stSidebar h3 {
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.2px;
    }

    /* 🎯 予想パターンの数字：完全正円・立体球体デザイン */
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
        font-size: 20px;
        font-weight: bold;
        width: 42px;
        height: 42px;
        min-width: 42px;
        min-height: 42px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 -3px 5px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.1);
        border: 2px solid #ffffff;
    }
    
    /* 📌 予想結果が出たときだけ最上部に固定するヘッダー */
    .absolute-fixed-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(8px);
        z-index: 999999 !important;
        padding: 8px 15px !important;
        border-bottom: 2px solid #3b82f6 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        text-align: center;
    }

    /* 前回の当選数字用のミニボール */
    .prev-ball-container-fixed {
        display: flex;
        justify-content: center;
        gap: 10px;
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

# --- 迫力のあるタイトルの描画 ---
st.markdown(
    '<h1 class="premium-title">🎯 宝田式・ロト7 フルカスタム予想</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="premium-subtitle">✨ 黄金値データ ＆ 奇偶バランスを完全融合させた次世代予測プラットフォーム</p>',
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
st.sidebar.subheader("📊 条件フィルター調整")

hot_min, hot_max = st.sidebar.slider(
    "🔥 ホット数字軸の個数範囲", min_value=0, max_value=5, value=(1, 3)
)

zone_min, zone_max = st.sidebar.slider(
    "📦 各帯（低・中・高）の許容個数範囲", min_value=1, max_value=5, value=(2, 3)
)

sum_min, sum_max = st.sidebar.slider(
    "📈 7個の合計値の範囲", min_value=100, max_value=200, value=(125, 145)
)

tail_min, tail_max = st.sidebar.slider(
    "🔢 末尾被り（同尾数ペア）の許容個数", min_value=0, max_value=3, value=(0, 2)
)

renban_min, renban_max = st.sidebar.slider(
    "🔗 連番ペアの許容個数", min_value=0, max_value=3, value=(0, 2)
)


# --- 過去データベース（最新の第693回データを反映した正確な24回分） ---
recent_24_draws = [
    [16, 17, 22, 23, 25, 33, 35],  # 第693回 (最新)
    [7, 9, 15, 18, 20, 28, 31],    # 第692回
    [8, 10, 20, 22, 23, 27, 37],   # 第691回
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


# --- フルカスタム対応抽選アルゴリズム（黄金値基準の奇偶バランス対応） ---
def generate_takarada_custom(
    user_axes,
    exclude_nums,
    h_range,
    z_range,
    t_range,
    r_range,
):
    all_nums = list(range(1, 38))
    valid_nums = [n for n in all_nums if n not in exclude_nums]

    for a in user_axes:
        if a in exclude_nums:
            return None, {}, "軸数字に除外数字が含まれています！"

    flat_draws = [num for draw in recent_24_draws for num in draw]
    counts = Counter(flat_draws)

    golden_values = [
        num
        for num, cnt in counts.items()
        if 4 <= cnt <= 6 and num not in exclude_nums
    ]

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

    hot_candidates = [
        n
        for n in golden_values
        if n in pull_numbers or n in slide_numbers
    ]

    attempts = 0
    while attempts < 8000:
        attempts += 1
        selected = set(user_axes)
        reasons = {}

        for a in user_axes:
            cnt_a = counts.get(a, 0)
            oddeven_a = "奇数" if a % 2 != 0 else "偶数"
            golden_tag = " [黄金値該当]" if 4 <= cnt_a <= 6 else ""
            reasons[a] = f"🔑 **ユーザー指定固定軸 ({oddeven_a}){golden_tag}**: ご自身で指定されたカスタム軸数字です。（直近24回出現数: {cnt_a}回）"

        valid_hot = [n for n in hot_candidates if n not in selected]
        if valid_hot and h_range[1] > 0:
            possible_counts = [
                c
                for c in range(h_range[0], h_range[1] + 1)
                if c <= len(valid_hot)
            ]
            hot_count_target = (
                random.choice(possible_counts) if possible_counts else 0
            )

            random.shuffle(valid_hot)
            added_hot = 0
            for h_num in valid_hot:
                if added_hot < hot_count_target and len(selected) < 7:
                    selected.add(h_num)
                    cnt_h = counts.get(h_num, 0)
                    oddeven_h = "奇数" if h_num % 2 != 0 else "偶数"
                    if h_num in pull_numbers:
                        reasons[h_num] = f"🔥 **ホット数字（引っ張り・{oddeven_h}・出現{cnt_h}回）**: 黄金値基準を満たし、前回（第693回）からそのまま「引っ張り」された強力な連動数字です。"
                    else:
                        origin = (
                            h_num - 1 if (h_num - 1 in previous_draw) else h_num + 1
                        )
                        direction = "+1" if h_num > origin else "-1"
                        reasons[h_num] = f"🔥 **ホット数字（スライド{direction}・{oddeven_h}・出現{cnt_h}回）**: 黄金値基準を満たし、前回第693回の当選数字「{origin:02d}」からスライドして選出されました。"
                    added_hot += 1

        while len(selected) < 7:
            low_cnt = sum(1 for n in selected if 1 <= n <= 12)
            mid_cnt = sum(1 for n in selected if 13 <= n <= 24)
            high_cnt = sum(1 for n in selected if 25 <= n <= 37)

            pool = []
            for n in valid_nums:
                if n in selected:
                    continue
                if 1 <= n <= 12 and low_cnt < z_range[1]:
                    pool.extend([n] * 2)
                elif 13 <= n <= 24 and mid_cnt < z_range[1]:
                    pool.extend([n] * 2)
                elif 25 <= n <= 37 and high_cnt < z_range[1]:
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

            zone_name = "低帯（01〜12）" if 1 <= cand <= 12 else ("中帯（13〜24）" if 13 <= cand <= 24 else "高帯（25〜37）")
            oddeven_type = "奇数" if cand % 2 != 0 else "偶数"
            is_golden = 4 <= cnt_c <= 6
            golden_str = "【🌟黄金値帯】" if is_golden else "【通常出現帯】"
            
            if cnt_c >= 5:
                profile_desc = f"直近24回で【{cnt_c}回】出現の**高頻度・主力{oddeven_type}**です。{golden_str} 勢いが安定しており軸を支える優秀な数値として採用されました。"
            elif 3 <= cnt_c <= 4:
                profile_desc = f"直近24回で【{cnt_c}回】出現の**中頻度・安定バランス{oddeven_type}**です。{golden_str} 偏りのない堅実な組合せの土台を作るために選出されました。"
            elif cnt_c == 2:
                profile_desc = f"直近24回で【2回】出現の**潜伏・低頻度狙い目{oddeven_type}**です。そろそろ出現タイミングが巡ってくる波としてピックアップされました。"
            else:
                profile_desc = f"直近24回で【{cnt_c}回】の**大穴・反発期待{oddeven_type}**です。全体の組合せに爆発力をもたらす隠し味として選出されました。"

            reasons[cand] = f"📦 **{zone_name}バランス枠**: {profile_desc}"

        if len(selected) != 7:
            continue

        lotto_list = sorted(list(selected))

        # 偶数・奇数のバランスフィルター（極端な偏り 7:0 や 0:7 を自動排除）
        odd_final = sum(1 for n in lotto_list if n % 2 != 0)
        if not (2 <= odd_final <= 5):  # 奇数が2〜5個（偶数が2〜5個）の黄金バランス
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

    return (
        None,
        {},
        "条件に一致する組み合わせが見つかりませんでした。サイドバーの設定値（帯の許容範囲や合計値など）を少し広げ直してください。",
    )


# --- メイン画面：抽選ボタン ---
st.markdown("---")
generate_btn = st.button("🚀 宝田式・フルカスタム予想を生成する", type="primary")

if generate_btn:
    # 📌 ボタンが押されたとき（結果表示時）だけ、画面最上部に固定ヘッダーを表示＆上部にパディングを追加
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

    latest_draw = recent_24_draws[0]
    fixed_header_html = """
    <div class="absolute-fixed-header">
        <div style="font-size: 11px; font-weight: bold; color: #64748b; margin-bottom: 2px;">
            📌 【追従中】最新（前回 第693回）の当選数字
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

    st.markdown("### 📊 フルカスタム・厳選シミュレーション結果")

    success_count = 0
    attempts = 0

    with st.spinner("カスタム条件で厳選中..."):
        while success_count < num_predictions and attempts < 12000:
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

                    # 奇数・偶数の個数を集計
                    odd_count = sum(1 for n in lotto_numbers if n % 2 != 0)
                    even_count = sum(1 for n in lotto_numbers if n % 2 == 0)

                    with st.container(border=True):
                        st.markdown(f"#### 🏷️ 予想パターン #{success_count}")

                        balls_html = "<div class='lotto-number-container'>"
                        for n in lotto_numbers:
                            balls_html += f"<div class='lotto-ball'>{n:02d}</div>"
                        balls_html += "</div>"
                        st.markdown(balls_html, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"📊 **合計値**: **{total_sum}** （指定 {sum_min}〜{sum_max}）")
                        with col2:
                            st.success(f"⚖️ **奇偶バランス**: **奇数 {odd_count}個 / 偶数 {even_count}個**")

                        with st.expander("📖 【詳細】なぜこの7つの数字が選ばれたのか？（個別選定根拠）"):
                            st.markdown("各数字の出現データと奇偶バランス特性の個別解説は以下の通りです：")
                            for num in lotto_numbers:
                                detail_text = reasons.get(num, "個別特性枠として選出されました。")
                                st.markdown(f"- **数字 `[ {num:02d} ]` の根拠**: {detail_text}")

                            st.markdown("---")
                            st.markdown("💡 **カスタムゾーン内訳**: "
                                        f"低帯({sum(1 for n in lotto_numbers if 1<=n<=12)}個) / "
                                        f"中帯({sum(1 for n in lotto_numbers if 13<=n<=24)}個) / "
                                        f"高帯({sum(1 for n in lotto_numbers if 25<=n<=37)}個)")

    if success_count < num_predictions and not err:
        st.warning(
            f"⚠️ 指定されたカスタム条件（合計値 {sum_min}〜{sum_max} や帯・末尾・連番の制限）が厳しいため、{success_count}件のみの表示となりました。サイドバーの数値を少し緩めるとたくさん生成されます。"
        )
    elif success_count > 0:
        st.success(
            "🎉 黄金値ベースの奇偶バランスとすべてのカスタム条件を満たした予想の生成が完了しました！"
        )

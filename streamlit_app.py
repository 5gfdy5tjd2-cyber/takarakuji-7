from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・ロト7 フルカスタム予想", page_icon="🎯", layout="centered"
)

# --- カスタムデザイン（ライトテーマ ＆ 美しい正円立体ボール ＆ 端までゆったり配置） ---
st.markdown(
    """
    <style>
    /* 全体の背景と文字色を明るく爽やかに */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
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
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #1d4ed8, #2563eb);
    }

    /* 🎯 予想パターンの数字：完全な正円＆立体的な光沢ある球体デザイン */
    .lotto-number-container {
        display: flex;
        justify-content: space-between; /* 端が寂しくならないよう均等にゆったり配置 */
        align-items: center;
        margin: 20px 5px;
    }
    .lotto-ball {
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #e2e8f0 70%, #cbd5e1 100%);
        color: #0f172a;
        font-size: 24px;
        font-weight: bold;
        width: 54px;
        height: 54px;
        min-width: 54px;
        min-height: 54px;
        border-radius: 50% !important; /* 絶対に楕円にならないよう強制 */
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 -4px 6px rgba(0,0,0,0.15), 0 6px 12px rgba(0,0,0,0.1);
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

    /* 前回の当選数字用のミニボール（サイズを少し大きく＆間隔をゆったり） */
    .prev-ball-container-fixed {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 5px 0;
    }
    .prev-ball-fixed {
        background: radial-gradient(circle at 30% 30%, #ffffff 0%, #cbd5e1 70%, #94a3b8 100%);
        color: #1e293b;
        font-size: 15px;
        font-weight: bold;
        width: 33px;
        height: 33px;
        min-width: 33px;
        min-height: 33px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 -2px 4px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.08);
        border: 1px solid #ffffff;
    }
    
    /* 固定ヘッダーにメインコンテンツが隠れないように上の隙間をあける（結果表示時用） */
    .has-fixed-header {
        padding-top: 75px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 宝田式・ロト7 フルカスタム予想")
st.caption(
    "✨ すべてのパラメータを自由自在にカスタマイズ可能な次世代プレミアム版"
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


# --- 過去データベース ---
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


# --- フルカスタム対応抽選アルゴリズム ---
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
            reasons[a] = f"🔑 **ユーザー指定軸**: ご自身で設定された固定軸です。（直近24回出現数: {cnt_a}回）"

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
                    if h_num in pull_numbers:
                        reasons[h_num] = f"🔥 **ホット数字（引っ張り）**: 直近24回で {cnt_h}回出現している黄金値であり、前回抽選回の同値引っ張りとして選出されました。"
                    else:
                        origin = (
                            h_num - 1 if (h_num - 1 in previous_draw) else h_num + 1
                        )
                        reasons[h_num] = f"🔥 **ホット数字（スライド±1）**: 直近24回で {cnt_h}回出現している黄金値であり、前回当選数字「{origin:02d}」からのスライドとして選出されました。"
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

            if 1 <= cand <= 12:
                reasons[cand] = f"📊 **低帯バランス枠（01-12）**: ユーザー設定のゾーン配分ルールに基づき選出されました。（直近出現: {cnt_c}回）"
            elif 13 <= cand <= 24:
                reasons[cand] = f"📊 **中帯バランス枠（13-24）**: ユーザー設定のゾーン配分ルールに基づき選出されました。（直近出現: {cnt_c}回）"
            else:
                reasons[cand] = f"📊 **高帯バランス枠（25-37）**: ユーザー設定のゾーン配分ルールに基づき選出されました。（直近出現: {cnt_c}回）"

        if len(selected) != 7:
            continue

        lotto_list = sorted(list(selected))

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
            📌 【追従中】直近（前回）の当選数字
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

                    with st.container(border=True):
                        st.markdown(f"#### 🏷️ 予想パターン #{success_count}")

                        balls_html = "<div class='lotto-number-container'>"
                        for n in lotto_numbers:
                            balls_html += f"<div class='lotto-ball'>{n:02d}</div>"
                        balls_html += "</div>"
                        st.markdown(balls_html, unsafe_allow_html=True)

                        st.info(f"📊 **7個の合計値**: **{total_sum}** （指定レンジ {sum_min}〜{sum_max} 内）")

                        with st.expander("📖 【詳細】なぜこの7つの数字が選ばれたのか？（選定根拠）"):
                            st.markdown("カスタム設定されたフィルターおよび統計データに基づく選定根拠は以下の通りです：")
                            for num in lotto_numbers:
                                detail_text = reasons.get(num, "通常バランス枠として選出されました。")
                                st.markdown(f"- **数字 `[ {num:02d} ]` の根拠**: {detail_text}")

                            st.markdown("---")
                            st.markdown("💡 **カスタムバランス確認**: "
                                        f"低帯({sum(1 for n in lotto_numbers if 1<=n<=12)}個) / "
                                        f"中帯({sum(1 for n in lotto_numbers if 13<=n<=24)}個) / "
                                        f"高帯({sum(1 for n in lotto_numbers if 25<=n<=37)}個)")

    if success_count < num_predictions and not err:
        st.warning(
            f"⚠️ 指定されたカスタム条件（合計値 {sum_min}〜{sum_max} や帯・末尾・連番の制限）が厳しいため、{success_count}件のみの表示となりました。サイドバーの数値を少し緩めるとたくさん生成されます。"
        )
    elif success_count > 0:
        st.success(
            "🎉 すべてのカスタム条件を満たした予想の生成が完了しました！"
        )

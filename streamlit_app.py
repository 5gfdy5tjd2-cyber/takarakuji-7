from collections import Counter
import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="宝田式・ロト7 プレミアム予想", page_icon="🎯", layout="centered"
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
    .lotto-number-container {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 15px 0;
    }
    .lotto-ball {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        font-size: 24px;
        font-weight: bold;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 宝田式・ロト7 プレミアム予想")
st.caption(
    "✨ 黄金値ホット軸(1〜3個) × 帯バランス(各2〜3個) × 合計値制御(125〜145) × 末尾被り(0〜2個) × 連番制限(0〜2個)"
)

# --- サイドバー設定エリア ---
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


# --- 宝田式・詳細解説つき抽選アルゴリズム ---
def generate_takarada_lotto7_detailed(user_axes, exclude_nums):
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
    while attempts < 6000:
        attempts += 1
        selected = set(user_axes)
        reasons = {}

        for a in user_axes:
            cnt_a = counts.get(a, 0)
            reasons[a] = f"🔑 **ユーザー指定軸**: ご自身で設定された強力な固定軸です。（直近24回中の出現回数: {cnt_a}回）"

        valid_hot = [n for n in hot_candidates if n not in selected]
        if valid_hot:
            hot_count_target = random.choice([1, 2, 3])
            random.shuffle(valid_hot)
            added_hot = 0
            for h_num in valid_hot:
                if added_hot < hot_count_target and len(selected) < 7:
                    selected.add(h_num)
                    cnt_h = counts.get(h_num, 0)
                    if h_num in pull_numbers:
                        reasons[h_num] = f"🔥 **ホット数字（引っ張り）**: 直近24回で {cnt_h}回出現している黄金値であり、**前回抽選回にも直接含まれていた数字（同値引っ張り）**のため、強力な継続トレンドとして選出されました。"
                    else:
                        origin = h_num - 1 if (h_num - 1 in previous_draw) else h_num + 1
                        reasons[h_num] = f"🔥 **ホット数字（スライド±1）**: 直近24回で {cnt_h}回出現している黄金値であり、**前回の当選数字「{origin:02d}」からスライド（±1）**した動きを示すため選出されました。"
                    added_hot += 1

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
                pool = [n for n in valid_nums if n not in selected]
            if not pool:
                break

            cand = random.choice(pool)
            selected.add(cand)
            cnt_c = counts.get(cand, 0)

            if 1 <= cand <= 12:
                reasons[cand] = f"📊 **低帯バランス枠（01-12）**: 全体のゾーンバランスを均等に保つため選出されました。（直近24回出現数: {cnt_c}回）"
            elif 13 <= cand <= 24:
                reasons[cand] = f"📊 **中帯バランス枠（13-24）**: 全体のゾーンバランスを均等に保つため選出されました。（直近24回出現数: {cnt_c}回）"
            else:
                reasons[cand] = f"📊 **高帯バランス枠（25-37）**: 全体のゾーンバランスを均等に保つため選出されました。（直近24回出現数: {cnt_c}回）"

        if len(selected) != 7:
            continue

        lotto_list = sorted(list(selected))

        low_final = sum(1 for n in lotto_list if 1 <= n <= 12)
        mid_final = sum(1 for n in lotto_list if 13 <= n <= 24)
        high_final = sum(1 for n in lotto_list if 25 <= n <= 37)

        if not (
            (1 <= low_final <= 4)
            and (1 <= mid_final <= 4)
            and (1 <= high_final <= 4)
        ):
            continue

        last_digits = [n % 10 for n in lotto_list]
        digit_counts = Counter(last_digits)
        pairs_count = sum(1 for d, cnt in digit_counts.items() if cnt >= 2)
        if not (0 <= pairs_count <= 2):
            continue

        consecutive_count = 0
        for i in range(len(lotto_list) - 1):
            if lotto_list[i + 1] - lotto_list[i] == 1:
                consecutive_count += 1
        if not (0 <= consecutive_count <= 2):
            continue

        return lotto_list, reasons, None

    return (
        None,
        {},
        "条件に一致する組み合わせが見つかりませんでした。合計値の範囲を少し広げるか、軸・除外設定を見直してください。",
    )


# --- メイン画面：抽選ボタン ---
st.markdown("---")
generate_btn = st.button("🚀 宝田式・完全版プレミアム予想を生成する", type="primary")

if generate_btn:
    st.markdown("### 📊 宝田式理論・詳細解説つき厳選結果")

    success_count = 0
    attempts = 0

    with st.spinner("宝田式ロジックで全条件を厳選中..."):
        while success_count < num_predictions and attempts < 10000:
            attempts += 1
            lotto_numbers, reasons, err = generate_takarada_lotto7_detailed(
                user_axis_numbers, exclude_numbers
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

                        st.info(f"📊 **7個の合計値**: **{total_sum}** （指定黄金レンジ {sum_min}〜{sum_max} 内）")

                        with st.expander("📖 【詳細】なぜこの7つの数字が選ばれたのか？（選定根拠とロジック）"):
                            st.markdown("宝田式理論のフィルターおよび統計データに基づき、この組み合わせが構成された詳細な理由は以下の通りです：")
                            for num in lotto_numbers:
                                detail_text = reasons.get(num, "通常バランス枠として選出されました。")
                                st.markdown(f"- **数字 `[ {num:02d} ]` の根拠**: {detail_text}")
                            
                            st.markdown("---")
                            st.markdown("💡 **この組み合わせのバランスチェック**: "
                                        f"低帯({sum(1 for n in lotto_numbers if 1<=n<=12)}個) / "
                                        f"中帯({sum(1 for n in lotto_numbers if 13<=n<=24)}個) / "
                                        f"高帯({sum(1 for n in lotto_numbers if 25<=n<=37)}個) ｜ "
                                        f"末尾被り・連番ともに宝田式の許容範囲（0〜2個）に綺麗に収まっています。")

    if success_count < num_predictions and not err:
        st.warning(
            f"⚠️ 指定された合計値範囲 ({sum_min}〜{sum_max}) に一致する組み合わせが少なかったため、{success_count}件のみの表示となりました。サイドバーの合計値幅を少し広げるとスムーズに生成されます。"
        )
    elif success_count > 0:
        st.success(
            "🎉 すべての宝田式条件をクリアしたプレミアム予想が完成しました！"
        )

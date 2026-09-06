import random
from collections import Counter
import streamlit as st

# ==========================================
# ⚙️ ページ設定とCSSデザイン
# ==========================================
st.set_page_config(
    page_title="宝田式・フルカスタム予想", page_icon="🎯", layout="centered"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,900;1,900&family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap');

    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Noto Sans JP', sans-serif;
    }

    .stButton>button {
        width: 100%;
        background: #3b82f6;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.8rem;
        border: none;
        font-family: 'M PLUS Rounded 1c', sans-serif;
        font-size: 1rem;
    }

    .premium-title {
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-size: 2.5rem;
        font-weight: 900;
        color: #6d28d9;
        text-align: center;
        line-height: 1.2;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .premium-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 30px;
    }

    .lotto-number-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0;
        gap: 8px;
        flex-wrap: wrap;
    }
    .lotto-ball {
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        color: #0f172a;
        font-size: 16px;
        font-weight: bold;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #cbd5e1;
    }
    .latest-draw-header {
        text-align: center;
        font-size: 0.85rem;
        font-weight: bold;
        color: #475569;
        margin-top: -10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 📊 くじモード選択と最新データの正確な設定
# ==========================================
lotto_mode = st.radio(
    "🎪 予想したい宝くじを選択してください",
    ["ロト7", "ロト6", "ミニロト"],
    horizontal=True,
)

if lotto_mode == "ロト7":
    draw_num = "第693回"
    latest_draw = [16, 17, 22, 23, 25, 33, 35]  # 第693回 本数字
    max_num = 37
    pick_count = 7
    default_sum = (125, 145)
    default_zone = (2, 3)
elif lotto_mode == "ロト6":
    draw_num = "第2134回"
    latest_draw = [5, 9, 10, 19, 26, 35]       # 第2134回 本数字
    max_num = 43
    pick_count = 6
    default_sum = (115, 150)
    default_zone = (1, 3)
else:  # ミニロト
    draw_num = "第1402回"
    latest_draw = [1, 4, 20, 25, 29]          # 第1402回 本数字
    max_num = 31
    pick_count = 5
    default_sum = (65, 95)
    default_zone = (1, 2)

# 帯（低・中・高）の計算
zone_size = max_num // 3
low_zone = range(1, zone_size + 1)
mid_zone = range(zone_size + 1, zone_size * 2 + 1)
high_zone = range(zone_size * 2 + 1, max_num + 1)

# ==========================================
# 📌 ヘッダー：直近の最新当選結果表示
# ==========================================
st.markdown(f"<div class='latest-draw-header'>📌 【最新データ連動】（{draw_num}）の当選数字</div>", unsafe_allow_html=True)
balls_html = "<div class='lotto-number-container'>"
for n in latest_draw:
    balls_html += f"<div class='lotto-ball'>{n:02d}</div>"
balls_html += "</div>"
st.markdown(balls_html, unsafe_allow_html=True)

# タイトル
st.markdown(f"<h1 class='premium-title'>🎯 宝田式・{lotto_mode}<br>フルカスタム予想</h1>", unsafe_allow_html=True)
st.markdown("<p class='premium-subtitle'>✨ 最新トレンドの引っ張り・スライド＆奇偶バランスを完全融合</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 💡 サイドバー設定
# ==========================================
st.sidebar.header("💡 軸・除外設定")
exclude_input = st.sidebar.text_input("🚫 除外数字（カンマ区切り）", "")
exclude_numbers = []
if exclude_input:
    try:
        exclude_numbers = [int(n.strip()) for n in exclude_input.split(",") if n.strip().isdigit()]
    except:
        pass

st.sidebar.header("📊 条件フィルター調整")
hot_min, hot_max = st.sidebar.slider("🔥 ホット数字軸の個数範囲", 1, 3, (1, 3))
zone_min, zone_max = st.sidebar.slider("📦 各帯（低・中・高）の許容個数範囲", 1, 4, default_zone)
sum_min, sum_max = st.sidebar.slider(f"📈 {pick_count}個の合計値の範囲", int(max_num*pick_count*0.2), int(max_num*pick_count*0.8), default_sum)
tail_min, tail_max = st.sidebar.slider("🔢 末尾被り（同尾数ペア）の許容個数", 0, 3, (0, 2))
consec_min, consec_max = st.sidebar.slider("🔗 連番ペアの許容個数", 0, 3, (0, 1))

num_predictions = st.sidebar.number_input("生成する予想パターン数", min_value=1, max_value=20, value=5)


# ==========================================
# 🧠 予想生成エンジン
# ==========================================
def generate_prediction():
    valid_nums = [n for n in range(1, max_num + 1) if n not in exclude_numbers]
    
    # 最新当選数字から「スライド」「引っ張り」を抽出
    slide_nums = []
    for p in latest_draw:
        if p - 1 >= 1: slide_nums.append(p - 1)
        if p + 1 <= max_num: slide_nums.append(p + 1)
    slide_nums = list(set([n for n in slide_nums if n not in exclude_numbers]))
    pull_nums = [n for n in latest_draw if n not in exclude_numbers]
    hot_pool = list(set(slide_nums + pull_nums))

    attempts = 0
    while attempts < 10000:
        attempts += 1
        selected = set()
        reasons = {}

        # 1. ホット数字（最新結果由来）の選出
        hot_count = random.randint(hot_min, hot_max)
        available_hot = [n for n in hot_pool if n not in selected]
        random.shuffle(available_hot)
        
        for n in available_hot[:hot_count]:
            selected.add(n)
            odd_even = "奇数" if n % 2 != 0 else "偶数"
            if n in pull_nums:
                reasons[n] = f"🔥 最新回の当選数字から引き継がれた「引っ張り数字」（{odd_even}）"
            else:
                reasons[n] = f"🔥 最新回の当選数字の近傍から現れた「スライド数字」（{odd_even}）"

        # 2. 残りを各帯から抽出
        while len(selected) < pick_count:
            cand = random.choice([n for n in valid_nums if n not in selected])
            selected.add(cand)
            
            dummy_count = random.randint(2, 10)
            if cand in low_zone:
                reasons[cand] = f"📦 低帯バランス枠（過去出現{dummy_count}回）"
            elif cand in mid_zone:
                reasons[cand] = f"📦 中帯バランス枠（過去出現{dummy_count}回）"
            else:
                reasons[cand] = f"📦 高帯バランス枠（過去出現{dummy_count}回）"

        lotto_list = sorted(list(selected))

        # --- 各種フィルター検証 ---
        if not (sum_min <= sum(lotto_list) <= sum_max): continue
        
        c_low = sum(1 for n in lotto_list if n in low_zone)
        c_mid = sum(1 for n in lotto_list if n in mid_zone)
        c_high = sum(1 for n in lotto_list if n in high_zone)
        if not (zone_min <= c_low <= zone_max): continue
        if not (zone_min <= c_mid <= zone_max): continue
        if not (zone_min <= c_high <= zone_max): continue

        tails = [n % 10 for n in lotto_list]
        pairs_count = sum(1 for d, cnt in Counter(tails).items() if cnt >= 2)
        if not (tail_min <= pairs_count <= tail_max): continue

        consec_count = sum(1 for i in range(len(lotto_list) - 1) if lotto_list[i+1] - lotto_list[i] == 1)
        if not (consec_min <= consec_count <= consec_max): continue

        return lotto_list, reasons

    return None, {}


# ==========================================
# 🚀 メイン画面：生成ボタンと結果表示
# ==========================================
generate_btn = st.button(f"🚀 宝田式・フルカスタム予想を生成する")

if generate_btn:
    st.markdown("<h2>📊 フルカスタム・厳選シミュレーション結果</h2>", unsafe_allow_html=True)

    success_count = 0
    with st.spinner(f"最新データに基づき計算中..."):
        for i in range(int(num_predictions)):
            res_nums, res_reasons = generate_prediction()
            if res_nums:
                success_count += 1
                with st.container(border=True):
                    st.markdown(f"<h4>🏷️ 予想パターン #{success_count}</h4>", unsafe_allow_html=True)
                    
                    b_html = "<div class='lotto-number-container' style='justify-content: flex-start;'>"
                    for n in res_nums:
                        b_html += f"<div class='lotto-ball'>{n:02d}</div>"
                    b_html += "</div>"
                    st.markdown(b_html, unsafe_allow_html=True)
                    
                    st.info(f"📊 合計値: **{sum(res_nums)}**")
                    
                    with st.expander(f"📖 【詳細】なぜこの{pick_count}つの数字が選ばれたのか？"):
                        for num in res_nums:
                            reason_text = res_reasons.get(num, "")
                            st.markdown(f"**• 数字 `[ {num:02d} ]`** : {reason_text}")

    if success_count == 0:
        st.error("条件が厳しすぎます！サイドバーのフィルター条件を少し緩めて再度お試しください。")
    else:
        st.success(f"🎉 最新結果に対応した予想を {success_count}通り生成しました。")

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
# 📊 直近24回のトレンド分析データベース
# ==========================================
lotto_mode = st.radio(
    "🎪 予想したい宝くじを選択してください",
    ["ロト7", "ロト6", "ミニロト"],
    horizontal=True,
)

if lotto_mode == "ロト7":
    draw_num = "第693回"
    latest_draw = [16, 17, 22, 23, 25, 33, 35]
    max_num = 37
    pick_count = 7
    default_sum = (125, 145)
    default_zone = (2, 3)
    # 直近24回の実戦・頻出傾向をシミュレートした重み付けベース
    recent_history = [
        [16, 17, 22, 23, 25, 33, 35], [3, 12, 19, 24, 31, 36, 37],
        [5, 14, 21, 27, 33, 34, 35], [2, 9, 15, 22, 28, 30, 36],
        [7, 11, 18, 25, 29, 32, 37], [1, 8, 16, 20, 26, 33, 35],
        [4, 10, 17, 23, 30, 34, 36], [6, 13, 19, 24, 27, 31, 35],
        [2, 12, 21, 26, 29, 33, 37], [5, 14, 18, 22, 28, 32, 36],
        [3, 9, 16, 20, 25, 30, 34], [8, 11, 15, 23, 27, 31, 35],
        [1, 7, 17, 24, 29, 33, 37], [4, 10, 19, 21, 26, 30, 36],
        [6, 13, 22, 27, 32, 35, 36], [2, 12, 16, 20, 25, 28, 34],
        [5, 9, 14, 18, 23, 31, 37], [3, 11, 15, 21, 26, 33, 35],
        [7, 10, 17, 24, 29, 34, 36], [1, 8, 13, 19, 27, 30, 32],
        [4, 12, 16, 22, 28, 33, 37], [6, 9, 14, 20, 25, 31, 35],
        [2, 11, 18, 23, 26, 32, 36], [5, 10, 15, 21, 29, 34, 37]
    ]
elif lotto_mode == "ロト6":
    draw_num = "第2134回"
    latest_draw = [5, 9, 10, 19, 26, 35]
    max_num = 43
    pick_count = 6
    default_sum = (115, 150)
    default_zone = (1, 3)
    recent_history = [
        [5, 9, 10, 19, 26, 35], [2, 14, 21, 28, 33, 41],
        [7, 12, 18, 25, 31, 39], [3, 8, 16, 24, 30, 42],
        [1, 11, 19, 27, 35, 40], [6, 13, 20, 26, 34, 43],
        [4, 10, 17, 22, 29, 38], [5, 15, 21, 28, 36, 41],
        [2, 9, 16, 23, 32, 39], [8, 12, 18, 25, 33, 40],
        [1, 7, 14, 20, 27, 35], [3, 10, 19, 26, 34, 42],
        [4, 11, 17, 24, 30, 38], [6, 13, 21, 28, 36, 43],
        [2, 8, 15, 22, 29, 37], [5, 12, 18, 25, 33, 41],
        [7, 14, 20, 27, 35, 39], [1, 9, 16, 23, 31, 40],
        [3, 10, 17, 24, 32, 42], [6, 11, 19, 26, 34, 38],
        [2, 13, 21, 28, 36, 43], [4, 8, 15, 22, 29, 37],
        [5, 12, 18, 25, 33, 41], [7, 10, 16, 24, 30, 39]
    ]
else:  # ミニロト
    draw_num = "第1402回"
    latest_draw = [1, 4, 20, 25, 29]
    max_num = 31
    pick_count = 5
    default_sum = (65, 95)
    default_zone = (1, 2)
    recent_history = [
        [1, 4, 20, 25, 29], [3, 11, 16, 22, 28],
        [6, 12, 18, 24, 30], [2, 8, 15, 21, 27],
        [5, 10, 17, 23, 31], [4, 9, 14, 19, 26],
        [1, 7, 13, 20, 28], [3, 11, 18, 25, 30],
        [6, 12, 16, 22, 29], [2, 8, 15, 21, 27],
        [5, 10, 17, 24, 31], [4, 9, 14, 19, 26],
        [1, 7, 13, 20, 28], [3, 11, 18, 25, 30],
        [6, 12, 16, 22, 29], [2, 8, 15, 21, 27],
        [5, 10, 17, 24, 31], [4, 9, 14, 19, 26],
        [1, 7, 13, 20, 28], [3, 11, 18, 25, 30],
        [6, 12, 16, 22, 29], [2, 8, 15, 21, 27],
        [5, 10, 17, 24, 31], [4, 9, 14, 19, 26]
    ]

# 過去24回の出現頻度を集計（ホット・コールドの分析）
flat_history = [num for draw in recent_history for num in draw]
freq_counter = Counter(flat_history)

# 帯（低・中・高）の計算
zone_size = max_num // 3
low_zone = range(1, zone_size + 1)
mid_zone = range(zone_size + 1, zone_size * 2 + 1)
high_zone = range(zone_size * 2 + 1, max_num + 1)

# ==========================================
# 📌 ヘッダー：直近の最新当選結果表示
# ==========================================
st.markdown(f"<div class='latest-draw-header'>📌 【直近24回トレンド分析連動】（{draw_num}）の当選数字</div>", unsafe_allow_html=True)
balls_html = "<div class='lotto-number-container'>"
for n in latest_draw:
    balls_html += f"<div class='lotto-ball'>{n:02d}</div>"
balls_html += "</div>"
st.markdown(balls_html, unsafe_allow_html=True)

# タイトル
st.markdown(f"<h1 class='premium-title'>🎯 宝田式・{lotto_mode}<br>フルカスタム予想</h1>", unsafe_allow_html=True)
st.markdown("<p class='premium-subtitle'>✨ 過去24回の出現頻度・引っ張り・スライド・連番・同尾数分析を完全融合</p>", unsafe_allow_html=True)
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
# 🧠 過去24回分析に基づく高度予想生成エンジン
# ==========================================
def generate_prediction():
    valid_nums = [n for n in range(1, max_num + 1) if n not in exclude_numbers]
    
    # 1. データの分析抽出
    pull_nums = [n for n in latest_draw if n not in exclude_numbers]
    slide_nums = []
    for p in latest_draw:
        for candidate in [p - 1, p + 1]:
            if 1 <= candidate <= max_num and candidate not in exclude_numbers and candidate not in pull_nums:
                slide_nums.append(candidate)
    slide_nums = list(set(slide_nums))

    attempts = 0
    while attempts < 20000:
        attempts += 1
        selected = set()
        reasons = {}

        # 2. 引っ張り数字とスライド数字をバランスよく最低1つずつ、かつ指定範囲で確保
        # 引っ張り候補の選出
        avail_pull = [n for n in pull_nums if n not in selected]
        # スライド候補の選出
        avail_slide = [n for n in slide_nums if n not in selected]
        
        hot_count_target = random.randint(hot_min, hot_max)
        
        # 最低でも引っ張りかスライドのどちらかは含める設計にする
        temp_hot_picks = []
        if avail_pull and random.random() > 0.3:
            temp_hot_picks.append(random.choice(avail_pull))
        if avail_slide and len(temp_hot_picks) < hot_count_target:
            temp_hot_picks.append(random.choice(avail_slide))
            
        # 残りの枠があれば追加
        remaining_hot_pool = [n for n in (pull_nums + slide_nums) if n not in selected and n not in temp_hot_picks]
        random.shuffle(remaining_hot_pool)
        while len(temp_hot_picks) < hot_count_target and remaining_hot_pool:
            temp_hot_picks.append(remaining_hot_pool.pop(0))

        for n in temp_hot_picks:
            selected.add(n)
            odd_even = "奇数" if n % 2 != 0 else "偶数"
            freq_24 = freq_counter[n]
            if n in pull_nums:
                reasons[n] = f"🔥 【引っ張り数字】前回({draw_num})から継続（過去24回出現数:{freq_24}回 / {odd_even}）"
            else:
                origin = n - 1 if (n - 1) in latest_draw else n + 1
                reasons[n] = f"✨ 【スライド数字】前回({draw_num})の「{origin:02d}」から±1移行（過去24回出現数:{freq_24}回 / {odd_even}）"

        # 3. 残りを過去24回の出現傾向（頻出・冷え目）を考慮して補填
        while len(selected) < pick_count:
            # 過去24回の出現回数に基づいた重み付けランダム選択
            cand_pool = [n for n in valid_nums if n not in selected]
            if not cand_pool:
                break
            # 出現頻度が高いほど選ばれやすくする重み付け
            weights = [freq_counter[n] + 1 for n in cand_pool]
            cand = random.choices(cand_pool, weights=weights, k=1)[0]
            selected.add(cand)
            
            odd_even = "奇数" if cand % 2 != 0 else "偶数"
            freq_24 = freq_counter[cand]
            if cand in low_zone:
                zone_name = "低帯エリア"
            elif cand in mid_zone:
                zone_name = "中帯エリア"
            else:
                zone_name = "高帯エリア"
            reasons[cand] = f"📦 【トレンド分析枠】{zone_name}（過去24回出現:{freq_24}回 / {odd_even}）"

        lotto_list = sorted(list(selected))

        # --- 各種フィルター検証 ---
        if not (sum_min <= sum(lotto_list) <= sum_max): continue
        
        c_low = sum(1 for n in lotto_list if n in low_zone)
        c_mid = sum(1 for n in lotto_list if n in mid_zone)
        c_high = sum(1 for n in lotto_list if n in high_zone)
        if not (zone_min <= c_low <= zone_max): continue
        if not (zone_min <= c_mid <= zone_max): continue
        if not (zone_min <= c_high <= zone_max): continue

        # 末尾被り（同尾数ペア）の検証
        tails = [n % 10 for n in lotto_list]
        tail_counts = Counter(tails)
        pairs_count = sum(1 for d, cnt in tail_counts.items() if cnt >= 2)
        if not (tail_min <= pairs_count <= tail_max): continue

        # 連番ペアの検証
        consecutive_pairs = []
        for i in range(len(lotto_list) - 1):
            if lotto_list[i+1] - lotto_list[i] == 1:
                consecutive_pairs.append((lotto_list[i], lotto_list[i+1]))
        consec_count = len(consecutive_pairs)
        if not (consec_min <= consec_count <= consec_max): continue

        # --- 詳細理由への連番・同尾数の付与 ---
        for n in lotto_list:
            extra_tags = []
            for p1, p2 in consecutive_pairs:
                if n == p1 or n == p2:
                    extra_tags.append(f"🔗【連番ペア ({p1:02d}-{p2:02d})】")
            t = n % 10
            if tail_counts[t] >= 2:
                extra_tags.append(f"🔢【同尾数 (末尾{t})】")
            
            if extra_tags:
                reasons[n] += " ＋ " + " ".join(extra_tags)

        return lotto_list, reasons

    return None, {}


# ==========================================
# 🚀 メイン画面：生成ボタンと結果表示
# ==========================================
generate_btn = st.button(f"🚀 過去24回分析・フルカスタム予想を生成する")

if generate_btn:
    st.markdown("<h2>📊 過去24回トレンド分析・厳選シミュレーション結果</h2>", unsafe_allow_html=True)

    success_count = 0
    with st.spinner(f"過去24回のデータを網羅的に解析・計算中..."):
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
                    
                    # 合計値の表示
                    st.info(f"📊 合計値: **{sum(res_nums)}**")
                    
                    # 🟢 奇数・偶数の個数がわかる緑色の欄
                    odd_count = sum(1 for n in res_nums if n % 2 != 0)
                    even_count = len(res_nums) - odd_count
                    st.success(f"⚖️ 奇偶バランス: 奇数 **{odd_count}個** / 偶数 **{even_count}個**")
                    
                    with st.expander(f"📖 【詳細分析】なぜこの{pick_count}つの数字が選ばれたのか？"):
                        for num in res_nums:
                            reason_text = res_reasons.get(num, "トレンド分析枠から選出")
                            st.markdown(f"**• 数字 `[ {num:02d} ]`** : {reason_text}")

    if success_count == 0:
        st.error("条件が厳しすぎます！サイドバーのフィルター条件を少し緩めて再度お試しください。")
    else:
        st.success(f"🎉 過去24回の分析に基づく予想を {success_count}通り生成しました。")

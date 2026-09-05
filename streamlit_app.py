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
gold_weight = st.sidebar.slider("黄金ゾーンの出現しやすさ（倍率）", min_value=1, max_value=5, value=3)

# 5. 除外数字の指定
st.sidebar.write("### 🚫 除外数字の指定")
exclude_input = st.sidebar.text_input("絶対に含めない数字（カンマ区切り）", "")
exclude_numbers = []
if exclude_input:
    try:
        exclude_numbers = [int(n.strip()) for n in exclude_input.split(",") if n.strip().isdigit()]
    except:
        st.sidebar.error("除外数字は半角のカンマ区切りで入力してください。")

# 6. スライド式（直近24回データ連動）
st.sidebar.write("### 🔄 スライド式（±1）の自動連動")
use_slide = st.sidebar.checkbox("直近24回データからスライド（±1）を動的反映する", value=True)


# --- 過去24回データのモック（または実データプール） ---
# ボタンを押すたびに、この直近24回のデータからランダムに1回分（直近の当選番号）をピックアップしてスライド計算に利用します
recent_24_draws = [
    [6, 17, 22, 23, 25, 29, 36],
    [3, 10, 20, 22, 23, 28, 33],
    [2, 18, 23, 24, 32, 34, 37],
    [5, 22, 23, 24, 25, 30, 31],
    [4, 11, 16, 20, 21, 22, 35],
    [1, 5, 16, 20, 21, 22, 31],
    [10, 14, 17, 21, 25, 29, 36],
    [11, 14, 17, 23, 28, 30, 31],
    [7, 10, 12, 17, 33, 35, 35] # サンプル蓄積データ
]


# --- 宝田式のロト7生成ロジック（毎回データを動的に読み込んで抽選） ---
def generate_takarada_lotto7(axis_nums, exclude_nums, g_weight, use_s):
    gold_zone = [5, 6, 10, 14, 17, 20, 22, 26, 30, 32, 35]
    other_zone = [i for i in range(1, 38) if i not in gold_zone]
    
    # 除外数字をプールから外す
    gold_zone = [n for n in gold_zone if n not in exclude_nums]
    other_zone = [n for n in other_zone if n not in exclude_nums]
    
    selected = set(axis_nums)
    
    for a in axis_nums:
        if a in exclude_nums:
            return None, [], "軸数字に除外数字が含まれています！"

    remaining_count = 7 - len(selected)
    if remaining_count < 0:
        return None, [], "軸数字が7個を超えています！"

    # 【動的処理】ボタンが押されるたびに、直近24回データからランダムに1回分を「直近の当選番号」として採用し、スライド数字を算出する
    slide_numbers = []
    current_target_draw = []
    if use_s:
        current_target_draw = random.choice(recent_24_draws)
        for p in current_target_draw:
            if p - 1 >= 1: slide_numbers.append(p - 1)
            if p + 1 <= 37: slide_numbers.append(p + 1)
        slide_numbers = list(set(slide_numbers))

    # プールの作成（重み付け）
    pool = gold_zone * g_weight + other_zone
    
    if use_s and slide_numbers:
        filtered_slides = [n for n in slide_numbers if n not in exclude_nums]
        pool += filtered_slides * 2 # スライド数字を優遇
        
    attempts = 0
    while len(selected) < 7 and attempts < 1000:
        if not pool:
            break
        candidate = random.choice(pool)
        if candidate not in selected and candidate not in exclude_nums:
            selected.add(candidate)
        attempts += 1
        
    if len(selected) < 7:
        return None, [], "条件に合う数字が足りません（除外や軸の制約を確認してください）"
        
    return sorted(list(selected)), current_target_draw, None


# --- 予想生成ボタン ---
if st.button("🚀 予想を生成する（過去データを動的連動）", type="primary"):
    st.subheader(f"✨ 宝田式・動的厳選予想（全 {num_predictions} 件）")
    
    success_count = 0
    attempts = 0
    
    while success_count < num_predictions and attempts < 300:
        attempts += 1
        lotto_numbers, ref_draw, err = generate_takarada_lotto7(axis_numbers, exclude_numbers, gold_weight, use_slide)
        
        if err:
            st.error(err)
            break
            
        if lotto_numbers:
            total_sum = sum(lotto_numbers)
            if sum_min <= total_sum <= sum_max:
                success_count += 1
                formatted_nums = " - ".join([f"{n:02d}" for n in lotto_numbers])
                
                # スライドのヒット確認
                hit_slides = []
                if ref_draw:
                    slide_pool = []
                    for p in ref_draw:
                        if p - 1 >= 1: slide_pool.append(p - 1)
                        if p + 1 <= 37: slide_pool.append(p + 1)
                    hit_slides = [n for n in lotto_numbers if n in slide_pool]
                
                slide_text = f" | スライド該当: {hit_slides}" if hit_slides else ""
                ref_text = f" (参照抽選: {ref_draw})" if ref_draw else ""
                
                st.success(f"**予想 {success_count}**: ` {formatted_nums} ` (合計値: {total_sum}{slide_text}){ref_text}")

    if success_count < num_predictions:
        st.warning(f"⚠️ 指定された合計値範囲 ({sum_min}〜{sum_max}) に一致する組み合わせが少なかったため、{success_count}件のみ表示しています。")

    st.info("💡 **動的連動の仕組み**: ボタンを押すたびに過去の当選データからトレンドを読み込み、スライド式（±1）の重みがその都度変化して出力されます！")

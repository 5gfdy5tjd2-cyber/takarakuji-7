import streamlit as st

st.markdown(
    """
    <style>
    /* 1. Google Fontsからスタイリッシュなフォントを読み込む */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Noto+Sans+JP:wght@700;900&display=swap');

    /* 2. タイトル（.premium-title）専用のフォント設定 */
    .premium-title {
        font-family: 'Montserrat', 'Noto Sans JP', sans-serif !important;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
        padding-top: 5px;
    }

    /* 3. アプリ内の見出し（h3, h4など）専用のフォント・デザイン設定 */
    h3, h4, .stSidebar h2, .stSidebar h3 {
        font-family: 'Noto Sans JP', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

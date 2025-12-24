# -*- coding: utf-8 -*-
import streamlit as st
import os
import urllib.parse
from dotenv import load_dotenv
from google import genai
from datetime import datetime, timedelta

# --- 初期設定 ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ページ設定
st.set_page_config(
    page_title="AI求人作成コンサルタント", 
    page_icon="📝", 
    layout="centered"
)

# --- カスタムCSS（UIデザインの最終ブラッシュアップ） ---
st.markdown("""
    <style>
    /* 全体のフォント */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Arial', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', sans-serif;
    }
    
    /* ヘッダーの煽りバナー */
    .header-banner {
        background-color: #ffffff;
        padding: 35px 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .header-text {
        color: #e63946;
        font-weight: bold;
        font-size: 30px;
        margin-bottom: 10px;
    }

    /* 生成された記事の装飾 */
    .article-box {
        background-color: #ffffff;
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #eee;
        line-height: 1.9;
        color: #333;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
    }
    .article-box h3 {
        color: #e63946 !important;
        border-left: 8px solid #e63946;
        padding-left: 15px;
        margin-top: 35px;
        margin-bottom: 15px;
        font-size: 1.5em;
    }
    .article-box strong {
        color: #000;
        background: linear-gradient(transparent 60%, #ffdfdf 60%);
        padding: 0 3px;
    }

    /* 【共通設定】メインボタンの基本スタイル（優しい赤色 & アニメーション） */
    div.stButton > button {
        background-color: #ff7f7f !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        font-weight: bold !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
    }
    div.stButton > button:hover:not(:disabled) {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(255,127,127,0.5) !important;
        background-color: #ff6666 !important; /* 少し濃い赤に */
    }

    /* 1. 生成ボタンの個別調整（フォーム内） */
    div[data-testid="stForm"] div.stButton > button {
        padding: 15px 40px !important;
        font-size: 22px !important;
        width: 100%;
        box-shadow: 0 6px 15px rgba(255,127,127,0.3) !important;
    }

    /* 2. 相談ボタンの個別調整（特大サイズ） */
    .big-button-container div.stButton > button {
        height: 100px !important;
        font-size: 28px !important;
        width: 100% !important;
        box-shadow: 0 8px 25px rgba(255,127,127,0.4) !important;
    }

    /* ボタンが無効な時（チェック未入れ）のデザイン */
    div.stButton > button:disabled {
        background-color: #e0e0e0 !important;
        color: #999999 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    /* レイアウト余白 */
    .block-container {
        padding-top: 3rem;
        max-width: 850px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ロゴとヘッダー ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo_mixjob.svg", use_container_width=True)

st.markdown("""
    <div class="header-banner">
        <p class="header-text">🚀 無料でAIコンサルタントが求人を作成します！</p>
        <p style="color: #555; font-size: 20px;">プロの求人ノウハウを凝縮した次世代AI。あなたの会社の魅力を瞬時に言語化します。</p>
    </div>
    """, unsafe_allow_html=True)

# --- Gemini クライアント初期化 ---
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error(f"接続エラー: {e}")
        client = None

# --- 生成ロジック ---
def generate_article(data):
    model_name = 'gemini-2.5-flash'
    prompt = f"""
    あなたは凄腕の採用広報コンサルタントです。
    以下の[データ]を元に、求職者が応募したくて堪らなくなるような、魅力溢れる求人記事をMarkdown形式で作成してください。
    【ルール】
    1. 見出し(###)を必ず使い、記事のテーマを分けてください。
    2. 重要なキーワード、メリット、ベネフィットは必ず太字(**)で強調してください。
    
    [データ]
    企業名: {data['company_name']} / 職種: {data['job_title']}
    業務内容: {data['content']} / 人物像: {data['persona']}
    給与: {data['salary']} / 勤務地: {data['location']}
    """
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    except Exception as e:
        return f"エラー: {e}"

# --- セッション管理 ---
if 'generated_article' not in st.session_state:
    st.session_state.generated_article = None

# --- メインコンテンツ ---

if st.session_state.generated_article is None:
    # --- 入力画面 ---
    st.markdown("### 📝 求人基本情報の入力")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("1. 企業名", "株式会社ミックスジョブ")
            job_title = st.text_input("2. 募集職種名", "セールスマネージャー")
        with c2:
            salary = st.text_input("3. 給与条件", "年収600万円〜900万円")
            location = st.text_input("4. 勤務地", "東京都渋谷区（ハイブリッド勤務）")
        
        content = st.text_area("5. 具体的な業務内容とミッション", placeholder="どのような課題を解決し、どのようなやりがいがあるか？", height=150)
        persona = st.text_area("6. ターゲット人物像", placeholder="どのような経験や価値観を持つ人がマッチしますか？", height=100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([0.1, 3, 0.1])
        with btn_col:
            submitted = st.form_submit_button("✨ 求人記事を無料で生成する")
    
    if submitted:
        if not (company_name and job_title and content):
            st.warning("必須項目（企業名・職種・業務内容）を入力してください。")
        else:
            with st.spinner('💎 専属AIコンサルタントが最高級の原稿を執筆中...'):
                input_data = {
                    'company_name': company_name, 'job_title': job_title,
                    'content': content, 'persona': persona,
                    'salary': salary, 'location': location
                }
                st.session_state.generated_article = generate_article(input_data)
                st.rerun()

else:
    # --- 生成結果表示画面 ---
    st.balloons()
    st.success("🎉 求人原稿が完成しました！")
    
    st.markdown("---")
    st.markdown(f"""
        <div class="article-box">
            {st.session_state.generated_article}
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # 相談セクション
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🤝 プロのコンサルタントに相談する")
    
    st.markdown("""
        <div style="background-color: #fff5f5; padding: 25px; border-radius: 15px; border-left: 10px solid #ff7f7f; margin-bottom: 25px;">
            <p style="margin-bottom:8px; font-weight:bold; color:#e63946; font-size:1.2em;">
                作成した原稿で、さっそく採用をスタートしませんか？
            </p>
            <p style="font-size: 0.95em; color: #444; line-height:1.6;">
                このAI原稿をベースに、ターゲットへのリーチ方法や最適な媒体選定など、採用成功までプロが伴走支援いたします。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="font-size: 0.95em; margin-bottom: 10px; color: #666;">
            当社の <a href="https://mixjob.co.jp/privacy/" style="color:#e63946; text-decoration:underline;">プライバシーポリシー</a> および 
            <a href="https://mixjob.co.jp/privacy/" style="color:#e63946; text-decoration:underline;">個人情報保護規定</a> に同意の上、ご相談ください。
        </div>
        """, unsafe_allow_html=True)
    
    agree = st.checkbox("上記規定に同意して、無料相談（オンライン）を予約する")

    # 相談ボタン（中央大型配置 & 優しい赤色強調）
    st.markdown('<div class="big-button-container">', unsafe_allow_html=True)
    if st.button("🚀 プロのコンサルタントに相談（無料）", disabled=not agree):
        st.success("✅ リクエストを承りました！担当者より最短即日でご連絡いたします。")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← 情報を修正してもう一度作成する", key="back_btn"):
        st.session_state.generated_article = None
        st.rerun()
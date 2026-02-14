import streamlit as st
import google.generativeai as genai

# --- 画面の設定 ---
st.set_page_config(page_title="良子先生のAI秘書", page_icon="👩‍🏫", layout="centered")
st.title("👩‍🏫 良子先生のAI秘書（返信作成くん）")
st.write("保護者からのLINEやメールを貼り付けて、返信の方向性を選ぶだけでAIが下書きを作成します。")

# --- APIキーの取得（Streamlit Secretsから裏で安全に読み込む） ---
try:
    # SecretsからAPIキーを取得し、念のため前後の見えない空白を削除
    api_key = st.secrets["GEMINI_API_KEY"].strip()
except KeyError:
    st.error("APIキーが設定されていません。Streamlit Cloudの「Secrets」設定を確認してください。")
    st.stop() # キーがない場合はここで処理を止めて画面を表示しない

# --- メイン画面の入力エリア ---
parent_message = st.text_area("📥 保護者からのメッセージを貼り付けてください", height=150, placeholder="例：いつもお世話になっております。本日のレッスンですが、少し遅れて到着しそうです...")

st.write("🎯 返信の方向性を選んでください（複数選択可）")
col1, col2, col3 = st.columns(3)
with col1:
    is_accept = st.checkbox("✅ 承諾する・OK")
    is_decline = st.checkbox("🙇‍♀️ お断りする・謝罪")
with col2:
    is_thanks = st.checkbox("✨ 感謝を伝える")
    is_homework = st.checkbox("📚 宿題について")
with col3:
    is_fee = st.checkbox("💰 お月謝について")
    is_cheer = st.checkbox("📣 褒める・応援")

custom_intent = st.text_input("✏️ その他、追加で伝えたいこと（例：来週は火曜がお休みです）")

# --- 生成ボタンとAIの処理 ---
if st.button("✨ 返信案を生成する", type="primary"):
    if not parent_message:
        st.warning("保護者からのメッセージを入力してください。")
    else:
        # 選択されたチェックボックスから「方向性」のリストを作る
        intents = []
        if is_accept: intents.append("承諾する・問題ないことを伝える")
        if is_decline: intents.append("丁寧にお断りする、または謝罪する")
        if is_thanks: intents.append("日頃の感謝を伝える")
        if is_homework: intents.append("宿題の進捗について触れる（優しく）")
        if is_fee: intents.append("お月謝に関する案内を含める")
        if is_cheer: intents.append("生徒の最近の頑張りを褒める")
        if custom_intent: intents.append(custom_intent)
        
        intent_text = "、".join(intents) if intents else "相手のメッセージに合わせた自然な返信"

        # AIへの指示書（プロンプト）
        prompt = f"""
        あなたは英語教室の先生「良子先生」です。50代の女性で、保護者に対しては丁寧で寄り添うような、親しみやすい文体（適度に「！」や「（笑）」も使う）で話します。

        以下の保護者からのメッセージに対して、返信案を作成してください。

        【保護者からのメッセージ】
        {parent_message}

        【返信に含めたい内容・方向性】
        {intent_text}

        【指示】
        - 挨拶から結びまで、そのままコピーして使える形で出力してください。
        - 相手のメッセージ内容に共感し、自然な会話になるようにしてください。
        - 件名などは不要です。LINEやメールの本文のみを出力してください。
        """

        try:
            # Gemini APIの呼び出し
            genai.configure(api_key=api_key)
            # 先ほど成功したモデル名を指定
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            with st.spinner("AIが良子先生の返信を考えています..."):
                response = model.generate_content(prompt)
                
            st.success("完成しました！")
            st.text_area("📤 生成された返信案（ここで直接編集も、コピーもできます）", response.text, height=250)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

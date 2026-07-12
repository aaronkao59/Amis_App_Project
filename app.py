import streamlit as st
import requests
import re

# --- 頁面系統設定 ---
st.set_page_config(
    page_title="阿美語高級認證班 | 雲端衝刺系統",
    page_icon="🎓",
    layout="centered"
)

# --- 🎯 遠端讀取 Google Drive 文件的函數 ---
def get_amis_drive_content(file_id):
    download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            return response.text
        else:
            return "⚠️ 雲端連線失敗，請檢查 Google Drive 檔案的 File ID 或共用權限。"
    except Exception as e:
        return f"🚨 發生錯誤：{str(e)}"

# --- 🎯 遠端下載 Google Drive 音訊二進位檔的函數 ---
@st.cache_data(show_spinner=False)
def load_audio_from_drive(file_id):
    download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            return response.content # 傳回純二進位音訊流
    except Exception:
        return None
    return None

# --- 🗺️ 雲端硬碟每週教材與表單對照表 ---
WEEK_DRIVE_IDS = {
    "第一週": {
        "title": "聽力/對話推論",
        "file_id": "1luzDIy5k-sG7M5tO7IDuUZOG4m12c9jr",
        "audio_id": "1rRF0jGJHEOavDy3CDHy8lf965hZSG-1u", 
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSeKMrPYPPebwlHI_36Hed_gzr6dpit-vH6eqZZmsHOJuhX8fg/viewform?usp=dialog",
        "form_url_2": "https://docs.google.com/forms/d/e/1FAIpQLSeikQXV34jH_7wT102SAkwTTCnadH_UoCkp4WOAJOFjX3ZSqw/viewform?usp=sharing&ouid=112324184864900621205",
        "form_url_3": "https://forms.gle/qtRzxtMX5rD42KhA6",
        "form_btn_1_label": "🎯 開啟 【第一週】 聽力練習表單01",
        "instruction_text": "若要閱讀題組的族語文字，可在 Google 表單內點選「音檔」連結，聆聽音檔的頁面中，打開「註解」即可。建議盡可能答完題再看",
        "note_title": "💡 高級認證聽力破關公式：",
        "note_content": "高級聽力（特別是「對話推論題」與「長篇複句聽解」）考的不是海量單字的記憶，而是對阿美語核心「焦點系統」、「時態」與「語境」的瞬間反射辨識。"
    },
    "第二週": {
        "title": "閱讀/詞彙語意",
        "file_id": "1eAgUnx0deSaq1ACX1KIYuKGSw4xWelkX",
        "audio_id": "",
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSdaDrTXKvbbZq7GzTUJIt7dQC9dtcIqL2BLW-7zxPy7RoQUnQ/viewform?usp=sharing&ouid=112324184864900621205",
        "form_url_2": "", 
        "form_url_3": "", 
        "form_btn_1_label": "🎯 開啟 【第二週】 閱讀與詞彙測驗01", 
        "instruction_text": "練習完表單詞彙語意測驗後，亦可至「📖 每週線上教材」閱讀本週的線上課程內容，複習相關解析以鞏固記憶。",
        "note_title": "💡 閱讀與詞彙攻略：",
        "note_content": "本週重點在於理解上下文語意與詞根構詞後的語意變化。快速閱讀的核心技巧，先找出主詞與動詞的核心結構！" 
    },
    "第三週": {
        "title": "聽力/對話理解",
        "file_id": "1XDvuv_bA7XrUXksfPIAJh_eu-_T_uOs9", # 已更新為最新的 ID
"audio_id": "", # 舊版單一音檔保留為空
        # 🚀 新增：支援多重音檔注入
        "audio_id_1": "1ctC9rFxHikByxtppwIy0vwfbpov6uRnu", 
        "audio_id_2": "1tSalduXeWPsrc-DJ48uwOCoHcT3ZFCTw", 
        "audio_id_3": "1q7qhKY4sRCeed8ShkZUeAbfGybRYD6Cc",
        "form_url": "", # 尚未上傳表單，暫時留空隱藏
        "form_url_2": "",
        "form_url_3": "",
        "form_btn_1_label": "🎯 開啟 【第三週】 聽力/對話理解測驗",
        "instruction_text": "尚未上傳測驗表單，敬請期待。",
        "note_title": "💡 聽力與對話理解攻略：",
        "note_content": "本週重點在於掌握段落主旨與長句結構。遇到不認識的單字，嘗試從前後文推敲語意，不要停頓太久。"
    }
}

# --- 前端視覺渲染層 ---
st.title("🎓 阿美語高級認證班")
st.divider()

# 劃分三個分頁標籤（每週教材、使用音訊、課後練習）
tab1, tab2, tab3 = st.tabs(["📖 每週線上教材", "🎵 課堂使用音訊", "✍️ 課後練習"])

# =================================================================
# 📖 欄位一：每週線上教材
# =================================================================
with tab1:
    with st.expander("📅 選擇複習週次", expanded=False):
        selected_week = st.selectbox(
            "請選取你要複習的週次：",
            options=["請選擇"] + list(WEEK_DRIVE_IDS.keys()),
            index=0,
            key="selector_t1",
            label_visibility="collapsed"
        )
    
    if selected_week == "請選擇":
        st.write(" ")
        st.info("💡 請點擊上方「📅 選擇複習週次」按鈕，並選取您要複習的週次以顯示教材內容。")
    else:
        current_week_info = WEEK_DRIVE_IDS[selected_week]
        st.header(f"📘 {current_week_info['title']}")
        
        with st.spinner(f"🔄 正在實時安全同步 Google Drive 【{selected_week}】教材與音訊..."):
            lecture_content = get_amis_drive_content(current_week_info["file_id"])
            # 支援舊版全域單一音檔 (第一週相容)
            audio_bytes = load_audio_from_drive(current_week_info["audio_id"]) if current_week_info.get("audio_id") else None
            # 🚀 支援新版動態多重音檔 (第三週專用)
            audio_bytes_1 = load_audio_from_drive(current_week_info.get("audio_id_1")) if current_week_info.get("audio_id_1") else None
            audio_bytes_2 = load_audio_from_drive(current_week_info.get("audio_id_2")) if current_week_info.get("audio_id_2") else None
            audio_bytes_3 = load_audio_from_drive(current_week_info.get("audio_id_3")) if current_week_info.get("audio_id_3") else None
        
        if lecture_content and "⚠️" not in lecture_content and "🚨" not in lecture_content:
            # 🚀 擴充正則表達式：新增【W3表單測驗-短文推論】
            pattern = r'(【對話\s*t\d+-\d+-\d+】|【對話推論完整題組】|【附加題組問答】|【第二週課程內容】|【第三週線上課程】|【作業-表單01 答案解析】|【W3L1表單測驗-短文推論】)'
            blocks = re.split(pattern, lecture_content)
            
            is_full_exam_block = False
            current_expander = None
            
            for block in blocks:
                if not block.strip():
                    continue
                
                # 🚀 判斷是否為大標題的摺疊標籤：新增【W3表單測驗-短文推論】
                is_match = (
                    re.match(r'【對話\s*t\d+-\d+-\d+】', block.strip()) or 
                    block.strip() in ["【對話推論完整題組】", "【附加題組問答】", "【第二週課程內容】", "【第三週線上課程】", "【作業-表單01 答案解析】", "【W3L1表單測驗-短文推論】"]
                )
                
                if is_match:
                    current_expander = st.expander(f"{block.strip()} 顯示/隱藏", expanded=False)
                    # 只有在第一週的「完整題組」才需要渲染頂部音檔
                    if "完整題組" in block.strip():
                        is_full_exam_block = True
                    else:
                        is_full_exam_block = False
                else:
                    if current_expander:
                        with current_expander:
                            # 渲染舊版全域音檔 (第一週)
                            if is_full_exam_block:
                                if audio_bytes:
                                    st.audio(audio_bytes, format="audio/mp3")
                                else:
                                    st.error("⚠️ 本週聽力音檔載入失敗，請確認雲端硬碟權限是否開啟。")
                                st.write(" ")
                            
                            # 動態音檔標籤解析引擎
                            sub_blocks = re.split(r'(【插入音檔\d】)', block)
                            
                            for sub in sub_blocks:
                                if sub == '【插入音檔1】':
                                    if audio_bytes_1: st.audio(audio_bytes_1, format="audio/mp3")
                                    else: st.error("⚠️ 音檔 1 載入失敗或未設定 ID")
                                elif sub == '【插入音檔2】':
                                    if audio_bytes_2: st.audio(audio_bytes_2, format="audio/mp3")
                                    else: st.error("⚠️ 音檔 2 載入失敗或未設定 ID")
                                elif sub == '【插入音檔3】':
                                    if audio_bytes_3: st.audio(audio_bytes_3, format="audio/mp3")
                                    else: st.error("⚠️ 音檔 3 載入失敗或未設定 ID")
                                else:
                                    # 正常文本渲染
                                    st.markdown(sub, unsafe_allow_html=True)
                    else:
                        # 標籤外的文本，直接顯示
                        st.markdown(block, unsafe_allow_html=True)
        else:
            # 發生錯誤時直接顯示文本
            st.markdown(lecture_content, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎯 記事")
        
        # 動態讀取並渲染每週專屬的記事內容
        note_title = current_week_info.get("note_title", "💡 學習重點：")
        note_content = current_week_info.get("note_content", "請持續累積實力，完成本週進度！")
        
        st.markdown(f"""
        <div style='background-color: #F0F7FF; padding: 18px; border-radius: 10px; border-left: 6px solid #1E88E5;'>
            <b style='color: #1E88E5; font-size: 18px;'>{note_title}</b><br>
            <p style='color: #31333F; margin-top: 8px;'>
                {note_content}
            </p>
        </div>
        """, unsafe_allow_html=True)

# =================================================================
# 🎵 欄位二：課堂使用音訊
# =================================================================
with tab2:
    with st.expander("📅 選擇複習週次", expanded=False):
        selected_week_t2 = st.selectbox(
            "請選取你要複習的週次：",
            options=["請選擇"] + list(WEEK_DRIVE_IDS.keys()),
            index=0,
            key="selector_t2",
            label_visibility="collapsed"
        )
        
    if selected_week_t2 == "請選擇":
        st.write(" ")
        st.info("🎧 暫不提供「每週線上課程」教材音訊。")
    else:
        st.header(f"🎧 課堂串流音訊同步 ({selected_week_t2})")
        st.write(" ")
        st.warning("⚠️ 暫時不提供音檔。")

# =================================================================
# ✍️ 欄位三：課後練習
# =================================================================
with tab3:
    with st.expander("📅 選擇複習週次", expanded=False):
        selected_week_t3 = st.selectbox(
            "請選取你要複習的週次：",
            options=["請選擇"] + list(WEEK_DRIVE_IDS.keys()),
            index=0,
            key="selector_t3",
            label_visibility="collapsed"
        )
        
    if selected_week_t3 == "請選擇":
        st.write(" ")
        st.info("✍️ 請先選取週次以獲取該週的課後練習表單。")
    else:
        current_week_info = WEEK_DRIVE_IDS[selected_week_t3]
        st.header(f"📝 {selected_week_t3} 課後複習驗證")
        st.write("點擊下方按鈕，填寫本週的線上測驗表單：")
        
        # 🎯 動態渲染表單01（有網址才顯示，並讀取自訂按鈕名稱）
        if current_week_info.get("form_url"):
            btn_label_1 = current_week_info.get("form_btn_1_label", f"🎯 開啟 【{selected_week_t3}】 練習表單01")
            st.link_button(
                label=btn_label_1,
                url=current_week_info["form_url"],
                type="primary",
                use_container_width=True
            )
            st.write(" ") 
        
        # 📝 動態渲染表單02（有網址才顯示）
        if current_week_info.get("form_url_2"):
            st.link_button(
                label=f"📝 開啟 【{selected_week_t3}】 聽力練習表單02",
                url=current_week_info["form_url_2"],
                type="primary",
                use_container_width=True
            )
            st.write(" ") 

        # 🚀 動態渲染表單03（有網址才顯示）
        if current_week_info.get("form_url_3"):
            st.link_button(
                label=f"🚀 開啟 【{selected_week_t3}】 聽力練習表單03",
                url=current_week_info["form_url_3"],
                type="primary",
                use_container_width=True
            )
        
        # 動態讀取每週專屬說明文字
        instruction = current_week_info.get("instruction_text", "請依循表單內的指示完成測驗。")
        
        st.markdown(f"""
        <div style='background-color: #FFF9E6; padding: 15px; border-radius: 8px; border-left: 5px solid #FFA000; margin-top: 20px;'>
            <span style='color: #FFA000; font-weight: bold;'>📌 填寫說明：</span><br>
            <p style='color: #31333F; margin-top: 5px;'>
                {instruction}
            </p>
        </div>
        """, unsafe_allow_html=True)

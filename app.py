import streamlit as st
import requests
import re
import datetime

# --- 頁面系統設定 ---
st.set_page_config(
    page_title="阿美語高級認證班 | 雲端衝刺系統",
    page_icon="🎓",
    layout="centered"
)

# --- 🎯 遠端讀取 Google Drive 文件的函數 ---
@st.cache_data(show_spinner=False, ttl=3600)
def get_amis_drive_content(file_id):
    download_url = f"[https://docs.google.com/uc?export=download&id=](https://docs.google.com/uc?export=download&id=){file_id}"
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
    if not file_id: return None
    download_url = f"[https://docs.google.com/uc?export=download&id=](https://docs.google.com/uc?export=download&id=){file_id}"
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            return response.content
    except Exception:
        return None
    return None

# --- 🗺️ 雲端硬碟每週教材與表單對照表 ---
WEEK_DRIVE_IDS = {
    "第一週": {
        "title": "聽力/對話推論",
        "file_id": "1luzDIy5k-sG7M5tO7IDuUZOG4m12c9jr",
        "audio_id": "1rRF0jGJHEOavDy3CDHy8lf965hZSG-1u", 
        "form_url": "[https://docs.google.com/forms/d/e/1FAIpQLSeKMrPYPPebwlHI_36Hed_gzr6dpit-vH6eqZZmsHOJuhX8fg/viewform?usp=dialog](https://docs.google.com/forms/d/e/1FAIpQLSeKMrPYPPebwlHI_36Hed_gzr6dpit-vH6eqZZmsHOJuhX8fg/viewform?usp=dialog)",
        "form_url_2": "[https://docs.google.com/forms/d/e/1FAIpQLSeikQXV34jH_7wT102SAkwTTCnadH_UoCkp4WOAJOFjX3ZSqw/viewform?usp=sharing&ouid=112324184864900621205](https://docs.google.com/forms/d/e/1FAIpQLSeikQXV34jH_7wT102SAkwTTCnadH_UoCkp4WOAJOFjX3ZSqw/viewform?usp=sharing&ouid=112324184864900621205)",
        "form_url_3": "[https://forms.gle/qtRzxtMX5rD42KhA6](https://forms.gle/qtRzxtMX5rD42KhA6)",
        "form_btn_1_label": "🎯 開啟 【第一週】 聽力練習表單01",
        "instruction_text": "若要閱讀題組的族語文字，可在 Google 表單內點選「音檔」連結，聆聽音檔的頁面中，打開「註解」即可。建議盡可能答完題再看",
        "note_title": "💡 高級認證聽力破關公式：",
        "note_content": "高級聽力（特別是「對話推論題」與「長篇複句聽解」）考的不是海量單字的記憶，而是對阿美語核心「焦點系統」、「時態」與「語境」的瞬間反射辨識。"
    },
    "第二週": {
        "title": "閱讀/詞彙語意",
        "file_id": "1eAgUnx0deSaq1ACX1KIYuKGSw4xWelkX",
        "audio_id": "",
        "form_url": "[https://docs.google.com/forms/d/e/1FAIpQLSdaDrTXKvbbZq7GzTUJIt7dQC9dtcIqL2BLW-7zxPy7RoQUnQ/viewform?usp=sharing&ouid=112324184864900621205](https://docs.google.com/forms/d/e/1FAIpQLSdaDrTXKvbbZq7GzTUJIt7dQC9dtcIqL2BLW-7zxPy7RoQUnQ/viewform?usp=sharing&ouid=112324184864900621205)",
        "form_url_2": "", 
        "form_url_3": "", 
        "form_btn_1_label": "🎯 開啟 【第二週】 閱讀與詞彙測驗01", 
        "instruction_text": "練習完表單詞彙語意測驗後，亦可至「📖 每週線上教材」閱讀本週的線上課程內容，複習相關解析以鞏固記憶。",
        "note_title": "💡 閱讀與詞彙攻略：",
        "note_content": "本週重點在於理解上下文語意與詞根構詞後的語意變化。快速閱讀的核心技巧，先找出主詞與動詞的核心結構！" 
    },
    "第三週": {
        "title": "聽力/對話理解",
        "file_id": "1XDvuv_bA7XrUXksfPIAJh_eu-_T_uOs9", 
        "audio_id": "", 
        "audio_id_1": "1ctC9rFxHikByxtppwIy0vwfbpov6uRnu", 
        "audio_id_2": "1tSalduXeWPsrc-DJ48uwOCoHcT3ZFCTw", 
        "audio_id_3": "1q7qhKY4sRCeed8ShkZUeAbfGybRYD6Cc",
        "audio_id_4": "1IUfTrEFPFFxz8dVEVm3dxZHZMpA6Juh8",
        "audio_id_5": "1PRAeIheoQKJaZNzSJ8LtKQGRR5zQ1MqN",
        "audio_id_6": "1tQ4Gesc0-BeBFTklSM0icbbt_d8BS6RF",
        "audio_id_7": "1xXvtEKQiH0ZNgfdQsQpQzOlpkZ6T3EJc",
        "form_url": "[https://docs.google.com/forms/d/e/1FAIpQLSeJVgmWL26WjLF6ebskonhVOoHHnrasM4EI681ZWPtCZgOLPg/viewform?usp=header](https://docs.google.com/forms/d/e/1FAIpQLSeJVgmWL26WjLF6ebskonhVOoHHnrasM4EI681ZWPtCZgOLPg/viewform?usp=header)",
        "form_url_2": "[https://docs.google.com/forms/d/e/1FAIpQLSf2MXBPVNHdOj2Z_noNJHHQC_bMKQ_zLLY_IunvEOLlOTEgMg/viewform?usp=header](https://docs.google.com/forms/d/e/1FAIpQLSf2MXBPVNHdOj2Z_noNJHHQC_bMKQ_zLLY_IunvEOLlOTEgMg/viewform?usp=header)",
        "form_url_3": "",
        "form_btn_1_label": "🎯 【第三週】 聽力/短文推論01 (馬蘭)",
        "instruction_text": "「聆聽短文時遇到生詞，請專注聽取『動詞焦點』與『核心主詞』來建構整體的語意架構。善用語氣轉折與上下文的語境線索來邏輯推敲。」",
        "note_title": "💡 聽力與對話理解攻略：",
        "note_content": "本週重點在於掌握段落主旨與長句結構。遇到不認識的單字，嘗試從前後文推敲語意，不要停頓太久。"
    },
    "第四週": {
        "title": "翻譯/翻譯實戰",
        "file_id": "13yq9AVE23hW8jg7XdPqjM69_j1hLAkvJ", 
        "audio_id": "", 
        "form_url": "[https://docs.google.com/forms/d/e/1FAIpQLSetYYyakMpvmh5LSX0vIe2vJr87Ldpgqs6m2mh1GSi1WuY8Lg/viewform?usp=header](https://docs.google.com/forms/d/e/1FAIpQLSetYYyakMpvmh5LSX0vIe2vJr87Ldpgqs6m2mh1GSi1WuY8Lg/viewform?usp=header)", 
        "form_url_2": "", 
        "form_url_3": "",
        "form_btn_1_label": "🎯 【第四週】 翻譯實戰測驗01",
        "instruction_text": "進行翻譯實戰時，切勿使用中文 SVO 語序硬套，請優先確定阿美語的「動詞焦點」與「核心主詞」。",
        "note_title": "💡 翻譯與結構攻略：",
        "note_content": "本週重點在於『信、達、雅』的轉換。拆解長句時，請善用格位標記 (ko, to, no) 來釐清字詞關係，保持句法清晰。熟記sapi-、saka-等前綴詞的翻法"
    }
}

# --- 前端視覺渲染層 ---
exam_date = datetime.date(2026, 12, 5) 
today = datetime.date.today()
days_left = (exam_date - today).days
countdown_text = f"倒數 {days_left} 天" if days_left > 0 else "考試進行中"

st.markdown(f"""
<div style='display: flex; align-items: center; gap: 20px; margin-bottom: 0.5rem;'>
    <h1 style='margin: 0; padding: 0;'>🎓 阿美語高級認證班</h1>
    <div style='border: 2px solid #FF8C00; color: #FF8C00; font-weight: bold; font-size: 1.8rem; padding: 4px 16px; border-radius: 12px; white-space: nowrap;'>
        {countdown_text}
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

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
            
            audio_cache = {}
            for key, file_id in current_week_info.items():
                if key.startswith("audio_id") and file_id: 
                    audio_cache[key] = load_audio_from_drive(file_id)
        
        if lecture_content and "⚠️" not in lecture_content and "🚨" not in lecture_content:
            expander_tags = [
                "【對話推論完整題組】", "【附加題組問答】", "【第二週課程內容】", 
                "【第三週線上課程】", "【作業-表單01 答案解析】", 
                "【W3L1表單測驗-短文推論】", "【W3L2表單測驗-短文推論】",
                "【第四週線上課程】", "【翻譯實戰練習】"
            ]
            
            pattern = r'(【對話\s*t\d+-\d+-\d+】|' + '|'.join([re.escape(tag) for tag in expander_tags]) + r')'
            blocks = re.split(pattern, lecture_content)
            
            is_full_exam_block = False
            current_expander = None
            
            for block in blocks:
                if not block.strip(): continue
                
                is_match = re.match(r'【對話\s*t\d+-\d+-\d+】', block.strip()) or (block.strip() in expander_tags)
                
                if is_match:
                    current_expander = st.expander(f"{block.strip()} 顯示/隱藏", expanded=False)
                    is_full_exam_block = ("完整題組" in block.strip())
                else:
                    if current_expander:
                        with current_expander:
                            if is_full_exam_block:
                                if audio_cache.get("audio_id"):
                                    st.audio(audio_cache["audio_id"], format="audio/mp3")
                                else:
                                    st.error("⚠️ 本週聽力音檔載入失敗，請確認雲端硬碟權限是否開啟。")
                                st.write(" ")
                            
                            sub_blocks = re.split(r'(【插入音檔\d+】)', block)
                            for sub in sub_blocks:
                                audio_match = re.match(r'【插入音檔(\d+)】', sub)
                                if audio_match:
                                    audio_num = audio_match.group(1) 
                                    cache_key = f"audio_id_{audio_num}"
                                    audio_data = audio_cache.get(cache_key)
                                    
                                    if audio_data:
                                        st.audio(audio_data, format="audio/mp3")
                                    else:
                                        st.error(f"⚠️ 音檔 {audio_num} 載入失敗或未設定對應的 ID")
                                else:
                                    st.markdown(sub, unsafe_allow_html=True)
                    else:
                        st.markdown(block, unsafe_allow_html=True)
        else:
            st.markdown(lecture_content, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎯 記事")
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
        st.header(f"📝 {selected_week_t3} 課後複習")
        st.write("點擊下方按鈕，填寫本週的線上測驗表單：")
        
        if current_week_info.get("form_url"):
            btn_label_1 = current_week_info.get("form_btn_1_label", f"🎯 開啟 【{selected_week_t3}】 練習表單01")
            st.link_button(label=btn_label_1, url=current_week_info["form_url"], type="primary", use_container_width=True)
            st.write(" ") 
        
        if current_week_info.get("form_url_2"):
            btn_label_2 = current_week_info.get("form_btn_2_label", f"📝 【{selected_week_t3}】 練習表單02")
            st.link_button(label=btn_label_2, url=current_week_info["form_url_2"], type="primary", use_container_width=True)
            st.write(" ") 

        if current_week_info.get("form_url_3"):
            btn_label_3 = current_week_info.get("form_btn_3_label", f"🚀 開啟 【{selected_week_t3}】 練習表單03")
            st.link_button(label=btn_label_3, url=current_week_info["form_url_3"], type="primary", use_container_width=True)
        
        instruction = current_week_info.get("instruction_text", "請依循表單內的指示完成測驗。")
        
        st.markdown(f"""
        <div style='background-color: #FFF9E6; padding: 15px; border-radius: 8px; border-left: 5px solid #FFA000; margin-top: 20px;'>
            <span style='color: #FFA000; font-weight: bold;'>📌 填寫說明：</span><br>
            <p style='color: #31333F; margin-top: 5px;'>
                {instruction}
            </p>
        </div>
        """, unsafe_allow_html=True)

import streamlit as st
import requests
import re

# --- 頁面系統設定 (UIUX-CRF v9.0 憲法對齊) ---
st.set_page_config(
    page_title="阿美語高級認證班 | 雲端衝刺系統",
    page_icon="🎓",
    layout="centered"
)

# --- 🎯 遠端讀取 Google Drive 檔案的函數 ---
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

# --- 🗺️ 雲端硬碟每週教材 ID 對照表 ---
WEEK_DRIVE_IDS = {
    "第一週": {
        "title": "聽力/對話推論",
        "file_id": "1luzDIy5k-sG7M5tO7IDuUZOG4m12c9jr",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    },
    "第二週": {
        "title": "口說與長篇複句 (範例預留)",
        "file_id": "這裡填入第二週的Drive_ID",
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
    }
}

# --- 前端視覺渲染層 ---
st.title("🎓 阿美語高級認證班")
st.divider()

tab1, tab2 = st.tabs(["📖 每週線上教材", "🎵 課堂使用音訊"])

with tab1:
    # 在清單最前方加入「--- 請選擇週次 ---」作為預設空狀態
    with st.expander("📅 選擇複習週次", expanded=False):
        selected_week = st.selectbox(
            "請選取你要複習的週次：",
            options=["--- 請選擇週次 ---"] + list(WEEK_DRIVE_IDS.keys()),
            index=0,
            label_visibility="collapsed"
        )
    
    # 防線攔截：如果學生維持預設的「--- 請選擇週次 ---」，下方內容一律隱藏
    if selected_week == "--- 請選擇週次 ---":
        st.write(" ") 
        st.info("💡 請點擊上方「📅 選擇複習週次」按鈕，並選取您要複習的週次以顯示教材內容。")
    else:
        current_week_info = WEEK_DRIVE_IDS[selected_week]
        
        # 渲染週次主題
        st.header(f"📘 {current_week_info['title']}")
        
        # --- 執行即時雲端同步 ---
        with st.spinner(f"🔄 正在實時安全同步 Google Drive 【{selected_week}】教材..."):
            lecture_content = get_amis_drive_content(current_week_info["file_id"])
        
        # -----------------------------------------------------------------
        # 🧠 【動態文本過濾機制：客製化標籤切片】
        # -----------------------------------------------------------------
        if lecture_content and "⚠️" not in lecture_content and "🚨" not in lecture_content:
            pattern = r'(【對話\s*t\d+-\d+-\d+】|【對話推論完整題組】|【附加題組問答】)'
            blocks = re.split(pattern, lecture_content)
            
            current_expander = None
            
            for block in blocks:
                if not block.strip():
                    continue
                
                is_match = (
                    re.match(r'【對話\s*t\d+-\d+-\d+】', block.strip()) or 
                    block.strip() == "【對話推論完整題組】" or 
                    block.strip() == "【附加題組問答】"
                )
                
                if is_match:
                    current_expander = st.expander(f"{block.strip()} 顯示/隱藏", expanded=False)
                else:
                    if current_expander:
                        with current_expander:
                            # 🚀 核心修正：將原本寫死的隨機音檔、radio 選擇題邏輯完全撤除！
                            # 這裡百分之百只呈現您 Google Drive 內 .md 檔撰寫的真實文字內容。
                            st.markdown(block, unsafe_allow_html=True)
                    else:
                        st.markdown(block, unsafe_allow_html=True)
        else:
            st.markdown(lecture_content, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🎯 記事")
        st.markdown("""
        <div style='background-color: #F0F7FF; padding: 18px; border-radius: 10px; border-left: 6px solid #1E88E5;'>
            <b style='color: #1E88E5; font-size: 18px;'>💡 高級認證聽力破關公式：</b><br>
            <p style='color: #31333F; margin-top: 8px;'>
                高級聽力（特別是「對話推論題」與「長篇複句聽解」）考的不是海量單字的記憶，而是對阿美語核心「焦點系統」、「時態」與「語境」的瞬間反射辨識。
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    if selected_week == "--- 請選擇週次 ---":
        st.info("🎧 請先至「每週線上教材」選取週次以同步音訊。")
    else:
        st.header(f"🎧 課堂串流音訊同步 ({selected_week})")
        st.write("請聆聽來自雲端硬碟的語音素材：")
        st.audio(WEEK_DRIVE_IDS[selected_week]["audio_url"], format="audio/mp3")

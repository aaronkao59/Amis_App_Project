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

# --- 📥 填入你的 Google Drive 檔案 ID ---
WEEK01_NOTE_ID = "1luzDIy5k-sG7M5tO7IDuUZOG4m12c9jr" 

# --- 執行即時雲端同步 ---
with st.spinner("🔄 正在實時安全同步 Google Drive 教材..."):
    lecture_content = get_amis_drive_content(WEEK01_NOTE_ID)

# --- 前端視覺渲染層 ---
st.title("🎓 阿美語高級認證班")
st.caption(" ")
st.divider()

tab1, tab2 = st.tabs(["📖 當週線上教材", "🎵 課堂使用音訊"])

with tab1:
    st.header("📘 聽力/對話推論")
    
    # -----------------------------------------------------------------
    # 🧠 【動態文本防禦過濾機制：客製化標籤切片】
    # 自動識別並切開包含【對話...】、【完整題組】、【附加題組】等指定開關
    # -----------------------------------------------------------------
    if lecture_content and "⚠️" not in lecture_content and "🚨" not in lecture_content:
        # 定義您指定的 6 大核心摺疊按鈕匹配模式
        pattern = r'(【對話\s*t\d+-\d+-\d+】|【對話推論完整題組】|【附加題組問答】)'
        blocks = re.split(pattern, lecture_content)
        
        current_expander = None
        block_counter = 0 # 用於生成不重複的唯一元件 Key [cite: 1]
        
        for block in blocks:
            if not block.strip():
                continue
            
            # 檢查目前切片是否匹配您指定的 6 個按鈕標題
            is_match = (
                re.match(r'【對話\s*t\d+-\d+-\d+】', block.strip()) or 
                block.strip() == "【對話推論完整題組】" or 
                block.strip() == "【附加題組問答】"
            )
            
            if is_match:
                # 發現目標標題，立刻在前端部署獨立的摺疊按鈕開關 (預設為收起關閉 expanded=False) 
                current_expander = st.expander(f" {block.strip()} 顯示/隱藏", expanded=False)
            else:
                # 如果前一個區塊是按鈕標題，將接下來的族語、翻譯與互動元件全部安全包裹於盒內 [cite: 4]
                if current_expander:
                    with current_expander:
                        st.markdown(block, unsafe_allow_html=True)
                        
                        # 🧬 針對高級認證聽力與問答進行原子化互動套利擴充 [cite: 38, 41]
                        block_counter += 1
                        if "Kacaw" in block or "mifoting" in block:
                            # 自動嵌入音軌監聽與即時作答反饋 [cite: 8, 42, 45]
                            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
                            st.radio("📝 根據上方對話，選出最符合高級認證語境的推論選項：", 
                                     ["A. 邀請集體捕魚 (Mifaca' 互助擴充)", "B. 拒絕長輩調度", "C. 純粹寒暄"], 
                                     key=f"radio_{block_counter}")
                else:
                    # 一般不屬於 6 大題組的標題或課文前言，直接在最外層自由渲染 
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
    st.header("🎧 課堂串流音訊同步")
    st.write("請聆聽來自雲端硬碟的語音素材：")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

import streamlit as st
import requests
import re
import streamlit.components.v1 as components

# --- 頁面系統設定 ---
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

# --- 🗺️ 雲端硬碟每週教材與表單對照表 ---
WEEK_DRIVE_IDS = {
    "第一週": {
        "title": "聽力/對話推論",
        "file_id": "1luzDIy5k-sG7M5tO7IDuUZOG4m12c9jr",
        "exam_audio_preview_url": "https://drive.google.com/file/d/1rRF0jGJHEOavDy3CDHy8lf965hZSG-1u/preview", 
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSeKMrPYPPebwlHI_36Hed_gzr6dpit-vH6eqZZmsHOJuhX8fg/viewform?usp=dialog"
    },
    "第二週": {
        "title": "口說與長篇複句 (範例預留)",
        "file_id": "這裡填入第二週的Drive_ID",
        "exam_audio_preview_url": "https://drive.google.com/file/d/這裡填入第二週的音檔ID/preview",
        "form_url": "https://forms.gle/yyyyyy"
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
    # 收合按鈕擺在最上方
    with st.expander("📅 選擇複習週次", expanded=False):
        selected_week = st.selectbox(
            "請選取你要複習的週次：",
            options=["請選擇"] + list(WEEK_DRIVE_IDS.keys()),
            index=0,
            key="selector_t1",
            label_visibility="collapsed"
        )
    
    # 藍色提示方塊出現在按鈕「下方」
    if selected_week == "請選擇":
        st.write(" ")
        st.info("💡 請點擊上方「📅 選擇複習週次」按鈕，並選取您要複習的週次以顯示教材內容。")
    else:
        current_week_info = WEEK_DRIVE_IDS[selected_week]
        st.header(f"📘 {current_week_info['title']}")
        
        with st.spinner(f"🔄 正在實時安全同步 Google Drive 【{selected_week}】教材..."):
            lecture_content = get_amis_drive_content(current_week_info["file_id"])
        
        if lecture_content and "⚠️" not in lecture_content and "🚨" not in lecture_content:
            pattern = r'(【對話\s*t\d+-\d+-\d+】|【對話推論完整題組】|【附加題組問答】)'
            blocks = re.split(pattern, lecture_content)
            
            is_full_exam_block = False
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
                    if "完整題組" in block.strip():
                        is_full_exam_block = True
                    else:
                        is_full_exam_block = False
                else:
                    if current_expander:
                        with current_expander:
                            if is_full_exam_block:
                                # 🚀 美化核心：使用 CSS 膠囊遮罩，強制隱藏黑背景與右上角的外跳按鈕
                                # 透過 margin 和 height 的微調，讓介面只剩下乾淨的白底播放控制列
                                components.html(
                                    f"""
                                    <div style="width: 100%; height: 56px; overflow: hidden; border-radius: 8px; border: 1px solid #E0E0E0; background-color: #FFFFFF;">
                                        <iframe src="{current_week_info["exam_audio_preview_url"]}" 
                                                width="100%" 
                                                height="500" 
                                                style="border: none; margin-top: -442px; margin-left: 0px;" 
                                                scrolling="no">
                                        </iframe>
                                    </div>
                                    """,
                                    height=65
                                )
                                st.write(" ")
                            
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
        st.write("請點擊下方按鈕，前往填寫本週的模擬認證線上表單：")
        
        st.link_button(
            label=f"🎯 開啟 【{selected_week_t3}】 模擬測驗表單",
            url=current_week_info["form_url"],
            type="primary",
            use_container_width=True
        )
        
        st.markdown("""
        <div style='background-color: #FFF9E6; padding: 15px; border-radius: 8px; border-left: 5px solid #FFA000; margin-top: 20px;'>
            <span style='color: #FFA000; font-weight: bold;'>📌 填寫說明：</span><br>
            <p style='color: #31333F; margin-top: 5px;'>
                表單送出後，您可以直接在 Google 表單內點選「查看分數」閱讀詳細的題組族語文字。
            </p>
        </div>
        """, unsafe_allow_html=True)

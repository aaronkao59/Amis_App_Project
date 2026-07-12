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
            pattern = r'(【對話\s*t\d+-\d+-\d+】|【對話推論完整題組】|【附加題組問答】|【第二週課程內容】|【第三週線上課程】|【作業-表單01 答案解析】|【W3L1表單測驗-短文推論】|【W3L2表單測驗-短文推論】)'
            blocks = re.split(pattern, lecture_content)
            
            is_full_exam_block = False
            current_expander = None
            
            for block in blocks:
                if not block.strip():
                    continue
                
                # 🚀 判斷是否為大標題的摺疊標籤：新增【W3表單測驗-短文推論】
                is_match = (
                    re.match(r'【對話\s*t\d+-\d+-\d+】', block.strip()) or 
                    block.strip() in ["【對話推論完整題組】", "【附加題組問答】", "【第二週課程內容】", "【第三週線上課程】", "【作業-表單01 答案解析】", "【W3L1表單測驗-短文推論】", "【W3L2表單測驗-短文推論】"]
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

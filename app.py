"""
English Sentence Practice App - Winamp Style
영어 문장 반복 연습 프로그램
"""

import streamlit as st
import time
from utils import (
    initialize_session_state,
    load_and_validate_csv,
    parse_text_input,
    pregenerate_audio,
    play_audio_with_stats_v2,
    play_audio_with_mediaelement,
)


def main():
    """메인 애플리케이션"""

    # 페이지 설정
    st.set_page_config(
        page_title="영어 문장 반복 연습 - Winamp Style",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 세션 초기화
    initialize_session_state()

    # Modern Player CSS
    st.markdown("""
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">

    <!-- MediaElement.js Core -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/mediaelement@7.0.3/build/mediaelementplayer.min.css">
    <script src="https://cdn.jsdelivr.net/npm/mediaelement@7.0.3/build/mediaelement-and-player.min.js"></script>

    <!-- MediaElement.js Playlist Plugin -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/mediaelement-plugins@2.5.1/dist/playlist/playlist.min.css">
    <script src="https://cdn.jsdelivr.net/npm/mediaelement-plugins@2.5.1/dist/playlist/playlist.min.js"></script>

    <style>
    :root {
        --primary: #ff4081;
        --primary-light: #ff79b0;
        --primary-dark: #c60055;
        --secondary: #00bcd4;
        --accent: #ffd740;
        --bg-dark: #0a0e27;
        --bg-card: #1a1f3a;
        --bg-display: #0d1128;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --text-accent: #64ffda;
        --glow: rgba(255, 64, 129, 0.4);
        --shadow: rgba(0, 0, 0, 0.6);
    }

    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1342 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(circle at 20% 50%, rgba(255, 64, 129, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(0, 188, 212, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* 메인 플레이어 카드 */
    .winamp-player {
        background: var(--bg-card);
        border-radius: 24px;
        padding: 32px;
        box-shadow:
            0 20px 60px var(--shadow),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
        animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .winamp-player::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
        animation: shimmer 3s linear infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* 플레이어 헤더 */
    .winamp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }

    .winamp-title {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--text-accent);
        font-family: 'JetBrains Mono', monospace;
    }

    /* 디스플레이 영역 */
    .winamp-display {
        background: var(--bg-display);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow:
            inset 0 4px 12px rgba(0, 0, 0, 0.5),
            0 1px 0 rgba(255, 255, 255, 0.05);
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    .winamp-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, transparent 0%, rgba(255, 64, 129, 0.05) 100%);
        pointer-events: none;
    }

    .winamp-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 48px;
        font-weight: 700;
        color: var(--primary);
        text-align: center;
        margin-bottom: 24px;
        text-shadow:
            0 0 20px var(--glow),
            0 0 40px var(--glow);
        letter-spacing: 4px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .winamp-text {
        font-size: 20px;
        line-height: 1.6;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 16px;
        font-weight: 400;
        animation: fadeIn 0.6s ease-out;
    }

    .winamp-text-korean {
        font-size: 16px;
        line-height: 1.6;
        color: var(--text-secondary);
        text-align: center;
        font-weight: 300;
        animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Winamp 컨트롤 패널 - 숨김 */
    .winamp-controls {
        display: none;
    }

    /* 비주얼라이저 */
    .visualizer {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
        padding: 0 32px 12px;
        opacity: 0.3;
    }

    .viz-bar {
        width: 4px;
        background: linear-gradient(to top, var(--primary), var(--secondary));
        border-radius: 2px 2px 0 0;
        animation: wave 1.5s ease-in-out infinite;
    }

    .viz-bar:nth-child(1) { animation-delay: 0s; height: 20%; }
    .viz-bar:nth-child(2) { animation-delay: 0.1s; height: 35%; }
    .viz-bar:nth-child(3) { animation-delay: 0.2s; height: 50%; }
    .viz-bar:nth-child(4) { animation-delay: 0.3s; height: 70%; }
    .viz-bar:nth-child(5) { animation-delay: 0.4s; height: 85%; }
    .viz-bar:nth-child(6) { animation-delay: 0.5s; height: 70%; }
    .viz-bar:nth-child(7) { animation-delay: 0.6s; height: 50%; }
    .viz-bar:nth-child(8) { animation-delay: 0.7s; height: 35%; }
    .viz-bar:nth-child(9) { animation-delay: 0.8s; height: 20%; }

    @keyframes wave {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(1.5); }
    }

    /* 버튼 컨테이너 */
    .winamp-btn {
        display: none;
        border-color: #00cc00;
        width: 60px;
        height: 50px;
        font-size: 24px;
    }

    .winamp-btn-play:hover {
        background: linear-gradient(180deg, #00cc00 0%, #00aa00 100%);
    }

    /* Winamp 플레이리스트 */
    .winamp-playlist {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%);
        border: 2px outset #4a6a8a;
        border-radius: 0;
        padding: 0;
        margin: 20px auto;
        max-width: 800px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.8);
    }

    .playlist-header {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%);
        padding: 4px 8px;
        border-bottom: 1px solid #1a2a3a;
        color: #ffffff;
        font-size: 11px;
        font-weight: bold;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.5);
    }

    .playlist-content {
        background: #000000;
        border: 2px inset #1a2a3a;
        margin: 8px;
        padding: 8px;
        max-height: 400px;
        overflow-y: auto;
    }

    .playlist-item {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        padding: 4px 8px;
        cursor: pointer;
        border-left: 3px solid transparent;
    }

    .playlist-item:hover {
        background: rgba(0, 255, 0, 0.1);
        border-left: 3px solid #00ff00;
    }

    .playlist-item-current {
        background: rgba(0, 255, 0, 0.2);
        border-left: 3px solid #00ff00;
        font-weight: bold;
    }

    .playlist-time {
        color: #00aaaa;
        float: right;
    }

    /* 버튼 스타일 - 모던 컨트롤 */
    .winamp-controls-container .stButton > button {
        width: 56px !important;
        height: 56px !important;
        border-radius: 50% !important;
        border: none !important;
        background: var(--bg-display) !important;
        color: var(--text-primary) !important;
        font-size: 20px !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow:
            0 4px 12px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .winamp-controls-container .stButton > button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow:
            0 8px 24px rgba(0, 0, 0, 0.5),
            0 0 0 2px var(--primary),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    .winamp-controls-container .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* 재생 버튼 특별 스타일 - 핑크 그라디언트 */
    .winamp-controls-container div[data-testid="column"]:nth-child(2) .stButton > button,
    .winamp-controls-container div[data-testid="column"]:nth-child(2) .stButton > button[kind="primary"] {
        width: 72px !important;
        height: 72px !important;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        font-size: 24px !important;
        box-shadow:
            0 8px 24px var(--glow),
            0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }

    .winamp-controls-container div[data-testid="column"]:nth-child(2) .stButton > button:hover,
    .winamp-controls-container div[data-testid="column"]:nth-child(2) .stButton > button[kind="primary"]:hover {
        box-shadow:
            0 12px 32px var(--glow),
            0 0 0 3px rgba(255, 64, 129, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-3px) scale(1.08) !important;
    }

    /* 사이드바 버튼 스타일 */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%) !important;
        border: 2px outset #5a7a9a !important;
        border-radius: 3px !important;
        color: #ffffff !important;
        font-family: 'Tahoma', 'Arial', sans-serif !important;
        font-size: 12px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.5) !important;
        padding: 6px 12px !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(180deg, #5a7a9a 0%, #3a5a7a 100%) !important;
    }

    [data-testid="stSidebar"] .stButton > button:active {
        border: 2px inset #3a5a7a !important;
    }

    /* 슬라이더 스타일 */
    .stSlider > div > div > div {
        background: #1a2a3a !important;
    }

    .stSlider > div > div > div > div {
        background: #00ff00 !important;
    }

    /* 라디오 버튼 */
    .stRadio > label {
        color: #00ff00 !important;
        font-family: 'Courier New', monospace !important;
    }

    /* 스크롤바 */
    .playlist-content::-webkit-scrollbar {
        width: 12px;
    }

    .playlist-content::-webkit-scrollbar-track {
        background: #0a0a0a;
        border: 1px solid #1a2a3a;
    }

    .playlist-content::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%);
        border: 1px solid #5a7a9a;
    }

    .playlist-content::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #5a7a9a 0%, #3a5a7a 100%);
    }

    /* Winamp 컨트롤 컨테이너 배경 */
    .winamp-controls-container {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%);
        padding: 15px 20px;
        border-radius: 5px;
        margin: 10px auto;
        max-width: 700px;
        border: 2px outset #4a6a8a;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }

    /* 컬럼 간격 조정 */
    .winamp-controls-container div[data-testid="column"] {
        padding: 0 5px !important;
    }

    /* Two-column layout for player and playlist */
    .player-playlist-container {
        display: flex;
        gap: 20px;
        margin: 20px auto;
        max-width: 1400px;
    }

    .player-section {
        flex: 1;
        min-width: 0;
    }

    .playlist-section {
        width: 450px;
        flex-shrink: 0;
    }

    @media (max-width: 1024px) {
        .player-playlist-container {
            flex-direction: column;
        }
        .playlist-section {
            width: 100%;
        }
    }

    /* MediaElement.js Player Styling - Winamp Theme */
    .mejs__container {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%) !important;
        border: 2px outset #4a6a8a !important;
        border-radius: 0 !important;
        margin: 10px 0 !important;
        font-family: 'Courier New', monospace !important;
    }

    .mejs__controls {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%) !important;
        border-top: 1px solid #4a6a8a !important;
    }

    .mejs__button button {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%) !important;
        border: 1px outset #5a7a9a !important;
        color: #00ff00 !important;
    }

    .mejs__button button:hover {
        background: linear-gradient(180deg, #5a7a9a 0%, #3a5a7a 100%) !important;
    }

    .mejs__time {
        color: #00ff00 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 4px rgba(0, 255, 0, 0.6) !important;
    }

    .mejs__time-rail .mejs__time-total {
        background: #1a2a3a !important;
    }

    .mejs__time-rail .mejs__time-current {
        background: #00ff00 !important;
    }

    .mejs__volume-current {
        background: #00ff00 !important;
    }

    /* MediaElement.js Playlist Styling */
    .mejs__playlist {
        background: #000000 !important;
        border: 2px inset #1a2a3a !important;
        max-height: 500px !important;
        overflow-y: auto !important;
        font-family: 'Courier New', monospace !important;
    }

    .mejs__playlist-item {
        color: #00ff00 !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
        border-left: 3px solid transparent !important;
        border-bottom: 1px solid #1a2a3a !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    .mejs__playlist-item:hover {
        background: rgba(0, 255, 0, 0.1) !important;
        border-left: 3px solid #00ff00 !important;
    }

    .mejs__playlist-current {
        background: rgba(0, 255, 0, 0.2) !important;
        border-left: 3px solid #00ff00 !important;
        font-weight: bold !important;
    }

    .mejs__playlist-title {
        color: #00ff00 !important;
        text-shadow: 0 0 4px rgba(0, 255, 0, 0.6) !important;
    }

    .mejs__playlist-description {
        color: #00aaff !important;
        font-size: 11px !important;
        margin-top: 4px !important;
    }

    /* Playlist 컨테이너 스타일 */
    [data-testid="column"]:has(.mejs__playlist) {
        padding: 0 !important;
    }

    /* Playlist button styling - 모던 테마 */
    [data-testid="column"]:has(.mejs__playlist) .stButton > button,
    [data-testid="column"]:has(.mejs__playlist) .stButton > button[kind="secondary"] {
        background: var(--bg-display) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid transparent !important;
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 13px !important;
        text-align: left !important;
        padding: 12px 16px !important;
        margin: 0 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        height: auto !important;
        min-height: 48px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    [data-testid="column"]:has(.mejs__playlist) .stButton > button:hover,
    [data-testid="column"]:has(.mejs__playlist) .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 64, 129, 0.1) !important;
        border-left: 3px solid var(--primary) !important;
        color: var(--text-primary) !important;
        transform: translateX(4px) !important;
    }

    /* 현재 재생 중인 항목 - 핑크 그라디언트 */
    [data-testid="column"]:has(.mejs__playlist) .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, rgba(255, 64, 129, 0.2), rgba(255, 64, 129, 0.1)) !important;
        border: 1px solid rgba(255, 64, 129, 0.3) !important;
        border-left: 3px solid var(--primary) !important;
        color: var(--text-accent) !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 64, 129, 0.5) !important;
    }

    [data-testid="column"]:has(.mejs__playlist) .stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, rgba(255, 64, 129, 0.3), rgba(255, 64, 129, 0.15)) !important;
        color: var(--text-accent) !important;
        transform: translateX(4px) !important;
    }

    /* Remove gap between playlist buttons */
    [data-testid="column"]:has(.mejs__playlist) .element-container {
        margin-bottom: 0 !important;
    }

    [data-testid="column"]:has(.mejs__playlist) .stButton {
        margin-bottom: 0 !important;
    }

    /* Playlist 스크롤바 스타일 */
    .mejs__playlist::-webkit-scrollbar {
        width: 8px;
    }

    .mejs__playlist::-webkit-scrollbar-track {
        background: #1a2a3a;
    }

    .mejs__playlist::-webkit-scrollbar-thumb {
        background: #00ff00;
        border-radius: 4px;
    }

    .mejs__playlist::-webkit-scrollbar-thumb:hover {
        background: #00cc00;
    }

    /* 오디오 플레이어 숨기기 - 빈 박스 제거 */
    .winamp-player audio {
        display: none !important;
    }

    /* 빈 요소 숨기기 */
    .element-container:has(> .stMarkdown:empty) {
        display: none !important;
    }

    .element-container:has(audio) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 오디오 컨트롤을 완전히 숨김 */
    audio {
        position: absolute !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ========== 사이드바 ==========
    with st.sidebar:
        st.markdown('<p style="color: #00ff00; font-family: Courier New, monospace; font-size: 18px; font-weight: bold;">⚙️ SETTINGS</p>', unsafe_allow_html=True)

        # 데이터 입력
        st.markdown('<p style="color: #00ff00; font-family: Courier New, monospace; font-size: 14px;">📁 DATA INPUT</p>', unsafe_allow_html=True)

        input_method = st.radio(
            "Input Method",
            ["CSV Upload", "Text Paste"],
            label_visibility="collapsed"
        )

        if input_method == "CSV Upload":
            uploaded_file = st.file_uploader(
                "Upload CSV",
                type=['csv'],
                help="CSV with English and Korean columns"
            )

            if uploaded_file is not None:
                # 파일 이름이 변경되었을 때만 새로 로드
                file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                if 'loaded_file_id' not in st.session_state or st.session_state.loaded_file_id != file_id:
                    df = load_and_validate_csv(uploaded_file)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.loaded_file_id = file_id
                        pregenerate_audio(df)
                        st.success(f"✓ {len(df)} sentences loaded")

        else:
            english_text = st.text_area(
                "English Sentences",
                height=150,
                placeholder="One sentence per line...",
                label_visibility="collapsed"
            )

            if st.button("LOAD", use_container_width=True):
                if english_text.strip():
                    df = parse_text_input(english_text, False, "")
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.loaded_file_id = f"text_{hash(english_text)}"
                        pregenerate_audio(df)
                        st.success(f"✓ {len(df)} loaded")
                else:
                    st.warning("Enter sentences")

        st.divider()

        # 재생 모드
        st.markdown('<p style="color: #00ff00; font-family: Courier New, monospace; font-size: 14px;">🔁 PLAY MODE</p>', unsafe_allow_html=True)

        repeat_mode = st.radio(
            "Mode",
            ["Individual", "Loop All", "Shadowing"],
            label_visibility="collapsed"
        )
        st.session_state.repeat_mode = repeat_mode

        # 재생 속도
        playback_speed = st.slider(
            "Speed",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.playback_speed,
            step=0.1,
            format="%.1fx"
        )
        st.session_state.playback_speed = playback_speed

        # 모드별 설정
        if repeat_mode == "Individual":
            target_repeats = st.number_input(
                "Repeats per sentence",
                min_value=1,
                max_value=20,
                value=st.session_state.target_repeats
            )
            st.session_state.target_repeats = target_repeats

        elif repeat_mode == "Loop All":
            loop_target = st.number_input(
                "Loop count",
                min_value=1,
                max_value=100,
                value=st.session_state.loop_target
            )
            st.session_state.loop_target = loop_target
            st.caption(f"Current: {st.session_state.loop_count} / {st.session_state.loop_target}")

        elif repeat_mode == "Shadowing":
            shadowing_delay = st.slider(
                "Delay (seconds)",
                min_value=1,
                max_value=10,
                value=st.session_state.shadowing_delay
            )
            st.session_state.shadowing_delay = shadowing_delay

        st.divider()

        # 리셋 버튼
        if st.button("🔄 RESET", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ========== 메인 영역 ==========
    if st.session_state.df is None:
        st.markdown("""
        <div style="text-align: center; margin-top: 100px;">
            <h1 style="color: #00ff00; font-family: Courier New, monospace; text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);">
                🎧 ENGLISH PRACTICE - WINAMP STYLE
            </h1>
            <p style="color: #00aaaa; font-family: Courier New, monospace; font-size: 16px;">
                ← Load sentences from sidebar to start
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    df = st.session_state.df
    current_idx = st.session_state.current_index
    if current_idx >= len(df):
        current_idx = 0
        st.session_state.current_index = 0

    current_sentence = df.iloc[current_idx]

    # Create two-column layout using Streamlit columns
    col_player, col_playlist = st.columns([2, 1], gap="medium")

    # ========== LEFT COLUMN: Player Section ==========
    with col_player:
        # Winamp 플레이어
        st.markdown('<div class="winamp-player">', unsafe_allow_html=True)

        # 헤더
        st.markdown(f'<div class="winamp-header"><span class="winamp-title">ENGLISH PRACTICE PLAYER</span><span class="winamp-title">{current_idx + 1} of {len(df)}</span></div>', unsafe_allow_html=True)

        # 디스플레이
        st.markdown('<div class="winamp-display">', unsafe_allow_html=True)

        # 현재 문장의 오디오 길이 표시
        if current_idx in st.session_state.audio_durations:
            duration_sec = int(st.session_state.audio_durations[current_idx])
            time_display = f"{duration_sec // 60:02d}:{duration_sec % 60:02d}"
        else:
            time_display = "00:00"

        st.markdown(f'<div class="winamp-time">{time_display}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="winamp-text">{current_sentence["English"]}</div>', unsafe_allow_html=True)
        if current_sentence['Korean']:
            st.markdown(f'<div class="winamp-text-korean">{current_sentence["Korean"]}</div>', unsafe_allow_html=True)

        # 비주얼라이저 추가
        visualizer_html = '''
        <div class="visualizer">
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
            <div class="viz-bar"></div>
        </div>
        '''
        st.markdown(visualizer_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Winamp 컨트롤 패널 시작
        st.markdown('<div class="winamp-controls">', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # MediaElement.js 플레이어
        audio_placeholder = st.empty()

        # Winamp 스타일 버튼 컨테이너
        st.markdown('<div class="winamp-controls-container">', unsafe_allow_html=True)

        btn_col1, btn_col2, btn_col3 = st.columns([1, 1.5, 1])

        with btn_col1:
            if st.button("⏮", use_container_width=True, help="이전 문장"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                else:
                    st.session_state.current_index = len(df) - 1
                st.rerun()

        with btn_col2:
            if st.button("▶️", use_container_width=True, help="재생", type="primary"):
                play_audio_with_stats_v2(
                    current_sentence['English'],
                    current_idx,
                    st.session_state.playback_speed,
                    audio_placeholder
                )

        with btn_col3:
            if st.button("⏭", use_container_width=True, help="다음 문장"):
                st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ========== RIGHT COLUMN: Playlist Section ==========
    with col_playlist:
        # Playlist header
        st.markdown(f'''
        <div style="background: var(--bg-card); border-radius: 16px 16px 0 0; padding: 16px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-top: 10px;">
            <div style="color: var(--text-accent); font-weight: 700; font-family: 'JetBrains Mono', monospace; font-size: 12px; text-transform: uppercase; letter-spacing: 2px;">
                PLAYLIST • {len(df)} TRACKS
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Create scrollable container for playlist items
        st.markdown('<div class="mejs__playlist" style="max-height: 500px; overflow-y: auto; margin-top: 0; padding: 0;">', unsafe_allow_html=True)

        # Display each sentence as a clickable item
        for idx, row in df.iterrows():
            is_current = idx == st.session_state.current_index

            # Get duration
            if idx in st.session_state.audio_durations:
                duration_sec = int(st.session_state.audio_durations[idx])
                timestamp = f"{duration_sec // 60:02d}:{duration_sec % 60:02d}"
            else:
                timestamp = "00:00"

            # Create button label with sentence info
            english_text = row["English"]
            korean_text = row.get("Korean", "")

            # Truncate if too long
            if len(english_text) > 50:
                display_english = english_text[:47] + "..."
            else:
                display_english = english_text

            button_label = f"{idx + 1}. {display_english}"

            # Create clickable button
            button_type = "primary" if is_current else "secondary"
            if st.button(
                button_label,
                key=f"playlist_{idx}",
                help=f"{english_text}\n{korean_text}\n[{timestamp}]",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_index = idx
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

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

    # Winamp 스타일 CSS
    st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp {
        background: #000000 !important;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
    }

    /* Winamp 메인 플레이어 */
    .winamp-player {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%);
        border: 2px outset #4a6a8a;
        border-radius: 0;
        padding: 0;
        margin: 20px auto;
        max-width: 900px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.8);
        font-family: 'Tahoma', 'Arial', sans-serif;
    }

    /* 플레이어 헤더 */
    .winamp-header {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%);
        padding: 4px 8px;
        border-bottom: 1px solid #1a2a3a;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .winamp-title {
        color: #ffffff;
        font-size: 11px;
        font-weight: bold;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.5);
    }

    /* 디스플레이 영역 */
    .winamp-display {
        background: #000000;
        border: 2px inset #1a2a3a;
        margin: 8px;
        padding: 20px 15px;
        min-height: 100px;
    }

    .winamp-time {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.8);
        letter-spacing: 4px;
    }

    .winamp-text {
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 28px;
        text-shadow: 0 0 4px rgba(0, 255, 0, 0.6);
        margin-top: 12px;
        font-weight: bold;
    }

    .winamp-text-korean {
        color: #00aaff;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        font-size: 18px;
        text-shadow: 0 0 4px rgba(0, 170, 255, 0.6);
        margin-top: 8px;
    }

    /* 비주얼라이저 */
    .visualizer {
        background: #000000;
        border: 2px inset #1a2a3a;
        margin: 0 8px 8px 8px;
        padding: 12px 8px;
        height: 80px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 2px;
    }

    .viz-bar {
        width: 4px;
        background: linear-gradient(180deg, #00ff00 0%, #00aa00 100%);
        border: 1px solid #00ff00;
        box-shadow: 0 0 4px rgba(0, 255, 0, 0.6);
        animation: vizPulse 0.8s ease-in-out infinite;
    }

    @keyframes vizPulse {
        0%, 100% { transform: scaleY(0.3); opacity: 0.6; }
        50% { transform: scaleY(1); opacity: 1; }
    }

    /* Winamp 컨트롤 패널 */
    .winamp-controls {
        background: linear-gradient(180deg, #2a4a6a 0%, #1a2a3a 100%);
        padding: 12px 20px;
        border-top: 1px solid #4a6a8a;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
    }

    .winamp-btn {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%);
        border: 2px outset #5a7a9a;
        border-radius: 3px;
        color: #ffffff;
        font-family: 'Tahoma', sans-serif;
        font-size: 18px;
        font-weight: bold;
        width: 50px;
        height: 40px;
        cursor: pointer;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.5);
        transition: all 0.05s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .winamp-btn:hover {
        background: linear-gradient(180deg, #5a7a9a 0%, #3a5a7a 100%);
        border-color: #6a8aaa;
    }

    .winamp-btn:active {
        border-style: inset;
        background: linear-gradient(180deg, #3a5a7a 0%, #2a4a6a 100%);
    }

    .winamp-btn-play {
        background: linear-gradient(180deg, #00aa00 0%, #008800 100%);
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

    /* 버튼 스타일 - Winamp 컨트롤용 */
    .winamp-controls-container .stButton > button {
        background: linear-gradient(180deg, #4a6a8a 0%, #2a4a6a 100%) !important;
        border: 2px outset #5a7a9a !important;
        border-radius: 3px !important;
        color: #ffffff !important;
        font-family: 'Tahoma', 'Arial', sans-serif !important;
        font-size: 20px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.5) !important;
        padding: 8px 16px !important;
        min-width: 60px !important;
        height: 50px !important;
        transition: all 0.05s !important;
    }

    .winamp-controls-container .stButton > button:hover {
        background: linear-gradient(180deg, #5a7a9a 0%, #3a5a7a 100%) !important;
        border: 2px outset #6a8aaa !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }

    .winamp-controls-container .stButton > button:active {
        border: 2px inset #3a5a7a !important;
        background: linear-gradient(180deg, #3a5a7a 0%, #2a4a6a 100%) !important;
        transform: translateY(1px);
        box-shadow: none !important;
    }

    /* 재생 버튼 특별 스타일 */
    .winamp-controls-container div[data-testid="column"]:nth-child(3) .stButton > button {
        background: linear-gradient(180deg, #00aa00 0%, #008800 100%) !important;
        border: 2px outset #00cc00 !important;
        min-width: 80px !important;
        height: 60px !important;
        font-size: 28px !important;
    }

    .winamp-controls-container div[data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: linear-gradient(180deg, #00cc00 0%, #00aa00 100%) !important;
        border: 2px outset #00ff00 !important;
    }

    .winamp-controls-container div[data-testid="column"]:nth-child(3) .stButton > button:active {
        background: linear-gradient(180deg, #008800 0%, #006600 100%) !important;
        border: 2px inset #00aa00 !important;
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
    st.markdown('</div>', unsafe_allow_html=True)

    # 비주얼라이저 - 랜덤 높이로 동적 변화
    import random
    heights = [random.randint(10, 70) for _ in range(40)]
    viz_bars = ''.join([f'<div class="viz-bar" style="height: {h}px; animation-delay: {i*0.05}s;"></div>' for i, h in enumerate(heights)])
    st.markdown(f'<div class="visualizer">{viz_bars}</div>', unsafe_allow_html=True)

    # Winamp 컨트롤 패널 시작
    st.markdown('<div class="winamp-controls">', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # MediaElement.js 플레이어
    audio_placeholder = st.empty()

    # Winamp 스타일 버튼 컨테이너
    st.markdown('<div class="winamp-controls-container">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])

    with col1:
        if st.button("⏮", use_container_width=True, help="이전 문장"):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
            else:
                st.session_state.current_index = len(df) - 1
            st.rerun()

    with col2:
        if st.button("⏪", use_container_width=True, help="처음으로"):
            st.session_state.current_index = 0
            st.rerun()

    with col3:
        if st.button("▶️", use_container_width=True, help="재생", type="primary"):
            play_audio_with_stats_v2(
                current_sentence['English'],
                current_idx,
                st.session_state.playback_speed,
                audio_placeholder
            )

    with col4:
        if st.button("⏩", use_container_width=True, help="마지막으로"):
            st.session_state.current_index = len(df) - 1
            st.rerun()

    with col5:
        if st.button("⏭", use_container_width=True, help="다음 문장"):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Winamp 플레이리스트
    st.markdown('<div class="winamp-playlist">', unsafe_allow_html=True)
    st.markdown(f'<div class="playlist-header">PLAYLIST - {len(df)} SENTENCES</div>', unsafe_allow_html=True)
    st.markdown('<div class="playlist-content">', unsafe_allow_html=True)

    for idx, row in df.iterrows():
        is_current = idx == st.session_state.current_index
        item_class = "playlist-item-current" if is_current else "playlist-item"

        # 실제 오디오 길이로 시간 계산
        if idx in st.session_state.audio_durations:
            duration_sec = int(st.session_state.audio_durations[idx])
            timestamp = f"{duration_sec // 60:02d}:{duration_sec % 60:02d}"
        else:
            timestamp = "00:00"

        sentence_html = f'<div class="{item_class}">{idx + 1}. {row["English"]}<span class="playlist-time">{timestamp}</span></div>'
        st.markdown(sentence_html, unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

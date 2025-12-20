"""
English Sentence Practice App
영어 문장 반복 연습 프로그램

세련된 Streamlit 기반 영어 반복 학습 애플리케이션
"""

import streamlit as st
import time
from utils import (
    initialize_session_state,
    load_and_validate_csv,
    parse_text_input,
    get_sentence_stats,
    generate_audio,
    pregenerate_audio,
    play_audio_with_stats,
    save_session_to_json,
    load_session_from_json,
    apply_custom_css,
    display_transcript_list
)


def main():
    """메인 애플리케이션"""

    # 페이지 설정
    st.set_page_config(
        page_title="영어 문장 반복 연습",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 세션 초기화
    initialize_session_state()

    # 커스텀 CSS 적용
    apply_custom_css(st.session_state.dark_mode)

    # ========== 사이드바 ==========
    with st.sidebar:
        st.title("⚙️ 설정")

        # 입력 방식 선택
        st.subheader("데이터 입력")
        input_method = st.radio(
            "입력 방식 선택",
            ["CSV 파일 업로드", "텍스트 붙여넣기"],
            help="CSV 파일을 업로드하거나 영어 문장을 직접 붙여넣으세요"
        )

        if input_method == "CSV 파일 업로드":
            # CSV 파일 업로드
            uploaded_file = st.file_uploader(
                "CSV 파일 업로드",
                type=['csv'],
                help="English와 Korean 열이 포함된 CSV 파일을 업로드하세요"
            )

            if uploaded_file is not None:
                df = load_and_validate_csv(uploaded_file)
                if df is not None:
                    st.session_state.df = df

                    # 모든 오디오를 미리 생성
                    pregenerate_audio(df)

                    st.success(f"✓ {len(df)}개 문장 로드 완료")

        else:  # 텍스트 붙여넣기
            # 영어 문장 입력
            english_text = st.text_area(
                "영어 문장 입력",
                height=200,
                placeholder="영어 문장을 한 줄에 하나씩 입력하세요.\n예:\nI love programming.\nPython is awesome.\nLet's practice English!",
                help="각 줄에 하나의 영어 문장을 입력하세요"
            )

            # 한국어 번역 포함 여부
            include_korean = st.checkbox(
                "한국어 번역 포함",
                value=False,
                help="한국어 번역도 함께 입력하려면 체크하세요"
            )

            korean_text = ""
            if include_korean:
                korean_text = st.text_area(
                    "한국어 번역 입력",
                    height=200,
                    placeholder="한국어 번역을 한 줄에 하나씩 입력하세요.\n예:\n나는 프로그래밍을 좋아합니다.\n파이썬은 멋집니다.\n영어를 연습해봅시다!",
                    help="영어 문장과 같은 순서로 한국어 번역을 입력하세요"
                )

            # 로드 버튼
            if st.button("문장 로드", use_container_width=True, type="primary"):
                if english_text.strip():
                    df = parse_text_input(english_text, include_korean, korean_text)
                    if df is not None:
                        st.session_state.df = df

                        # 모든 오디오를 미리 생성
                        pregenerate_audio(df)

                        st.success(f"✓ {len(df)}개 문장 로드 완료")
                else:
                    st.warning("영어 문장을 입력해주세요.")

        st.divider()

        # 재생 모드 선택
        st.subheader("재생 모드")
        repeat_mode = st.radio(
            "모드 선택",
            ["개별 반복", "전체 루프", "쉐도잉"],
            key="repeat_mode_selector",
            help="학습 방식을 선택하세요"
        )
        st.session_state.repeat_mode = repeat_mode

        # 재생 설정
        st.subheader("재생 설정")

        playback_speed = st.slider(
            "재생 속도",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.playback_speed,
            step=0.1,
            format="%.1fx"
        )
        st.session_state.playback_speed = playback_speed

        auto_play = st.checkbox(
            "자동 재생",
            value=st.session_state.auto_play,
            help="재생 버튼을 누르면 모든 문장을 자동으로 순차 재생합니다"
        )
        st.session_state.auto_play = auto_play

        # 자동 재생이 활성화된 경우 간격 설정
        if auto_play:
            auto_play_interval = st.slider(
                "문장 간 간격 (초)",
                min_value=0,
                max_value=5,
                value=st.session_state.get('auto_play_interval', 1),
                help="다음 문장 재생 전 대기 시간"
            )
            st.session_state.auto_play_interval = auto_play_interval

        # 모드별 추가 설정
        if repeat_mode == "개별 반복":
            target_repeats = st.number_input(
                "목표 반복 횟수",
                min_value=1,
                max_value=20,
                value=st.session_state.target_repeats,
                help="각 문장을 몇 번 반복할지 설정하세요"
            )
            st.session_state.target_repeats = target_repeats

        elif repeat_mode == "전체 루프":
            loop_target = st.number_input(
                "목표 루프 횟수",
                min_value=1,
                max_value=100,
                value=st.session_state.loop_target,
                help="전체 문장을 몇 번 반복할지 설정하세요"
            )
            st.session_state.loop_target = loop_target

            # 현재 루프 진행 상황
            st.caption(f"현재 루프: {st.session_state.loop_count} / {st.session_state.loop_target}")

        elif repeat_mode == "쉐도잉":
            shadowing_delay = st.slider(
                "쉐도잉 대기 시간 (초)",
                min_value=1,
                max_value=10,
                value=st.session_state.shadowing_delay,
                help="음성 재생 후 따라 말할 시간을 설정하세요"
            )
            st.session_state.shadowing_delay = shadowing_delay

        st.divider()

        # UI 옵션
        st.subheader("표시 옵션")

        show_translation = st.checkbox(
            "한국어 번역 표시",
            value=st.session_state.show_translation
        )
        st.session_state.show_translation = show_translation

        show_stats = st.checkbox(
            "통계 표시",
            value=st.session_state.show_stats
        )
        st.session_state.show_stats = show_stats

        dark_mode = st.checkbox(
            "다크 모드",
            value=st.session_state.dark_mode
        )
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()

        st.divider()

        # 세션 관리
        st.subheader("세션 관리")

        if st.button("💾 진행 상황 저장", use_container_width=True):
            json_data = save_session_to_json()
            st.download_button(
                label="다운로드",
                data=json_data,
                file_name=f"session_{st.session_state.session_start_time.strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            st.success("세션이 저장되었습니다!")

        uploaded_session = st.file_uploader(
            "진행 상황 불러오기",
            type=['json'],
            key="session_upload"
        )

        if uploaded_session is not None:
            json_str = uploaded_session.read().decode('utf-8')
            if load_session_from_json(json_str):
                st.success("세션이 복원되었습니다!")
                st.rerun()

        if st.button("🔄 세션 초기화", use_container_width=True):
            # 세션 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ========== 메인 영역 ==========
    # Winamp 스타일 CSS
    st.markdown("""
    <style>
    /* Winamp 메인 컨테이너 */
    .media-player-container {
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        border: 2px solid #4a4a4a;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 4px 8px rgba(0,0,0,0.5);
        font-family: 'Courier New', monospace;
    }
    
    /* Winamp 스타일 오디오 비주얼라이저 */
    .audio-visualizer {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 2px solid #4a4a4a;
        border-radius: 4px;
        padding: 20px;
        margin: 15px 0;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);
    }
    
    .waveform-bars {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
        height: 100px;
    }
    
    .waveform-bar {
        width: 5px;
        background: linear-gradient(180deg, #00FF41 0%, #00FF00 50%, #00A8FF 100%);
        border: 1px solid #00FF41;
        border-radius: 2px;
        animation: winampWave 0.8s ease-in-out infinite;
        box-shadow: 0 0 4px rgba(0, 255, 65, 0.6);
    }
    
    @keyframes winampWave {
        0%, 100% { transform: scaleY(0.2); opacity: 0.6; }
        50% { transform: scaleY(1); opacity: 1; }
    }
    
    /* Winamp 스타일 문장 디스플레이 */
    .sentence-display {
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        border: 2px solid #4a4a4a;
        border-radius: 4px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .sentence-display h2 {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 255, 65, 0.8), 0 0 4px rgba(0, 255, 65, 0.6);
        font-size: 28px;
        margin-bottom: 15px;
    }
    
    .sentence-display p {
        color: #00A8FF !important;
        font-family: 'Courier New', monospace;
        font-size: 18px;
        text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);
    }
    
    /* Winamp 스타일 진행 바 */
    .progress-container {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 2px solid #4a4a4a;
        border-radius: 4px;
        padding: 12px;
        margin: 15px 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);
    }
    
    .progress-container > div:first-child {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8);
    }
    
    .progress-container > div:last-child {
        background: #1a1a1a !important;
        border: 1px solid #4a4a4a;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);
    }
    
    .progress-container > div:last-child > div {
        background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%) !important;
        box-shadow: 0 0 8px rgba(0, 255, 65, 0.6);
    }
    
    /* Winamp 스타일 통계 카드 */
    .stat-card {
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        border: 2px solid #4a4a4a;
        border-radius: 4px;
        padding: 12px;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .stat-card > div:first-child {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);
    }
    
    .stat-card > div:last-child {
        color: #00A8FF !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);
    }
    
    /* Winamp 스타일 버튼 */
    .stButton > button {
        background: linear-gradient(180deg, #3a3a3a 0%, #2a2a2a 100%) !important;
        border: 2px solid #4a4a4a !important;
        border-radius: 4px !important;
        color: #00FF41 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 2px 4px rgba(0,0,0,0.5) !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(180deg, #4a4a4a 0%, #3a3a3a 100%) !important;
        border-color: #00FF41 !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 0 8px rgba(0, 255, 65, 0.4) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #00A8FF 0%, #0088CC 100%) !important;
        border-color: #00FF41 !important;
        color: #000000 !important;
        text-shadow: none !important;
    }
    
    /* MediaElement.js Winamp 스타일 */
    .mejs__container {
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
        border: 2px solid #4a4a4a !important;
        border-radius: 4px !important;
        padding: 8px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    .mejs__controls {
        background: transparent !important;
    }
    
    .mejs__button > button {
        color: #00FF41 !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
    }
    
    .mejs__time {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
    }
    
    .mejs__time-rail {
        background: #1a1a1a !important;
        border: 1px solid #4a4a4a !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8) !important;
    }
    
    .mejs__time-loaded {
        background: #2a2a2a !important;
    }
    
    .mejs__time-current {
        background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%) !important;
        box-shadow: 0 0 6px rgba(0, 255, 65, 0.6) !important;
    }
    
    .mejs__volume-button > button {
        color: #00FF41 !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
    }
    
    .mejs__horizontal-volume-slider {
        background: #1a1a1a !important;
        border: 1px solid #4a4a4a !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.8) !important;
    }
    
    .mejs__horizontal-volume-current {
        background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%) !important;
        box-shadow: 0 0 4px rgba(0, 255, 65, 0.6) !important;
    }
    
    /* Winamp 스타일 체크박스 */
    .stCheckbox > label {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.6) !important;
    }
    
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%) !important;
    }
    
    /* 제목 스타일 */
    h1, h2, h3 {
        color: #00FF41 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 8px rgba(0, 255, 65, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("👈 왼쪽 사이드바에서 데이터를 입력해주세요.")
        st.markdown("""
        ### 사용 방법
        1. **데이터 입력**:
           - **CSV 파일**: English와 Korean 열이 포함된 CSV 파일 업로드
           - **텍스트 붙여넣기**: 영어 문장을 복사해서 붙여넣기 (선택적으로 한국어 번역 포함)
        2. **모드 선택**: 개별 반복, 전체 루프, 쉐도잉 중 선택
        3. **학습 시작**: 재생 버튼을 눌러 학습 시작

        ### 3가지 학습 모드
        - **개별 반복**: 한 문장을 여러 번 반복한 후 다음으로 진행
        - **전체 루프**: 모든 문장을 처음부터 끝까지 여러 번 반복
        - **쉐도잉**: 음성 재생 후 따라 말할 시간을 제공

        ### 텍스트 붙여넣기 예시
        사이드바에서 "텍스트 붙여넣기"를 선택한 후:
        ```
        I love learning English.
        Practice makes perfect.
        Every day is a new opportunity.
        ```
        """)
        return

    df = st.session_state.df

    # ===== 미디어 플레이어 스타일 메인 컨테이너 =====
    current_idx = st.session_state.current_index
    if current_idx >= len(df):
        current_idx = 0
        st.session_state.current_index = 0

    current_sentence = df.iloc[current_idx]
    sentence_stats = get_sentence_stats(current_idx)

    # 현재 문장을 표시할 placeholder 생성
    current_sentence_display = st.empty()
    audio_visualizer_placeholder = st.empty()
    progress_info_placeholder = st.empty()

    # 오디오 시각화 생성 함수
    def render_audio_visualizer(is_playing=False):
        """오디오 시각화를 렌더링"""
        import random
        bars = []
        bar_heights = []
        for i in range(40):
            if is_playing:
                height = random.randint(20, 120)
            else:
                height = random.randint(5, 30)
            bar_heights.append(height)
            delay = i * 0.05
            bars.append(f'<div class="waveform-bar" style="height: {height}px; animation-delay: {delay}s;"></div>')
        
        visualizer_html = f"""
        <div class="audio-visualizer">
            <div class="waveform-bars">
                {''.join(bars)}
            </div>
        </div>
        """
        return visualizer_html

    # 문장 카드 렌더링 함수
    def render_sentence_card(sentence_text, translation_text=""):
        """문장 카드를 미디어 플레이어 스타일로 렌더링"""
        card_html = f"""
        <div class="sentence-display">
            <h2 style='font-size: 36px; margin-bottom: 20px; color: #1a1a1a; font-weight: 600;'>{sentence_text}</h2>
        """
        if translation_text and st.session_state.show_translation:
            card_html += f"<p style='color: #666; font-size: 20px; font-style: italic; margin-top: 10px;'>{translation_text}</p>"
        card_html += "</div>"
        return card_html

    # 미디어 플레이어 컨테이너 시작
    st.markdown('<div class="media-player-container">', unsafe_allow_html=True)
    
    # 초기 표시
    current_sentence_display.markdown(
        render_sentence_card(current_sentence['English'], current_sentence['Korean']),
        unsafe_allow_html=True
    )
    audio_visualizer_placeholder.markdown(
        render_audio_visualizer(is_playing=False),
        unsafe_allow_html=True
    )

    # 진행 정보 표시 (Winamp 스타일)
    progress_percentage = ((current_idx + 1) / len(df)) * 100
    progress_html = f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: #00FF41; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 255, 65, 0.8);">
            <span>문장 {current_idx + 1} / {len(df)}</span>
            <span>{progress_percentage:.1f}%</span>
        </div>
        <div style="background: #1a1a1a; height: 10px; border: 1px solid #4a4a4a; border-radius: 2px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);">
            <div style="background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%); height: 100%; width: {progress_percentage}%; transition: width 0.3s ease; box-shadow: 0 0 6px rgba(0, 255, 65, 0.6);"></div>
        </div>
    </div>
    """
    progress_info_placeholder.markdown(progress_html, unsafe_allow_html=True)

    # 통계 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 24px; font-weight: bold; color: #00FF41; font-family: 'Courier New', monospace; text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);">{sentence_stats['listen_count']}</div>
            <div style="font-size: 12px; color: #00A8FF; margin-top: 5px; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);">재생 횟수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        mastered_count = len(st.session_state.mastered_sentences)
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 24px; font-weight: bold; color: #00FF41; font-family: 'Courier New', monospace; text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);">{mastered_count}</div>
            <div style="font-size: 12px; color: #00A8FF; margin-top: 5px; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);">마스터 완료</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_practiced = len(st.session_state.practice_stats)
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 24px; font-weight: bold; color: #00FF41; font-family: 'Courier New', monospace; text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);">{total_practiced}</div>
            <div style="font-size: 12px; color: #00A8FF; margin-top: 5px; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);">연습한 문장</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mode_icon = "🔁" if st.session_state.repeat_mode == "전체 루프" else "🔂" if st.session_state.repeat_mode == "개별 반복" else "🎤"
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 24px; font-weight: bold; color: #00FF41; font-family: 'Courier New', monospace; text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);">{mode_icon}</div>
            <div style="font-size: 12px; color: #00A8FF; margin-top: 5px; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 168, 255, 0.6);">{st.session_state.repeat_mode}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 마스터 체크박스
    is_mastered = current_idx in st.session_state.mastered_sentences
    if st.checkbox("✓ 마스터 완료", value=is_mastered, key=f"master_{current_idx}"):
        st.session_state.mastered_sentences.add(current_idx)
    else:
        st.session_state.mastered_sentences.discard(current_idx)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 미디어 플레이어 컨테이너 종료
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== 미디어 플레이어 스타일 컨트롤 버튼들 =====
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

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
        play_button_clicked = st.button("▶️ 재생", use_container_width=True, type="primary", help="재생/일시정지")
        if play_button_clicked:
            # 개별 반복 모드인 경우
            if st.session_state.repeat_mode == "개별 반복":
                repeat_count = st.session_state.target_repeats
                progress_placeholder = st.empty()
                audio_container = st.container()

                # 자동 재생이 활성화된 경우 현재 문장부터 끝까지 재생
                if st.session_state.auto_play:
                    start_idx = current_idx
                    for idx in range(start_idx, len(df)):
                        row = df.iloc[idx]

                        # 화면 업데이트
                        current_sentence_display.markdown(
                            render_sentence_card(row['English'], row['Korean']),
                            unsafe_allow_html=True
                        )
                        audio_visualizer_placeholder.markdown(
                            render_audio_visualizer(is_playing=True),
                            unsafe_allow_html=True
                        )
                        
                        # 진행 정보 업데이트
                        progress_percentage = ((idx + 1) / len(df)) * 100
                        progress_html = f"""
                        <div class="progress-container">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: #00FF41; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 255, 65, 0.8);">
                                <span>문장 {idx + 1} / {len(df)}</span>
                                <span>{progress_percentage:.1f}%</span>
                            </div>
                            <div style="background: #1a1a1a; height: 10px; border: 1px solid #4a4a4a; border-radius: 2px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);">
                                <div style="background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%); height: 100%; width: {progress_percentage}%; transition: width 0.3s ease; box-shadow: 0 0 6px rgba(0, 255, 65, 0.6);"></div>
                            </div>
                        </div>
                        """
                        progress_info_placeholder.markdown(progress_html, unsafe_allow_html=True)

                        # 각 문장을 반복 횟수만큼 재생
                        for i in range(repeat_count):
                            progress_placeholder.info(f"🔊 **{idx + 1}/{len(df)} 문장 - {i+1}/{repeat_count}회 재생 중...**")

                            with audio_container:
                                audio_placeholder = st.empty()
                                audio_duration = play_audio_with_stats(
                                    row['English'],
                                    idx,
                                    st.session_state.playback_speed,
                                    autoplay=True,
                                    audio_placeholder=audio_placeholder
                                )

                            # 실제 오디오 재생 시간만큼 대기
                            time.sleep(audio_duration)

                        # 문장 간 간격
                        if idx < len(df) - 1:
                            time.sleep(st.session_state.auto_play_interval)

                        # 현재 인덱스 업데이트
                        st.session_state.current_index = idx

                    # 다음 문장으로 이동
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=False),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.success(f"✓ 자동 재생 완료!")

                # 수동 재생 (현재 문장만)
                else:
                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=True),
                        unsafe_allow_html=True
                    )
                    for i in range(repeat_count):
                        progress_placeholder.info(f"🔊 **{i+1}/{repeat_count}회 재생 중...**")

                        with audio_container:
                            audio_placeholder = st.empty()
                            audio_duration = play_audio_with_stats(
                                current_sentence['English'],
                                current_idx,
                                st.session_state.playback_speed,
                                autoplay=True,
                                audio_placeholder=audio_placeholder
                            )

                        # 실제 오디오 재생 시간만큼 대기
                        time.sleep(audio_duration)

                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=False),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.success(f"✓ {repeat_count}번 반복 완료!")

            # 쉐도잉 모드인 경우
            elif st.session_state.repeat_mode == "쉐도잉":
                progress_placeholder = st.empty()
                audio_container = st.container()

                # 자동 재생이 활성화된 경우
                if st.session_state.auto_play:
                    start_idx = current_idx
                    for idx in range(start_idx, len(df)):
                        row = df.iloc[idx]

                        # 화면 업데이트
                        current_sentence_display.markdown(
                            render_sentence_card(row['English'], row['Korean']),
                            unsafe_allow_html=True
                        )
                        audio_visualizer_placeholder.markdown(
                            render_audio_visualizer(is_playing=True),
                            unsafe_allow_html=True
                        )
                        
                        # 진행 정보 업데이트
                        progress_percentage = ((idx + 1) / len(df)) * 100
                        progress_html = f"""
                        <div class="progress-container">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: #00FF41; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 255, 65, 0.8);">
                                <span>문장 {idx + 1} / {len(df)}</span>
                                <span>{progress_percentage:.1f}%</span>
                            </div>
                            <div style="background: #1a1a1a; height: 10px; border: 1px solid #4a4a4a; border-radius: 2px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);">
                                <div style="background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%); height: 100%; width: {progress_percentage}%; transition: width 0.3s ease; box-shadow: 0 0 6px rgba(0, 255, 65, 0.6);"></div>
                            </div>
                        </div>
                        """
                        progress_info_placeholder.markdown(progress_html, unsafe_allow_html=True)

                        # 재생
                        progress_placeholder.info(f"🔊 **{idx + 1}/{len(df)} 문장 재생 중...**")
                        with audio_container:
                            audio_placeholder = st.empty()
                            audio_duration = play_audio_with_stats(
                                row['English'],
                                idx,
                                st.session_state.playback_speed,
                                autoplay=True,
                                audio_placeholder=audio_placeholder
                            )

                        # 실제 오디오 재생 시간만큼 대기
                        time.sleep(audio_duration)

                        # 쉐도잉 시간
                        audio_visualizer_placeholder.markdown(
                            render_audio_visualizer(is_playing=False),
                            unsafe_allow_html=True
                        )
                        progress_placeholder.info(f"🎤 **따라 말하세요... ({st.session_state.shadowing_delay}초)**")
                        time.sleep(st.session_state.shadowing_delay)

                        # 문장 간 간격
                        if idx < len(df) - 1:
                            time.sleep(st.session_state.auto_play_interval)

                        # 현재 인덱스 업데이트
                        st.session_state.current_index = idx

                    # 다음 문장으로 이동
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
                    progress_placeholder.success("✓ 쉐도잉 자동 재생 완료!")

                # 수동 재생 (현재 문장만)
                else:
                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=True),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.info("🔊 **재생 중...**")
                    with audio_container:
                        audio_placeholder = st.empty()
                        audio_duration = play_audio_with_stats(
                            current_sentence['English'],
                            current_idx,
                            st.session_state.playback_speed,
                            autoplay=True,
                            audio_placeholder=audio_placeholder
                        )

                    # 실제 오디오 재생 시간만큼 대기
                    time.sleep(audio_duration)

                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=False),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.info(f"🎤 **따라 말하세요... ({st.session_state.shadowing_delay}초)**")
                    time.sleep(st.session_state.shadowing_delay)

                    progress_placeholder.success("✓ 다음 문장으로 이동할 수 있습니다!")

            # 전체 루프 모드인 경우
            else:
                progress_placeholder = st.empty()
                audio_container = st.container()

                # 자동 재생이 활성화된 경우
                if st.session_state.auto_play:
                    start_idx = current_idx
                    for idx in range(start_idx, len(df)):
                        row = df.iloc[idx]

                        # 화면 업데이트
                        current_sentence_display.markdown(
                            render_sentence_card(row['English'], row['Korean']),
                            unsafe_allow_html=True
                        )
                        audio_visualizer_placeholder.markdown(
                            render_audio_visualizer(is_playing=True),
                            unsafe_allow_html=True
                        )
                        
                        # 진행 정보 업데이트
                        progress_percentage = ((idx + 1) / len(df)) * 100
                        progress_html = f"""
                        <div class="progress-container">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: #00FF41; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 4px rgba(0, 255, 65, 0.8);">
                                <span>문장 {idx + 1} / {len(df)}</span>
                                <span>{progress_percentage:.1f}%</span>
                            </div>
                            <div style="background: #1a1a1a; height: 10px; border: 1px solid #4a4a4a; border-radius: 2px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);">
                                <div style="background: linear-gradient(90deg, #00FF41 0%, #00A8FF 100%); height: 100%; width: {progress_percentage}%; transition: width 0.3s ease; box-shadow: 0 0 6px rgba(0, 255, 65, 0.6);"></div>
                            </div>
                        </div>
                        """
                        progress_info_placeholder.markdown(progress_html, unsafe_allow_html=True)

                        # 재생
                        progress_placeholder.info(f"🔊 **{idx + 1}/{len(df)} 문장 재생 중...**")
                        with audio_container:
                            audio_placeholder = st.empty()
                            audio_duration = play_audio_with_stats(
                                row['English'],
                                idx,
                                st.session_state.playback_speed,
                                autoplay=True,
                                audio_placeholder=audio_placeholder
                            )

                        # 실제 오디오 재생 시간만큼 대기
                        time.sleep(audio_duration)

                        # 문장 간 간격
                        if idx < len(df) - 1:
                            time.sleep(st.session_state.auto_play_interval)

                        # 현재 인덱스 업데이트
                        st.session_state.current_index = idx

                    # 다음 문장으로 이동
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(df)
                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=False),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.success("✓ 자동 재생 완료!")

                # 수동 재생 (현재 문장만)
                else:
                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=True),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.info("🔊 **재생 중...**")
                    with audio_container:
                        audio_placeholder = st.empty()
                        audio_duration = play_audio_with_stats(
                            current_sentence['English'],
                            current_idx,
                            st.session_state.playback_speed,
                            autoplay=True,
                            audio_placeholder=audio_placeholder
                        )

                    # 실제 오디오 재생 시간만큼 대기
                    time.sleep(audio_duration)

                    audio_visualizer_placeholder.markdown(
                        render_audio_visualizer(is_playing=False),
                        unsafe_allow_html=True
                    )
                    progress_placeholder.success("✓ 재생 완료!")

    with col4:
        if st.button("⏩", use_container_width=True, help="마지막으로"):
            st.session_state.current_index = len(df) - 1
            st.rerun()

    with col5:
        if st.button("⏭", use_container_width=True, help="다음 문장"):
            # 다음 문장으로 이동
            st.session_state.current_index = (st.session_state.current_index + 1) % len(df)

            # 전체 루프 모드인 경우, 처음으로 돌아왔을 때 루프 카운트 증가
            if st.session_state.repeat_mode == "전체 루프" and st.session_state.current_index == 0:
                st.session_state.loop_count += 1
                if st.session_state.loop_count >= st.session_state.loop_target:
                    st.balloons()
                    st.success(f"🎉 목표 달성! {st.session_state.loop_target}회 루프 완료!")

            st.rerun()

    st.divider()

    # ===== 하단: 전체 문장 리스트 =====
    display_transcript_list(df)


if __name__ == "__main__":
    main()

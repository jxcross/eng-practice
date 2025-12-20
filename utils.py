"""
Utility functions for English sentence practice app
영어 문장 반복 연습 프로그램 유틸리티 함수
"""

import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from pydub import AudioSegment


# ============================================================
# 세션 상태 관리
# ============================================================

def initialize_session_state():
    """모든 세션 상태 변수를 초기화합니다."""

    # 데이터 관련
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    # 재생 모드 관련
    if 'repeat_mode' not in st.session_state:
        st.session_state.repeat_mode = "개별 반복"  # "개별 반복", "전체 루프", "쉐도잉"
    if 'playback_speed' not in st.session_state:
        st.session_state.playback_speed = 1.0
    if 'auto_play' not in st.session_state:
        st.session_state.auto_play = False
    if 'auto_play_interval' not in st.session_state:
        st.session_state.auto_play_interval = 1

    # 반복 설정
    if 'target_repeats' not in st.session_state:
        st.session_state.target_repeats = 3
    if 'loop_count' not in st.session_state:
        st.session_state.loop_count = 0
    if 'loop_target' not in st.session_state:
        st.session_state.loop_target = 5
    if 'shadowing_delay' not in st.session_state:
        st.session_state.shadowing_delay = 3

    # 진행 추적
    if 'practice_stats' not in st.session_state:
        st.session_state.practice_stats = {}
    if 'mastered_sentences' not in st.session_state:
        st.session_state.mastered_sentences = set()

    # 세션 정보
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if 'total_listens' not in st.session_state:
        st.session_state.total_listens = 0

    # UI 설정
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'show_translation' not in st.session_state:
        st.session_state.show_translation = True
    if 'show_stats' not in st.session_state:
        st.session_state.show_stats = True

    # Audio cache
    if 'audio_cache' not in st.session_state:
        st.session_state.audio_cache = {}  # {index: audio_bytes}
    if 'audio_durations' not in st.session_state:
        st.session_state.audio_durations = {}  # {index: duration_seconds}


def save_session_to_json() -> str:
    """세션 상태를 JSON 문자열로 저장합니다."""

    # datetime을 직렬화하기 위한 헬퍼 함수
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    # 세션 데이터 준비
    session_data = {
        'practice_stats': st.session_state.practice_stats,
        'mastered_sentences': list(st.session_state.mastered_sentences),
        'current_index': st.session_state.current_index,
        'session_start_time': st.session_state.session_start_time.isoformat(),
        'total_listens': st.session_state.total_listens,
        'loop_count': st.session_state.loop_count,
        'timestamp': datetime.now().isoformat(),
    }

    return json.dumps(session_data, indent=2, ensure_ascii=False, default=serialize_datetime)


def load_session_from_json(json_str: str) -> bool:
    """JSON 문자열에서 세션 상태를 복원합니다."""

    try:
        data = json.loads(json_str)

        # practice_stats의 키를 문자열에서 정수로 변환
        practice_stats = {}
        for key, value in data.get('practice_stats', {}).items():
            practice_stats[int(key)] = {
                'listen_count': value.get('listen_count', 0),
                'repeat_count': value.get('repeat_count', 0),
                'first_practiced': datetime.fromisoformat(value['first_practiced']) if 'first_practiced' in value else datetime.now(),
                'last_practiced': datetime.fromisoformat(value['last_practiced']) if 'last_practiced' in value else datetime.now(),
            }

        st.session_state.practice_stats = practice_stats
        st.session_state.mastered_sentences = set(data.get('mastered_sentences', []))
        st.session_state.current_index = data.get('current_index', 0)
        st.session_state.total_listens = data.get('total_listens', 0)
        st.session_state.loop_count = data.get('loop_count', 0)
        st.session_state.session_start_time = datetime.fromisoformat(data.get('session_start_time', datetime.now().isoformat()))

        return True
    except Exception as e:
        st.error(f"세션 로드 실패: {str(e)}")
        return False


# ============================================================
# 데이터 처리
# ============================================================

@st.cache_data
def load_and_validate_csv(file) -> pd.DataFrame:
    """CSV 파일을 로드하고 검증합니다."""

    try:
        df = pd.read_csv(file, encoding='utf-8')

        # 필수 컬럼 확인
        if 'English' not in df.columns or 'Korean' not in df.columns:
            raise ValueError("CSV 파일은 'English'와 'Korean' 열이 필요합니다.")

        if df.empty:
            raise ValueError("CSV 파일이 비어있습니다.")

        return df

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")
        return None


def parse_text_input(text: str, include_korean: bool = False, korean_text: str = "") -> pd.DataFrame:
    """
    텍스트 입력을 파싱하여 DataFrame으로 변환합니다.

    Args:
        text: 영어 문장들 (줄바꿈으로 구분)
        include_korean: 한국어 번역 포함 여부
        korean_text: 한국어 번역 텍스트 (줄바꿈으로 구분)

    Returns:
        pd.DataFrame: English와 Korean 열을 가진 데이터프레임
    """

    try:
        # 영어 문장 파싱
        english_sentences = [line.strip() for line in text.strip().split('\n') if line.strip()]

        if not english_sentences:
            raise ValueError("영어 문장을 입력해주세요.")

        # 한국어 번역 파싱
        if include_korean and korean_text:
            korean_sentences = [line.strip() for line in korean_text.strip().split('\n') if line.strip()]

            # 영어와 한국어 문장 수가 다른 경우, 한국어를 빈 문자열로 채움
            if len(korean_sentences) < len(english_sentences):
                korean_sentences.extend([''] * (len(english_sentences) - len(korean_sentences)))
            elif len(korean_sentences) > len(english_sentences):
                korean_sentences = korean_sentences[:len(english_sentences)]
        else:
            # 한국어 번역이 없는 경우 빈 문자열
            korean_sentences = [''] * len(english_sentences)

        # 데이터프레임 생성
        df = pd.DataFrame({
            'English': english_sentences,
            'Korean': korean_sentences
        })

        return df

    except Exception as e:
        st.error(f"텍스트 파싱 중 오류가 발생했습니다: {str(e)}")
        return None


def get_sentence_stats(index: int) -> dict:
    """특정 문장의 통계를 반환합니다."""

    if index in st.session_state.practice_stats:
        return st.session_state.practice_stats[index]
    else:
        return {
            'listen_count': 0,
            'repeat_count': 0,
            'first_practiced': None,
            'last_practiced': None,
        }


def calculate_progress() -> tuple:
    """전체 진행률을 계산합니다. (마스터한 문장 수, 전체 문장 수, 진행률)"""

    if st.session_state.df is None:
        return 0, 0, 0.0

    total = len(st.session_state.df)
    mastered = len(st.session_state.mastered_sentences)
    percentage = (mastered / total * 100) if total > 0 else 0.0

    return mastered, total, percentage


# ============================================================
# 오디오 생성 및 재생
# ============================================================

@st.cache_data
def _generate_base_audio(text: str) -> bytes:
    """
    기본 음성을 생성합니다 (속도 조절 없음).

    Args:
        text: 변환할 텍스트

    Returns:
        bytes: 기본 오디오 데이터
    """
    tts = gTTS(text=text, lang='en', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.getvalue()


def pregenerate_audio(df):
    """
    DataFrame의 모든 문장에 대해 기본 오디오를 미리 생성하여 캐시에 저장합니다.

    Args:
        df: English 컬럼이 있는 pandas DataFrame
    """
    import streamlit as st
    import time

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, row in df.iterrows():
        if idx not in st.session_state.audio_cache:
            status_text.text(f"오디오 생성 중... {idx + 1}/{len(df)}")

            # 기본 오디오 생성 (속도 조절 없이)
            base_audio_bytes = _generate_base_audio(row['English'])

            # 오디오 길이 계산
            fp = BytesIO(base_audio_bytes)
            audio = AudioSegment.from_file(fp, format="mp3")
            duration = len(audio) / 1000.0

            # 캐시에 저장
            st.session_state.audio_cache[idx] = base_audio_bytes
            st.session_state.audio_durations[idx] = duration

        progress_bar.progress((idx + 1) / len(df))

    status_text.text("✓ 모든 오디오 생성 완료!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()


def generate_audio(text: str, speed: float = 1.0) -> tuple:
    """
    텍스트를 음성으로 변환합니다 (기본 속도만).
    속도 조절은 브라우저의 playbackRate로 처리됩니다.

    Args:
        text: 변환할 텍스트
        speed: 재생 속도 (duration 계산에만 사용)

    Returns:
        tuple: (오디오 데이터 bytes, 재생 시간 float)
    """
    # 기본 오디오 생성 (캐싱됨)
    base_audio_bytes = _generate_base_audio(text)

    # 오디오 길이 계산
    fp = BytesIO(base_audio_bytes)
    audio = AudioSegment.from_file(fp, format="mp3")
    base_duration = len(audio) / 1000.0

    # 속도를 고려한 실제 재생 시간 계산
    duration = base_duration / speed

    return base_audio_bytes, duration


def play_audio_with_stats(text: str, index: int, speed: float = 1.0, autoplay: bool = True, audio_placeholder=None) -> float:
    """오디오를 재생하고 통계를 업데이트합니다.

    Returns:
        float: 오디오 재생 시간(초)
    """

    try:
        # 캐시에서 오디오를 가져오거나 생성
        if index in st.session_state.audio_cache:
            audio_bytes = st.session_state.audio_cache[index]
            base_duration = st.session_state.audio_durations[index]
            # 속도에 따른 재생 시간 계산
            duration = base_duration / speed
        else:
            # 캐시에 없으면 생성 (fallback)
            audio_bytes, duration = generate_audio(text, speed)

        if autoplay:
            # 간단하고 확실한 HTML5 오디오 플레이어 사용
            import base64
            import time as time_module
            import random
            audio_base64 = base64.b64encode(audio_bytes).decode()

            # 고유한 ID 생성 (timestamp + random으로 더 확실하게)
            unique_id = f"audio_{int(time_module.time() * 1000)}_{random.randint(1000, 9999)}"

            audio_html = f"""
                <audio id="{unique_id}" autoplay style="display: none;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                <script>
                    (function() {{
                        // 이전 오디오들 정지
                        if (window.currentAudioElement) {{
                            try {{
                                window.currentAudioElement.pause();
                                window.currentAudioElement.currentTime = 0;
                            }} catch(e) {{
                                console.log('Error stopping previous audio:', e);
                            }}
                        }}

                        // 새 오디오 엘리먼트 가져오기
                        var audio = document.getElementById('{unique_id}');
                        if (audio) {{
                            // 재생 속도 설정
                            audio.playbackRate = {speed};

                            // 현재 재생 중인 오디오로 설정
                            window.currentAudioElement = audio;

                            // 자동 재생
                            var playPromise = audio.play();
                            if (playPromise !== undefined) {{
                                playPromise.then(function() {{
                                    console.log('Audio playback started successfully');
                                }}).catch(function(error) {{
                                    console.error('Audio play failed:', error);
                                    // 재시도
                                    setTimeout(function() {{
                                        audio.play().catch(function(err) {{
                                            console.error('Audio play retry failed:', err);
                                        }});
                                    }}, 100);
                                }});
                            }}

                            // 재생 종료 시 정리
                            audio.addEventListener('ended', function() {{
                                if (window.currentAudioElement === audio) {{
                                    window.currentAudioElement = null;
                                }}
                            }});

                            // 에러 처리
                            audio.addEventListener('error', function(e) {{
                                console.error('Audio error:', e);
                            }});
                        }} else {{
                            console.error('Audio element not found');
                        }}
                    }})();
                </script>
            """

            # placeholder가 제공되면 먼저 비우고 새로 렌더링
            if audio_placeholder is not None:
                audio_placeholder.empty()
                audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.markdown(audio_html, unsafe_allow_html=True)
        else:
            # 일반 오디오 플레이어 표시
            st.audio(audio_bytes, format='audio/mp3')

        # 통계 업데이트
        st.session_state.total_listens += 1

        # 현재 문장 통계 업데이트
        if index not in st.session_state.practice_stats:
            st.session_state.practice_stats[index] = {
                'listen_count': 0,
                'repeat_count': 0,
                'first_practiced': datetime.now(),
                'last_practiced': datetime.now(),
            }

        st.session_state.practice_stats[index]['listen_count'] += 1
        st.session_state.practice_stats[index]['last_practiced'] = datetime.now()

        return duration

    except Exception as e:
        st.error(f"오디오 생성 실패: {str(e)}")
        return 0.0


# ============================================================
# UI 헬퍼 함수
# ============================================================

def apply_custom_css(dark_mode: bool = False):
    """커스텀 CSS를 적용합니다."""

    if dark_mode:
        css = """
        <style>
        /* Winamp 스타일 다크 모드 - 기본적으로 Winamp 스타일이므로 동일하게 유지 */
        .stApp {
            background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%) !important;
            color: #00FF41 !important;
        }
        .stMarkdown, .stText {
            color: #00A8FF !important;
            font-family: 'Courier New', monospace !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00FF41 !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 8px rgba(0, 255, 65, 0.8) !important;
        }

        /* Winamp 스타일 문장 카드 */
        div[style*="background-color: #f8f9fa"] {
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
            border: 2px solid #4a4a4a !important;
        }
        
        .sentence-display {
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
            border: 2px solid #4a4a4a !important;
        }
        .sentence-display h2 {
            color: #00FF41 !important;
            text-shadow: 0 0 8px rgba(0, 255, 65, 0.8) !important;
        }
        .sentence-display p {
            color: #00A8FF !important;
            text-shadow: 0 0 4px rgba(0, 168, 255, 0.6) !important;
        }
        .media-player-container {
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
            border: 2px solid #4a4a4a !important;
        }
        .audio-visualizer {
            background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%) !important;
            border: 2px solid #4a4a4a !important;
        }
        
        /* Winamp 스타일 MediaElement.js 플레이어 */
        .mejs__container {
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
            border: 2px solid #4a4a4a !important;
        }
        .mejs__button > button {
            color: #00FF41 !important;
            text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
        }
        .mejs__time {
            color: #00FF41 !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
        }
        .mejs__time-rail {
            background: #1a1a1a !important;
            border: 1px solid #4a4a4a !important;
        }
        .mejs__time-loaded {
            background: #2a2a2a !important;
        }
        .mejs__volume-button > button {
            color: #00FF41 !important;
            text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
        }
        .mejs__horizontal-volume-slider {
            background: #1a1a1a !important;
            border: 1px solid #4a4a4a !important;
        }

        /* Winamp 스타일 플레이리스트 */
        .transcript-current {
            background: linear-gradient(90deg, #1a3a5a 0%, #2a4a6a 100%) !important;
            border-left: 3px solid #00FF41 !important;
            color: #00FF41 !important;
        }
        .transcript-row:hover {
            background: linear-gradient(90deg, #2a2a2a 0%, #3a3a3a 100%) !important;
        }
        .timestamp {
            color: #00A8FF !important;
            font-family: 'Courier New', monospace !important;
        }
        .badge {
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%) !important;
            border: 1px solid #4a4a4a !important;
            color: #00FF41 !important;
            font-family: 'Courier New', monospace !important;
        }
        .badge-master {
            background: linear-gradient(180deg, #00FF41 0%, #00A8FF 100%) !important;
            color: #000000 !important;
            font-weight: bold !important;
        }
        </style>
        """
    else:
        css = """
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)


def display_transcript_list(df: pd.DataFrame):
    """Display sentences as media player transcript with timestamps."""

    st.subheader("📝 전체 문장")

    # Winamp 스타일 플레이리스트 CSS
    st.markdown("""
    <style>
    .transcript-row {
        padding: 8px 12px;
        border-bottom: 1px solid #4a4a4a;
        cursor: pointer;
        transition: all 0.2s;
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        border-left: 2px solid transparent;
    }
    .transcript-row:hover {
        background: linear-gradient(90deg, #2a2a2a 0%, #3a3a3a 100%) !important;
        border-left: 2px solid #00FF41;
    }
    .transcript-current {
        background: linear-gradient(90deg, #1a3a5a 0%, #2a4a6a 100%) !important;
        border-left: 3px solid #00FF41 !important;
        font-weight: bold !important;
        color: #00FF41 !important;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.8) !important;
    }
    .timestamp {
        font-family: 'Courier New', monospace !important;
        color: #00A8FF !important;
        font-size: 14px !important;
        text-align: right !important;
        text-shadow: 0 0 4px rgba(0, 168, 255, 0.6) !important;
    }
    .badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 2px;
        font-size: 11px;
        margin-left: 6px;
        background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
        border: 1px solid #4a4a4a;
        color: #00FF41;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 4px rgba(0, 255, 65, 0.6);
    }
    .badge-master {
        background: linear-gradient(180deg, #00FF41 0%, #00A8FF 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 1px solid #00FF41 !important;
        text-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Each sentence row
    for idx, row in df.iterrows():
        is_current = idx == st.session_state.current_index
        is_mastered = idx in st.session_state.mastered_sentences
        stats = get_sentence_stats(idx)

        # Get timestamp
        if 'Time' in df.columns:
            time_val = str(df.iloc[idx]['Time'])
            # Parse "5s", "10s" format
            if 's' in time_val.lower():
                seconds = int(time_val.lower().replace('s', ''))
                timestamp = f"{seconds // 60:02d}:{seconds % 60:02d}"
            else:
                timestamp = time_val
        else:
            # Sequential: 5 seconds per sentence
            total_sec = idx * 5
            timestamp = f"{total_sec // 60:02d}:{total_sec % 60:02d}"

        # 2-column layout: sentence + timestamp
        col1, col2 = st.columns([6, 1])

        with col1:
            # Build sentence text with badges
            sentence_text = row['English']

            # Clickable button
            if st.button(
                sentence_text,
                key=f"transcript_{idx}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.current_index = idx
                st.rerun()

            # Show badges below button
            badges_html = ""
            if is_mastered:
                badges_html += '<span class="badge badge-master">✓ 마스터</span>'
            if stats['listen_count'] > 0:
                badges_html += f'<span class="badge">🎧 {stats["listen_count"]}회</span>'

            if badges_html:
                st.markdown(badges_html, unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="timestamp">{timestamp}</div>', unsafe_allow_html=True)

        # Add divider except for last row
        if idx < len(df) - 1:
            st.markdown('<hr style="margin: 4px 0; border-color: #f0f0f0;">', unsafe_allow_html=True)


def display_practice_chart():
    """연습 통계 차트를 표시합니다."""

    stats = st.session_state.practice_stats

    if not stats:
        st.info("아직 연습 기록이 없습니다.")
        return

    # 데이터 준비
    indices = sorted(stats.keys())
    listen_counts = [stats[i]['listen_count'] for i in indices]

    # Plotly 막대 그래프
    fig = go.Figure(data=[
        go.Bar(
            name='청취 횟수',
            x=[f"문장 {i+1}" for i in indices],
            y=listen_counts,
            marker_color='lightblue'
        )
    ])

    fig.update_layout(
        title="문장별 연습 횟수",
        xaxis_title="문장",
        yaxis_title="횟수",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def display_session_stats():
    """세션 통계를 표시합니다."""

    # 세션 시간 계산
    duration = datetime.now() - st.session_state.session_start_time
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    seconds = int(duration.total_seconds() % 60)

    # 통계 표시
    col1, col2 = st.columns(2)

    with col1:
        st.metric("세션 시간", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        st.metric("총 청취 횟수", st.session_state.total_listens)

    with col2:
        practiced = len(st.session_state.practice_stats)
        st.metric("연습한 문장 수", practiced)
        st.metric("완료한 루프", st.session_state.loop_count)

    # 마스터한 문장 목록
    if st.session_state.mastered_sentences:
        st.write("**마스터한 문장:**")
        mastered_list = sorted(list(st.session_state.mastered_sentences))
        st.write(", ".join([f"문장 {i+1}" for i in mastered_list]))

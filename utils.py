"""
Utility functions for English sentence practice app
영어 문장 반복 연습 프로그램 유틸리티 함수
"""

import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
from datetime import datetime
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
        st.session_state.repeat_mode = "Individual"
    if 'playback_speed' not in st.session_state:
        st.session_state.playback_speed = 1.0

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

    # 세션 정보
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if 'total_listens' not in st.session_state:
        st.session_state.total_listens = 0

    # Audio cache
    if 'audio_cache' not in st.session_state:
        st.session_state.audio_cache = {}  # {index: audio_bytes}
    if 'audio_durations' not in st.session_state:
        st.session_state.audio_durations = {}  # {index: duration_seconds}




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


def play_audio_with_stats_v2(text: str, index: int, speed: float = 1.0, audio_placeholder=None) -> float:
    """오디오를 재생합니다.

    Returns:
        float: 오디오 재생 시간(초)
    """

    try:
        # 캐시에서 오디오를 가져오거나 생성
        if index in st.session_state.audio_cache:
            audio_bytes = st.session_state.audio_cache[index]
            base_duration = st.session_state.audio_durations[index]
            duration = base_duration / speed
        else:
            audio_bytes, duration = generate_audio(text, speed)

        # HTML5 오디오 플레이어 (자동 재생)
        import base64
        import time as time_module
        audio_base64 = base64.b64encode(audio_bytes).decode()
        unique_id = f"audio_{int(time_module.time() * 1000000)}"

        audio_html = f"""
        <audio id="{unique_id}" controls autoplay style="width: 100%; margin: 10px 0;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            (function() {{
                var audio = document.getElementById('{unique_id}');
                if (audio) {{
                    audio.playbackRate = {speed};
                    audio.volume = 0.8;

                    // 자동 재생 시도
                    var playPromise = audio.play();
                    if (playPromise !== undefined) {{
                        playPromise.catch(function(error) {{
                            console.log('Auto-play prevented:', error);
                        }});
                    }}
                }}
            }})();
        </script>
        """

        # 플레이어 렌더링
        if audio_placeholder is not None:
            audio_placeholder.empty()
            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.markdown(audio_html, unsafe_allow_html=True)

        # 통계 업데이트
        st.session_state.total_listens += 1

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
        st.error(f"❌ 오디오 재생 실패: {str(e)}")
        return 0.0



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
def generate_audio(text: str, speed: float = 1.0) -> bytes:
    """
    텍스트를 음성으로 변환합니다.

    Args:
        text: 변환할 텍스트
        speed: 재생 속도 (0.5 ~ 2.0)

    Returns:
        bytes: 오디오 데이터
    """

    # gTTS로 기본 오디오 생성
    tts = gTTS(text=text, lang='en', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    # 속도 조절이 필요한 경우
    if speed != 1.0:
        try:
            audio = AudioSegment.from_file(fp, format="mp3")

            # 속도 변경 (pitch 유지)
            # 재생 속도를 높이려면 frame_rate를 높이고, 다시 원래대로 설정
            new_sample_rate = int(audio.frame_rate * speed)
            audio_with_speed = audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": new_sample_rate}
            ).set_frame_rate(audio.frame_rate)

            output = BytesIO()
            audio_with_speed.export(output, format="mp3")
            return output.getvalue()
        except Exception as e:
            st.warning(f"속도 조절 실패, 기본 속도로 재생합니다: {str(e)}")
            fp.seek(0)
            return fp.getvalue()

    return fp.getvalue()


def play_audio_with_stats(text: str, index: int, speed: float = 1.0, autoplay: bool = True, audio_placeholder=None) -> None:
    """오디오를 재생하고 통계를 업데이트합니다."""

    try:
        audio_bytes = generate_audio(text, speed)

        if autoplay:
            # 자동 재생되는 숨겨진 오디오 플레이어
            import base64
            import time as time_module
            audio_base64 = base64.b64encode(audio_bytes).decode()

            # 고유한 ID 생성 (timestamp 사용)
            unique_id = f"audio_{int(time_module.time() * 1000)}"

            audio_html = f"""
                <audio id="{unique_id}" autoplay="true" style="display:none;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                <script>
                    // 오디오가 끝나면 요소 제거
                    document.getElementById('{unique_id}').addEventListener('ended', function() {{
                        this.remove();
                    }});
                </script>
            """

            # placeholder가 제공되면 그것을 사용, 아니면 새로 생성
            if audio_placeholder is not None:
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

    except Exception as e:
        st.error(f"오디오 생성 실패: {str(e)}")


# ============================================================
# UI 헬퍼 함수
# ============================================================

def apply_custom_css(dark_mode: bool = False):
    """커스텀 CSS를 적용합니다."""

    if dark_mode:
        css = """
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #E0E0E0;
        }
        .stMarkdown, .stText {
            color: #E0E0E0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
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


def display_sentence_list(df: pd.DataFrame):
    """전체 문장 목록을 진행 상황과 함께 표시합니다."""

    st.subheader("전체 문장 목록")

    for idx, row in df.iterrows():
        # 마스터 여부 및 현재 문장 여부 확인
        is_mastered = idx in st.session_state.mastered_sentences
        is_current = idx == st.session_state.current_index

        # 통계 가져오기
        stats = get_sentence_stats(idx)

        # 컬럼 생성
        col1, col2, col3, col4, col5 = st.columns([0.5, 5, 1, 0.8, 0.8])

        with col1:
            # 인덱스 표시
            if is_current:
                st.markdown("**➡️**")
            else:
                st.write(f"{idx + 1}")

        with col2:
            # 문장 표시 (마스터 여부에 따라 스타일 변경)
            if is_mastered:
                st.markdown(f"<p style='color: green; font-weight: bold;'>{row['English']}</p>",
                          unsafe_allow_html=True)
            elif is_current:
                st.markdown(f"<p style='color: blue; font-weight: bold;'>{row['English']}</p>",
                          unsafe_allow_html=True)
            else:
                st.write(row['English'])

        with col3:
            # 청취 횟수
            st.caption(f"🎧 {stats['listen_count']}")

        with col4:
            # 재생 버튼
            if st.button("▶️", key=f"play_{idx}"):
                # 각 재생마다 새로운 컨테이너 사용
                audio_container = st.container()
                with audio_container:
                    audio_placeholder = st.empty()
                    play_audio_with_stats(
                        row['English'],
                        idx,
                        st.session_state.playback_speed,
                        autoplay=True,
                        audio_placeholder=audio_placeholder
                    )

        with col5:
            # 이동 버튼
            if st.button("이동", key=f"goto_{idx}"):
                st.session_state.current_index = idx
                st.rerun()


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

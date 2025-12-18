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
    calculate_progress,
    generate_audio,
    play_audio_with_stats,
    save_session_to_json,
    load_session_from_json,
    apply_custom_css,
    display_sentence_list,
    display_practice_chart,
    display_session_stats
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
            help="일정 간격으로 자동으로 다음 문장을 재생합니다"
        )
        st.session_state.auto_play = auto_play

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
    st.title("🎧 영어 문장 반복 연습 프로그램")

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

    # ===== 상단: 전체 통계 =====
    if st.session_state.show_stats:
        mastered, total, progress = calculate_progress()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("전체 문장", total)

        with col2:
            st.metric("마스터한 문장", mastered)

        with col3:
            st.metric("진행률", f"{progress:.1f}%")

        with col4:
            st.metric("총 청취 횟수", st.session_state.total_listens)

        # 진행률 바
        if total > 0:
            st.progress(progress / 100)

    st.divider()

    # ===== 중앙: 현재 문장 표시 =====
    st.subheader("현재 문장")

    current_idx = st.session_state.current_index
    if current_idx >= len(df):
        current_idx = 0
        st.session_state.current_index = 0

    current_sentence = df.iloc[current_idx]

    # 현재 문장 큰 글씨로 표시
    st.markdown(f"### {current_sentence['English']}")

    if st.session_state.show_translation:
        st.markdown(f"*{current_sentence['Korean']}*")

    # 이 문장의 통계
    sentence_stats = get_sentence_stats(current_idx)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption(f"청취 횟수: {sentence_stats['listen_count']}")

    with col2:
        is_mastered = current_idx in st.session_state.mastered_sentences
        if st.checkbox("마스터 완료", value=is_mastered, key=f"master_{current_idx}"):
            st.session_state.mastered_sentences.add(current_idx)
        else:
            st.session_state.mastered_sentences.discard(current_idx)

    with col3:
        st.caption(f"문장 {current_idx + 1} / {len(df)}")

    st.divider()

    # ===== 컨트롤 버튼들 =====
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("⏮️ 처음으로", use_container_width=True):
            st.session_state.current_index = 0
            st.rerun()

    with col2:
        if st.button("◀️ 이전", use_container_width=True):
            if st.session_state.current_index > 0:
                st.session_state.current_index -= 1
            else:
                st.session_state.current_index = len(df) - 1
            st.rerun()

    with col3:
        if st.button("▶️ 재생", use_container_width=True, type="primary"):
            # 개별 반복 모드인 경우
            if st.session_state.repeat_mode == "개별 반복":
                repeat_count = st.session_state.target_repeats

                # 진행 상황을 표시할 placeholder 생성
                progress_placeholder = st.empty()
                # 오디오 재생을 위한 컨테이너
                audio_container = st.container()

                for i in range(repeat_count):
                    # 같은 위치에 진행 상황 업데이트
                    progress_placeholder.info(f"🔊 **{i+1}/{repeat_count}회 재생 중...**")

                    # 각 반복마다 새로운 placeholder 사용
                    with audio_container:
                        audio_placeholder = st.empty()
                        play_audio_with_stats(
                            current_sentence['English'],
                            current_idx,
                            st.session_state.playback_speed,
                            autoplay=True,
                            audio_placeholder=audio_placeholder
                        )

                    # 오디오가 재생될 시간 대기
                    wait_time = max(1.5, len(current_sentence['English'].split()) * 0.5 / st.session_state.playback_speed)
                    time.sleep(wait_time)

                    # 마지막 반복이 아니면 짧은 간격 추가
                    if i < repeat_count - 1:
                        time.sleep(0.5)

                # 완료 메시지로 업데이트
                progress_placeholder.success(f"✓ {repeat_count}번 반복 완료!")

            # 쉐도잉 모드인 경우
            elif st.session_state.repeat_mode == "쉐도잉":
                progress_placeholder = st.empty()
                audio_container = st.container()

                progress_placeholder.info("🔊 **재생 중...**")
                with audio_container:
                    audio_placeholder = st.empty()
                    play_audio_with_stats(
                        current_sentence['English'],
                        current_idx,
                        st.session_state.playback_speed,
                        autoplay=True,
                        audio_placeholder=audio_placeholder
                    )

                # 오디오가 재생될 시간 대기
                wait_time = max(1.5, len(current_sentence['English'].split()) * 0.5 / st.session_state.playback_speed)
                time.sleep(wait_time)

                progress_placeholder.info(f"🎤 **따라 말하세요... ({st.session_state.shadowing_delay}초)**")
                time.sleep(st.session_state.shadowing_delay)

                progress_placeholder.success("✓ 다음 문장으로 이동할 수 있습니다!")

            # 전체 루프 모드인 경우 (1번만 재생)
            else:
                progress_placeholder = st.empty()
                audio_container = st.container()

                progress_placeholder.info("🔊 **재생 중...**")
                with audio_container:
                    audio_placeholder = st.empty()
                    play_audio_with_stats(
                        current_sentence['English'],
                        current_idx,
                        st.session_state.playback_speed,
                        autoplay=True,
                        audio_placeholder=audio_placeholder
                    )

                # 오디오가 재생될 시간 대기
                wait_time = max(1.5, len(current_sentence['English'].split()) * 0.5 / st.session_state.playback_speed)
                time.sleep(wait_time)

                progress_placeholder.success("✓ 재생 완료!")

    with col4:
        if st.button("다음 ▶️", use_container_width=True):
            # 다음 문장으로 이동
            st.session_state.current_index = (st.session_state.current_index + 1) % len(df)

            # 전체 루프 모드인 경우, 처음으로 돌아왔을 때 루프 카운트 증가
            if st.session_state.repeat_mode == "전체 루프" and st.session_state.current_index == 0:
                st.session_state.loop_count += 1
                if st.session_state.loop_count >= st.session_state.loop_target:
                    st.balloons()
                    st.success(f"🎉 목표 달성! {st.session_state.loop_target}회 루프 완료!")

            st.rerun()

    with col5:
        if st.button("전체 재생 ⏯️", use_container_width=True):
            # 진행 상황 표시용 placeholder
            play_progress = st.empty()
            audio_container = st.container()

            for idx, row in df.iterrows():
                # 같은 위치에 현재 재생 중인 문장 표시
                play_progress.info(f"🔊 **{idx + 1}/{len(df)}. {row['English']}**")

                # 각 문장마다 새로운 placeholder 사용
                with audio_container:
                    audio_placeholder = st.empty()
                    play_audio_with_stats(
                        row['English'],
                        idx,
                        st.session_state.playback_speed,
                        autoplay=True,
                        audio_placeholder=audio_placeholder
                    )

                # 오디오 재생 시간 대기 (대략적인 시간: 문장 길이 기반)
                wait_time = max(2, len(row['English'].split()) * 0.5 / st.session_state.playback_speed)
                time.sleep(wait_time)

            # 완료 메시지
            play_progress.success("✓ 전체 재생이 완료되었습니다!")

    st.divider()

    # ===== 하단: 전체 문장 리스트 =====
    display_sentence_list(df)

    # ===== 통계 탭 =====
    if st.session_state.show_stats:
        st.divider()

        tab1, tab2, tab3 = st.tabs(["📊 연습 통계", "📝 세션 기록", "📈 차트"])

        with tab1:
            st.subheader("연습 통계")

            if st.session_state.practice_stats:
                # 통계 데이터프레임 생성
                stats_data = []
                for idx, stats in sorted(st.session_state.practice_stats.items()):
                    if idx < len(df):
                        stats_data.append({
                            "문장 번호": idx + 1,
                            "영어": df.iloc[idx]['English'],
                            "청취 횟수": stats['listen_count'],
                            "마스터": "✓" if idx in st.session_state.mastered_sentences else ""
                        })

                import pandas as pd
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True, height=400)
            else:
                st.info("아직 연습 기록이 없습니다.")

        with tab2:
            st.subheader("세션 기록")
            display_session_stats()

        with tab3:
            st.subheader("연습 차트")
            display_practice_chart()


if __name__ == "__main__":
    main()

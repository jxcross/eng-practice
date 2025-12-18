import streamlit as st
import pandas as pd
from gtts import gTTS
import os
import time
from io import BytesIO

st.set_page_config(page_title="영어 듣기 연습", layout="wide")

def text_to_speech(text, lang='en'):
    """텍스트를 음성으로 변환하는 함수"""
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def main():
    st.title("🎧 영어 듣기 연습 프로그램")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("영어-한국어 CSV 파일을 업로드하세요", type=['csv'])
    
    if uploaded_file is not None:
        # CSV 파일 읽기
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            if 'English' not in df.columns or 'Korean' not in df.columns:
                st.error("CSV 파일은 'English'와 'Korean' 열이 있어야 합니다.")
                return
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")
            return

        # 세션 상태 초기화
        if 'current_sentence_index' not in st.session_state:
            st.session_state.current_sentence_index = 0

        # 컨트롤 버튼들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("전체 문장 듣기"):
                full_text = " ".join(df['English'].tolist())
                audio_bytes = text_to_speech(full_text)
                st.audio(audio_bytes, format='audio/mp3')

        with col2:
            if st.button("다음 문장 듣기"):
                current_text = df['English'].iloc[st.session_state.current_sentence_index]
                audio_bytes = text_to_speech(current_text)
                st.audio(audio_bytes, format='audio/mp3')
                
                # 다음 문장으로 이동
                st.session_state.current_sentence_index = (st.session_state.current_sentence_index + 1) % len(df)

        with col3:
            if st.button("이전 문장으로"):
                st.session_state.current_sentence_index = (st.session_state.current_sentence_index - 1) % len(df)

        # 현재 문장 표시
        st.markdown("### 현재 문장")
        current_eng = df['English'].iloc[st.session_state.current_sentence_index]
        current_kor = df['Korean'].iloc[st.session_state.current_sentence_index]
        
        st.markdown(f"**English**: {current_eng}")
        st.markdown(f"**한국어**: {current_kor}")
        
        # 전체 스크립트 표시
        st.markdown("### 전체 스크립트")
        script_df = df[['English', 'Korean']].copy()
        script_df.index = script_df.index + 1  # 1부터 시작하는 인덱스
        st.dataframe(script_df, height=400)

if __name__ == "__main__":
    main()
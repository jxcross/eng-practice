import streamlit as st
import pandas as pd
from gtts import gTTS
import os
import tempfile
from streamlit.runtime.scriptrunner import RerunException

# Initialize session state
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "df" not in st.session_state:
    st.session_state.df = None

def play_audio(text):
    """Generate and play audio from text."""
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")
        os.unlink(fp.name)

st.title("영어 듣고 따라하기 프로그램")

# Upload CSV file
uploaded_file = st.file_uploader("(영어,한국어)로 구성된 CSV 파일을 업로드하세요.", type="csv")
if uploaded_file:
    st.session_state.df = pd.read_csv(uploaded_file)

if st.session_state.df is not None:
    df = st.session_state.df

    # Display the uploaded file's content
    st.write("업로드된 스크립트:")
    st.dataframe(df)

    if "English" not in df.columns or "Korean" not in df.columns:
        st.error("CSV 파일은 'English'와 'Korean' 열이 필요합니다.")
    else:
        # Buttons for listening
        if st.button("전체 문장 듣기"):
            for index, row in df.iterrows():
                play_audio(row["English"])

        if st.button("한 문장 듣기"):
            if st.session_state.current_index < len(df):
                row = df.iloc[st.session_state.current_index]
                play_audio(row["English"])
                st.session_state.current_index += 1
            else:
                st.warning("모든 문장을 들었습니다. 처음으로 돌아갑니다.")
                st.session_state.current_index = 0
                raise RerunException()

        # Show the current script
        if st.session_state.current_index < len(df):
            current_row = df.iloc[st.session_state.current_index]
            st.subheader("현재 문장")
            st.write(f"**English:** {current_row['English']}")
            st.write(f"**Korean:** {current_row['Korean']}")
        else:
            st.warning("모든 문장을 들었습니다.")

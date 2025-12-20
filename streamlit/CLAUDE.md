# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

English Sentence Practice App (영어 문장 반복 연습 프로그램) - A Streamlit-based web application for practicing English sentences through audio playback with multiple learning modes.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Architecture

### Core Components

- **app.py** - Main Streamlit application entry point and UI orchestration
  - Handles all UI rendering and user interactions
  - Manages three learning modes: Individual Repeat (개별 반복), Full Loop (전체 루프), and Shadowing (쉐도잉)
  - Controls playback flow including auto-play and manual play modes

- **utils.py** - Utility functions and business logic
  - Session state management
  - Audio generation using gTTS (Google Text-to-Speech)
  - Audio speed adjustment using pyrubberband (maintains pitch)
  - Statistics tracking and progress calculation
  - Data parsing (CSV and text input)
  - Chart generation with Plotly

### Session State Architecture

The app heavily relies on Streamlit's `st.session_state` to maintain user progress and settings:

- **Data**: `df` (sentence DataFrame), `current_index`
- **Playback modes**: `repeat_mode`, `playback_speed`, `auto_play`, `auto_play_interval`
- **Progress tracking**: `practice_stats`, `mastered_sentences`, `total_listens`
- **Loop tracking**: `loop_count`, `loop_target`, `target_repeats`, `shadowing_delay`
- **UI settings**: `dark_mode`, `show_translation`, `show_stats`

Session state can be saved to/loaded from JSON files for persistence.

### Audio System

Audio generation is a two-stage process:

1. **Base audio generation** (`_generate_base_audio`) - Cached using `@st.cache_data` to avoid regenerating the same text
2. **Speed adjustment** (`generate_audio`) - Uses pyrubberband to time-stretch audio while preserving pitch

Key implementation detail: Each audio playback uses a unique HTML audio element with a timestamp-based ID to prevent caching issues during auto-play sequences.

### Learning Modes

1. **Individual Repeat (개별 반복)**: Repeats each sentence N times before moving to the next
2. **Full Loop (전체 루프)**: Plays all sentences from start to finish, then repeats the entire set
3. **Shadowing (쉐도잉)**: Plays each sentence with a pause afterward for user repetition

Auto-play mode can chain sentences together across all three learning modes.

## Data Input

The app supports two input methods:

1. **CSV Upload**: Requires `English` and `Korean` columns
2. **Text Paste**: Plain text with optional Korean translations

Sample CSV files are in the `samples/` directory.

## Key Technical Patterns

- **Audio placeholder management**: Uses `st.empty()` placeholders to update audio elements without recreating UI components during auto-play
- **Rerun triggers**: `st.rerun()` is called after navigation actions to update the UI with new sentence context
- **Caching strategy**: Base audio (without speed adjustment) is cached to improve performance; speed-adjusted audio is generated on-demand
- **Statistics persistence**: All practice statistics use integer-indexed dictionaries that map to DataFrame row indices

## Dependencies

- streamlit - Web app framework
- pandas - Data handling
- gtts - Text-to-speech
- pydub - Audio manipulation
- pyrubberband - Pitch-preserving time stretching
- plotly - Interactive charts

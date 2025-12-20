import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="English Practice Player",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Remove gap between elements */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
    }
    
    /* Reduce column gaps */
    div[data-testid="column"] {
        padding: 0 !important;
    }
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1342 100%);
        font-family: 'Outfit', sans-serif;
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
    
    /* Player card */
    .player-card {
        background: #1a1f3a;
        border-radius: 24px;
        padding: 32px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.6),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        position: relative;
        margin: 20px auto;
        max-width: 600px;
    }
    
    .player-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff4081, #00bcd4, #ffd740);
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Header */
    .player-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    
    .player-title {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #64ffda;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .track-info {
        font-size: 13px;
        font-weight: 600;
        color: #a0aec0;
        font-family: 'JetBrains Mono', monospace;
        background: #0d1128;
        padding: 6px 12px;
        border-radius: 8px;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Display area */
    .display-area {
        background: #0d1128;
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
    }
    
    .time-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        color: #ff4081;
        text-align: right;
        margin-bottom: 16px;
        text-shadow: 0 0 10px rgba(255, 64, 129, 0.4);
        letter-spacing: 2px;
        opacity: 0.8;
    }
    
    .text-english {
        font-size: 28px;
        line-height: 1.5;
        color: #ffffff;
        text-align: center;
        margin-bottom: 16px;
        font-weight: 600;
    }
    
    .text-korean {
        font-size: 16px;
        line-height: 1.6;
        color: #a0aec0;
        text-align: center;
        font-weight: 300;
    }
    
    /* Progress bar */
    .progress-container {
        margin-bottom: 32px;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background: #0d1128;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff4081, #ff79b0);
        border-radius: 10px;
        transition: width 0.3s ease;
        box-shadow: 0 0 10px rgba(255, 64, 129, 0.4);
    }
    
    /* Streamlit button overrides */
    .stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stButton > button {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: none;
        background: #0d1128;
        color: #ffffff;
        font-size: 20px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.5),
            0 0 0 2px #ff4081,
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    /* Primary button (play) - target by key */
    button[kind="primary"] {
        width: 72px !important;
        height: 72px !important;
        background: linear-gradient(135deg, #ff4081, #c60055) !important;
        font-size: 24px !important;
        box-shadow: 
            0 8px 24px rgba(255, 64, 129, 0.4),
            0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.08) !important;
        box-shadow: 
            0 12px 32px rgba(255, 64, 129, 0.4),
            0 0 0 3px rgba(255, 64, 129, 0.3) !important;
    }
    
    /* Controls container */
    .controls-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    /* Speed and repeat buttons */
    .speed-btn button, .repeat-btn button {
        min-height: 40px !important;
        height: 40px !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        width: 100% !important;
    }
    
    /* Secondary control section */
    .secondary-controls {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    .control-label {
        font-size: 12px;
        font-weight: 600;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Playlist */
    .playlist-section {
        margin-top: 32px;
        padding-top: 32px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .playlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .playlist-title {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #64ffda;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .playlist-count {
        font-size: 12px;
        color: #a0aec0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Playlist item buttons */
    .playlist-item button {
        width: 100% !important;
        text-align: left !important;
        background: #0d1128 !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        color: #ffffff !important;
        font-size: 14px !important;
        height: auto !important;
        min-height: auto !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    .playlist-item button:hover {
        background: rgba(255, 64, 129, 0.1) !important;
        border-color: #ff4081 !important;
        transform: translateX(4px) !important;
    }
    
    .playlist-item button[kind="primary"] {
        background: linear-gradient(90deg, rgba(255, 64, 129, 0.2), transparent) !important;
        border-color: #ff4081 !important;
        position: relative;
    }
    
    .playlist-item button[kind="primary"]::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: #ff4081;
    }
    
    /* Visualizer */
    .visualizer {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 3px;
        height: 60px;
        margin-top: 20px;
        opacity: 0.3;
    }
    
    .bar {
        width: 4px;
        background: linear-gradient(to top, #ff4081, #00bcd4);
        border-radius: 2px 2px 0 0;
        animation: wave 1.5s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { height: 20%; }
        50% { height: 80%; }
    }
    
    .bar:nth-child(1) { animation-delay: 0s; }
    .bar:nth-child(2) { animation-delay: 0.1s; }
    .bar:nth-child(3) { animation-delay: 0.2s; }
    .bar:nth-child(4) { animation-delay: 0.3s; }
    .bar:nth-child(5) { animation-delay: 0.4s; }
    .bar:nth-child(6) { animation-delay: 0.5s; }
    .bar:nth-child(7) { animation-delay: 0.6s; }
    .bar:nth-child(8) { animation-delay: 0.7s; }
    .bar:nth-child(9) { animation-delay: 0.8s; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_track' not in st.session_state:
    st.session_state.current_track = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'repeat_mode' not in st.session_state:
    st.session_state.repeat_mode = 'none'  # 'none', 'one', 'all'
if 'progress' not in st.session_state:
    st.session_state.progress = 0

# Track data
tracks = [
    {
        "english": "So, today was our VSMR quarterly wrap-up meeting.",
        "korean": "오늘은 VSMR 분기 총괄회의가 있었어요.",
        "duration": "00:04"
    },
    {
        "english": "We reviewed all the major projects from Q4.",
        "korean": "우리는 4분기의 모든 주요 프로젝트를 검토했습니다.",
        "duration": "00:05"
    },
    {
        "english": "The presentation was really well organized.",
        "korean": "발표는 정말 잘 구성되어 있었어요.",
        "duration": "00:04"
    },
    {
        "english": "I think we exceeded our targets this quarter.",
        "korean": "이번 분기에 목표를 초과 달성한 것 같아요.",
        "duration": "00:05"
    },
    {
        "english": "The team collaboration has been outstanding.",
        "korean": "팀 협업이 정말 훌륭했습니다.",
        "duration": "00:04"
    },
    {
        "english": "We need to improve our communication channels.",
        "korean": "우리는 커뮤니케이션 채널을 개선해야 합니다.",
        "duration": "00:05"
    },
    {
        "english": "The client feedback was overwhelmingly positive.",
        "korean": "고객 피드백은 압도적으로 긍정적이었습니다.",
        "duration": "00:05"
    },
    {
        "english": "Let's celebrate our achievements together.",
        "korean": "함께 우리의 성과를 축하합시다.",
        "duration": "00:04"
    },
    {
        "english": "Next quarter looks very promising.",
        "korean": "다음 분기는 매우 유망해 보입니다.",
        "duration": "00:04"
    },
    {
        "english": "I'm excited about the new initiatives.",
        "korean": "새로운 계획들이 기대됩니다.",
        "duration": "00:04"
    },
    {
        "english": "We should schedule a follow-up meeting soon.",
        "korean": "곧 후속 회의를 예약해야 합니다.",
        "duration": "00:05"
    },
    {
        "english": "The data analysis revealed interesting insights.",
        "korean": "데이터 분석에서 흥미로운 통찰이 드러났습니다.",
        "duration": "00:05"
    },
    {
        "english": "Everyone contributed their best work.",
        "korean": "모두가 최선을 다해 기여했습니다.",
        "duration": "00:04"
    },
    {
        "english": "The budget allocation seems reasonable.",
        "korean": "예산 배분이 합리적으로 보입니다.",
        "duration": "00:04"
    },
    {
        "english": "We're building momentum for next year.",
        "korean": "내년을 위한 탄력을 만들고 있습니다.",
        "duration": "00:04"
    },
    {
        "english": "Thank you all for your hard work.",
        "korean": "모두 수고하셨습니다.",
        "duration": "00:04"
    }
]

# Main player card
st.markdown('<div class="player-card">', unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="player-header">
    <div class="player-title">ENGLISH PRACTICE</div>
    <div class="track-info">{st.session_state.current_track + 1} of {len(tracks)}</div>
</div>
""", unsafe_allow_html=True)

# Display area
current_track = tracks[st.session_state.current_track]
st.markdown(f"""
<div class="display-area">
    <div class="time-display">{current_track['duration']}</div>
    <div class="text-english">{current_track['english']}</div>
    <div class="text-korean">{current_track['korean']}</div>
</div>
""", unsafe_allow_html=True)

# Progress bar
progress_percent = st.session_state.progress
st.markdown(f"""
<div class="progress-container">
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percent}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main controls
st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1.2, 1], gap="small")

with col1:
    if st.button("⏮", key="prev", use_container_width=False):
        if st.session_state.current_track > 0:
            st.session_state.current_track -= 1
            st.session_state.progress = 0
        elif st.session_state.repeat_mode == 'all':
            st.session_state.current_track = len(tracks) - 1
            st.session_state.progress = 0
        st.rerun()

with col2:
    play_label = "⏸" if st.session_state.is_playing else "▶️"
    if st.button(play_label, key="play", type="primary", use_container_width=False):
        st.session_state.is_playing = not st.session_state.is_playing
        st.rerun()

with col3:
    if st.button("⏭", key="next", use_container_width=False):
        if st.session_state.current_track < len(tracks) - 1:
            st.session_state.current_track += 1
            st.session_state.progress = 0
        elif st.session_state.repeat_mode == 'all':
            st.session_state.current_track = 0
            st.session_state.progress = 0
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Speed control
st.markdown('<div class="secondary-controls">', unsafe_allow_html=True)
st.markdown('<div class="control-label">⚡ SPEED</div>', unsafe_allow_html=True)
speed_cols = st.columns(5, gap="small")
speeds = [0.5, 0.75, 1.0, 1.25, 1.5]
for idx, col in enumerate(speed_cols):
    with col:
        speed = speeds[idx]
        btn_type = "primary" if st.session_state.playback_speed == speed else "secondary"
        if st.button(f"{speed}x", key=f"speed_{speed}", type=btn_type, use_container_width=True):
            st.session_state.playback_speed = speed
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Repeat control
st.markdown('<div class="secondary-controls">', unsafe_allow_html=True)
st.markdown('<div class="control-label">🔁 REPEAT</div>', unsafe_allow_html=True)
repeat_col1, repeat_col2, repeat_col3 = st.columns([1, 1, 2], gap="small")
with repeat_col1:
    btn_type = "primary" if st.session_state.repeat_mode == 'one' else "secondary"
    if st.button("🔂 One", key="repeat_one", type=btn_type, use_container_width=True):
        st.session_state.repeat_mode = 'one' if st.session_state.repeat_mode != 'one' else 'none'
        st.rerun()

with repeat_col2:
    btn_type = "primary" if st.session_state.repeat_mode == 'all' else "secondary"
    if st.button("🔁 All", key="repeat_all", type=btn_type, use_container_width=True):
        st.session_state.repeat_mode = 'all' if st.session_state.repeat_mode != 'all' else 'none'
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Visualizer
st.markdown("""
<div class="visualizer">
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
    <div class="bar"></div>
</div>
""", unsafe_allow_html=True)

# Playlist section
st.markdown("""
<div class="playlist-section">
    <div class="playlist-header">
        <div class="playlist-title">PLAYLIST</div>
        <div class="playlist-count">16 tracks</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Playlist items
for idx, track in enumerate(tracks):
    col1, col2 = st.columns([5, 1], gap="small")
    
    with col1:
        is_current = idx == st.session_state.current_track
        btn_type = "primary" if is_current else "secondary"
        
        # Create custom styling class for playlist items
        st.markdown('<div class="playlist-item">', unsafe_allow_html=True)
        
        if st.button(
            f"{idx + 1:02d} • {track['english']}",
            key=f"track_{idx}",
            type=btn_type,
            use_container_width=True
        ):
            st.session_state.current_track = idx
            st.session_state.progress = 0
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(
            f"<div style='text-align: right; color: #a0aec0; font-family: JetBrains Mono, monospace; "
            f"font-size: 12px; padding-top: 8px; line-height: 40px;'>{track['duration']}</div>",
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# Auto-play logic (simulated)
if st.session_state.is_playing:
    if st.session_state.progress < 100:
        st.session_state.progress += 2 * st.session_state.playback_speed
        time.sleep(0.1)
        st.rerun()
    else:
        # Track finished
        st.session_state.progress = 0
        
        if st.session_state.repeat_mode == 'one':
            # Repeat current track
            st.rerun()
        elif st.session_state.repeat_mode == 'all':
            # Move to next track or loop
            if st.session_state.current_track < len(tracks) - 1:
                st.session_state.current_track += 1
            else:
                st.session_state.current_track = 0
            st.rerun()
        else:
            # Normal mode: move to next or stop
            if st.session_state.current_track < len(tracks) - 1:
                st.session_state.current_track += 1
                st.rerun()
            else:
                st.session_state.is_playing = False
                st.rerun()
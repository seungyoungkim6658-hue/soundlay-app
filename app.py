import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Neural & Nature Master")
st.markdown("김작가님의 콘텐츠 제작을 위한 전용 사운드 엔진입니다.")

# --- 사이드바: 컨트롤 패널 ---
st.sidebar.header("1. 🧠 바이노럴 비트 설정")
base_hz = st.sidebar.slider("기준 주파수 (Carrier)", 100, 250, 140, help="100~250Hz 사이의 안정적인 저음")
offset_hz = st.sidebar.slider("유도 뇌파 (Offset)", 0.1, 40.0, 7.83, help="차이값이 곧 뇌파 동조 주파수가 됩니다.")

st.sidebar.header("2. 🍃 자연 배경음 선택")
noise_choice = st.sidebar.selectbox("사운드 소스", 
    ["빗소리 (Pink Rain)", "파도소리 (Brown Ocean)", "바람소리 (Deep Wind)", "모닥불소리 (Fire Crackle)", "시냇물소리 (Stream)"])
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 1.0, 0.4)

st.sidebar.header("3. 🫁 호흡 주기 (Hz)")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05, step=0.01)

# --- 사운드 생성 엔진 ---
def generate_soundlay_session(duration_min=3):
    fs = 44100
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # Binaural Beats 생성
    l_ch = np.sin(2 * np.pi * base_hz * t)
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t)
    
    # Noise Generation (알고리즘 기반 자연음)
    white = np.random.normal(0, 1, len(t))
    if "빗소리" in noise_choice:
        noise = np.cumsum(white)
    elif "파도소리" in noise_choice:
        noise = np.cumsum(np.cumsum(white))
    elif "바람소리" in noise_choice:
        noise = np.convolve(white, np.ones(200)/200, mode='same')
    elif "모닥불소리" in noise_choice:
        noise = white * np.where(np.random.rand(len(t)) > 0.999, 2.0, 0.05)
    else: # 시냇물
        noise = np.sin(2 * np.pi * 0.2 * t) * white
    
    # 노이즈 정규화 및 볼륨 조절
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    
    # Volume Envelope (호흡 주기 변조)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    
    # 최종 믹싱 및 정규화
    final = (np.vstack((l_ch, r_ch)) * 0.5 + noise) * envelope
    final_clipped = np.clip(final, -1.0, 1.0).T.astype(np.float32)
    return fs, final_clipped

# --- 메인 화면 실행 ---

st.info("💡 밸런스 확인을 위해 3분 미리듣기를 먼저 해보세요.")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ 3분 미리듣기 생성"):
        with st.spinner("3분 분량의 사운드를 정밀하게 조율 중입니다..."):
            fs, audio_data = generate_soundlay_session(3) # 3분
            buf = io.BytesIO()
            wavfile.write(buf, fs, audio_data)
            st.audio(buf.getvalue(), format="audio/wav")
            st.success("3분 미리듣기 준비 완료! 위 플레이어를 재생하세요.")

with col2:
    if st.button("🔴 5분 본 세션 녹음"):
        with st.spinner("고음질 5분 세션 렌더링 중..."):
            fs, audio_data = generate_soundlay_session(5) # 5분
            buf = io.BytesIO()
            wavfile.write(buf, fs, audio_data)
            st.audio(buf.getvalue(), format="audio/wav")
            st.download_button(
                label="💾 고음질 WAV 다운로드",
                data=buf.getvalue(),
                file_name=f"SoundLay_{noise_choice}.wav",
                mime="audio/wav"
            )
            st.success("본 세션 생성이 완료되었습니다!")

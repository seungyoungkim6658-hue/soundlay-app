import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Neural & Nature Master")
st.markdown("김작가님의 콘텐츠 제작을 위한 전용 사운드 엔진입니다.")

# --- 사이드바 설정 ---
st.sidebar.header("1. 🧠 바이노럴 비트 설정")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음 선택")
noise_choice = st.sidebar.selectbox("사운드 소스", 
    ["빗소리", "파도소리", "바람소리", "모닥불소리", "시냇물소리"])
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 1.0, 0.4)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 ---
def generate_soundlay_session(duration_min=3):
    fs = 44100
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # Binaural Beats
    l_ch = np.sin(2 * np.pi * base_hz * t)
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t)
    
    # Noise Generation
    white = np.random.normal(0, 1, len(t))
    if "빗" in noise_choice:
        noise = np.cumsum(white)
    elif "파도" in noise_choice:
        noise = np.cumsum(np.cumsum(white))
    else:
        noise = np.convolve(white, np.ones(200)/200, mode='same')
    
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    
    # 최종 믹싱 및 int16 변환 (브라우저 호환성 최적화)
    final = (np.vstack((l_ch, r_ch)) * 0.5 + noise) * envelope
    final = np.clip(final, -1.0, 1.0)
    # float -> int16 변환 (용량 최적화 핵심)
    audio_int16 = (final.T * 32767).astype(np.int16)
    return fs, audio_int16

# --- 실행부 ---
if st.button("▶️ 3분 미리듣기 생성"):
    with st.spinner("사운드를 생성 중입니다..."):
        fs, audio_data = generate_soundlay_session(3)
        buf = io.BytesIO()
        wavfile.write(buf, fs, audio_data)
        
        # 오디오 출력 (형식을 명확히 지정)
        st.audio(buf, format="audio/wav")
        st.success("이제 위 플레이어에서 시간이 표시되면 재생 버튼을 누르세요!")

if st.button("🔴 5분 본 세션 다운로드"):
    with st.spinner("5분 고음질 파일을 준비 중입니다..."):
        fs, audio_data = generate_soundlay_session(5)
        buf = io.BytesIO()
        wavfile.write(buf, fs, audio_data)
        st.download_button(
            label="💾 고음질 WAV 다운로드",
            data=buf.getvalue(),
            file_name="SoundLay_Final.wav",
            mime="audio/wav"
        )

import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Advanced Sound Engine")
st.markdown("바이노럴 비트는 유지되고, 자연 배경음만 호흡 주기에 맞춰 변주됩니다.")

# --- 사이드바 설정 ---
st.sidebar.header("1. 🧠 바이노럴 비트 (지속음)")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음 (호흡 주기 적용)")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 1.0, 0.4)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 ---
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 1. Binaural Beats (호흡 주기 적용 안 함 - 지속적으로 유지)
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.5
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.5
    
    # 2. Noise Generation (자연음)
    white = np.random.normal(0, 1, len(t))
    if noise_choice == "빗소리":
        noise = np.cumsum(white)
        noise = noise - np.convolve(noise, np.ones(50)/50, mode='same')
    elif noise_choice == "파도소리":
        noise = np.cumsum(np.cumsum(white))
    elif noise_choice == "바람소리":
        noise = np.convolve(white, np.ones(500)/500, mode='same')
    elif noise_choice == "모닥불소리":
        crackle = np.where(np.random.rand(len(t)) > 0.9995, 2.0, 0.0)
        noise = white * 0.1 + crackle
    else: # 시냇물소리
        water_mod = np.sin(2 * np.pi * 0.5 * t) * 0.5 + 0.5
        noise = white * water_mod
    
    # 노이즈 정규화
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    
    # 3. 호흡 주기 엔벨로프 (배경음에만 곱해줌)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    breathing_noise = noise * envelope
    
    # 4. 최종 믹싱 (바이노럴 비트 + 호흡하는 자연음)
    final_l = l_ch + breathing_noise
    final_r = r_ch + breathing_noise
    
    final = np.vstack((final_l, final_r))
    return fs, (np.clip(final, -1.0, 1.0).T * 32767).astype(np.int16)

# --- 실행부 ---
with st.status("🔄 사운드 조율 중...", expanded=False) as status:
    fs, audio_data = generate_audio(3)
    buf = io.BytesIO()
    wavfile.write(buf, fs, audio_data)
    audio_bytes = buf.getvalue()
    status.update(label="✅ 조율 완료!", state="complete")

st.subheader(f"🎵 모니터링 중: {noise_choice}")
st.audio(audio_bytes, format="audio/wav")

if st.button("🔴 최종 5분 고음질 파일 추출"):
    with st.spinner("고음질 세션을 생성 중입니다..."):
        fs_high, audio_high = generate_audio(5, 44100)
        buf_h = io.BytesIO()
        wavfile.write(buf_h, fs_high, audio_high)
        st.download_button(
            label="💾 WAV 다운로드",
            data=buf_h.getvalue(),
            file_name=f"SoundLay_{noise_choice}_{offset_hz}Hz.wav",
            mime="audio/wav"
        )

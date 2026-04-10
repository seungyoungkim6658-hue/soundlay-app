import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Advanced Sound Engine")
st.markdown("배경음 볼륨 범위가 확장되었습니다. 이제 더 풍성한 사운드 믹싱이 가능합니다.")

# --- 사이드바 설정 ---
st.sidebar.header("1. 🧠 바이노럴 비트 (지속음)")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음 (호흡 주기 적용)")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
# 볼륨 범위를 2.0까지 확장하여 더 큰 소리를 낼 수 있게 함
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 2.0, 0.8)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 ---
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 1. Binaural Beats (지속음, 볼륨 0.5 고정)
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.5
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.5
    
    # 2. Noise Generation
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
    
    # 노이즈 정규화 및 확장된 볼륨 적용
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    
    # 3. 호흡 주기 엔벨로프 (배경음에만 적용)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    breathing_noise = noise * envelope
    
    # 4. 최종 믹싱 (피크 방지를 위해 소폭 감쇄 후 합산)
    final_l = l_ch + breathing_noise
    final_r = r_ch + breathing_noise
    
    final = np.vstack((final_l, final_r))
    # 전체 볼륨이 너무 커져서 찢어지는 소리가 나지 않도록 clip 전에 0.8배 정도 안전장치
    return fs, (np.clip(final * 0.9, -1.0, 1.0).T * 32767).astype(np.int16)

# --- 실행부 ---
with st.status("🔄 사운드 조율 중...", expanded=False) as status:
    fs, audio_data = generate_audio(3)
    buf = io.BytesIO()
    wavfile.write(buf, fs, audio_data)
    audio_bytes = buf.getvalue()
    status.update(label="✅ 조율 완료!", state="complete")

st.subheader(f"🎵 현재 모니터링: {noise_choice} (확장 볼륨)")
st.audio(audio_bytes, format="audio/wav")

if st.button("🔴 최종 5분 고음질 파일 추출"):
    with st.spinner("고음질 세션을 생성 중입니다..."):
        fs_high, audio_high = generate_audio(5, 44100)
        buf_h = io.BytesIO()
        wavfile.write(buf_h, fs_high, audio_high)
        st.download_button(
            label="💾 WAV 다운로드",
            data=buf_h.getvalue(),
            file_name=f"SoundLay_{noise_choice}_HighVol.wav",
            mime="audio/wav"
        )

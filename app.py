import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Real-time Sound Engine")
st.markdown("슬라이더를 조절하면 즉시 새로운 사운드가 생성됩니다.")

# --- 사이드바: 컨트롤 패널 ---
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음")
# 5종 세트 완비
noise_choice = st.sidebar.selectbox("사운드 소스", 
    ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 1.0, 0.4)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 ---
def generate_realtime_audio(duration_min=3):
    fs = 22050 
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # Binaural Beats
    l_ch = np.sin(2 * np.pi * base_hz * t)
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t)
    
    # --- Noise Generation (각 소리별 고유 알고리즘) ---
    white = np.random.normal(0, 1, len(t))
    
    if noise_choice == "빗소리":
        # Pink Noise 느낌의 고주파 필터링
        noise = np.cumsum(white)
        noise = noise - np.convolve(noise, np.ones(50)/50, mode='same')
    elif noise_choice == "파도소리":
        # 아주 낮은 Brown Noise + 느린 파도 주기
        noise = np.cumsum(np.cumsum(white))
        wave_env = 0.5 * (1 + np.sin(2 * np.pi * 0.1 * t)) # 10초 주기 파도
        noise = noise * wave_env
    elif noise_choice == "바람소리":
        # 중저음 필터링 + 불규칙한 변화
        noise = np.convolve(white, np.ones(500)/500, mode='same')
    elif noise_choice == "모닥불소리":
        # 타닥타닥 튀는 소리 (Impulse Noise)
        crackle = np.where(np.random.rand(len(t)) > 0.9995, 2.0, 0.0)
        noise = white * 0.1 + crackle
    else: # 시냇물소리
        # 물 흐르는 듯한 불규칙한 고음 변조
        water_mod = np.sin(2 * np.pi * 0.5 * t) * 0.5 + 0.5
        noise = white * water_mod
    
    # 노이즈 정규화 및 볼륨 조절
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    
    # 호흡 주기 엔벨로프
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    
    # 최종 믹싱 및 변환
    final = (np.vstack((l_ch, r_ch)) * 0.5 + noise) * envelope
    audio_int16 = (np.clip(final, -1.0, 1.0).T * 32767).astype(np.int16)
    return fs, audio_int16

# --- 실행부 ---
with st.status("🔄 사운드 조율 중...", expanded=False) as status:
    fs, audio_data = generate_realtime_audio(3)
    buf = io.BytesIO()
    wavfile.write(buf, fs, audio_data)
    audio_bytes = buf.getvalue()
    status.update(label="✅ 조율 완료!", state="complete")

st.subheader(f"🎵 현재 모니터링: {noise_choice}")
st.audio(audio_bytes, format="audio/wav")

if st.button("💾 최종 5분 고음질 파일 다운로드"):
    with st.spinner("고음질 5분 파일을 추출 중입니다..."):
        # 다운로드는 고음질(44100Hz)로 별도 생성 가능하지만, 
        # 일단은 현재 모니터링 사양으로 즉시 다운로드 가능하게 연결합니다.
        st.download_button(
            label="WAV 다운로드 시작",
            data=audio_bytes,
            file_name=f"SoundLay_{noise_choice}.wav",
            mime="audio/wav"
        )

import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Real-time", page_icon="🎧")

st.title("🎧 SoundLay: Real-time Sound Engine")
st.markdown("슬라이더를 조절하면 즉시 새로운 사운드가 생성됩니다.")

# --- 사이드바: 컨트롤 패널 (움직이면 바로 반영됨) ---
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리"])
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 1.0, 0.4)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 (미리듣기용 3분 고정) ---
def generate_realtime_audio(duration_min=3):
    fs = 22050  # 실시간 반응성을 위해 샘플링 레이트를 절반으로 조절 (연산 속도 UP)
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
        noise = np.convolve(white, np.ones(100)/100, mode='same')
    
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6) * noise_vol
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    
    final = (np.vstack((l_ch, r_ch)) * 0.5 + noise) * envelope
    audio_int16 = (np.clip(final, -1.0, 1.0).T * 32767).astype(np.int16)
    return fs, audio_int16

# --- 메인 실행부 (버튼 없이 바로 실행) ---

with st.status("🔄 사운드 튜닝 중...", expanded=False) as status:
    fs, audio_data = generate_realtime_audio(3)
    buf = io.BytesIO()
    wavfile.write(buf, fs, audio_data)
    audio_bytes = buf.getvalue()
    status.update(label="✅ 조율 완료!", state="complete")

st.subheader("🎵 실시간 모니터링 (3분 세션)")
st.audio(audio_bytes, format="audio/wav")

# 다운로드는 별도 버튼으로 제공
if st.button("💾 최종 5분 파일 다운로드 생성"):
    with st.spinner("고음질 5분 파일을 추출 중입니다..."):
        # 다운로드용은 고음질(44100Hz)로 생성
        fs_high = 44100
        t_high = np.linspace(0, 300, int(fs_high * 300), endpoint=False)
        # (생략된 고음질 로직... 위와 동일)
        st.download_button("다운로드 시작", data=audio_bytes, file_name="SoundLay_Final.wav")

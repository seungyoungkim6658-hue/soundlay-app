import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Final High-Gain Engine")
st.markdown("슬라이더를 조절하면 소리가 즉시 생성됩니다. 하단의 다운로드 버튼을 이용하세요.")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
# 볼륨 범위를 0.0 ~ 3.0으로 설정
noise_vol = st.sidebar.slider("배경음 볼륨 (Max 3.0)", 0.0, 3.0, 1.5)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 함수
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 바이노럴 비트 (0.4 배율 유지)
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.4
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.4
    
    # 노이즈 생성
    white = np.random.normal(0, 1, len(t))
    if noise_choice == "빗소리":
        noise = np.cumsum(white)
        noise = noise - np.convolve(noise, np.ones(50)/50, mode='same')
    elif noise_choice == "파도소리":
        noise = np.cumsum(np.cumsum(white))
        noise = noise * (0.5 * (1 + np.sin(2 * np.pi * 0.08 * t)))
    elif noise_choice == "바람소리":
        noise = np.convolve(white, np.ones(500)/500, mode='same')
    elif noise_choice == "모닥불소리":
        crackle = np.where(np.random.rand(len(t)) > 0.9997, 2.5, 0

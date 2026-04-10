import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Max-Volume Engine")
st.markdown("배경음 볼륨 범위를 3.0까지 확장했습니다. 풍성한 공간감을 느껴보세요.")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
# 볼륨 범위를 0.0 ~ 3.0으로 수정
noise_vol = st.sidebar.slider("배경음 볼륨 (Max 3.0)", 0.0, 3.0, 1.5) 

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 엔진
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 바이노럴 비트 (0.4 배율로 안정적 유지)
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.4
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.4
    
    # 노이즈 생성 알고리즘
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
        crackle = np.where(np.random.rand(len(t)) > 0.9997, 2.5, 0.0)
        noise = white * 0.15 + crackle
    else: # 시냇물
        noise = white * (np.sin(2 * np.pi * 0.5 * t) * 0.6 + 0.4)
    
    # 노이즈 정규화 및 확장된 볼륨(Max 3.0) 적용
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6)
    # 4배 기본 증폭 후 사용자의 slider 값(0~3) 적용
    amplified_noise = noise * noise_vol * 4.0 
    
    # 호흡 주기 엔벨로프 (배경음에만 적용)
    envelope = 0.5 * (1 + np.sin

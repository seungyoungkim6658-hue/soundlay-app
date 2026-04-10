import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: High-Volume Engine")
st.markdown("자연 배경음의 출력을 대폭 강화했습니다. 델타파 베이스와 최적의 밸런스를 맞춰보세요.")

# --- 사이드바 설정 ---
st.sidebar.header("1. 🧠 바이노럴 비트 (지속음)")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음 (출력 강화)")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
# 기본값을 1.2로 높여서 바로 풍성하게 들리도록 설정
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 2.0, 1.2)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# --- 사운드 생성 엔진 ---
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 1. Binaural Beats (안정적인 베이스 유지)
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.4
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.4
    
    # 2. Noise Generation (알고리즘 보강)
    white = np.random.normal(0, 1, len(t))
    if noise_choice == "빗소리":
        noise = np.cumsum(white)
        noise = noise - np.convolve(noise, np.ones(50)/50, mode='same')
    elif noise_choice == "파도소리":
        noise = np.cumsum(np.cumsum(white))
        wave_env = 0.5 * (1 + np.sin(2 * np.pi * 0.08 * t)) # 파도 주기를 약간 더 느리게
        noise = noise * wave_env
    elif noise_choice == "바람소리":
        noise = np.convolve(white, np.ones(500)/500, mode='same')
    elif noise_choice == "모닥불소리":
        crackle = np.where(np.random.rand(len(t)) > 0.9997, 2.5, 0.0)
        noise = white * 0.15 + crackle
    else: # 시냇물소리
        water_mod = np.sin(2 * np.pi * 0.5 * t) * 0.6 + 0.4
        noise = white * water_mod
    
    # 노이즈 정규화 및 강력한 증폭 적용 (4.0배 부스트)
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6)
    amplified_noise = noise * noise_vol * 4.0 
    
    # 3. 호흡 주기 엔벨로프 (배경음에만 적용)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    breathing_noise = amplified_noise * envelope
    
    # 4. 최종 믹싱 및 리미팅 (소리 깨짐 방지)
    final_l = l_ch + breathing_noise
    final_r = r_ch + breathing_noise
    
    final = np.vstack((final_l, final_r))
    
    # Soft Clipping: 소리가 한계를 넘을 때 부드럽게 눌

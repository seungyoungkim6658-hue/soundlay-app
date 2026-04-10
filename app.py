import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Final Max-Volume Engine")
st.markdown("모든 버그가 수정된 최종 엔진입니다. 슬라이더를 조절하여 사운드를 설계하세요.")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍃 자연 배경음")
noise_choice = st.sidebar.selectbox("사운드 소스", ["빗소리", "파도소리", "바람소리", "시냇물소리", "모닥불소리"])
# 볼륨 범위 0.0 ~ 3.0
noise_vol = st.sidebar.slider("배경음 볼륨 (Max 3.0)", 0.0, 3.0, 1.5)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 함수
def generate_audio(duration_min=3, fs=22050):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # 바이노럴 비트
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
        # 44행 괄호 오류 수정 완료
        crackle = np.where(np.random.rand(len(t)) > 0.9997, 2.5, 0.0)
        noise = white * 0.15 + crackle
    else: # 시냇물
        noise = white * (np.sin(2 * np.pi * 0.5 * t) * 0.6 + 0.4)
    
    # 정규화 및 증폭
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6)
    amplified_noise = noise * noise_vol * 4.0 
    
    # 호흡 주기 엔벨로프 (55행 괄호 오류 수정 완료)
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    breathing_noise = amplified_noise * envelope
    
    # 최종 믹싱 및 리미팅
    final = np.tanh(np.vstack((l_ch + breathing_noise, r_ch + breathing_noise)))
    
    return fs, (final.T * 32767).astype(np.int16)

# 4. 실시간 모니터링 출력
st.subheader(f"🎵 모니터링: {noise_choice}")
with st.spinner("사운드 엔진 가동 중..."):
    fs_pre, data_pre = generate_audio(3)
    buf_pre = io.BytesIO()
    wavfile.write(buf_pre, fs_pre, data_pre)
    st.audio(buf_pre.getvalue(), format="audio/wav")

st.divider()

# 5. 최종 음원 저장 버튼
st.subheader("🔴 최종 음원 저장")
if st.button("💾 고음질 5분 세션 생성하기"):
    with st.spinner("5분 고출력 파일을 추출 중입니다..."):
        fs_final, data_final = generate_audio(5, 44100)
        buf_final = io.BytesIO()
        wavfile.write(buf_final, fs_final, data_final)
        
        st.download_button(
            label="✅ 준비 완료! 클릭하여 다운로드",
            data=buf_final.getvalue(),
            file_name=f"SoundLay_Final_{noise_choice}.wav",
            mime="audio/wav"
        )
        st.success("고출력 세션 생성이 완료되었습니다!")

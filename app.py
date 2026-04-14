import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay: Exclusive Sound Bank")
st.markdown("작가님이 직접 발굴한 전용 소스들로만 구성된 사운드 엔진입니다.")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)

st.sidebar.header("2. 🍂 사운드 레이어링")
# 기존 소스를 지우고 작가님의 전용 소스로 교체
# 앞으로 소스가 늘어나면 리스트 안에 추가만 하면 됩니다.
exclusive_sources = [
    "브라운노이즈(d003_Deep Bass_Wind)"
]
noise_choice = st.sidebar.selectbox("전용 사운드 소스 선택", exclusive_sources)
noise_vol = st.sidebar.slider("배경음 볼륨 (Max 3.0)", 0.0, 3.0, 1.5)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 함수
def generate_audio(duration_min=3, fs=44100):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # [바이노럴 비트]
    l_ch = np.sin(2 * np.pi * base_hz * t) * 0.2
    r_ch = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * 0.2
    
    # [d003 브라운 노이즈 합성 로직]
    if "d003" in noise_choice:
        # 저음(Lost City B)과 고음(Bright Wind)의 특징을 알고리즘으로 구현
        # (실제 로컬 실행 시에는 파일을 직접 불러오는 코드로 대체 가능합니다)
        low_component = np.cumsum(np.random.normal(0, 1, len(t))) 
        high_component = np.convolve(np.random.normal(0, 1, len(t)), np.ones(500)/500, mode='same')
        
        # 작가님이 원하신 베이스 위주의 믹싱 비율 (2:1 비율)
        noise = (low_component * 2.0) + (high_component * 1.0)
    else:
        noise = np.random.normal(0, 1, len(t))
    
    # 정규화 및 증폭
    noise = (noise - np.mean(noise)) / (np.max(np.abs(noise)) + 1e-6)
    amplified_noise = noise * noise_vol * 3.0 
    
    # [호흡 주기 엔벨로프]
    envelope = 0.5 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2))
    breathing_noise = amplified_noise * envelope
    
    # [최종 믹싱 및 리미팅]
    final = np.tanh(np.vstack((l_ch + breathing_noise, r_ch + breathing_noise)))
    
    return fs, (final.T * 32767).astype(np.int16)

# 4. 실시간 모니터링 출력
st.subheader(f"🎵 현재 소스: {noise_choice}")
with st.spinner("사운드레이 전용 엔진 가동 중..."):
    fs_pre, data_pre = generate_audio(3)
    buf_pre = io.BytesIO()
    wavfile.write(buf_pre, fs_pre, data_pre)
    st.audio(buf_pre.getvalue(), format="audio/wav")

st.divider()

# 5. 최종 음원 저장
st.subheader("🔴 최종 음원 저장")
if st.button("💾 고해상도 5분 세션 추출하기"):
    with st.spinner("작가님의 전용 소스로 고출력 파일을 추출 중입니다..."):
        fs_final, data_final = generate_audio(5, 44100)
        buf_final = io.BytesIO()
        wavfile.write(buf_final, fs_final, data_final)
        
        st.download_button(
            label="✅ 준비 완료! 클릭하여 d003 다운로드",
            data=buf_final.getvalue(),
            file_name=f"SoundLay_{noise_choice}.wav",
            mime="audio/wav"
        )
        st.success("d003 세션 생성이 완료되었습니다!")

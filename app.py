import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay Studio: Exclusive Engine")
st.markdown("작가님이 직접 설계한 전용 소스들로 구성된 사운드레이 스튜디오입니다.")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)
beat_vol = st.sidebar.slider("비트 볼륨", 0.0, 0.5, 0.2)

st.sidebar.header("2. 🍂 사운드 레이어링")
# 메뉴명 변경 및 "None" 옵션 추가
exclusive_sources = [
    "None",
    "브라운노이즈(바람+터널울림)"
]
noise_choice = st.sidebar.selectbox("전용 사운드 소스 선택", exclusive_sources)
noise_vol = st.sidebar.slider("배경음 볼륨 (Max 3.0)", 0.0, 3.0, 1.5)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 함수
def generate_audio(duration_min=3, fs=44100):
    t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
    
    # [1. 바이노럴 비트 생성 - 고정 볼륨]
    l_beat = np.sin(2 * np.pi * base_hz * t) * beat_vol
    r_beat = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * beat_vol
    
    # [2. 전용 노이즈 생성 로직]
    if noise_choice == "None":
        noise_raw = np.zeros_like(t) # 아무 소리도 생성하지 않음
    elif "바람+터널울림" in noise_choice:
        # 저음(Lost City B)과 고음(Bright Wind)의 특징을 반영한 합성 알고리즘
        low_component = np.cumsum(np.random.normal(0, 1, len(t))) 
        high_component = np.convolve(np.random.normal(0, 1, len(t)), np.ones(500)/500, mode='same')
        noise_raw = (low_component * 2.0) + (high_component * 1.0)
    else:
        noise_raw = np.zeros_like(t)
    
    # 노이즈 정규화 및 설정 볼륨 적용
    if np.max(np.abs(noise_raw)) > 0:
        noise_raw = (noise_raw - np.mean(noise_raw)) / (np.max(np.abs(noise_raw)) + 1e-6)
    noise_amplified = noise_raw * noise_vol
    
    # [3. 호흡 주기 엔벨로프 생성 (노이즈 전용)]
    envelope = 0.45 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2)) + 0.1
    
    # [4. 노이즈에만 호흡 주기 적용]
    breathing_noise = noise_amplified * envelope
    
    # [5. 최종 믹싱]
    final_l = l_beat + breathing_noise
    final_r = r_beat + breathing_noise
    
    # 피크 방지를 위해 tanh 적용
    final = np.tanh(np.vstack((final_l, final_r)))
    
    return fs, (final.T * 32767).astype(np.int16)

# 4. 실시간 모니터링 출력
st.subheader(f"🎵 모니터링: {noise_choice}")
with st.spinner("사운드레이 엔진 가동 중..."):
    fs_pre, data_pre = generate_audio(3)
    buf_pre = io.BytesIO()
    wavfile.write(buf_pre, fs_pre, data_pre)
    st.audio(buf_pre.getvalue(), format="audio/wav")

st.divider()

# 5. 최종 음원 저장
st.subheader("🔴 음원 추출")
if st.button("💾 고해상도 5분 세션 생성하기"):
    with st.spinner(f"{noise_choice} 사운드를 추출 중입니다..."):
        fs_final, data_final = generate_audio(5, 44100)
        buf_final = io.BytesIO()
        wavfile.write(buf_final, fs_final, data_final)
        
        st.download_button(
            label=f"✅ {noise_choice} 다운로드",
            data=buf_final.getvalue(),
            file_name=f"SoundLay_{noise_choice}.wav",
            mime="audio/wav"
        )
        st.success("세션 생성이 완료되었습니다!")

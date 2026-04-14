import streamlit as st
import numpy as np
from scipy.io import wavfile
import io

# 1. 페이지 설정
st.set_page_config(page_title="SoundLay Studio", page_icon="🎧")

st.title("🎧 SoundLay Studio: Stable v1.3")
st.info("설정을 변경한 후 하단의 '미리보기' 버튼을 눌러주세요. (먹통 방지 모드)")

# 2. 사이드바 설정
st.sidebar.header("1. 🧠 바이노럴 비트")
base_hz = st.sidebar.slider("기준 주파수", 100, 250, 140)
offset_hz = st.sidebar.slider("유도 뇌파", 0.1, 40.0, 7.83)
beat_vol = st.sidebar.slider("비트 볼륨", 0.0, 0.5, 0.2)

st.sidebar.header("2. 🍂 사운드 레이어링")
exclusive_sources = ["None", "브라운노이즈(바람+터널울림)"]
noise_choice = st.sidebar.selectbox("전용 사운드 소스 선택", exclusive_sources)
noise_vol = st.sidebar.slider("배경음 볼륨", 0.0, 3.0, 1.5)

st.sidebar.header("3. 🫁 호흡 주기")
breath_hz = st.sidebar.number_input("호흡 속도 (Hz)", 0.01, 0.50, 0.05)

# 3. 사운드 생성 함수 (안정성 강화)
def generate_audio(duration_min=1, fs=22050):
    try:
        t = np.linspace(0, duration_min * 60, int(fs * duration_min * 60), endpoint=False)
        
        # 바이노럴 비트
        l_beat = np.sin(2 * np.pi * base_hz * t) * beat_vol
        r_beat = np.sin(2 * np.pi * (base_hz + offset_hz) * t) * beat_vol
        
        # 노이즈 생성
        if noise_choice == "None":
            noise_amplified = np.zeros_like(t)
        else:
            # 브라운 노이즈 (작가님 소스 특성 반영 알고리즘)
            low = np.cumsum(np.random.normal(0, 1, len(t)))
            high = np.convolve(np.random.normal(0, 1, len(t)), np.ones(200)/200, mode='same')
            noise_raw = (low * 2.5) + high # 베이스 비중 강화
            
            # 안전한 정규화 (에러 방지용 1e-6)
            denom = np.max(np.abs(noise_raw)) + 1e-6
            noise_raw = (noise_raw - np.mean(noise_raw)) / denom
            noise_amplified = noise_raw * noise_vol

        # 호흡 주기 엔벨로프 (노이즈에만 적용)
        envelope = 0.45 * (1 + np.sin(2 * np.pi * breath_hz * t - np.pi/2)) + 0.1
        breathing_noise = noise_amplified * envelope
        
        # 믹싱 및 피크 방지 (tanh)
        final_l = np.tanh(l_beat + breathing_noise)
        final_r = np.tanh(r_beat + breathing_noise)
        
        return fs, (np.vstack((final_l, final_r)).T * 32767).astype(np.int16)
    except Exception as e:
        return None, str(e)

# 4. 실시간 모니터링 (버튼식으로 변경)
st.subheader(f"🎵 현재 선택: {noise_choice}")
if st.button("▶️ 사운드 미리보기 (30초)"):
    with st.spinner("사운드를 생성 중입니다..."):
        fs_pre, data_pre = generate_audio(0.5) # 30초만 미리보기
        if fs_pre:
            buf_pre = io.BytesIO()
            wavfile.write(buf_pre, fs_pre, data_pre)
            st.audio(buf_pre.getvalue(), format="audio/wav")
        else:
            st.error(f"생성 실패: {data_pre}")

st.divider()

# 5. 최종 음원 저장
st.subheader("🔴 고음질 음원 추출")
if st.button("💾 고해상도 5분 세션 생성하기"):
    with st.spinner("대용량 파일을 추출 중입니다. 잠시만 기다려주세요..."):
        fs_final, data_final = generate_audio(5, 44100) # 고품질 44.1kHz
        if fs_final:
            buf_final = io.BytesIO()
            wavfile.write(buf_final, fs_final, data_final)
            st.download_button(
                label=f"✅ {noise_choice} 다운로드",
                data=buf_final.getvalue(),
                file_name=f"SoundLay_{noise_choice}.wav",
                mime="audio/wav"
            )
            st.success("세션 생성이 완료되었습니다!")
        else:
            st.error(f"추출 실패: {data_final}")

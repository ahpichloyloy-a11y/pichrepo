import streamlit as st
import edge_tts
import asyncio

st.set_page_config(page_title="Khmer Edge TTS App", page_icon="🎙️")
st.title("🎙 កម្មវិធីបំប្លែងអត្ថបទខ្មែរ (Edge TTS Natural Voice)")

# ជ្រើសរើសសំឡេងខ្មែរ
voice_option = st.selectbox(
    "ជ្រើសរើសសំឡេង (Voice):",
    options=[
        ("ស្រី (Sreymom Neural)", "km-KH-SreymomNeural"),
        ("ប្រុស (Piseth Neural)", "km-KH-PisethNeural")
    ],
    format_func=lambda x: x[0]
)

# សារ៉េ Rate និង Pitch
col1, col2 = st.columns(2)
with col1:
    rate_val = st.slider("ល្បឿននិយាយ (Rate):", min_value=-50, max_value=50, value=0, step=5, format="%d%%")
with col2:
    pitch_val = st.slider("កម្រិតសំឡេង (Pitch):", min_value=-20, max_value=20, value=0, step=2, format="%dHz")

rate_str = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

text_input = st.text_area(
    "បញ្ចូលអត្ថបទខ្មែរ៖", 
    height=150, 
    placeholder="សួស្ដី! សូមស្វាគមន៍..."
)

async def generate_speech(text, voice, rate, pitch):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# Function សម្រាប់ដោះស្រាយបញ្ហា Asyncio ក្នុង Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        # បើ event loop កំពុងរ៉ាន់ ត្រូវបង្កើត loop ថ្មីដាច់ដោយឡែក
        new_loop = asyncio.new_event_loop()
        return new_loop.run_until_complete(coro)
    else:
        return loop.run_until_complete(coro)

if st.button("បង្កើតសំឡេង (Generate Audio)", type="primary"):
    if text_input.strip() == "":
        st.warning("សូមបញ្ចូលអត្ថបទជាមុនសិន!")
    else:
        with st.spinner("កំពុងបំប្លែងទៅជាសំឡេង..."):
            try:
                selected_voice = voice_option[1]
                
                # ហៅប្រើ function run_async ជំនួស asyncio.run()
                audio_bytes = run_async(generate_speech(text_input, selected_voice, rate_str, pitch_str))
                
                st.success("បំប្លែងរួចរាល់!")
                st.audio(audio_bytes, format='audio/mp3')
                
                st.download_button(
                    label="📥 ទាញយកឯកសារ MP3",
                    data=audio_bytes,
                    file_name="khmer_speech.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"មានបញ្ហា៖ {e}")
import streamlit as st
import os
from transcriber import YouTubeTranscriber

# Asset loading functions
def local_css(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Couldn't load CSS: {str(e)}")

def local_js(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Couldn't load JavaScript: {str(e)}")

def main():
    # Load assets
    local_css("assets/style.css")
    local_js("assets/script.js")

    # Add this to your main() function after loading CSS/JS
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Fira+Code&display=swap" rel="stylesheet">
     """, unsafe_allow_html=True)

    # App Header
    st.markdown("""
    <div class="header">
        <h1>🎥 YouTube Video Transcriber</h1>
        <p class="subtitle">Convert YouTube videos to text transcripts</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize transcriber
    if 'transcriber' not in st.session_state:
        st.session_state.transcriber = YouTubeTranscriber()

    # Main UI
    youtube_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    model_choice = st.selectbox("Select Model Size:", list(st.session_state.transcriber.model_choices.keys()))

    if youtube_url:
        # Show video thumbnail
        st.video(youtube_url)
        
        if st.button("Transcribe Video"):
            try:
                with st.spinner("Downloading and transcribing..."):
                    audio_file = st.session_state.transcriber.download_youtube_audio(youtube_url)
                    transcript = st.session_state.transcriber.transcribe_audio(
                        audio_file, 
                        st.session_state.transcriber.model_choices[model_choice]
                    )
                    st.session_state.formatted_transcript = st.session_state.transcriber.format_transcript(transcript)
                    st.success("Transcription complete!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                if 'audio_file' in locals() and os.path.exists(audio_file):
                    os.remove(audio_file)

    # Show results if available
    if 'formatted_transcript' in st.session_state:
        st.subheader("Transcript")
        st.text_area("Full Transcript", st.session_state.formatted_transcript, height=300)

        # Download button
        st.download_button(
            label="Download Transcript",
            data=st.session_state.formatted_transcript,
            file_name="transcript.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
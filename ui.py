import streamlit as st
import cv2

class UI:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()
        self.frame_placeholder = None
        self.stats_placeholder = None

    def setup_page(self):
        st.set_page_config(page_title="NailGuard", layout="wide")
        st.markdown("<h1 style='text-align: center;'>🖐️ NailGuard</h1>", unsafe_allow_html=True)
        st.markdown("---")

    def initialize_session_state(self):
        if 'bite_attempts' not in st.session_state:
            st.session_state.bite_attempts = 0
        if 'warning_active' not in st.session_state:
            st.session_state.warning_active = False

    def setup_layout(self):
        col1, col2 = st.columns([2, 1])
        self.frame_placeholder = col1.empty()
        self.stats_placeholder = col2.empty()
        return col1, col2

    def create_sidebar(self):
        with st.sidebar:
            st.title("Settings")
            sensitivity = st.slider("Sensitivity (lower = stricter)", 30, 80, 50)
            sound_enabled = st.checkbox("Enable Warning Sound", value=True)
            return sensitivity, sound_enabled

    def update_frame(self, frame):
        if self.frame_placeholder:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_placeholder.image(frame, channels='RGB')

    def update_stats(self, bite_attempts, sensitivity):
        if self.stats_placeholder:
            self.stats_placeholder.markdown(
                f"### Stats\n- **Bite Attempts:** {bite_attempts}\n- **Sensitivity:** {sensitivity}"
            )
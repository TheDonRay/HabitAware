import streamlit as st
import cv2

class UI:
    """
    Manages the Streamlit user interface for the web version of the application.
    This class handles page setup, layout, and updating the display with
    camera frames and statistics.
    """
    def __init__(self):
        """
        Initialize the UI manager by setting up the page and session state.
        """
        self.setup_page()
        self.initialize_session_state()
        self.frame_placeholder = None  # Will hold the frame display area
        self.stats_placeholder = None  # Will hold the statistics display area

    def setup_page(self):
        """
        Configure the Streamlit page with title and layout settings.
        """
        st.set_page_config(page_title="NailGuard", layout="wide")
        st.markdown("<h1 style='text-align: center;'>🖐️ NailGuard</h1>", unsafe_allow_html=True)
        st.markdown("---")

    def initialize_session_state(self):
        """
        Initialize Streamlit session state variables.
        These variables persist between reruns of the app.
        """
        if 'bite_attempts' not in st.session_state:
            st.session_state.bite_attempts = 0
        if 'warning_active' not in st.session_state:
            st.session_state.warning_active = False

    def setup_layout(self):
        """
        Create the main layout with two columns for frame display and statistics.
        
        Returns:
            tuple: (col1, col2) Streamlit column objects
        """
        col1, col2 = st.columns([2, 1])  # Create two columns with 2:1 ratio
        self.frame_placeholder = col1.empty()  # Placeholder for camera frame
        self.stats_placeholder = col2.empty()  # Placeholder for statistics
        return col1, col2

    def create_sidebar(self):
        """
        Create the sidebar with settings controls.
        
        Returns:
            tuple: (sensitivity, sound_enabled)
                - sensitivity: The current sensitivity value
                - sound_enabled: Whether sound is enabled
        """
        with st.sidebar:
            st.title("Settings")
            sensitivity = st.slider("Sensitivity (lower = stricter)", 30, 80, 50)
            sound_enabled = st.checkbox("Enable Warning Sound", value=True)
            return sensitivity, sound_enabled

    def update_frame(self, frame):
        """
        Update the frame display with a new camera frame.
        
        Args:
            frame: The frame to display
        """
        if self.frame_placeholder:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
            self.frame_placeholder.image(frame, channels='RGB')

    def update_stats(self, bite_attempts, sensitivity):
        """
        Update the statistics display with current values.
        
        Args:
            bite_attempts: Number of bite attempts detected
            sensitivity: Current sensitivity setting
        """
        if self.stats_placeholder:
            self.stats_placeholder.markdown(
                f"### Stats\n- **Bite Attempts:** {bite_attempts}\n- **Sensitivity:** {sensitivity}"
            )
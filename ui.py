import streamlit as st
import cv2
import time  
from StressPopup import StressPopUp

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
        self.stress_popup = StressPopUp() 

    def setup_page(self):
        """
        Configure the Streamlit page with title and layout settings.
        """
        st.set_page_config(page_title="HabitAware", layout="wide")
        st.markdown("<h1 style='text-align: center;'>🖐️ HabitAware</h1>", unsafe_allow_html=True)
        st.markdown("---")

    def initialize_session_state(self):
        """
        Initialize Streamlit session state variables.
        These variables persist between reruns of the app.
        """
        if 'stress_attempts' not in st.session_state:
            st.session_state.stress_attempts = 0
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

    def format_time(self, seconds):
        """
        Format time duration into a human-readable string.
        
        Args:
            seconds: Time duration in seconds
            
        Returns:
            str: Formatted time string
        """
        seconds = int(seconds)
        if seconds < 60: 
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        else: 
            return f"{seconds//3600}h {(seconds%3600)//60}m"

    def update_stats(self, stress_attempts, sensitivity, stress_duration=0, time_since_last_stress=0):
        """
        Update the statistics display with current values.
        
        Args:
            stress_attempts: Number of stress behavior attempts detected
            sensitivity: Current sensitivity setting
            stress_duration: Total duration of stress behaviors
            time_since_last_stress: Time since last stress behavior
        """
        if self.stats_placeholder:
            # Format last stress time
            if time_since_last_stress == 0 and st.session_state.last_stress_time == 0:
                last_stress_str = "Never"
            elif time_since_last_stress == 0:
                last_stress_str = "Now"
            elif time_since_last_stress < 60: 
                last_stress_str = f"{int(time_since_last_stress)}s ago"
            elif time_since_last_stress < 3600:
                last_stress_str = f"{int(time_since_last_stress)//60}m ago"
            else: 
                last_stress_str = f"{int(time_since_last_stress//3600)}h ago"
                
            self.stats_placeholder.markdown(
                f"""
                <div style='background-color: #black; padding: 1px; border-radius: 2px;'>
                    <h3 style='color: #666; margin-bottom: 1px; font-size: 14px;'>📊 Stats</h3>
                    <div style='display: flex; flex-direction: column; gap: 1px;'>
                        <div style='background-color: black; padding: 1px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>
                            <p style='margin: 0; color: #666; font-size: 12px;'>Stress Behaviors</p>
                            <h2 style='margin: 1px 0; color: #e74c3c; font-size: 16px;'>🔴 {stress_attempts}</h2>
                        </div>
                        <div style='background-color: black; padding: 1px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>
                            <p style='margin: 0; color: #666; font-size: 12px;'>Sensitivity</p>
                            <h2 style='margin: 1px 0; color: #3498db; font-size: 16px;'>🎚️ {sensitivity}</h2>
                        </div>
                        <div style='background-color: black; padding: 1px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>
                            <p style='margin: 0; color: #666; font-size: 12px;'>Duration</p>
                            <h2 style='margin: 1px 0; color: #2ecc71; font-size: 16px;'>⏱️ {self.format_time(stress_duration)}</h2>
                        </div>
                        <div style='background-color: black; padding: 1px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>
                            <p style='margin: 0; color: #666; font-size: 12px;'>Last Stressed</p>
                            <h2 style='margin: 1px 0; color: #9b59b6; font-size: 16px;'>🕒 {last_stress_str}</h2>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


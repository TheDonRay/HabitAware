# libraries:
import time
import streamlit as st
import cv2
import pandas as pd
import plotly.express as px
from detection import DetectionManager
from sound_manager import SoundManager
from camera_manager import CameraManager
from ui import UI 
from StressPopup import StressPopup

def main():
    # Initialize components
    ui = UI()
    detection_manager = DetectionManager()
    sound_manager = SoundManager()
    camera_manager = CameraManager() 
    stress_popup = StressPopup() 
    
    # Initialize timer variables

    # Initialize session state variables
    if 'stress_attempts' not in st.session_state:
        st.session_state.stress_attempts = 0
    if 'warning_active' not in st.session_state:
        st.session_state.warning_active = False
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = 0
    if 'total_duration' not in st.session_state:
        st.session_state.total_duration = 0
    if 'no_stress_start' not in st.session_state:
        st.session_state.no_stress_start = time.time()
    if 'total_no_stress' not in st.session_state:
        st.session_state.total_no_stress = 0
    if 'last_stress_time' not in st.session_state:
        st.session_state.last_stress_time = 0  # 0 means never
    if 'behavior_log' not in st.session_state:
        st.session_state.behavior_log = []

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "My Dashboard"])

    if page == "Home":
        # Setup layout and get settings
        col1, col2 = ui.setup_layout()
        sensitivity, sound_enabled = ui.create_sidebar()
        sound_manager.set_sound_enabled(sound_enabled)
        # Camera controls
        if st.sidebar.button("Start Camera") and not camera_manager.camera_active:
            # Reset all stats when starting camera
            st.session_state.stress_attempts = 0
            st.session_state.warning_active = False
            st.session_state.timer_active = False
            st.session_state.start_time = 0
            st.session_state.total_duration = 0
            st.session_state.no_stress_start = time.time()
            st.session_state.total_no_stress = 0
            st.session_state.last_stress_time = 0  # Reset to "Never"
            st.session_state.behavior_log = []
            camera_manager.start_camera()

        if st.sidebar.button("Stop Camera") and camera_manager.camera_active:
            camera_manager.stop_camera()

        # Main processing loop
        if camera_manager.is_active():
            try:
                while camera_manager.camera_active:
                    success, frame = camera_manager.read_frame()
                    
                    if not success:
                        st.error("Failed to capture frame")
                        break

                    if frame is not None:
                        # Process frame for detection
                        frame, hand_coords, face_zones, behavior = detection_manager.process_frame(frame, sensitivity)

                        # Check behavior and show warning
                        if behavior is not None and None not in hand_coords:
                            timestamp = time.time()
                            st.session_state.behavior_log.append({
                                'timestamp': timestamp,
                                'behavior': behavior
                            })

                            if not st.session_state.timer_active:
                                st.session_state.timer_active = True 
                                st.session_state.start_time = time.time()  
                            
                            current_duration = st.session_state.total_duration + (time.time() - st.session_state.start_time)

                            if behavior == 'hair_pulling':
                                cv2.putText(frame, "Don't Pull Hair!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                            else:
                                cv2.putText(frame, "Don't Bite!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

                            cv2.putText(frame, f"Duration: {current_duration:.1f}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                            if not st.session_state.warning_active:
                                st.session_state.stress_attempts += 1
                                st.session_state.warning_active = True
                                st.session_state.last_stress_time = time.time()  # Update last stress time when behavior is detected
                                sound_manager.play_warning_sound_threaded()

                                stress_popup.check_and_show_motivation(st.session_state.stress_attempts)
                                
                            if st.session_state.no_stress_start is not None:
                                st.session_state.total_no_stress += time.time() - st.session_state.no_stress_start
                                st.session_state.no_stress_start = None
                        else:
                            if st.session_state.timer_active:
                                st.session_state.total_duration += time.time() - st.session_state.start_time
                                st.session_state.timer_active = False
                            st.session_state.warning_active = False

                            if st.session_state.no_stress_start is None:
                                st.session_state.no_stress_start = time.time()

                        # Update UI with frame
                        ui.update_frame(frame)

                        # Stats
                        current_duration = st.session_state.total_duration
                        if st.session_state.timer_active:
                            current_duration += time.time() - st.session_state.start_time

                        current_no_stress = st.session_state.total_no_stress
                        if st.session_state.no_stress_start is not None:
                            current_no_stress += time.time() - st.session_state.no_stress_start

                        time_since_last_stress = 0
                        if st.session_state.last_stress_time > 0:
                            # Only increase time if there's no current stress behavior
                            if behavior is None:
                                time_since_last_stress = time.time() - st.session_state.last_stress_time
                            else:
                                # Reset the last stress time if stress behavior is detected
                                st.session_state.last_stress_time = time.time()

                        # Check for positive reinforcement when user is doing well
                        stress_popup.check_and_show_positive_reinforcement(time_since_last_stress)

                        ui.update_stats(
                            stress_attempts=st.session_state.stress_attempts,
                            sensitivity=sensitivity,
                            stress_duration=current_duration,
                            time_since_last_stress=time_since_last_stress
                        )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                camera_manager.stop_camera()
                detection_manager.cleanup()

    elif page == "My Dashboard":
        st.header("Check your stats!!")

        if st.session_state.behavior_log:
            df = pd.DataFrame(st.session_state.behavior_log)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

            df_grouped = df.groupby([pd.Grouper(key='timestamp', freq='10S'), 'behavior']).size().reset_index(name='count')

            fig = px.line(
                df_grouped,
                x='timestamp',
                y='count',
                color='behavior',
                color_discrete_map={
                    'Hair Pulls': 'red',
                    'Nail Biting': 'blue'
                },
                title="Your Frequent Behaviors"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No behavior data to show yet. Start using the app from the Home tab.")

if __name__ == "__main__":
    main()

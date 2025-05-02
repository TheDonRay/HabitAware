#libraries: 

import time 
import streamlit as st
import cv2
from detection import DetectionManager
from sound_manager import SoundManager
from camera_manager import CameraManager
from ui import UI

def main():
    # Initialize components
    ui = UI()
    detection_manager = DetectionManager()
    sound_manager = SoundManager()
    camera_manager = CameraManager() 
    
    #to show the timer need to initialize timer variables - Rays Work  
    #here im basically just initializng the states to make sure they are initialized. 
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

    # Setup layout and get settings
    col1, col2 = ui.setup_layout()
    sensitivity, sound_enabled = ui.create_sidebar()
    sound_manager.set_sound_enabled(sound_enabled)

    # Camera controls
    if st.sidebar.button("Start Camera") and not camera_manager.camera_active:
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
                    frame, hand_coords, mouth_coords, behavior = detection_manager.process_frame(frame, sensitivity)

                    # Check behavior and show warning
                    if behavior is not None and None not in hand_coords and None not in mouth_coords:
                        # Timer logic
                        if not st.session_state.timer_active: 
                            st.session_state.timer_active = True 
                            st.session_state.start_time = time.time()  
                            
                        # Calculate the current duration
                        current_duration = st.session_state.total_duration + (time.time() - st.session_state.start_time)
                        
                        # Show appropriate warning
                        if behavior == 'hair_pulling':
                            cv2.putText(frame, "Don't Pull Hair!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                        else:  # nail_biting
                            cv2.putText(frame, "Don't Bite!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                        
                        cv2.putText(frame, f"Duration: {current_duration:.1f}s", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        
                        if not st.session_state.warning_active:
                            st.session_state.stress_attempts += 1
                            st.session_state.warning_active = True
                            sound_manager.play_warning_sound_threaded()
                    else: 
                        if st.session_state.timer_active: 
                            st.session_state.total_duration += time.time() - st.session_state.start_time
                            st.session_state.timer_active = False 
                        st.session_state.warning_active = False 

                    # Update UI
                    ui.update_frame(frame) 
                    current_duration = st.session_state.total_duration 
                    if st.session_state.timer_active: 
                        current_duration += time.time() - st.session_state.start_time
                    ui.update_stats(st.session_state.stress_attempts, sensitivity, current_duration)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            camera_manager.stop_camera()
            detection_manager.cleanup()

if __name__ == "__main__":
    main()

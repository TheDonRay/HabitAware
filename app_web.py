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
                    frame, hand_coords, mouth_coords = detection_manager.process_frame(frame)

                    # Check distance and show warning
                    if None not in hand_coords and None not in mouth_coords:
                        cv2.line(frame, mouth_coords, hand_coords, (0, 255, 0), 2)
                        distance = detection_manager.calculate_distance(hand_coords, mouth_coords)

                        if distance < sensitivity:
                            cv2.putText(frame, "Don't Bite!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                            
                            if not st.session_state.warning_active:
                                st.session_state.bite_attempts += 1
                                st.session_state.warning_active = True
                                sound_manager.play_warning_sound_threaded()
                        else:
                            st.session_state.warning_active = False

                    # Update UI
                    ui.update_frame(frame)
                    ui.update_stats(st.session_state.bite_attempts, sensitivity)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            camera_manager.stop_camera()
            detection_manager.cleanup()

if __name__ == "__main__":
    main()

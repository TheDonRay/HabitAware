import cv2
from detection import DetectionManager
from camera_manager import CameraManager

def main():
    # Initialize components
    detection_manager = DetectionManager(draw_landmarks=True)
    camera_manager = CameraManager()
    
    # Start camera
    camera_manager.start_camera()
    
    try:
        while True:
            success, frame = camera_manager.read_frame()
            if not success:
                print("Failed to capture frame")
                break

            # Process frame for detection
            frame, hand_coords, mouth_coords = detection_manager.process_frame(frame)

            # Check distance and show warning
            if None not in hand_coords and None not in mouth_coords:
                cv2.line(frame, mouth_coords, hand_coords, (0, 255, 0), 2)
                distance = detection_manager.calculate_distance(hand_coords, mouth_coords)

                if distance < 50:  # Fixed sensitivity for desktop version
                    cv2.putText(frame, "Don't Bite!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

            # Show the frame
            cv2.imshow('NailGuard', frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        camera_manager.stop_camera()
        detection_manager.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

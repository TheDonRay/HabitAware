#installed CV2. 
import time 
import cv2 
from detection import DetectionManager
from camera_manager import CameraManager

def main():
    # Initialize components
    detection_manager = DetectionManager(draw_landmarks=True)
    camera_manager = CameraManager()
     
    #create timer variables Rays work 
    is_timer_active = False  
    start_time = 0 #set it equal to 0 
    total_duration = 0 #becausse we want a timer to keep track how long you are biting your nail 
    proximity_threshold = 50 #handles the distance 
    
    # Start camera
    camera_manager.start_camera()
    
    try:
        while True:
            success, frame = camera_manager.read_frame()
            if not success:
                print("Failed to capture frame")
                break

            # Process frame for detection
            frame, hand_coords, face_zones, behavior = detection_manager.process_frame(frame)

            # Check behavior and show warning
            if behavior is not None:
                # Draw line to show the interaction
                if None not in hand_coords and face_zones['top'] is not None:
                    if behavior == 'hair_pulling':
                        zone = face_zones['top']
                        zone_center = ((zone['left'] + zone['right']) // 2, 
                                     (zone['top'] + zone['bottom']) // 2)
                        cv2.line(frame, hand_coords, zone_center, (0, 255, 0), 2)
                    elif behavior == 'nail_biting':
                        zone = face_zones['bottom']
                        zone_center = ((zone['left'] + zone['right']) // 2, 
                                     (zone['top'] + zone['bottom']) // 2)
                        cv2.line(frame, hand_coords, zone_center, (0, 0, 255), 2)
                
                #Timer Logic
                if behavior in ['hair_pulling', 'nail_biting']:
                    if not is_timer_active: 
                        is_timer_active = True 
                        start_time = time.time() 
                    current_duration = total_duration + (time.time() - start_time)
                    # Add your timer display logic here
                else:
                    is_timer_active = False
                    total_duration = 0

            # Display the frame
            cv2.imshow('NailGuard', frame)
            
            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        # Cleanup
        camera_manager.stop_camera()
        detection_manager.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

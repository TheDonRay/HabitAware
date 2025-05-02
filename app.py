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
            frame, hand_coords, mouth_coords = detection_manager.process_frame(frame)

            # Check distance and show warning
            if None not in hand_coords and None not in mouth_coords:
                cv2.line(frame, mouth_coords, hand_coords, (0, 255, 0), 2)
                distance = detection_manager.calculate_distance(hand_coords, mouth_coords) 
                
                #Timer Logic Rayats work. 
                if distance < proximity_threshold: 
                    if not timer_active: 
                        #need to start the timer 
                        timer_active = True 
                        start_time = time.time() 
                    #okay so now what im going to do is update the current duration 
                    current_duration = total_duration + (time.time() - start_time) #basically starts at 0 and starts the timer 
                    
                  

                if distance < 50:  # Fixed sensitivity for desktop version
                    cv2.putText(frame, "Don't Bite!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                    
                    #now im adding the duration to show 
                    cv2.putText(frame, f"Duration: {current_duration:.1f}s", (5,0,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2) 
                 
                else: 
                    if timer_active: 
                        #we want to stop the timer and accumulate total duration 
                        total_duration += time.time() - start_time 
                        timer_active = False 
            else: #my work hends here after this else - Rayat for the if statement condition
                if timer_active: 
                    #we want to stop the timer if tracking is lost 
                    total_duration += time.time() - start_time 
                    timer_active = False
                    
                    
            # Show the frame
            cv2.imshow('HabitAware', frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        #print the final duration Rays work 
        if timer_active: 
            total_duration += time.time() - start_time
        print(f"Total time near mouth: {total_duration:.2f} seconds") 
        
        
        camera_manager.stop_camera()
        detection_manager.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

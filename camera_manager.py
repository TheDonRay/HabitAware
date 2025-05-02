import cv2

class CameraManager:
    """
    Manages camera operations including initialization, frame capture, and cleanup.
    This class provides a simple interface for working with the webcam and ensures
    proper resource management.
    """
    def __init__(self):
        """
        Initialize the camera manager with default values.
        The camera is not started until start_camera() is called.
        """
        self.cap = None  # Will hold the VideoCapture object
        self.camera_active = False  # Tracks if camera is currently active

    def start_camera(self):
        """
        Start the camera if it's not already active.
        Configures camera properties for optimal performance.
        
        Returns:
            bool: True if camera was started successfully, False otherwise
        """
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Small buffer to reduce latency
            
            self.camera_active = True
            return True
        return False

    def stop_camera(self):
        """
        Stop the camera and release resources if it's active.
        
        Returns:
            bool: True if camera was stopped successfully, False otherwise
        """
        if self.camera_active and self.cap is not None:
            self.cap.release()  # Release the camera
            self.cap = None
            self.camera_active = False
            return True
        return False

    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
            tuple: (success, frame)
                - success: Boolean indicating if frame was captured successfully
                - frame: The captured frame, or None if capture failed
        """
        if not self.camera_active or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Flip horizontally for mirror effect
            return True, frame
            
        return False, None

    def is_active(self):
        """
        Check if the camera is currently active and initialized.
        
        Returns:
            bool: True if camera is active and initialized, False otherwise
        """
        return self.camera_active and self.cap is not None
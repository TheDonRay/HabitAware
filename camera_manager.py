import cv2

class CameraManager:
    def __init__(self):
        self.cap = None
        self.camera_active = False

    def start_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            self.camera_active = True
            return True
        return False

    def stop_camera(self):
        if self.camera_active and self.cap is not None:
            self.cap.release()
            self.cap = None
            self.camera_active = False
            return True
        return False

    def read_frame(self):
        if self.camera_active and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                return True, frame
        return False, None

    def is_active(self):
        return self.camera_active and self.cap is not None
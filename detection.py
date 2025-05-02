import cv2
import mediapipe as mp
import math

class DetectionManager:
    """
    Manages all MediaPipe-based detection functionality for hand and face tracking.
    This class handles the initialization of MediaPipe models and provides methods
    for processing frames and calculating distances between detected points.
    """
    def __init__(self, draw_landmarks=True):
        """
        Initialize the detection manager with MediaPipe models.
        
        Args:
            draw_landmarks (bool): Whether to draw landmarks on the frame.
                                  Useful for debugging or visualization.
        """
        # Initialize MediaPipe models
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)  # Only track one hand
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1)  # Only track one face
        self.mp_draw = mp.solutions.drawing_utils  # For drawing landmarks
        self.draw_landmarks = draw_landmarks

    def process_frame(self, frame):
        """
        Process a single frame to detect hands and face landmarks.
        
        Args:
            frame: The input frame from the camera
            
        Returns:
            tuple: (processed_frame, hand_coords, mouth_coords)
                - processed_frame: The frame with optional landmarks drawn
                - hand_coords: (x, y) coordinates of the index finger tip
                - mouth_coords: (x, y) coordinates of the mouth center
        """
        # Convert frame to RGB (MediaPipe requires RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with both hand and face models
        hand_results = self.hands.process(frame_rgb)
        face_results = self.face_mesh.process(frame_rgb)

        # Initialize coordinates as None (will be updated if detected)
        hand_x, hand_y = None, None
        mouth_x, mouth_y = None, None

        # Process hand landmarks
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Draw landmarks if enabled
                if self.draw_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                # Get index finger tip coordinates (landmark 8)
                index_finger_tip = hand_landmarks.landmark[8]
                h, w, c = frame.shape
                hand_x, hand_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

        # Process face landmarks
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                h, w, c = frame.shape
                # Get mouth landmarks (13 and 14 are top and bottom of mouth)
                mouth_top = face_landmarks.landmark[13]
                mouth_bottom = face_landmarks.landmark[14]
                # Calculate mouth center
                mouth_x = int((mouth_top.x + mouth_bottom.x) / 2 * w)
                mouth_y = int((mouth_top.y + mouth_bottom.y) / 2 * h)
                # Draw mouth center if enabled
                if self.draw_landmarks:
                    cv2.circle(frame, (mouth_x, mouth_y), 5, (255, 0, 255), -1)

        return frame, (hand_x, hand_y), (mouth_x, mouth_y)

    def calculate_distance(self, hand_coords, mouth_coords):
        """
        Calculate the Euclidean distance between hand and mouth coordinates.
        
        Args:
            hand_coords: (x, y) coordinates of the hand
            mouth_coords: (x, y) coordinates of the mouth
            
        Returns:
            float: The distance between points, or infinity if either point is None
        """
        if None in hand_coords or None in mouth_coords:
            return float('inf')  # Return infinity if either point is not detected
        return math.hypot(mouth_coords[0] - hand_coords[0], mouth_coords[1] - hand_coords[1])

    def cleanup(self):
        """
        Clean up resources by closing MediaPipe models.
        Should be called when the application is closing.
        """
        self.hands.close()
        self.face_mesh.close()
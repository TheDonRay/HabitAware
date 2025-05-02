import cv2
import mediapipe as mp
import math

class DetectionManager:
    """
    Manages all MediaPipe-based detection functionality for hand and face tracking.
    This class handles the initialization of MediaPipe models and provides methods
    for processing frames and detecting specific bad habits (hair pulling and nail biting).
    """
    def __init__(self, draw_landmarks=True):
        """
        Initialize the detection manager with MediaPipe models.
        
        Args:
            draw_landmarks (bool): Whether to draw landmarks and detection zones on the frame.
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
        Process a single frame to detect hands and face landmarks, identifying specific bad habits.
        
        Args:
            frame: The input frame from the camera
            
        Returns:
            tuple: (processed_frame, hand_coords, face_zones, behavior)
                - processed_frame: The frame with optional landmarks drawn
                - hand_coords: (x, y) coordinates of the closest finger to face
                - face_zones: Dictionary containing top and bottom face zone coordinates
                - behavior: String indicating detected behavior ('hair_pulling', 'nail_biting', or None)
        """
        # Convert frame to RGB (MediaPipe requires RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with both hand and face models
        hand_results = self.hands.process(frame_rgb)
        face_results = self.face_mesh.process(frame_rgb)

        # Initialize coordinates and behavior
        hand_x, hand_y = None, None
        face_zones = {'top': None, 'bottom': None}
        behavior = None
        finger_tips = []

        # Process hand landmarks
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Draw landmarks if enabled
                if self.draw_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Get all finger tips coordinates
                h, w, c = frame.shape
                
                # Thumb (4), Index finger (8), middle finger (12), ring finger (16), pinky (20)
                finger_landmarks = [4, 8, 12, 16, 20]
                for landmark_id in finger_landmarks:
                    finger_tip = hand_landmarks.landmark[landmark_id]
                    finger_tips.append((int(finger_tip.x * w), int(finger_tip.y * h)))
                
                # Store all finger tips for later use
                if finger_tips:
                    hand_x, hand_y = finger_tips[0]  # Default to first finger if no face detected

        # Process face landmarks
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                h, w, c = frame.shape
                
                # Get face bounding box coordinates
                face_top = face_landmarks.landmark[10]  # Top of forehead
                face_bottom = face_landmarks.landmark[152]  # Bottom of chin
                face_left = face_landmarks.landmark[234]  # Left side
                face_right = face_landmarks.landmark[454]  # Right side
                
                # Calculate face zones
                face_top_y = int(face_top.y * h)
                face_bottom_y = int(face_bottom.y * h)
                face_mid_y = int((face_top_y + face_bottom_y) / 2)
                
                # Store face zone coordinates
                face_zones['top'] = {
                    'top': face_top_y,
                    'bottom': face_mid_y,
                    'left': int(face_left.x * w),
                    'right': int(face_right.x * w)
                }
                face_zones['bottom'] = {
                    'top': face_mid_y,
                    'bottom': face_bottom_y,
                    'left': int(face_left.x * w),
                    'right': int(face_right.x * w)
                }
                
                # Draw face zones if enabled
                if self.draw_landmarks:
                    # Draw top zone (hair pulling zone)
                    cv2.rectangle(frame, 
                                (face_zones['top']['left'], face_zones['top']['top']),
                                (face_zones['top']['right'], face_zones['top']['bottom']),
                                (0, 255, 0), 2)
                    # Draw bottom zone (nail biting zone)
                    cv2.rectangle(frame,
                                (face_zones['bottom']['left'], face_zones['bottom']['top']),
                                (face_zones['bottom']['right'], face_zones['bottom']['bottom']),
                                (0, 0, 255), 2)
                
                # Determine behavior based on hand position
                if hand_x is not None and hand_y is not None:
                    if (face_zones['top']['left'] <= hand_x <= face_zones['top']['right'] and
                        face_zones['top']['top'] <= hand_y <= face_zones['top']['bottom']):
                        behavior = 'hair_pulling'
                    elif (face_zones['bottom']['left'] <= hand_x <= face_zones['bottom']['right'] and
                          face_zones['bottom']['top'] <= hand_y <= face_zones['bottom']['bottom']):
                        behavior = 'nail_biting'

        return frame, (hand_x, hand_y), face_zones, behavior

    def get_finger_tips(self, hand_landmarks, frame_shape):
        """
        Get coordinates of all finger tips from hand landmarks.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: Shape of the frame (height, width, channels)
            
        Returns:
            list: List of (x, y) coordinates for each finger tip
        """
        h, w, c = frame_shape
        finger_tips = []
        # Thumb (4), Index finger (8), middle finger (12), ring finger (16), pinky (20)
        finger_landmarks = [4, 8, 12, 16, 20]
        for landmark_id in finger_landmarks:
            finger_tip = hand_landmarks.landmark[landmark_id]
            finger_tips.append((int(finger_tip.x * w), int(finger_tip.y * h)))
        return finger_tips

    def calculate_distance(self, hand_coords, target_coords):
        """
        Calculate the Euclidean distance between hand and target coordinates.
        
        Args:
            hand_coords: (x, y) coordinates of the hand
            target_coords: (x, y) coordinates of the target point
            
        Returns:
            float: The distance between points, or infinity if either point is None
        """
        if None in hand_coords or None in target_coords:
            return float('inf')  # Return infinity if either point is not detected
        return math.hypot(target_coords[0] - hand_coords[0], target_coords[1] - hand_coords[1])

    def cleanup(self):
        """
        Clean up resources by closing MediaPipe models.
        Should be called when the application is closing.
        """
        self.hands.close()
        self.face_mesh.close()
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

    def process_frame(self, frame, sensitivity=100):
        """
        Process a single frame to detect hands and face landmarks.
        
        Args:
            frame: The input frame from the camera
            sensitivity: The distance threshold for detecting behaviors (in pixels)
            
        Returns:
            tuple: (processed_frame, hand_coords, mouth_coords, behavior)
                - processed_frame: The frame with optional landmarks drawn
                - hand_coords: (x, y) coordinates of the closest finger to face
                - mouth_coords: (x, y) coordinates of the mouth center
                - behavior: String indicating detected behavior ('hair_pulling', 'nail_biting', or None)
        """
        # Convert frame to RGB (MediaPipe requires RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with both hand and face models
        hand_results = self.hands.process(frame_rgb)
        face_results = self.face_mesh.process(frame_rgb)

        # Initialize coordinates and behavior
        hand_x, hand_y = None, None
        mouth_x, mouth_y = None, None
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
                
                # Get mouth landmarks (13 and 14 are top and bottom of mouth)
                mouth_top = face_landmarks.landmark[13]
                mouth_bottom = face_landmarks.landmark[14]
                
                # Get hair landmarks (10 is top of forehead, 151 is eyebrow level)
                hair_top = face_landmarks.landmark[10]
                hair_bottom = face_landmarks.landmark[151]
                
                # Calculate mouth center
                mouth_x = int((mouth_top.x + mouth_bottom.x) / 2 * w)
                mouth_y = int((mouth_top.y + mouth_bottom.y) / 2 * h)
                
                # Calculate hair center (extend above head)
                hair_height = hair_bottom.y - hair_top.y
                hair_x = int(hair_top.x * w)
                hair_y = int((hair_top.y - hair_height) * h)  # Extend above head by one head height
                
                # Draw centers if enabled
                if self.draw_landmarks:
                    cv2.circle(frame, (mouth_x, mouth_y), 5, (255, 0, 255), -1)  # Pink for mouth
                    cv2.circle(frame, (hair_x, hair_y), 5, (0, 255, 0), -1)  # Green for hair
                
                # If we have finger tips, find the closest finger to either point
                if finger_tips:
                    min_distance = float('inf')
                    closest_finger = None
                    target_point = None
                    behavior = None
                    
                    for finger_x, finger_y in finger_tips:
                        # Calculate distances to both points
                        mouth_distance = math.hypot(mouth_x - finger_x, mouth_y - finger_y)
                        hair_distance = math.hypot(hair_x - finger_x, hair_y - finger_y)
                        
                        # Find which point is closer and within sensitivity
                        if mouth_distance < hair_distance and mouth_distance < sensitivity:
                            min_distance = mouth_distance
                            closest_finger = (finger_x, finger_y)
                            target_point = (mouth_x, mouth_y)
                            behavior = 'nail_biting'
                        elif hair_distance < mouth_distance and hair_distance < sensitivity:
                            min_distance = hair_distance
                            closest_finger = (finger_x, finger_y)
                            target_point = (hair_x, hair_y)
                            behavior = 'hair_pulling'
                    
                    if closest_finger:
                        hand_x, hand_y = closest_finger
                        # Draw line to show the interaction
                        if self.draw_landmarks:
                            color = (0, 255, 0) if behavior == 'hair_pulling' else (0, 0, 255)
                            cv2.line(frame, (hand_x, hand_y), target_point, color, 2)

        return frame, (hand_x, hand_y), (mouth_x, mouth_y), behavior

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
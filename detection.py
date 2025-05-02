import cv2
import mediapipe as mp
import math

class DetectionManager:
    def __init__(self, draw_landmarks=True):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1)
        self.mp_draw = mp.solutions.drawing_utils
        self.draw_landmarks = draw_landmarks

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hands and face
        hand_results = self.hands.process(frame_rgb)
        face_results = self.face_mesh.process(frame_rgb)

        hand_x, hand_y = None, None
        mouth_x, mouth_y = None, None

        # Get hand coordinates
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                if self.draw_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                index_finger_tip = hand_landmarks.landmark[8]
                h, w, c = frame.shape
                hand_x, hand_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

        # Get mouth coordinates
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                h, w, c = frame.shape
                mouth_top = face_landmarks.landmark[13]
                mouth_bottom = face_landmarks.landmark[14]
                mouth_x = int((mouth_top.x + mouth_bottom.x) / 2 * w)
                mouth_y = int((mouth_top.y + mouth_bottom.y) / 2 * h)
                if self.draw_landmarks:
                    cv2.circle(frame, (mouth_x, mouth_y), 5, (255, 0, 255), -1)

        return frame, (hand_x, hand_y), (mouth_x, mouth_y)

    def calculate_distance(self, hand_coords, mouth_coords):
        if None in hand_coords or None in mouth_coords:
            return float('inf')
        return math.hypot(mouth_coords[0] - hand_coords[0], mouth_coords[1] - hand_coords[1])

    def cleanup(self):
        self.hands.close()
        self.face_mesh.close()
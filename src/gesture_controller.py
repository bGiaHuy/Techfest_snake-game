import threading
import time
import pygame
import os

# Try importing OpenCV and MediaPipe. If they aren't installed or fail,
# the controller will fall back to "camera unavailable" mode gracefully.
try:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from src.config import (
    WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT,
    COLOR_SIDEBAR_BG, COLOR_TEXT_SECONDARY, get_font
)

# Standard Hand Skeleton Connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
]

class GestureController:
    def __init__(self):
        self.running = False
        self.camera_available = False
        self.current_direction = None  # (dx, dy)
        self.preview_surface = None
        self.thread = None
        self.lock = threading.Lock()
        self.error_message = "Initializing..."
        
        if not OPENCV_AVAILABLE:
            self.error_message = "OpenCV/MediaPipe not installed"
            
    def start(self):
        """Starts the background thread for camera frame acquisition and hand processing."""
        if not OPENCV_AVAILABLE:
            return
            
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stops the thread and releases resources."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
    def get_direction(self):
        """Returns the last detected direction from gestures."""
        with self.lock:
            direction = self.current_direction
            return direction

    def get_preview_surface(self):
        """Returns a Pygame Surface of the live feed, or a status text surface if unavailable."""
        with self.lock:
            if self.preview_surface:
                return self.preview_surface
                
        # Return fallback placeholder surface
        fallback = pygame.Surface((WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT))
        fallback.fill(COLOR_SIDEBAR_BG)
        pygame.draw.rect(fallback, (50, 58, 86), fallback.get_rect(), 2)
        
        # Render error text
        font = get_font(14)
        text_surf = font.render(self.error_message, True, COLOR_TEXT_SECONDARY)
        text_rect = text_surf.get_rect(center=(WEBCAM_PREVIEW_WIDTH // 2, WEBCAM_PREVIEW_HEIGHT // 2))
        fallback.blit(text_surf, text_rect)
        return fallback

    def _camera_loop(self):
        """Background camera frame acquisition and MediaPipe hand detection."""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            with self.lock:
                self.camera_available = False
                self.error_message = "No webcam detected"
            return

        with self.lock:
            self.camera_available = True
            self.error_message = "Camera active. Show hand!"

        # Initialize MediaPipe Tasks HandLandmarker
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hand_landmarker.task")
        if not os.path.exists(model_path):
            model_path = "hand_landmarker.task"

        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            detector = vision.HandLandmarker.create_from_options(options)
        except Exception as e:
            with self.lock:
                self.camera_available = False
                self.error_message = f"Model error: {str(e)[:25]}"
            cap.release()
            return

        # Direction threshold (Wrist to index tip normalized distance)
        GESTURE_THRESHOLD = 0.12

        while self.running:
            ret, frame = cap.read()
            if not ret:
                with self.lock:
                    self.camera_available = False
                    self.error_message = "Failed to grab frame"
                time.sleep(0.05)
                continue

            # 1. Mirror the frame horizontally so it acts like a mirror
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape

            # 2. Convert to RGB for MediaPipe processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp_ms = int(time.time() * 1000)
            results = detector.detect_for_video(mp_image, timestamp_ms)

            detected_dir = None

            # 3. Analyze landmarks if a hand is detected
            if results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
                    # Draw connections
                    for connection in HAND_CONNECTIONS:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        
                        start_lm = hand_landmarks[start_idx]
                        end_lm = hand_landmarks[end_idx]
                        
                        start_point = (int(start_lm.x * w), int(start_lm.y * h))
                        end_point = (int(end_lm.x * w), int(end_lm.y * h))
                        
                        # Draw green/cyan skeleton lines on the RGB frame directly
                        cv2.line(rgb_frame, start_point, end_point, (0, 240, 255), 2)
                        
                    # Draw joint circles
                    for lm in hand_landmarks:
                        pt = (int(lm.x * w), int(lm.y * h))
                        cv2.circle(rgb_frame, pt, 4, (112, 0, 255), -1)

                    # Extract relevant landmarks for scale-invariant pointing calculation
                    wrist = hand_landmarks[0]
                    index_mcp = hand_landmarks[5]
                    index_tip = hand_landmarks[8]
                    middle_mcp = hand_landmarks[9]

                    # Displacement vector from index knuckle to finger tip
                    dx = index_tip.x - index_mcp.x
                    dy = index_tip.y - index_mcp.y
                    finger_len = (dx**2 + dy**2)**0.5
                    
                    # Calculate hand size (wrist to middle knuckle) for scale invariance
                    hand_size = ((middle_mcp.x - wrist.x)**2 + (middle_mcp.y - wrist.y)**2)**0.5
                    ratio = finger_len / max(0.01, hand_size)

                    # Draw index finger vector with a bold amber glow
                    mcp_pt = (int(index_mcp.x * w), int(index_mcp.y * h))
                    tip_pt = (int(index_tip.x * w), int(index_tip.y * h))
                    cv2.line(rgb_frame, mcp_pt, tip_pt, (255, 170, 0), 4)

                    # Only register direction if index finger is extended (ratio >= 0.45)
                    if ratio >= 0.45:
                        if abs(dx) > abs(dy):
                            # Horizontal movement
                            detected_dir = (1, 0) if dx > 0 else (-1, 0)
                        else:
                            # Vertical movement
                            detected_dir = (0, 1) if dy > 0 else (0, -1)


            # 4. Save results thread-safely
            with self.lock:
                self.current_direction = detected_dir
                
                # Resize using OpenCV which is faster
                resized_rgb = cv2.resize(rgb_frame, (WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT))
                
                # Convert RGB numpy array to Pygame Surface
                pg_surf = pygame.image.frombuffer(
                    resized_rgb.tobytes(), 
                    (WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT), 
                    "RGB"
                )
                self.preview_surface = pg_surf

            # Control capture rate (~30 FPS camera loop is plenty)
            time.sleep(0.03)

        # Cleanup
        cap.release()
        detector.close()


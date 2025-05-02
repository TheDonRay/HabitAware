import winsound
import threading
import time

class SoundManager:
    """
    Manages warning sound functionality with rate limiting and threading.
    """
    def __init__(self):
        """Initialize sound manager with default settings."""
        self.last_sound_time = 0
        self.sound_enabled = True

    def play_warning_sound(self):
        """Play a warning beep sound if enabled."""
        if not self.sound_enabled:
            return
        try:
            winsound.Beep(800, 500)
        except:
            pass  # Silently fail if sound can't be played

    def play_warning_sound_threaded(self):
        """Play warning sound in a separate thread with rate limiting."""
        current_time = time.time()
        if current_time - self.last_sound_time > 1.0:
            threading.Thread(target=self.play_warning_sound).start()
            self.last_sound_time = current_time

    def set_sound_enabled(self, enabled):
        """Enable or disable sound playback."""
        self.sound_enabled = enabled
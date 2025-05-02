import winsound
import threading
import time

class SoundManager:
    """
    Manages warning sound functionality for the application.
    This class handles playing warning sounds with rate limiting to prevent
    too frequent sound playback.
    """
    def __init__(self):
        """
        Initialize the sound manager with default settings.
        Sound is enabled by default and last sound time is set to 0.
        """
        self.last_sound_time = 0  # Track when the last sound was played
        self.sound_enabled = True  # Whether sounds are enabled

    def play_warning_sound(self):
        """
        Play a warning beep sound if sound is enabled.
        Uses Windows' built-in Beep function with a frequency of 800Hz
        and duration of 500ms.
        """
        if not self.sound_enabled:
            return
            
        try:
            winsound.Beep(800, 500)  # 800Hz frequency, 500ms duration
        except:
            pass  # Silently fail if sound can't be played

    def play_warning_sound_threaded(self):
        """
        Play a warning sound in a separate thread with rate limiting.
        This ensures the sound doesn't play too frequently (minimum 1 second
        between sounds) and doesn't block the main thread.
        """
        current_time = time.time()
        if current_time - self.last_sound_time > 1.0:  # Rate limit to 1 second
            threading.Thread(target=self.play_warning_sound).start()
            self.last_sound_time = current_time

    def set_sound_enabled(self, enabled):
        """
        Enable or disable sound playback.
        
        Args:
            enabled (bool): True to enable sounds, False to disable
        """
        self.sound_enabled = enabled
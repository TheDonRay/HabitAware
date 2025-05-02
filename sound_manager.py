import winsound
import threading
import time

class SoundManager:
    def __init__(self):
        self.last_sound_time = 0
        self.sound_enabled = True

    def play_warning_sound(self):
        if not self.sound_enabled:
            return
            
        try:
            winsound.Beep(800, 500)
        except:
            pass  # Silently fail if sound can't be played

    def play_warning_sound_threaded(self):
        current_time = time.time()
        if current_time - self.last_sound_time > 1.0:
            threading.Thread(target=self.play_warning_sound).start()
            self.last_sound_time = current_time

    def set_sound_enabled(self, enabled):
        self.sound_enabled = enabled
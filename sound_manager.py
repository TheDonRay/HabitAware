import threading
from playsound import playsound
import os

class SoundManager:
    def __init__(self):
        self.sound_enabled = True
        self.sound_thread = None
        self.warning_sound_path = os.path.join(os.path.dirname(__file__), "assets", "warning.wav")
        
        if not os.path.exists(os.path.dirname(self.warning_sound_path)):
            os.makedirs(os.path.dirname(self.warning_sound_path))
            
        if not os.path.exists(self.warning_sound_path):
            self._create_default_sound()

    def _create_default_sound(self):
        try:
            import numpy as np
            from scipy.io import wavfile
            
            sample_rate = 44100
            duration = 0.5
            frequency = 1000
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(frequency * t * 2 * np.pi)
            
            fade_samples = int(0.1 * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            note[:fade_samples] *= fade_in
            note[-fade_samples:] *= fade_out
            
            audio = note * 32767
            audio = audio.astype(np.int16)
            
            wavfile.write(self.warning_sound_path, sample_rate, audio)
        except ImportError:
            with open(self.warning_sound_path, 'wb') as f:
                f.write(b'')

    def set_sound_enabled(self, enabled):
        self.sound_enabled = enabled

    def play_warning_sound_threaded(self):
        if self.sound_enabled:
            if self.sound_thread is None or not self.sound_thread.is_alive():
                self.sound_thread = threading.Thread(target=self._play_sound)
                self.sound_thread.start()

    def _play_sound(self):
        try:
            playsound(self.warning_sound_path)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def cleanup(self):
        if self.sound_thread and self.sound_thread.is_alive():
            self.sound_thread.join()
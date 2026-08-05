from kivy.core.audio import SoundLoader

class AudioService:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.sounds = {}
        self.bg_music = None

    def play_sound(self, sound_name: str):
        if not self.sound_enabled:
            return
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def play_music(self):
        if self.music_enabled and self.bg_music:
            self.bg_music.loop = True
            self.bg_music.play()

    def stop_music(self):
        if self.bg_music:
            self.bg_music.stop()

    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = enabled

    def set_music_enabled(self, enabled: bool):
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
        else:
            self.play_music()

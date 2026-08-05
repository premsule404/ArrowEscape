import sys
import os

# Ensure shared engine can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from ui.menu_screen import MenuScreen
from ui.level_select import LevelSelectScreen
from ui.settings_screen import SettingsScreen
from ui.game_screen import GameScreen
from services.storage_service import StorageService
from services.api_service import ApiService
from services.audio_service import AudioService

class ArrowEscapeApp(App):
    def build(self):
        Window.clearcolor = (0.07, 0.09, 0.15, 1) # #111827 Dark theme
        
        # Initialize Services
        self.storage = StorageService()
        self.api = ApiService()
        self.audio = AudioService()
        
        # Setup ScreenManager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LevelSelectScreen(name='level_select'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(GameScreen(name='game'))
        
        return sm

    def on_pause(self):
        if hasattr(self, 'root') and self.root and self.root.has_screen('game'):
            game_screen = self.root.get_screen('game')
            if game_screen and hasattr(game_screen, 'engine'):
                game_screen.engine.pause()
        return True

    def on_resume(self):
        pass

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        header = BoxLayout(size_hint_y=None, height=50)
        btn_back = Button(text="< Back", size_hint=(None, 1), width=80)
        btn_back.bind(on_press=self.go_back)
        title = Label(text="Settings", font_size='24sp', bold=True)
        header.add_widget(btn_back)
        header.add_widget(title)
        
        # Audio setting
        sfx_box = BoxLayout(size_hint_y=None, height=50)
        sfx_box.add_widget(Label(text="Sound Effects", font_size='18sp'))
        sfx_switch = Switch(active=True)
        sfx_box.add_widget(sfx_switch)
        
        music_box = BoxLayout(size_hint_y=None, height=50)
        music_box.add_widget(Label(text="Background Music", font_size='18sp'))
        music_switch = Switch(active=True)
        music_box.add_widget(music_switch)
        
        layout.add_widget(header)
        layout.add_widget(sfx_box)
        layout.add_widget(music_box)
        layout.add_widget(BoxLayout()) # Spacer
        
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'menu'

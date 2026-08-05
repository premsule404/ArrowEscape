from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        title = Label(
            text="ARROW ESCAPE",
            font_size='36sp',
            bold=True,
            color=(0.31, 0.56, 0.97, 1), # #4F8EF7
            size_hint_y=0.4
        )
        
        btn_play = Button(
            text="PLAY GAME",
            font_size='20sp',
            size_hint=(1, None),
            height=60,
            background_color=(0.31, 0.56, 0.97, 1)
        )
        btn_play.bind(on_press=self.on_play)
        
        btn_levels = Button(
            text="LEVEL SELECT",
            font_size='18sp',
            size_hint=(1, None),
            height=50,
            background_color=(0.48, 0.38, 1.0, 1) # #7B61FF
        )
        btn_levels.bind(on_press=self.on_levels)
        
        btn_settings = Button(
            text="SETTINGS",
            font_size='18sp',
            size_hint=(1, None),
            height=50
        )
        btn_settings.bind(on_press=self.on_settings)
        
        layout.add_widget(title)
        layout.add_widget(btn_play)
        layout.add_widget(btn_levels)
        layout.add_widget(btn_settings)
        
        self.add_widget(layout)

    def on_play(self, instance):
        self.manager.current = 'game'

    def on_levels(self, instance):
        self.manager.current = 'level_select'

    def on_settings(self, instance):
        self.manager.current = 'settings'

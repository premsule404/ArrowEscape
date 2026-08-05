from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        self.add_widget(self.main_layout)

    def on_pre_enter(self, *args):
        self.refresh_ui()

    def refresh_ui(self):
        self.main_layout.clear_widgets()
        
        app = App.get_running_app()
        summary = app.storage.get_player_summary(total_levels=50) if hasattr(app, 'storage') else {
            "total_stars": 0, "max_stars": 150, "total_coins": 0, "completed_count": 0, "total_levels": 50
        }
        
        header = BoxLayout(size_hint_y=None, height=40)
        btn_back = Button(text="< Back", size_hint=(None, 1), width=75)
        btn_back.bind(on_press=self.go_back)
        title = Label(text="LEVEL SELECT (1-50)", font_size='20sp', bold=True)
        header.add_widget(btn_back)
        header.add_widget(title)
        
        summary_bar = BoxLayout(size_hint_y=None, height=35, padding=2, spacing=8)
        lbl_stars = Label(
            text=f"[color=ffcc00]STARS: {summary['total_stars']}/{summary['max_stars']}[/color]",
            font_size='14sp', bold=True, markup=True
        )
        lbl_coins = Label(
            text=f"[color=ffcc00]COINS: {summary['total_coins']}[/color]",
            font_size='14sp', bold=True, markup=True
        )
        lbl_progress = Label(
            text=f"[color=38bdf8]COMPLETED: {summary['completed_count']}/{summary['total_levels']}[/color]",
            font_size='13sp', bold=True, markup=True
        )
        summary_bar.add_widget(lbl_stars)
        summary_bar.add_widget(lbl_coins)
        summary_bar.add_widget(lbl_progress)
        
        grid = GridLayout(cols=5, spacing=5, padding=2)
        
        for level_num in range(1, 51):
            is_unlocked = (level_num == 1)
            prog = {"completed": False, "best_stars": 0}
            
            if hasattr(app, 'storage'):
                prog = app.storage.get_level_progress(level_num)
                prev_prog = app.storage.get_level_progress(level_num - 1) if level_num > 1 else {"completed": True}
                if level_num > 1 and prev_prog.get("completed", False):
                    is_unlocked = True
                    
            if is_unlocked:
                stars_count = prog.get("best_stars", 0)
                card_text = f"Lvl {level_num}\n[color=ffcc00]{stars_count}/3 STARS[/color]"
                bg_color = (0.2, 0.45, 0.85, 1) if prog.get("completed", False) else (0.31, 0.56, 0.97, 1)
            else:
                card_text = f"Lvl {level_num}\n[color=888888][LOCKED][/color]"
                bg_color = (0.2, 0.25, 0.35, 1)
                
            btn = Button(
                text=card_text,
                font_size='10sp',
                markup=True,
                halign='center',
                valign='middle',
                size_hint=(1, None),
                height=42,
                background_color=bg_color,
                disabled=not is_unlocked
            )
            btn.level_num = level_num
            btn.bind(on_press=self.select_level)
            grid.add_widget(btn)
            
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(summary_bar)
        self.main_layout.add_widget(grid)

    def go_back(self, instance):
        self.manager.current = 'menu'

    def select_level(self, instance):
        game_screen = self.manager.get_screen('game')
        game_screen.load_level_number(instance.level_num)
        self.manager.current = 'game'

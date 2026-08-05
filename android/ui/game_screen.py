import os
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.app import App

from shared.engine.engine import GameEngine
from shared.engine.constants import GameState
from shared.engine.level_parser import LevelParser
from .board_widget import GameBoardWidget

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.engine = GameEngine()
        self.current_level = 1
        self.timer_event = None
        self.active_popup = None
        self.has_claimed_reward = False
        
        layout = BoxLayout(orientation='vertical')
        
        # HUD Top Bar: Pause Button, Level Title, Progress, Lives, Timer, Moves
        header = BoxLayout(size_hint_y=0.12, padding=8, spacing=6)
        
        btn_pause = Button(
            text="||",
            font_size='22sp',
            bold=True,
            size_hint_x=0.14,
            background_color=(0.3, 0.45, 0.65, 1)
        )
        btn_pause.bind(on_press=self.on_pause_button)
        
        self.lbl_title = Label(text="Lvl 1", font_size='16sp', bold=True, size_hint_x=0.20)
        self.lbl_progress = Label(text="0/0", font_size='14sp', color=(0.7, 0.8, 1, 1), size_hint_x=0.16)
        self.lbl_hearts = Label(text="[color=ff3344]LIVES: 3/3[/color]", font_size='15sp', bold=True, markup=True, size_hint_x=0.22)
        self.lbl_timer = Label(text="TIME: 00:00", font_size='15sp', bold=True, color=(1, 0.85, 0.3, 1), size_hint_x=0.20)
        self.lbl_moves = Label(text="M:0", font_size='14sp', color=(0.8, 0.8, 0.8, 1), size_hint_x=0.12)
        
        header.add_widget(btn_pause)
        header.add_widget(self.lbl_title)
        header.add_widget(self.lbl_progress)
        header.add_widget(self.lbl_hearts)
        header.add_widget(self.lbl_timer)
        header.add_widget(self.lbl_moves)
        
        # Board Widget
        self.board_widget = GameBoardWidget(self.engine, size_hint_y=0.78)
        
        # Footer
        footer = BoxLayout(size_hint_y=0.10, padding=8, spacing=8)
        btn_undo = Button(text="Undo", font_size='16sp')
        btn_undo.bind(on_press=self.on_undo)
        btn_restart = Button(text="Restart", font_size='16sp')
        btn_restart.bind(on_press=self.on_restart)
        
        footer.add_widget(btn_undo)
        footer.add_widget(btn_restart)
        
        layout.add_widget(header)
        layout.add_widget(self.board_widget)
        layout.add_widget(footer)
        
        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.load_level_number(self.current_level)

    def on_leave(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def update_hud(self):
        h = max(0, min(3, self.engine.hearts))
        self.lbl_hearts.text = f"[color=ff3344]LIVES: {h}/3[/color]"
        
        secs = int(math.ceil(self.engine.time_remaining))
        mins = secs // 60
        secs_rem = secs % 60
        self.lbl_timer.text = f"TIME: {mins:02d}:{secs_rem:02d}"
        
        remaining = len(self.engine.board.arrows) if self.engine.board else 0
        total = self.engine.total_arrows_count
        self.lbl_progress.text = f"{total - remaining}/{total}"
        self.lbl_moves.text = f"M:{self.engine.moves_count}"

    def on_timer_tick(self, dt):
        if self.engine.state == GameState.PLAYING:
            self.engine.tick_timer(dt)
        self.update_hud()

    def start_attempt(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            
        if self.active_popup:
            self.active_popup.dismiss()
            self.active_popup = None
            
        self.has_claimed_reward = False
        self.engine.restart()
        
        self.timer_event = Clock.schedule_interval(self.on_timer_tick, 0.1)
        
        self.update_hud()
        self.board_widget.update_board()

    def show_color_confusion_tutorial(self, storage):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text="COLOR CONFUSION MODE!",
            font_size='22sp', bold=True, color=(1, 0.85, 0.2, 1)
        ))
        content.add_widget(Label(
            text="Arrow colors are now randomized.\nFollow the ARROW DIRECTION, not its color!",
            font_size='16sp', halign='center', color=(0.9, 0.9, 0.9, 1)
        ))
        
        btn_dismiss = Button(
            text="GOT IT!",
            size_hint_y=None, height=50,
            font_size='18sp', bold=True,
            background_color=(0.2, 0.78, 0.4, 1)
        )
        content.add_widget(btn_dismiss)
        
        popup = Popup(title="New Mechanic Unlocked", content=content, size_hint=(0.88, 0.52), auto_dismiss=False)
        
        def dismiss_tutorial(inst):
            storage.set_setting("color_tutorial_dismissed", True)
            popup.dismiss()
            
        btn_dismiss.bind(on_press=dismiss_tutorial)
        popup.open()

    def load_level_number(self, level_num: int):
        self.current_level = level_num
        
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        level_file = os.path.join(root_dir, "levels", f"level{level_num:03d}.json")
        
        if os.path.exists(level_file):
            new_engine, metadata = LevelParser.load_from_file(level_file)
            self.engine = new_engine
            self.engine.events.add_listener("on_win", self.on_win)
            self.engine.events.add_listener("on_wrong_move", self.on_wrong_move)
            self.engine.events.add_listener("on_game_over", self.on_game_over)
            self.engine.events.add_listener("on_pause", self.on_engine_pause)
            self.engine.events.add_listener("on_resume", self.on_engine_resume)
            self.board_widget.engine = new_engine
            self.lbl_title.text = f"Lvl {level_num}"
            
            self.start_attempt()
            
            if level_num >= 31:
                app = App.get_running_app()
                if hasattr(app, 'storage') and not app.storage.get_setting("color_tutorial_dismissed", False):
                    self.show_color_confusion_tutorial(app.storage)

    def on_pause_button(self, instance):
        if self.engine.state in (GameState.PLAYING, GameState.READY):
            self.engine.pause()

    def on_engine_pause(self, data=None):
        if self.active_popup:
            return
            
        content = BoxLayout(orientation='vertical', padding=20, spacing=12)
        content.add_widget(Label(text="GAME PAUSED", font_size='26sp', bold=True, color=(1, 0.85, 0.3, 1)))
        
        btn_resume = Button(text="> RESUME", font_size='18sp', bold=True, size_hint_y=None, height=48, background_color=(0.2, 0.78, 0.4, 1))
        btn_restart = Button(text="RESTART", font_size='18sp', bold=True, size_hint_y=None, height=48, background_color=(0.95, 0.5, 0.2, 1))
        btn_exit = Button(text="EXIT LEVEL", font_size='18sp', bold=True, size_hint_y=None, height=48, background_color=(0.8, 0.3, 0.3, 1))
        
        content.add_widget(btn_resume)
        content.add_widget(btn_restart)
        content.add_widget(btn_exit)
        
        self.active_popup = Popup(title="Pause Menu", content=content, size_hint=(0.85, 0.55), auto_dismiss=False)
        
        def resume_game(inst):
            self.active_popup.dismiss()
            self.active_popup = None
            self.engine.resume()
            
        def restart_game(inst):
            self.start_attempt()
            
        def exit_game(inst):
            self.go_level_select(inst)

        btn_resume.bind(on_press=resume_game)
        btn_restart.bind(on_press=restart_game)
        btn_exit.bind(on_press=exit_game)
        self.active_popup.open()

    def on_engine_resume(self, data=None):
        pass

    def go_level_select(self, instance=None):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        if self.active_popup:
            self.active_popup.dismiss()
            self.active_popup = None
        self.manager.current = 'level_select'

    def on_undo(self, instance):
        if self.engine.undo():
            self.update_hud()
            self.board_widget.update_board()

    def on_restart(self, instance=None):
        self.start_attempt()

    def on_wrong_move(self, data):
        self.update_hud()

    def on_game_over(self, data):
        reason = data.get("reason", "out_of_hearts")
        title = "Out of Hearts!" if reason == "out_of_hearts" else "Time's Up!"
        message = "No hearts left!" if reason == "out_of_hearts" else "You ran out of time!"
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=title, font_size='24sp', bold=True, color=(0.95, 0.3, 0.3, 1)))
        content.add_widget(Label(text=message, font_size='16sp'))
        
        btn_restart = Button(
            text="Restart Level",
            size_hint_y=None,
            height=50,
            font_size='18sp',
            background_color=(0.95, 0.3, 0.3, 1)
        )
        content.add_widget(btn_restart)
        
        self.active_popup = Popup(title="Game Over", content=content, size_hint=(0.85, 0.45), auto_dismiss=False)
        
        def restart_level(inst):
            self.start_attempt()

        btn_restart.bind(on_press=restart_level)
        self.active_popup.open()

    def on_win(self, data=None):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            
        stars = data.get("stars", 3) if data else self.engine.stars_earned
        elapsed = data.get("elapsed_time", 0.1) if data else self.engine.elapsed_time
        base_coins = data.get("base_coins", 100) if data else self.engine.base_coins
        
        app = App.get_running_app()
        save_res = {}
        if hasattr(app, 'storage'):
            save_res = app.storage.save_level_progress(
                level_id=self.current_level,
                stars=stars,
                moves=self.engine.moves_count,
                time=elapsed,
                base_coins=base_coins
            )
            
        inc_coins = save_res.get("incremental_coins", 0)
        earned_coins = save_res.get("earned_coins", data.get("coins", 100) if data else 100)
        run_time = save_res.get("time", elapsed)
        best_time = save_res.get("best_time", run_time)
        is_new_best = save_res.get("is_new_best", False)
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        content.add_widget(Label(text=f"LEVEL {self.current_level}", font_size='16sp', color=(0.8, 0.9, 1, 1)))
        content.add_widget(Label(text="LEVEL COMPLETED!", font_size='22sp', bold=True, color=(0.2, 0.85, 0.4, 1)))
        
        if stars == 3:
            star_label = "[color=ffcc00]★★★ THREE STARS (3/3)[/color]"
        elif stars == 2:
            star_label = "[color=ffcc00]★★☆ TWO STARS (2/3)[/color]"
        elif stars == 1:
            star_label = "[color=ffcc00]★☆☆ ONE STAR (1/3)[/color]"
        else:
            star_label = "[color=888888]☆☆☆ ZERO STARS (0/3)[/color]"
            
        content.add_widget(Label(text=star_label, font_size='20sp', bold=True, markup=True))
        
        time_text = f"Time: {run_time:.1f}s | Best: {best_time:.1f}s"
        if is_new_best:
            time_text += " [color=ffcc00][NEW BEST!][/color]"
        content.add_widget(Label(text=time_text, font_size='15sp', markup=True, color=(0.9, 0.9, 0.9, 1)))
        
        if inc_coins > 0:
            coin_str = f"[color=ffcc00]+{inc_coins} COINS[/color]"
        else:
            coin_str = f"[color=ffcc00]+{earned_coins} COINS[/color] [color=888888](Best Claimed)[/color]"
        content.add_widget(Label(text=coin_str, font_size='18sp', bold=True, markup=True))
        
        btn_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=135)
        
        btn_continue = Button(text="> CONTINUE", font_size='16sp', bold=True, background_color=(0.2, 0.78, 0.4, 1))
        btn_replay = Button(text="REPLAY LEVEL", font_size='16sp', bold=True, background_color=(0.31, 0.56, 0.97, 1))
        btn_select = Button(text="LEVEL SELECT", font_size='16sp', bold=True, background_color=(0.5, 0.5, 0.6, 1))
        
        btn_box.add_widget(btn_continue)
        btn_box.add_widget(btn_replay)
        btn_box.add_widget(btn_select)
        
        content.add_widget(btn_box)
        
        self.active_popup = Popup(title="Level Complete!", content=content, size_hint=(0.88, 0.72), auto_dismiss=False)
        
        def continue_to_next(inst):
            if self.active_popup:
                self.active_popup.dismiss()
                self.active_popup = None
            next_num = 1 if self.current_level >= 50 else self.current_level + 1
            self.load_level_number(next_num)

        def replay_current(inst):
            self.start_attempt()

        def select_level(inst):
            self.go_level_select(inst)

        btn_continue.bind(on_press=continue_to_next)
        btn_replay.bind(on_press=replay_current)
        btn_select.bind(on_press=select_level)
        self.active_popup.open()

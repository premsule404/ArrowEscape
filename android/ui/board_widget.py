from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock
import math
from shared.engine.models import Position

COLOR_THEME_MAP = {
    "red": (0.9, 0.25, 0.25),
    "blue": (0.2, 0.6, 0.9),
    "green": (0.2, 0.8, 0.25),
    "orange": (0.95, 0.55, 0.1),
    "yellow": (0.9, 0.85, 0.15),
    "purple": (0.65, 0.3, 0.85),
    "cyan": (0.1, 0.8, 0.85),
    "gold": (1.0, 0.84, 0.0),
    "black": (0.08, 0.08, 0.12)
}

class GameBoardWidget(Widget):
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        self.shaking_arrow_id = None
        self.shake_step = 0
        self.shake_event = None
        self.animating_arrows = []
        self.slide_event = None

    def update_canvas(self, *args):
        self.update_board()

    def shake_tick(self, dt):
        self.shake_step += 1
        self.update_board()
        if self.shake_step >= 6:
            self.shaking_arrow_id = None
            if self.shake_event:
                self.shake_event.cancel()
                self.shake_event = None
            self.update_board()

    def slide_anim_tick(self, dt):
        w, h = self.size
        px, py = self.pos
        speed = self.cell_size * 22.0 * dt
        
        finished = []
        for anim in self.animating_arrows:
            anim['ax'] += anim['dx'] * speed
            anim['ay'] += anim['kivy_dy'] * speed
            
            if (anim['ax'] < px - self.cell_size * 2 or 
                anim['ax'] > px + w + self.cell_size * 2 or 
                anim['ay'] < py - self.cell_size * 2 or 
                anim['ay'] > py + h + self.cell_size * 2):
                finished.append(anim)
                
        for f in finished:
            if f in self.animating_arrows:
                self.animating_arrows.remove(f)
                
        self.update_board()
        
        if not self.animating_arrows:
            if self.slide_event:
                self.slide_event.cancel()
                self.slide_event = None

    def draw_single_arrow(self, ax, ay, dx, dy, is_shaking=False, color_theme="default", is_black_master=False, is_golden_master=False):
        is_black = is_black_master or (color_theme == "black")
        is_gold = is_golden_master or (color_theme == "gold")
        
        # Soft outer aura glow for Master Arrows
        if is_black and not is_shaking:
            Color(0.85, 0.85, 0.95, 0.5) # Soft silver/blue contrast aura
            RoundedRectangle(
                pos=(ax - dp(3), ay - dp(3)),
                size=(self.cell_size, self.cell_size),
                radius=[dp(8)]
            )
        elif is_gold and not is_shaking:
            Color(1.0, 0.9, 0.2, 0.45)
            RoundedRectangle(
                pos=(ax - dp(3), ay - dp(3)),
                size=(self.cell_size, self.cell_size),
                radius=[dp(8)]
            )
            
        if is_shaking:
            Color(0.95, 0.25, 0.25, 1) # Red on wrong move / blocked shake
        elif is_black:
            Color(0.06, 0.06, 0.09, 1) # Black Master - Sleek Obsidian Black
        elif is_gold:
            Color(1.0, 0.84, 0.0, 1) # Golden Master - Radiant Gold
        elif color_theme and color_theme in COLOR_THEME_MAP:
            r, g, b = COLOR_THEME_MAP[color_theme]
            Color(r, g, b, 1)
        elif dx == 1: Color(0.9, 0.2, 0.2, 1) # Right - Red
        elif dx == -1: Color(0.2, 0.6, 0.9, 1) # Left - Blue
        elif dy == 1: Color(0.2, 0.8, 0.2, 1) # Down - Green
        else: Color(0.9, 0.6, 0.1, 1) # Up - Orange
        
        RoundedRectangle(
            pos=(ax, ay),
            size=(self.cell_size - 6, self.cell_size - 6),
            radius=[dp(6)]
        )
        
        # Draw Arrow Pointer (Chevron & Shaft)
        Color(1, 1, 1, 1)
        cx = ax + (self.cell_size - 6) / 2
        cy = ay + (self.cell_size - 6) / 2
        
        kivy_dy = -dy # Invert Y vector for Kivy rendering
        
        s = (self.cell_size - 6) * 0.28
        px_vec = -kivy_dy
        py_vec = dx
        
        tip_x = cx + dx * s
        tip_y = cy + kivy_dy * s
        left_x = cx - dx * (s * 0.5) + px_vec * (s * 0.5)
        left_y = cy - kivy_dy * (s * 0.5) + py_vec * (s * 0.5)
        right_x = cx - dx * (s * 0.5) - px_vec * (s * 0.5)
        right_y = cy - kivy_dy * (s * 0.5) - py_vec * (s * 0.5)
        
        line_w = dp(4) if (is_black or is_gold) else dp(3)
        # Shaft line
        Line(points=[cx - dx * (s * 0.7), cy - kivy_dy * (s * 0.7), tip_x, tip_y], width=line_w)
        # Pointer Chevron
        Line(points=[left_x, left_y, tip_x, tip_y, right_x, right_y], width=line_w)

    def update_board(self):
        self.canvas.clear()
        
        if not self.engine.board:
            return
            
        board = self.engine.board
        
        w, h = self.size
        px, py = self.pos
        
        margin = dp(15)
        usable_w = w - (margin * 2)
        usable_h = h - (margin * 2)
        
        self.cell_size = min(usable_w / board.width, usable_h / board.height)
        
        self.offset_x = px + (w - (self.cell_size * board.width)) / 2
        self.offset_y = py + (h - (self.cell_size * board.height)) / 2
        
        with self.canvas:
            Color(0.18, 0.18, 0.22, 1)
            RoundedRectangle(
                pos=(self.offset_x - 8, self.offset_y - 8),
                size=(self.cell_size * board.width + 16, self.cell_size * board.height + 16),
                radius=[dp(8)]
            )
            
            for y in range(board.height):
                for x in range(board.width):
                    Color(0.12, 0.12, 0.14, 1)
                    RoundedRectangle(
                        pos=(self.offset_x + x * self.cell_size + 1, self.offset_y + y * self.cell_size + 1),
                        size=(self.cell_size - 2, self.cell_size - 2),
                        radius=[dp(4)]
                    )
            
            for arrow_id, arrow in board.arrows.items():
                dx, dy = arrow.direction.value
                is_shaking = (arrow_id == self.shaking_arrow_id)
                
                ax = self.offset_x + arrow.position.x * self.cell_size + 3
                ay = self.offset_y + (board.height - 1 - arrow.position.y) * self.cell_size + 3 
                
                if is_shaking:
                    shake_offset = (1 if self.shake_step % 2 == 1 else -1) * dp(5)
                    if dx != 0:
                        ax += shake_offset
                    else:
                        ay += shake_offset
                
                self.draw_single_arrow(
                    ax, ay, dx, dy, is_shaking,
                    color_theme=arrow.color_theme,
                    is_black_master=getattr(arrow, 'is_black_master', False),
                    is_golden_master=getattr(arrow, 'is_golden_master', False)
                )
                
            for anim in self.animating_arrows:
                self.draw_single_arrow(
                    anim['ax'], anim['ay'], anim['dx'], anim['dy'], False,
                    color_theme=anim.get('color_theme', 'default'),
                    is_black_master=anim.get('is_black_master', False),
                    is_golden_master=anim.get('is_golden_master', False)
                )
                
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
            
        board = self.engine.board
        if not board:
            return False
            
        tx, ty = touch.pos
        rel_x = tx - self.offset_x
        rel_y = ty - self.offset_y
        
        if 0 <= rel_x <= board.width * self.cell_size and 0 <= rel_y <= board.height * self.cell_size:
            grid_x = int(rel_x / self.cell_size)
            kivy_grid_y = int(rel_y / self.cell_size)
            grid_y = board.height - 1 - kivy_grid_y
            
            arrow = board.get_arrow_at(Position(grid_x, grid_y))
            
            if arrow:
                dx, dy = arrow.direction.value
                ax = self.offset_x + arrow.position.x * self.cell_size + 3
                ay = self.offset_y + (board.height - 1 - arrow.position.y) * self.cell_size + 3
                
                success = self.engine.tap_arrow(arrow.id)
                if success:
                    self.animating_arrows.append({
                        'id': arrow.id,
                        'ax': ax,
                        'ay': ay,
                        'dx': dx,
                        'dy': dy,
                        'kivy_dy': -dy,
                        'color_theme': arrow.color_theme,
                        'is_black_master': getattr(arrow, 'is_black_master', False),
                        'is_golden_master': getattr(arrow, 'is_golden_master', False)
                    })
                    if not self.slide_event:
                        self.slide_event = Clock.schedule_interval(self.slide_anim_tick, 1/60.0)
                    self.update_board()
                else:
                    self.shaking_arrow_id = arrow.id
                    self.shake_step = 0
                    if self.shake_event:
                        self.shake_event.cancel()
                    self.shake_event = Clock.schedule_interval(self.shake_tick, 0.04)
                return True
                
        return super().on_touch_down(touch)

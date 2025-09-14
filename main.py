from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.window import Window
import json
import os
from datetime import datetime

Window.size = (800, 600)

# Variables globales
touch_counter = 0
bar_direction = 1
bar_pos = 100
current_level = 1
bar_speed = 4
optimal_zone_start = 0.45
optimal_zone_end = 0.55
current_leg = "right"
score_file = "scores.json"
ball_y = 260
ball_ascending = False
ball_descending = False
ball_speed = 1.5

def save_score(points, level):
    if not os.path.exists(score_file):
        with open(score_file, 'w') as f:
            json.dump([], f)
    with open(score_file, 'r') as f:
        data = json.load(f)
    data.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": f"Level {level}",
        "touches": points
    })
    with open(score_file, 'w') as f:
        json.dump(data, f, indent=4)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Freestyle Football Touches", font_size=32, pos_hint={"center_x":0.5, "center_y":0.8}))
        play_btn = Button(text="Play", pos_hint={"center_x":0.5, "center_y":0.6}, size_hint=(0.3, 0.1))
        scores_btn = Button(text="Scores", pos_hint={"center_x":0.5, "center_y":0.45}, size_hint=(0.3, 0.1))
        quit_btn = Button(text="Quit", pos_hint={"center_x":0.5, "center_y":0.3}, size_hint=(0.3, 0.1))
        play_btn.bind(on_release=self.go_to_level)
        scores_btn.bind(on_release=self.go_to_scores)
        quit_btn.bind(on_release=self.quit_app)
        self.add_widget(play_btn)
        self.add_widget(scores_btn)
        self.add_widget(quit_btn)

    def go_to_level(self, instance):
        self.manager.current = "level"

    def go_to_scores(self, instance):
        self.manager.current = "scores"

    def quit_app(self, instance):
        App.get_running_app().stop()

class LevelMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Select Level", font_size=32, pos_hint={"center_x":0.5, "center_y":0.8}))
        for idx, y in enumerate([0.6, 0.45, 0.3], start=1):
            btn = Button(text=f"Level {idx}", pos_hint={"center_x":0.5, "center_y":y}, size_hint=(0.3, 0.1))
            btn.bind(on_release=lambda btn, idx=idx: self.start_game(idx))
            self.add_widget(btn)

    def start_game(self, level):
        global bar_speed, ball_speed, current_level, touch_counter, bar_pos, ball_y, bar_direction, ball_ascending, ball_descending, current_leg
        current_level = level
        if level == 1:
            bar_speed = 4
            ball_speed = 0.3
        elif level == 2:
            bar_speed = 6
            ball_speed = 0.6
        elif level == 3:
            bar_speed = 8
            ball_speed = 0.9
        touch_counter = 0
        bar_pos = 100
        ball_y = 260
        bar_direction = 1
        ball_ascending = False
        ball_descending = False
        current_leg = "right"
        self.manager.current = "playing"

class PlayingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas_widget = GameCanvas()
        self.add_widget(self.canvas_widget)

        # Botón Touch debajo del stickman
        self.touch_button = Button(text="Touch", size_hint=(None, None), size=(150, 50), pos=(325, 100))
        self.touch_button.bind(on_release=self.canvas_widget.touch_ball)
        self.add_widget(self.touch_button)

    def on_pre_enter(self):
        self.canvas_widget.start()

class GameCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text="Touches: 0", pos=(20, 520), font_size=24)
        self.add_widget(self.label)
        Window.bind(on_key_down=self._on_keyboard_down)

    def start(self):
        Clock.schedule_interval(self.update, 1/60)

    def stop(self):
        Clock.unschedule(self.update)

    def update(self, dt):
        global bar_pos, bar_direction, ball_y, ball_ascending, ball_descending, touch_counter
        bar_pos += bar_speed * bar_direction
        if bar_pos >= 700 or bar_pos <= 100:
            bar_direction *= -1

        if ball_ascending:
            ball_y += ball_speed
            if ball_y >= 290:
                ball_ascending = False
                ball_descending = True
        elif ball_descending:
            ball_y -= ball_speed
            if ball_y <= 260:
                ball_descending = False

        self.label.text = f"Touches: {touch_counter}"

        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0)
            Rectangle(pos=(0, 0), size=(800, 600))

            self.draw_stickman(400, 300, current_leg)

            Color(0.678, 0.847, 0.902)
            Line(rectangle=(100, 500, 600, 20), width=2)
            Line(points=[bar_pos, 490, bar_pos, 530], width=3)

            Color(1, 0, 0)
            zone_start = 100 + (600 * optimal_zone_start)
            zone_end = 100 + (600 * optimal_zone_end)
            Rectangle(pos=(zone_start, 500), size=(zone_end - zone_start, 20))

            Color(1, 1, 1)
            Ellipse(pos=(390, ball_y - 70), size=(20, 20))

            # Contador
            Color(1, 1, 1)
            Label(text=f"Touches: {touch_counter}", pos=(20, 10))

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if text == " ":
            self.touch_ball(None)

    def touch_ball(self, instance):
        global touch_counter, ball_ascending, ball_descending, current_leg
        pos_norm = (bar_pos - 100) / 600
        if optimal_zone_start <= pos_norm <= optimal_zone_end:
            # Si está dentro de la zona roja, sumar un toque
            touch_counter += 1
            current_leg = "left" if current_leg == "right" else "right"
            ball_ascending = True
            ball_descending = False
        else:
            # Si está fuera de la zona roja, game over
            save_score(touch_counter, current_level)
            self.stop()
            self.parent.manager.current = "finished"

    def draw_stickman(self, x, y, leg):
        Color(1, 1, 1)
        Ellipse(pos=(x-20, y+30), size=(40, 40))  # Cabeza
        Line(points=[x, y+30, x, y-50], width=3)  # Cuerpo

        # Brazos pegados al cuerpo y apuntando hacia abajo
        Line(points=[x, y, x-10, y-30], width=3)
        Line(points=[x, y, x+10, y-30], width=3)

        # Piernas alternadas
        if leg == "right":
            Line(points=[x, y-50, x+20, y-100], width=3)
            Line(points=[x, y-50, x-10, y-100], width=3)
        else:
            Line(points=[x, y-50, x-20, y-100], width=3)
            Line(points=[x, y-50, x+10, y-100], width=3)

class FinishedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text="", font_size=24, pos_hint={"center_x":0.5, "center_y":0.6})
        self.add_widget(self.label)
        back_btn = Button(text="Back to Menu", pos_hint={"center_x":0.5, "center_y":0.4}, size_hint=(0.3, 0.1))
        back_btn.bind(on_release=self.back_to_menu)
        self.add_widget(back_btn)

    def on_pre_enter(self):
        self.label.text = f"Game Over!\nScore: {touch_counter}"

    def back_to_menu(self, instance):
        self.manager.current = "main"

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
import json
import os

class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # ScrollView
        self.scroll = ScrollView(size_hint=(1, 0.8), bar_width=10)
        self.label_container = BoxLayout(size_hint_y=None, orientation='vertical')
        self.score_label = Label(text="", font_size=18, halign='left', valign='top', size_hint_y=None)
        self.score_label.bind(texture_size=self.update_label_height)
        self.score_label.text_size = (760, None)

        self.label_container.add_widget(self.score_label)
        self.scroll.add_widget(self.label_container)
        layout.add_widget(self.scroll)

        # Botón para volver
        back_btn = Button(text="Back to Menu", size_hint=(0.3, 0.1), pos_hint={"center_x": 0.5})
        back_btn.bind(on_release=self.back_to_menu)
        layout.add_widget(back_btn)

        self.add_widget(layout)

        Window.bind(on_key_down=self.on_key_down)

    def update_label_height(self, *args):
        self.score_label.height = self.score_label.texture_size[1]
        self.label_container.height = self.score_label.height

    def on_pre_enter(self):
        scores = []
        if os.path.exists(score_file):
            with open(score_file, 'r') as f:
                scores = json.load(f)
        sorted_scores = sorted(scores, key=lambda x: x["touches"], reverse=True)
        score_text = "\n".join([f"{s['date']} - {s['level']} - {s['touches']} touches" for s in sorted_scores])
        self.score_label.text = score_text if score_text else "No scores yet"
        self.scroll.scroll_y = 1  # Mostrar desde arriba

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        # Arriba: 273, Abajo: 274, PageUp: 280, PageDown: 281
        if self.manager.current != "scores":
            return

        step = 0.05
        if key == 273:  # Flecha arriba
            self.scroll.scroll_y = min(self.scroll.scroll_y + step, 1)
        elif key == 274:  # Flecha abajo
            self.scroll.scroll_y = max(self.scroll.scroll_y - step, 0)
        elif key == 280:  # Page Up
            self.scroll.scroll_y = min(self.scroll.scroll_y + 0.3, 1)
        elif key == 281:  # Page Down
            self.scroll.scroll_y = max(self.scroll.scroll_y - 0.3, 0)

    def back_to_menu(self, instance):
        self.manager.current = "main"

class FreestyleApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(LevelMenu(name="level"))
        sm.add_widget(PlayingScreen(name="playing"))
        sm.add_widget(FinishedScreen(name="finished"))
        sm.add_widget(ScoreScreen(name="scores"))
        return sm

if __name__ == "__main__":
    FreestyleApp().run()

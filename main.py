from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider


PARTS = {
    "Câmera 4K": ("Sensor 1/2, 4K/60fps", "Gimbal 3 eixos", "OK"),
    "Motor M1": ("Brushless 1500 KV", "15,8 × 2,4 cm", "98%"),
    "Motor M2": ("Brushless 1500 KV", "15,8 × 2,4 cm", "96%"),
    "Motor M3": ("Brushless 1500 KV", "15,8 × 2,4 cm", "97%"),
    "Motor M4": ("Brushless 1500 KV", "15,8 × 2,4 cm", "99%"),
    "Bateria LiPo": ("LiPo 6S · 22,2V", "5200 mAh", "86%"),
    "GPS / GNSS": ("Módulo multibanda", "12 satélites", "FIX"),
    "Controladores ESC": ("4 × 40A BLHeli", "Entrada 6S", "OK"),
    "LED de estado": ("RGB com aviso", "Posição / emergência", "OK"),
}


class DroneCanvas(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotor_angle = 0
        self.bind(pos=self.draw, size=self.draw)

    def draw(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.08, 0.12, 0.13)
            Rectangle(pos=self.pos, size=self.size)
            cx = self.center_x
            cy = self.center_y
            scale = min(self.width / 700, self.height / 430)
            arm_len = 145 * scale

            Color(0.22, 0.28, 0.29)
            for ax, ay in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                mx = cx + ax * arm_len * 0.72
                my = cy + ay * arm_len * 0.48
                Line(points=[cx, cy, mx, my], width=max(4 * scale, 1))

            Color(0.16, 0.22, 0.23)
            RoundedRectangle(pos=(cx - 75 * scale, cy - 58 * scale), size=(150 * scale, 116 * scale), radius=[22 * scale])
            Color(0.85, 0.91, 0.91)
            RoundedRectangle(pos=(cx - 58 * scale, cy - 46 * scale), size=(116 * scale, 92 * scale), radius=[18 * scale])
            Color(0.08, 0.12, 0.13)
            RoundedRectangle(pos=(cx - 20 * scale, cy - 28 * scale), size=(40 * scale, 56 * scale), radius=[14 * scale])
            Color(0.65, 0.96, 0.05)
            Ellipse(pos=(cx - 8 * scale, cy - 3 * scale), size=(16 * scale, 16 * scale))

            for ax, ay in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                mx = cx + ax * arm_len * 0.72
                my = cy + ay * arm_len * 0.48
                Color(0.65, 0.72, 0.72, 0.18)
                Ellipse(pos=(mx - 66 * scale, my - 9 * scale), size=(132 * scale, 18 * scale))
                Color(0.10, 0.15, 0.16)
                Ellipse(pos=(mx - 18 * scale, my - 18 * scale), size=(36 * scale, 36 * scale))
                Color(0.65, 0.72, 0.72, 0.7)
                Ellipse(pos=(mx - 5 * scale, my - 5 * scale), size=(10 * scale, 10 * scale))

    def rotate_motors(self, dt):
        self.rotor_angle = (self.rotor_angle + 20) % 360
        self.draw()


class NovaDroneApp(App):
    def build(self):
        self.flying = False
        self.altitude = 42.8
        self.speed = 18.4
        self.battery = 86

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        root.canvas.before.clear()

        header = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        header.add_widget(Label(text="[NOVA][X1]", markup=True, bold=True, size_hint_x=.3))
        self.status = Label(text="SISTEMA ONLINE", color=(0.65, 0.96, 0.05, 1))
        header.add_widget(self.status)
        self.header_flight = Label(text="ALT 42.8 m  |  VEL 18.4 m/s", halign="right")
        header.add_widget(self.header_flight)
        root.add_widget(header)

        body = BoxLayout(spacing=dp(8))
        left = BoxLayout(orientation="vertical", size_hint_x=.24, spacing=dp(6))
        left.add_widget(Label(text="CONTROLE DE VOO", size_hint_y=None, height=dp(30)))
        self.throttle = Slider(min=0, max=100, value=68)
        self.pitch = Slider(min=-30, max=30, value=12)
        self.yaw = Slider(min=0, max=360, value=34)
        self.control_labels = {}
        for label, slider in (("Aceleração", self.throttle), ("Inclinação", self.pitch), ("Direção", self.yaw)):
            value_label = Label(text=f"{label}: {int(slider.value)}", size_hint_y=None, height=dp(24))
            self.control_labels[label] = value_label
            left.add_widget(value_label)
            left.add_widget(slider)
        self.throttle.bind(value=lambda *x: self.update_controls())
        self.pitch.bind(value=lambda *x: self.update_controls())
        self.yaw.bind(value=lambda *x: self.update_controls())

        self.flight_button = Button(text="INICIAR VOO", background_color=(0.65, 0.96, 0.05, 1), color=(0.08, 0.12, 0.13, 1), size_hint_y=None, height=dp(46))
        self.flight_button.bind(on_press=self.toggle_flight)
        left.add_widget(self.flight_button)
        body.add_widget(left)

        center = DroneCanvas()
        body.add_widget(center)

        right = BoxLayout(orientation="vertical", size_hint_x=.28, spacing=dp(5))
        right.add_widget(Label(text="INSPEÇÃO DE COMPONENTES", size_hint_y=None, height=dp(30)))
        parts_scroll = ScrollView()
        parts_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        parts_box.bind(minimum_height=parts_box.setter("height"))
        for name in PARTS:
            button = Button(text=name, size_hint_y=None, height=dp(42), background_color=(0.12, 0.18, 0.19, 1))
            button.bind(on_press=lambda instance, n=name: self.inspect(n))
            parts_box.add_widget(button)
        parts_scroll.add_widget(parts_box)
        right.add_widget(parts_scroll)
        self.part_label = Label(text="Selecione uma peça para inspeção", size_hint_y=None, height=dp(80), halign="center", valign="middle")
        right.add_widget(self.part_label)
        body.add_widget(right)
        root.add_widget(body)

        Clock.schedule_interval(center.rotate_motors, 0.05)
        Clock.schedule_interval(self.tick, 1)
        return root

    def update_controls(self):
        self.control_labels["Aceleração"].text = f"Aceleração: {int(self.throttle.value)}"
        self.control_labels["Inclinação"].text = f"Inclinação: {int(self.pitch.value)}"
        self.control_labels["Direção"].text = f"Direção: {int(self.yaw.value)}"

    def toggle_flight(self, instance):
        self.flying = not self.flying
        instance.text = "POUSAR DRONE" if self.flying else "INICIAR VOO"
        instance.background_color = (1, 0.36, 0.29, 1) if self.flying else (0.65, 0.96, 0.05, 1)
        self.status.text = "VÔO EM CURSO" if self.flying else "SISTEMA ONLINE"

    def inspect(self, name):
        category, spec, status = PARTS[name]
        self.part_label.text = f"[b]{name}[/b]\n{category}\n{spec}\nEstado: {status}"
        self.part_label.markup = True

    def tick(self, dt):
        if self.flying:
            acceleration = (self.throttle.value - 48) / 20
            self.altitude = max(0, self.altitude + acceleration * 0.012)
            self.speed = max(0, self.throttle.value * .27 + abs(self.pitch.value) * .08)
            self.battery = max(5, self.battery - .02)
        self.header_flight.text = f"ALT {self.altitude:.1f} m  |  VEL {self.speed:.1f} m/s"


if __name__ == "__main__":
    NovaDroneApp().run()

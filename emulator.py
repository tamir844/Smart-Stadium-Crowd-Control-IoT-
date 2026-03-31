# emulator.py
"""
Premium Bloomfield Emulators App:
- Turnstiles: High-styled buttons for Hapoel (Red) & Maccabi (Yellow).
- Noise Sensor: Automatic sensor calculating dB relative to stadium crowd size.
- Gate Actuators: Flashing, massive high-alert LEDs.
"""
import sys
import random
import init
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QGridLayout, QHBoxLayout, QSpinBox, 
                             QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from agent import Mqtt_client

class SignalHandler(QObject):
    command_received = pyqtSignal(str, str)

class AnimatedProgressBar(QProgressBar):
    def __init__(self, color_gradient, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #333333;
                border-radius: 10px;
                text-align: center;
                color: #FFFFFF;
                background-color: #1A1A1A;
                font-weight: 800;
                font-size: 11pt;
            }}
            QProgressBar::chunk {{
                border-radius: 8px;
                background-color: {color_gradient};
            }}
        """)
        self.anim = QPropertyAnimation(self, b"value")
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_animated_value(self, val):
        self.anim.stop()
        self.anim.setEndValue(val)
        self.anim.start()

class EmulatorsApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.signals = SignalHandler()
        self.signals.command_received.connect(self.update_gate_ui)
        
        self.locked_gates = {g: False for g in init.GATES_CONFIG}
        self.gate_counts = {g: 0 for g in init.GATES_CONFIG}
        
        self.mqtt = Mqtt_client(client_id="emulator_node")
        self.mqtt.connect(init.MQTT_BROKER, init.MQTT_PORT)
        self.mqtt.subscribe(init.TOPIC_COMMAND_ALL, self.on_command_received)
        
        self.gate_buttons = {}
        self.gate_status_labels = {}
        
        # Flashing state for locked gates
        self.flash_state = True
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.blink_effect)
        self.flash_timer.start(500)  # Blink every 500ms
        
        self.init_ui()
        
        # Timer for Automatic Noise Sensor (Every 2 seconds)
        self.noise_timer = QTimer()
        self.noise_timer.timeout.connect(self.auto_publish_noise)
        self.noise_timer.start(2000)

    def init_ui(self):
        self.setWindowTitle("🏟️ Bloomfield Emulators Control Panel")
        self.resize(650, 580)
        
        # Master Premium Dark Theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {init.THEME_BG};
                color: {init.THEME_TEXT};
                font-family: {init.FONT_FAMILY};
            }}
            QGroupBox {{
                background-color: {init.THEME_CARD};
                border: 1px solid #333333;
                border-radius: 12px;
                margin-top: 25px;
                font-size: 13pt;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #B0BEC5;
            }}
            QSpinBox {{
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                color: white;
                padding: 5px;
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. Turnstile Emulators (Producers)
        turnstile_group = QGroupBox("TURNSTILE ACCESS CONTROL")
        turnstile_layout = QGridLayout()
        turnstile_layout.setSpacing(15)
        turnstile_layout.setContentsMargins(20, 30, 20, 20)
        
        spin_layout = QHBoxLayout()
        lbl_spin = QLabel("Crowd Batch Size:")
        lbl_spin.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_spin.setStyleSheet("color: #AAAAAA;")
        
        self.spin_fans = QSpinBox()
        self.spin_fans.setRange(1, 10000)
        self.spin_fans.setValue(1)
        self.spin_fans.setFont(QFont("Segoe UI", 12))
        
        spin_layout.addWidget(lbl_spin)
        spin_layout.addWidget(self.spin_fans)
        spin_layout.addStretch()
        turnstile_layout.addLayout(spin_layout, 0, 0, 1, 2)
        
        row = 1
        for gate_id, config in init.GATES_CONFIG.items():
            btn = QPushButton(f"ENTER {config['name'].upper()}")
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            
            # Premium styling with states
            color = config['color']
            hover = config['hover']
            pressed = config['pressed']
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    background-color: {pressed};
                }}
                QPushButton:disabled {{
                    background-color: #555555;
                    color: #888888;
                }}
            """)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 150))
            btn.setGraphicsEffect(shadow)
            
            btn.clicked.connect(lambda checked, gid=gate_id: self.simulate_entry(gid))
            
            self.gate_buttons[gate_id] = btn
            turnstile_layout.addWidget(btn, row // 2, row % 2)
            row += 1
            
        turnstile_group.setLayout(turnstile_layout)
        
        # 2. Noise Sensor Emulator (Producer)
        noise_group = QGroupBox("AUTO ACOUSTIC SENSOR")
        noise_layout = QVBoxLayout()
        noise_layout.setContentsMargins(20, 30, 20, 20)
        
        self.lbl_noise = QLabel("Sensing ambient noise... 40 dB")
        self.lbl_noise.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.lbl_noise.setAlignment(Qt.AlignCenter)
        self.lbl_noise.setStyleSheet("color: #4CAF50;")
        
        # We replace the slider with a visual progress bar acting as the sensor output dial
        self.noise_bar = AnimatedProgressBar("qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #4CAF50, stop: 0.7 #FFC107, stop: 1 #F44336)")
        self.noise_bar.setRange(40, 130)
        self.noise_bar.setValue(40)
        self.noise_bar.setFormat("%v dB")
        self.noise_bar.setFixedHeight(25)
        
        noise_layout.addWidget(self.lbl_noise)
        noise_layout.addWidget(self.noise_bar)
        noise_group.setLayout(noise_layout)
        
        # 3. Gate Lock Actuators (Relays)
        gate_group = QGroupBox("SECURITY ACTUATOR OVERVIEW")
        gate_layout = QGridLayout()
        gate_layout.setSpacing(15)
        gate_layout.setContentsMargins(20, 30, 20, 20)
        
        row = 0
        for gate_id, config in init.GATES_CONFIG.items():
            lbl = QLabel(f"{config['name']}: SECURE")
            lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                background-color: #1B5E20; 
                color: white; 
                border-radius: 6px; 
                padding: 8px;
            """)
            self.gate_status_labels[gate_id] = lbl
            gate_layout.addWidget(lbl, row // 2, row % 2)
            row += 1
            
        gate_group.setLayout(gate_layout)
        
        main_layout.addWidget(turnstile_group)
        main_layout.addWidget(noise_group)
        main_layout.addWidget(gate_group)
        
        self.setLayout(main_layout)

    def simulate_entry(self, gate_id):
        if not self.locked_gates[gate_id]:
            num_fans = self.spin_fans.value()
            topic = init.get_entry_topic(gate_id)
            
            # To keep the auto-noise sensor perfectly accurate, the emulator 
            # tracks the simulated allowed capacity locally exactly like the manager
            max_capacity = init.GATES_CONFIG[gate_id]['capacity']
            current = self.gate_counts[gate_id]
            allowed = min(num_fans, max_capacity - current)
            
            if allowed > 0:
                self.gate_counts[gate_id] += allowed
                if num_fans == 1:
                    self.mqtt.publish(topic, "ENTRY_EVENT")
                else:
                    self.mqtt.publish(topic, f"BATCH_ENTRY:{num_fans}")
        else:
            print(f"SECURITY: {init.GATES_CONFIG[gate_id]['name']} is physically locked.")

    def auto_publish_noise(self):
        """Automatically calculates stadium noise relative to current capacity and publishes it."""
        total_fans = sum(self.gate_counts.values())
        max_stadium_capacity = sum(config['capacity'] for config in init.GATES_CONFIG.values())
        
        # Base ambient noise is 40dB. Full capacity reaches up to 125dB.
        if total_fans == 0:
            base_noise = 40.0
        else:
            ratio = total_fans / max_stadium_capacity
            base_noise = 40.0 + (85.0 * ratio)
            
        # Add dynamic alive fluctuation (± 2.5 dB)
        noise_level = base_noise + random.uniform(-2.5, 2.5)
        
        # Clamp to realistic limits
        noise_level = max(40.0, min(noise_level, 130.0))
        noise_level = round(noise_level, 1)
        
        # Update styling
        color = "#4CAF50" # Green
        if noise_level > 90:
            color = "#FFC107" # Yellow
        if noise_level >= 100:
            color = "#F44336" # Red
            
        self.lbl_noise.setText(f"Live Crowd Acoustic: {noise_level} dB")
        self.lbl_noise.setStyleSheet(f"color: {color};")
        self.noise_bar.set_animated_value(int(noise_level))
        
        self.mqtt.publish(init.TOPIC_NOISE, str(noise_level))

    def on_command_received(self, topic, payload):
        parts = topic.split('/')
        if len(parts) == 4 and parts[3] == "command":
            gate_id = parts[2]
            self.signals.command_received.emit(gate_id, payload)

    def update_gate_ui(self, gate_id, command):
        if gate_id not in self.gate_status_labels:
            return
            
        name = init.GATES_CONFIG[gate_id]['name']
        if command == "LOCK":
            self.locked_gates[gate_id] = True
            self.gate_buttons[gate_id].setEnabled(False)
            self.gate_buttons[gate_id].setText("LOCKED")
        elif command == "UNLOCK":
            self.locked_gates[gate_id] = False
            self.gate_buttons[gate_id].setEnabled(True)
            self.gate_buttons[gate_id].setText(f"ENTER {name.upper()}")

    def blink_effect(self):
        """Creates a pulsing high-alert red effect on locked gates."""
        self.flash_state = not self.flash_state
        
        for gate_id, is_locked in self.locked_gates.items():
            name = init.GATES_CONFIG[gate_id]['name']
            lbl = self.gate_status_labels[gate_id]
            
            if is_locked:
                if self.flash_state:
                    lbl.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 6px; padding: 8px; border: 2px solid white;")
                else:
                    lbl.setStyleSheet("background-color: #B71C1C; color: #ffcccc; border-radius: 6px; padding: 8px;")
                lbl.setText(f"{name}: LOCKED")
            else:
                lbl.setStyleSheet("background-color: #1B5E20; color: white; border-radius: 6px; padding: 8px;")
                lbl.setText(f"{name}: SECURE")

    def closeEvent(self, event):
        self.mqtt.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EmulatorsApp()
    ex.show()
    sys.exit(app.exec_())

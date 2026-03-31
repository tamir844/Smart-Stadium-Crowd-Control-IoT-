# gui.py
"""
Premium Main Dashboard using PyQt5 for Bloomfield Stadium.
World-class desktop UI with dark themes, animations, glassmorphism, and audio alerts.
"""
import sys
import init
import winsound
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QTextEdit, QHBoxLayout, QGroupBox, QGridLayout, 
                             QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QTextCursor
from agent import Mqtt_client

def play_lock_sound():
    try:
        # A heavy, low-pitch double beep simulating a heavy steel gate locking
        winsound.Beep(350, 250)
        winsound.Beep(250, 400)
    except:
        pass

def play_siren_sound():
    try:
        # High pitched rotating siren for ear-damage warning
        for _ in range(4):
            winsound.Beep(1200, 250)
            winsound.Beep(900, 250)
    except:
        pass

def threaded_play_sound(sound_type):
    """Spawns a daemon thread to play blocking Beep sounds without freezing the GUI."""
    if sound_type == "lock":
        threading.Thread(target=play_lock_sound, daemon=True).start()
    elif sound_type == "siren":
        threading.Thread(target=play_siren_sound, daemon=True).start()


class SignalHandler(QObject):
    update_capacity = pyqtSignal(str, int)
    update_noise = pyqtSignal(float)
    update_gate_status = pyqtSignal(str, str)
    log_alarm = pyqtSignal(str, str)

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
        
    def set_format_text(self, current, maximum):
        self.setFormat(f"{current} / {maximum} Fans")

class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.signals = SignalHandler()
        self.signals.update_capacity.connect(self.set_capacity)
        self.signals.update_noise.connect(self.set_noise)
        self.signals.update_gate_status.connect(self.set_gate_status)
        self.signals.log_alarm.connect(self.add_alarm_log)
        
        self.gate_counts = {g: 0 for g in init.GATES_CONFIG}
        
        self.progress_bars = {}
        self.lbl_gate_statuses = {}
        
        self.init_ui()
        
        self.mqtt = Mqtt_client(client_id="dashboard_master")
        self.mqtt.connect(init.MQTT_BROKER, init.MQTT_PORT)
        
        self.mqtt.subscribe(init.TOPIC_ENTRY_ALL, self.on_entry)
        self.mqtt.subscribe(init.TOPIC_NOISE, self.on_noise)
        self.mqtt.subscribe(init.TOPIC_COMMAND_ALL, self.on_command)
        self.mqtt.subscribe(init.TOPIC_ALARMS, self.on_alarm)

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        widget.setGraphicsEffect(shadow)

    def init_ui(self):
        self.setWindowTitle("🏟️ Bloomfield Stadium Command Center")
        self.resize(1100, 780)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {init.THEME_BG};
            }}
            QWidget {{
                color: {init.THEME_TEXT};
                font-family: {init.FONT_FAMILY};
            }}
            QGroupBox {{
                background-color: {init.THEME_CARD};
                border: 1px solid #2C2C2C;
                border-radius: 12px;
                margin-top: 25px;
                font-size: 14pt;
                font-weight: 800;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #B0BEC5;
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # --- CRITICAL NOISE ALERT BANNER ---
        self.lbl_critical_alert = QLabel("⚠️ CRITICAL ALARM: NOISE LEVEL DANGEROUS TO HUMAN HEARING (>115 dB)! ⚠️")
        self.lbl_critical_alert.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_critical_alert.setStyleSheet("background-color: #D32F2F; color: white; padding: 12px; border-radius: 8px; border: 2px solid white;")
        self.lbl_critical_alert.setAlignment(Qt.AlignCenter)
        self.apply_shadow(self.lbl_critical_alert)
        self.lbl_critical_alert.hide() # Hidden by default
        
        main_layout.addWidget(self.lbl_critical_alert)
        
        # --- TEAMS GRID ---
        teams_layout = QHBoxLayout()
        teams_layout.setSpacing(30)
        
        # Hapoel
        h_color = init.GATES_CONFIG["gate_4_5"]["color"]
        hapoel_group = QGroupBox("🔴 HAPOEL TEL AVIV SECTORS")
        hapoel_group.setStyleSheet(f"QGroupBox::title {{ color: {h_color}; font-size: 16pt; }}")
        self.apply_shadow(hapoel_group)
        hapoel_layout = QVBoxLayout()
        hapoel_layout.setSpacing(20)
        hapoel_layout.setContentsMargins(20, 30, 20, 20)
        
        # Maccabi
        m_color = init.GATES_CONFIG["gate_10_11"]["color"]
        maccabi_group = QGroupBox("🟡 MACCABI TEL AVIV SECTORS")
        maccabi_group.setStyleSheet(f"QGroupBox::title {{ color: {m_color}; font-size: 16pt; }}")
        self.apply_shadow(maccabi_group)
        maccabi_layout = QVBoxLayout()
        maccabi_layout.setSpacing(20)
        maccabi_layout.setContentsMargins(20, 30, 20, 20)
        
        h_grad = "qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #B71C1C, stop: 1 #FF5252)"
        m_grad = "qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #F57F17, stop: 1 #FFF59D)"
        
        for gate_id, config in init.GATES_CONFIG.items():
            gate_container = QWidget()
            g_layout = QGridLayout(gate_container)
            g_layout.setContentsMargins(0, 0, 0, 0)
            
            name = config['name']
            max_c = config['capacity']
            
            lbl_name = QLabel(name.upper())
            lbl_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
            
            lbl_stat = QLabel("SECURE")
            lbl_stat.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl_stat.setStyleSheet("color: #4CAF50; background-color: #1B5E20; padding: 4px; border-radius: 4px;")
            lbl_stat.setAlignment(Qt.AlignCenter)
            self.lbl_gate_statuses[gate_id] = lbl_stat
            
            is_hapoel = "Hapoel" in config['team']
            bar = AnimatedProgressBar(h_grad if is_hapoel else m_grad)
            bar.setRange(0, max_c)
            bar.setValue(0)
            bar.set_format_text(0, max_c)
            bar.setFixedHeight(25)
            self.progress_bars[gate_id] = bar
            
            g_layout.addWidget(lbl_name, 0, 0)
            g_layout.addWidget(lbl_stat, 0, 1, Qt.AlignRight)
            g_layout.addWidget(bar, 1, 0, 1, 2)
            
            if is_hapoel:
                hapoel_layout.addWidget(gate_container)
            else:
                maccabi_layout.addWidget(gate_container)
                
        hapoel_group.setLayout(hapoel_layout)
        maccabi_group.setLayout(maccabi_layout)
        
        teams_layout.addWidget(hapoel_group)
        teams_layout.addWidget(maccabi_group)
        
        # --- NOISE METER ---
        noise_group = QGroupBox("🔊 DYNAMIC ACOUSTIC METER")
        self.apply_shadow(noise_group)
        noise_layout = QVBoxLayout()
        noise_layout.setContentsMargins(20, 20, 20, 20)
        
        self.noise_bar = AnimatedProgressBar("qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #4CAF50, stop: 0.7 #FFC107, stop: 1 #F44336)")
        self.noise_bar.setRange(40, 130)
        self.noise_bar.setValue(40)
        self.noise_bar.setFormat("%v dB")
        self.noise_bar.setFixedHeight(30)
        
        noise_layout.addWidget(self.noise_bar)
        noise_group.setLayout(noise_layout)
        
        # --- TERMINAL LOG ---
        log_group = QGroupBox("⚠️ SECURE ALERTS TERMINAL")
        self.apply_shadow(log_group)
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(20, 20, 20, 20)
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: #00FF00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        log_layout.addWidget(self.txt_log)
        log_group.setLayout(log_layout)
        
        main_layout.addLayout(teams_layout, 5)
        main_layout.addWidget(noise_group, 1)
        main_layout.addWidget(log_group, 3)
        central_widget.setLayout(main_layout)

    def on_entry(self, topic, payload):
        parts = topic.split('/')
        if len(parts) == 4:
            gate_id = parts[2]
            if gate_id in self.gate_counts:
                count_to_add = 0
                if payload == "ENTRY_EVENT":
                    count_to_add = 1
                elif payload.startswith("BATCH_ENTRY:"):
                    try:
                        count_to_add = int(payload.split(":")[1])
                    except ValueError:
                        pass
                
                if count_to_add > 0:
                    max_capacity = init.GATES_CONFIG[gate_id]['capacity']
                    current = self.gate_counts[gate_id]
                    allowed = min(count_to_add, max_capacity - current)
                    if allowed > 0:
                        self.gate_counts[gate_id] += allowed
                        self.signals.update_capacity.emit(gate_id, self.gate_counts[gate_id])

    def on_noise(self, topic, payload):
        try:
            val = float(payload)
            self.signals.update_noise.emit(val)
        except ValueError:
            pass

    def on_command(self, topic, payload):
        parts = topic.split('/')
        if len(parts) == 4:
            gate_id = parts[2]
            self.signals.update_gate_status.emit(gate_id, payload)

    def on_alarm(self, topic, payload):
        color = "#FF5252" if "ALARM" in payload or "WARNING" in payload else "#00FF00"
        self.signals.log_alarm.emit(payload, color)

    def set_capacity(self, gate_id, count):
        if gate_id in self.progress_bars:
            bar = self.progress_bars[gate_id]
            max_c = init.GATES_CONFIG[gate_id]['capacity']
            bar.set_animated_value(count)
            bar.set_format_text(count, max_c)
            
    def set_noise(self, val):
        self.noise_bar.set_animated_value(int(val))
        
        # Audio and Visual Ear-Damage Alert (115 dB Threshold)
        if val >= 115.0:
            if self.lbl_critical_alert.isHidden():
                self.lbl_critical_alert.show()
                threaded_play_sound("siren")
        else:
            if not self.lbl_critical_alert.isHidden():
                self.lbl_critical_alert.hide()
            
    def set_gate_status(self, gate_id, status):
        if gate_id in self.lbl_gate_statuses:
            lbl = self.lbl_gate_statuses[gate_id]
            if status == "LOCK":
                if "LOCKED" not in lbl.text():
                    threaded_play_sound("lock")
                lbl.setText("LOCKED")
                lbl.setStyleSheet("color: white; background-color: #D32F2F; padding: 4px; border-radius: 4px;")
            else:
                lbl.setText("SECURE")
                lbl.setStyleSheet("color: #4CAF50; background-color: #1B5E20; padding: 4px; border-radius: 4px;")
            
    def add_alarm_log(self, msg, color):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        html_msg = f'<span style="color: {color};">[{now}] {msg}</span>'
        self.txt_log.append(html_msg)
        self.txt_log.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        self.mqtt.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainDashboard()
    window.show()
    sys.exit(app.exec_())

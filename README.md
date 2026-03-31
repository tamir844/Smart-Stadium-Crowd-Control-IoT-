# Bloomfield Smart Stadium Crowd Control

This is a university course project implementing a Smart Stadium Crowd Control system representing Bloomfield Stadium in Tel Aviv, splitting gates effectively between Hapoel Tel Aviv and Maccabi Tel Aviv. It is built using Python, MQTT (`paho-mqtt`), highly-styled PyQt5 elements, and SQLite3.

## Premium UI/UX Features

This project was specifically upgraded to demonstrate world-class desktop UI techniques:
- **Animations & Depth**: Uses `QPropertyAnimation` for progress bars and `QGraphicsDropShadowEffect` for elevated cards.
- **Blinking & Pulsing**: Custom Qt timers simulate flashing LED alerts when a gate hits full capacity.
- **Glassmorphism & Rich Theming**: A comprehensive Dark Theme using `#121212` backgrounds, custom QSS buttons, and precise hover/pressed tactile feedbacks.
- **Intelligent Back-end**: Batch entry processing with completely safe strict overflow checks. Limits cannot be breached visually or in data.

## Project Architecture

1. **Emulators (`emulator.py`)**:
   - Turnstile Emulators (Hapoel Red and Maccabi Yellow specific).
   - Noise Acoustic Emulator (Responsive slider).
   - Gate Security Actuators (Flashing LEDs).
   
2. **Data Manager (`manager.py`)**:
   - Strict capacity enforcement.
   - Prevents overflow even in rapid, massive batch injections (`BATCH_ENTRY`).
   - SQLite reliable logic.
   
3. **Master Command Dashboard (`gui.py`)**:
   - Displays animated, custom-gradient `QProgressBar` dials.
   - Terminal-style secure alarms log highlighting limits in real-time.

## Prerequisites

- Python 3.x
- Required libraries must be installed:
  ```bash
  pip install paho-mqtt PyQt5
  ```

## Running the System

```bash
python start_system.py
```

## How to Upload to GitHub

```bash
git init
git add .
git commit -m "Added Premium UI/UX capabilities and strict capacity logic"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

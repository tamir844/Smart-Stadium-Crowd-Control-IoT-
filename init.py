# init.py
"""
Configuration file for Bloomfield Smart Stadium Crowd Control.
Contains MQTT broker details, topic mappings, and Premium Gate/Team specifications.
"""

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# Base topics
TOPIC_NOISE = "stadium/noise"
TOPIC_ALARMS = "stadium/alarms"

def get_entry_topic(gate_id):
    """Topic for a specific gate's turnstile entry event."""
    return f"stadium/gate/{gate_id}/entry"

def get_command_topic(gate_id):
    """Topic for a specific gate's actuator command (e.g. LOCK)."""
    return f"stadium/gate/{gate_id}/command"

# Wildcard topics used by the Data Manager
TOPIC_ENTRY_ALL = "stadium/gate/+/entry"
TOPIC_COMMAND_ALL = "stadium/gate/+/command"

# Environment Variables
NOISE_THRESHOLD_DB = 100.0

# UI Theme Config
THEME_BG = "#121212"
THEME_CARD = "#1e1e1e"
THEME_TEXT = "#ffffff"
FONT_FAMILY = "'Segoe UI', Roboto, Montserrat, Arial"

# Bloomfield Stadium Gate Configuration: Team, UI Color Theme, and Max Capacity
GATES_CONFIG = {
    # Hapoel Tel Aviv (Deep Red Theme)
    "gate_4_5": {"name": "Gates 4-5", "team": "Hapoel Tel Aviv", "color": "#D32F2F", "hover": "#FF5252", "pressed": "#B71C1C", "capacity": 4842},
    "gate_2": {"name": "Gate 2", "team": "Hapoel Tel Aviv", "color": "#D32F2F", "hover": "#FF5252", "pressed": "#B71C1C", "capacity": 3130},
    "gate_7": {"name": "Gate 7", "team": "Hapoel Tel Aviv", "color": "#D32F2F", "hover": "#FF5252", "pressed": "#B71C1C", "capacity": 5338},
    
    # Maccabi Tel Aviv (Vibrant Yellow Theme)
    "gate_10_11": {"name": "Gates 10-11", "team": "Maccabi Tel Aviv", "color": "#FBC02D", "hover": "#FFF59D", "pressed": "#F57F17", "capacity": 4861},
    "gate_13": {"name": "Gate 13", "team": "Maccabi Tel Aviv", "color": "#FBC02D", "hover": "#FFF59D", "pressed": "#F57F17", "capacity": 3149},
    "gate_8": {"name": "Gate 8", "team": "Maccabi Tel Aviv", "color": "#FBC02D", "hover": "#FFF59D", "pressed": "#F57F17", "capacity": 5342},
}

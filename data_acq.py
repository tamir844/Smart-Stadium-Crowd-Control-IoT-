# data_acq.py
"""
SQLite Database Handler for Bloomfield Smart Stadium.
Robust data acquisition architecture for IoT logs.
"""
import sqlite3
from datetime import datetime

DB_FILE = "bloomfield_stadium.db"

def get_connection():
    """Returns a highly reliable SQLite connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Critical Database Connection Error: {e}")
        return None

def init_db():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS noise_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    noise_level REAL NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alarms_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alarm_message TEXT NOT NULL
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database Initialization Error: {e}")
        finally:
            conn.close()

def insert_entry(gate_id, event_type):
    conn = get_connection()
    if conn:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO entries_log (timestamp, gate_id, event_type) VALUES (?, ?, ?)", 
                           (timestamp, gate_id, event_type))
            conn.commit()
        except sqlite3.Error as e:
            pass
        finally:
            conn.close()

def insert_noise(noise_level):
    conn = get_connection()
    if conn:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO noise_log (timestamp, noise_level) VALUES (?, ?)", 
                           (timestamp, noise_level))
            conn.commit()
        except sqlite3.Error as e:
            pass
        finally:
            conn.close()

def insert_alarm(alarm_message):
    conn = get_connection()
    if conn:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alarms_log (timestamp, alarm_message) VALUES (?, ?)", 
                           (timestamp, alarm_message))
            conn.commit()
        except sqlite3.Error as e:
            pass
        finally:
            conn.close()

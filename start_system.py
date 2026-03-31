# start_system.py
"""
Launcher script to simultaneously run all system components.
"""
import subprocess
import sys
import time
import os

def main():
    print("============================================")
    print(" 🏟️ B L O O M F I E L D   S Y S T E M S")
    print("============================================")
    
    python_exec = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    print("[1/3] Initializing Backend Data Manager...")
    manager_proc = subprocess.Popen([python_exec, "manager.py"])
    time.sleep(2)  

    print("[2/3] Launching Master Dashboard GUI...")
    gui_proc = subprocess.Popen([python_exec, "gui.py"])

    print("[3/3] Bringing Emulators Online...")
    emulator_proc = subprocess.Popen([python_exec, "emulator.py"])

    print("--------------------------------------------")
    print("✅ System is LIVE. Close UIs to terminate.")
    print("--------------------------------------------")

    try:
        gui_proc.wait()
        emulator_proc.wait()
    except KeyboardInterrupt:
        print("\nInterrupt received. Shutting down gracefully...")
    finally:
        print("Terminating background processes...")
        manager_proc.terminate()
        emulator_proc.terminate()
        gui_proc.terminate()
        print("System shutdown complete.")

if __name__ == "__main__":
    main()

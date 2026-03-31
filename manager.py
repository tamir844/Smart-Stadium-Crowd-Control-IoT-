# manager.py
"""
Data Manager for Bloomfield. Runs intelligently in the background.
Enforces strict gate capacities with IoT messaging.
"""
import time
import init
import data_acq
from agent import Mqtt_client

class DataManager:
    def __init__(self):
        data_acq.init_db()
        
        self.mqtt = Mqtt_client(client_id="data_manager")
        self.mqtt.connect(init.MQTT_BROKER, init.MQTT_PORT)
        
        self.gate_entries = {gate_id: 0 for gate_id in init.GATES_CONFIG}
        self.gate_locked = {gate_id: False for gate_id in init.GATES_CONFIG}
        
        self.mqtt.subscribe(init.TOPIC_ENTRY_ALL, self.handle_entry)
        self.mqtt.subscribe(init.TOPIC_NOISE, self.handle_noise)
        
        print("🏟️ Bloomfield Data Manager started and actively listening...")

    def handle_entry(self, topic, payload):
        parts = topic.split('/')
        if len(parts) == 4 and parts[3] == "entry":
            gate_id = parts[2]
            
            if gate_id in self.gate_entries:
                count_to_add = 0
                event_desc = ""
                
                if payload == "ENTRY_EVENT":
                    count_to_add = 1
                elif payload.startswith("BATCH_ENTRY:"):
                    try:
                        count_to_add = int(payload.split(":")[1])
                    except ValueError:
                        pass
                
                if count_to_add > 0:
                    max_capacity = init.GATES_CONFIG[gate_id]['capacity']
                    current_capacity = self.gate_entries[gate_id]
                    name = init.GATES_CONFIG[gate_id]['name']
                    
                    allowed_to_add = min(count_to_add, max_capacity - current_capacity)
                    denied = count_to_add - allowed_to_add
                    
                    if allowed_to_add > 0:
                        actual_desc = f"Entry ({allowed_to_add})" if allowed_to_add > 1 else "Single Entry"
                        data_acq.insert_entry(gate_id, actual_desc)
                        
                        self.gate_entries[gate_id] += allowed_to_add
                        current_capacity = self.gate_entries[gate_id]
                        
                        print(f"[Data Manager] {actual_desc} at {name}. ({current_capacity}/{max_capacity})")
                        
                        if denied > 0:
                            warning_msg = f"WARNING: {denied} fans denied entry at {name}. (Full Capacity)"
                            self.mqtt.publish(init.TOPIC_ALARMS, warning_msg)
                            data_acq.insert_alarm(warning_msg)
                            
                        # Lock if filled
                        if current_capacity >= max_capacity and not self.gate_locked[gate_id]:
                            print(f"[Data Manager] MAX CAPACITY REACHED ({max_capacity}) for {name}. Applying HARD LOCK.")
                            command_topic = init.get_command_topic(gate_id)
                            self.mqtt.publish(command_topic, "LOCK")
                            self.gate_locked[gate_id] = True
                            
                            alarm_msg = f"CRITICAL ALARM: {name} is Full!"
                            self.mqtt.publish(init.TOPIC_ALARMS, alarm_msg)
                            data_acq.insert_alarm(alarm_msg)
                    elif denied > 0:
                        warning_msg = f"SECURITY WARNING: {name} is already full! Denied {denied} fans."
                        self.mqtt.publish(init.TOPIC_ALARMS, warning_msg)
                        data_acq.insert_alarm(warning_msg)

    def handle_noise(self, topic, payload):
        try:
            noise_level = float(payload)
            data_acq.insert_noise(noise_level)
            
            if noise_level >= init.NOISE_THRESHOLD_DB:
                warning_msg = f"ACOUSTIC WARNING: High Noise Level ({noise_level} dB)"
                self.mqtt.publish(init.TOPIC_ALARMS, warning_msg)
                data_acq.insert_alarm(warning_msg)
        except ValueError:
            pass

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down Data Manager...")
            self.mqtt.disconnect()

if __name__ == "__main__":
    manager = DataManager()
    manager.run()

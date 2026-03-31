# agent.py
"""
Robust MQTT wrapper class using paho-mqtt to handle connect, disconnect, 
subscribe, publish, and message callbacks with proper error handling.
"""
import paho.mqtt.client as mqtt
import uuid
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Mqtt_client:
    def __init__(self, client_id=None):
        """Initialize the MQTT client with a random ID if none provided."""
        if client_id is None:
            client_id = f"stadium_node_{uuid.uuid4().hex[:8]}"
            
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        self.callbacks = {}

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"[{self.client._client_id.decode()}] Elegantly connected to MQTT broker.")
        else:
            logging.error(f"MQTT Connection failed with return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logging.warning(f"Unexpected disconnection from MQTT broker.")
        else:
            logging.info(f"[{self.client._client_id.decode()}] Gracefully disconnected from broker.")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = msg.payload.decode('utf-8')
        except UnicodeDecodeError:
            logging.error("Failed to decode MQTT message payload.")
            return

        # Exact match callback
        if topic in self.callbacks:
            self.callbacks[topic](topic, payload)

        # Wildcard match callbacks
        for sub_topic, callback in self.callbacks.items():
            if '+' in sub_topic:
                sub_parts = sub_topic.split('/')
                topic_parts = topic.split('/')
                if len(sub_parts) == len(topic_parts):
                    match = True
                    for sp, tp in zip(sub_parts, topic_parts):
                        if sp != '+' and sp != tp:
                            match = False
                            break
                    if match:
                        callback(topic, payload)

    def connect(self, broker, port, keepalive=60):
        """Connect to broker with robust error handling."""
        try:
            self.client.connect(broker, port, keepalive)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Failed to establish MQTT connection: {e}")

    def disconnect(self):
        """Stop the loop and disconnect safely."""
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self, topic, callback=None):
        """Subscribe to a topic and map a dedicated callback."""
        self.client.subscribe(topic)
        if callback:
            self.callbacks[topic] = callback

    def publish(self, topic, payload, qos=0, retain=False):
        """Publish a formatted message."""
        try:
            self.client.publish(topic, str(payload), qos, retain)
        except Exception as e:
            logging.error(f"Publish failed: {e}")

import glob
import time
import json
import paho.mqtt.client as mqtt

# MQTT Broker settings
MQTT_BROKER = "test.mosquitto.org"  # Using a public MQTT broker for testing
MQTT_PORT = 1883
MQTT_TOPIC = "raspberrypi/ds18b20/temperature"

# Path to the DS18B20 sensor data
BASE_DIR = '/sys/bus/w1/devices/'
SENSOR_FOLDER = glob.glob(BASE_DIR + '28*')[0]
SENSOR_FILE = SENSOR_FOLDER + '/w1_slave'

def read_temp_raw():
    with open(SENSOR_FILE, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.publish(MQTT_TOPIC, "DS18B20 Temperature Logger Connected")

client = mqtt.Client()
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        temp_c = read_temp()
        payload = json.dumps({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temp_c
        })
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(10)  # Publish every 5 seconds

except KeyboardInterrupt:
    print("Script stopped by user")
    client.disconnect()

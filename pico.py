from machine import Pin, time_pulse_us, ADC
import time
import network
import socket
import json
import urequests as requests

# Constants
SSID = 'Name of your WiFi'
PASSWORD = 'Password'
FIREBASE_URL = "URL link to Firebase"
AUTH_TOKEN = "Custom auth token"
TRIGGER_PIN = 15
ECHO_PIN = 14
TEMP_SENSOR_ADC = 4
TRIGGER_PULSE_DURATION = 10
ECHO_TIMEOUT = 30000
DISTANCE_CONVERSION_FACTOR = 29.1
CHECK_INTERVAL = 500
CONVERSION_FACTOR = 3.3 / (65535)

# Wi-Fi connection function
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f'Connected to WiFi. IP: {ip}')
            return ip
        print('Waiting for connection...')
        time.sleep(1)
    print("Failed to connect to WiFi")
    return None

# Firebase communication function
def send_to_firebase(data):
    headers = {'Content-Type': 'application/json'}
    url = f"{FIREBASE_URL}?auth={AUTH_TOKEN}"
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Data sent to Firebase successfully.")
        else:
            print("Error sending data to Firebase:", response.status_code, response.text)
    except Exception as e:
        print(f"Error sending data to Firebase: {e}")

# Setup GPIO pins for sensors
def setup_sensor_pins(trigger_pin, echo_pin):
    trigger = Pin(trigger_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)
    return trigger, echo

# Measure distance using ultrasonic sensor
def measure_distance(trigger, echo):
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(TRIGGER_PULSE_DURATION)
    trigger.value(0)
    duration = time_pulse_us(echo, 1, ECHO_TIMEOUT)
    return (duration / 2) / DISTANCE_CONVERSION_FACTOR if duration != -1 else None

# Read temperature from RP2040's built-in sensor
def read_temperature():
    sensor_temp = ADC(TEMP_SENSOR_ADC)
    reading = sensor_temp.read_u16() * CONVERSION_FACTOR
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

# Main function loop
def main():
    ip = connect_to_wifi()
    if not ip:
        return
    trigger, echo = setup_sensor_pins(TRIGGER_PIN, ECHO_PIN)
    while True:
        distance = measure_distance(trigger, echo)
        temperature = read_temperature()
        print(f"Temperature: {temperature:.2f} Â°C")
        if distance is None:
            print("No echo detected")
        else:
            print(f"Distance: {distance:.2f} cm")
        data = {"distance": distance, "temperature": temperature}
        send_to_firebase(data)
        time.sleep_ms(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user")
#!/usr/bin/env python3
import time
import datetime
import json

from seeed_dht import DHT
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802

import paho.mqtt.client as mqtt

# --------------- CONFIGURACIÓN MQTT / THINGSBOARD ---------------
TB_HOST = "demo.thingsboard.io"    # o el host que os hayan dado
TB_PORT = 1883
TB_ACCESS_TOKEN = "REPLACE_WITH_YOUR_TOKEN"   # Poned aquí vuestro token

# --------------- SENSOR SETUP ---------------

# DHT11 en D5
TEMPHUM_PIN = 5
dht_sensor = DHT('11', TEMPHUM_PIN)

# Canal analógico A0 (vuestro “noise” actual)
adc = ADC()
SOUND_CHANNEL = 0

# LCD I2C
lcd = JHD1802()
lcd.setCursor(0, 0)
lcd.write("DeustoAir Ready")

# --------------- FUNCIONES ---------------

def read_dht():
    hum, temp = dht_sensor.read()
    return temp, hum

def read_sound(samples=20, delay=0.01):
    total = 0
    for _ in range(samples):
        total += adc.read(SOUND_CHANNEL)
        time.sleep(delay)
    return total / samples

def compute_comfort(temp, hum, noise):
    if temp > 28 or hum > 70 or noise > 65:
        status = "VERY HIGH"
    elif temp > 24 or hum > 55 or noise > 55:
        status = "MODERATE"
    else:
        status = "GOOD"
    return status

def update_lcd(temp, hum, noise, status):
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.write(f"T:{temp:.1f}C H:{hum:.0f}%")
    lcd.setCursor(1, 0)
    lcd.write(f"N:{noise:.0f} {status}")

def log_to_csv(temp, hum, noise, status, filename="/home/pi08/deustoair/data.csv"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"{timestamp},{temp:.1f},{hum:.1f},{noise:.1f},{status}\n")

# --------------- MQTT: CONEXIÓN ---------------

def connect_mqtt():
    client = mqtt.Client()
    # En ThingsBoard el TOKEN va como "username" (sin password)
    client.username_pw_set(TB_ACCESS_TOKEN)
    client.connect(TB_HOST, TB_PORT, keepalive=60)
    return client

# --------------- MAIN LOOP ---------------

def main():
    print("Starting DeustoAir+Panel with MQTT...")
    lcd.clear()
    lcd.write("MQTT connecting")

    client = connect_mqtt()
    lcd.clear()
    lcd.write("MQTT connected")

    while True:
        try:
            temp, hum = read_dht()
            noise_value = read_sound()
            status = compute_comfort(temp, hum, noise_value)

            # Salida local
            now = datetime.datetime.now()
            print(f"{now} | "
                  f"Temp:{temp:.1f}C Hum:{hum:.1f}% Noise:{noise_value:.1f} Status:{status}")

            update_lcd(temp, hum, noise_value, status)
            log_to_csv(temp, hum, noise_value, status)

            # Payload para ThingsBoard (telemetry)
            payload = {
                "temperature": round(temp, 1),
                "humidity": round(hum, 1),
                "noise": round(noise_value, 1),
                "status": status
            }

            # En ThingsBoard el topic para telemetría MQTT es:
            # v1/devices/me/telemetry
            client.publish("v1/devices/me/telemetry", json.dumps(payload))
            # Opcional: mensaje en consola
            print("Published to TB:", payload)

            time.sleep(10)  # cada 10 segundos

        except KeyboardInterrupt:
            print("\nProgram interrupted by user.")
            lcd.clear()
            lcd.write("Stopped")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import time
import datetime
import json
import requests

from seeed_dht import DHT
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802

# --------------- CONFIGURACIÓN THINGSBOARD (HTTP) ---------------
TB_HOST = "demo.thingsboard.io"    # Servidor de ThingsBoard
TB_ACCESS_TOKEN = "WLqV3XCKBFV8a5riIsJ1"

TB_HTTP_URL = f"https://{TB_HOST}/api/v1/{TB_ACCESS_TOKEN}/telemetry"

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

def log_to_csv(temp, hum, noise, status, filename="data.csv"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"{timestamp},{temp:.1f},{hum:.1f},{noise:.1f},{status}\n")

def send_telemetry_http(payload):
    """Envía telemetría a ThingsBoard usando HTTP POST."""
    try:
        r = requests.post(TB_HTTP_URL, json=payload, timeout=5)
        if r.status_code == 200:
            print("HTTP telemetry sent OK")
        else:
            print(f"HTTP error {r.status_code}: {r.text}")
    except Exception as e:
        print("HTTP telemetry failed:", e)

# --------------- MAIN LOOP ---------------

def main():
    print("Starting DeustoAir+Panel with HTTP...")
    lcd.clear()
    lcd.write("HTTP mode")

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

            # Payload para ThingsBoard (telemetría)
            payload = {
                "temperature": round(temp, 1),
                "humidity": round(hum, 1),
                "noise": round(noise_value, 1),
                "status": status
            }

            send_telemetry_http(payload)

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

import time
import datetime
from seeed_dht import DHT
from grove.adc import ADC
from grove.display.jhd1802 import JHD1802   # For Grove LCD 16x2 I2C


#SENSOR SETUP

# DHT11 connected to D5 on Grove Hat
TEMPHUM_PIN = 5
dht_sensor = DHT('11', TEMPHUM_PIN)

# KY-037 sound sensor connected to A0 (analog input 0)
adc = ADC()
SOUND_CHANNEL = 0

# LCD panel on I2C bus
lcd = JHD1802()
lcd.setCursor(0, 0)
lcd.write("DeustoAir Ready")


#HELPER FUNCTIONS

def read_dht():
    """Reads temperature and humidity from DHT11"""
    hum, temp = dht_sensor.read()
    return temp, hum

def read_sound(samples=20, delay=0.01):
    """Estimates average sound level (simple analog sampling)"""
    total = 0
    for _ in range(samples):
        total += adc.read(SOUND_CHANNEL)
        time.sleep(delay)
    return total / samples

def compute_comfort(temp, hum, noise):
    """Determines comfort status based on thresholds"""
    if temp > 28 or hum > 70 or noise > 65:
        status = "VERY HIGH"
    elif temp > 24 or hum > 55 or noise > 55:
        status = "MODERATE"
    else:
        status = "GOOD"
    return status

def update_lcd(temp, hum, noise, status):
    """Displays readings and comfort message on LCD"""
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.write(f"T:{temp:.1f}C H:{hum:.0f}%")
    lcd.setCursor(1, 0)
    lcd.write(f"N:{noise:.0f} {status}")

def log_to_csv(temp, hum, noise, status, filename="/home/pi08/deustoair/data.csv"):
    """Appends readings to a CSV file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"{timestamp},{temp:.1f},{hum:.1f},{noise:.1f},{status}\n")


#MAIN LOOP

def main():
    print("Starting DeustoAir+Panel...")
    time.sleep(2)
    lcd.clear()

    while True:
        try:
            temp, hum = read_dht()
            noise_value = read_sound()
            status = compute_comfort(temp, hum, noise_value)

            # Output
            print(f"{datetime.datetime.now()} | "
                  f"Temp:{temp:.1f}C  Hum:{hum:.1f}%  Noise:{noise_value:.1f}  Status:{status}")
            update_lcd(temp, hum, noise_value, status)
            log_to_csv(temp, hum, noise_value, status)

            time.sleep(10)   # Read every 10 seconds

        except KeyboardInterrupt:
            print("\nProgram interrupted by user.")
            lcd.clear()
            lcd.write("Stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

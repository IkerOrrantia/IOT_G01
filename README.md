DeustoAir+Panel – IoT Final Project
Descripción general
DeustoAir+Panel es un proyecto IoT desarrollado como parte del curso de Internet of Things. El sistema utiliza una Raspberry Pi y sensores Grove para medir temperatura, humedad y ruido ambiental. La información se procesa para generar un estado de confort, se muestra en una pantalla LCD, se guarda en un archivo CSV y se envía a la nube usando HTTP hacia ThingsBoard.

Este documento explica cómo instalar, configurar y ejecutar el proyecto.



## REQUISITOS

Hardware requerido:

* Raspberry Pi 3B/3B+/4
* Grove Base Hat para Raspberry Pi
* Sensor DHT11 (puerto D5)
* Sensor de sonido (canal A0)
* Pantalla LCD Grove 16x2 I2C
* Conexión Wi-Fi

Software requerido:

* Raspberry Pi OS Bookworm
* Python 3
* Librerías necesarias:

  * seeed-python-dht
  * smbus2
  * grove.py
  * requests


## INSTALACIÓN DEL PROYECTO

Paso 1: Clonar el repositorio
Ejecutar en la Raspberry Pi:

git clone [https://github.com/IkerOrrantia/IOT_G01](https://github.com/IkerOrrantia/IOT_G01)

cd IOT_G01

Paso 2: Crear y activar el entorno virtual

python3 -m venv deustoair_env
source deustoair_env/bin/activate

Paso 3: Instalar dependencias

pip install seeed-python-dht
pip install smbus2
pip install grove.py
pip install requests


## CONFIGURACIÓN DE THINGSBOARD

1. Acceder a [https://demo.thingsboard.io](https://demo.thingsboard.io)
2. Crear una cuenta o iniciar sesión
3. Ir a Devices
4. Crear un nuevo dispositivo (por ejemplo “DeustoAir-RPi”)
5. Entrar en el dispositivo y abrir Credentials
6. Copiar el Access Token
7. Sustituir en el archivo `deustoair_main.py` la línea:

TB_ACCESS_TOKEN = "REPLACE_WITH_YOUR_TOKEN"

por:

TB_ACCESS_TOKEN = "ELTOKENDETHINGSBOARD"

Este token identifica a vuestro dispositivo en ThingsBoard.


## EJECUCIÓN DEL PROGRAMA

Para ejecutar el programa desde la Raspberry Pi:

cd ~/IOT_G01
source /home/pi08/deustoair_env/bin/activate
python3 deustoair_main.py

El programa realiza las siguientes acciones:

* Lee temperatura, humedad y ruido ambiental
* Calcula un estado de confort: GOOD, MODERATE o VERY HIGH
* Muestra la información en la pantalla LCD
* Registra los datos en un archivo local llamado `data.csv`
* Envía telemetría a ThingsBoard mediante HTTP


## VISUALIZACIÓN EN THINGSBOARD

Para ver los datos en la nube:

1. Entrar en ThingsBoard
2. Abrir el dispositivo creado
3. Ir a la pestaña “Latest Telemetry”
4. Verificar que aparecen las claves:

temperature
humidity
noise
status

También es posible crear dashboards con gráficas, tablas o indicadores.

## ESTRUCTURA DEL PROYECTO

IOT_G01/

* deustoair_main.py   (script principal)
* data.csv            (archivo generado automáticamente)
* README.txt          (este documento)
* otros archivos adicionales

## NOTAS IMPORTANTES

* El archivo `data.csv` se crea automáticamente en la carpeta del proyecto.
* Si la pantalla LCD no funciona, comprobar que I2C está habilitado mediante `raspi-config`.
* Si ThingsBoard devuelve error 401, el Access Token no es válido o está mal copiado.
* Si no se puede enviar telemetría, verificar la conexión Wi-Fi.
* La lógica de confort (GOOD, MODERATE, VERY HIGH) puede ajustarse según las necesidades del entorno.


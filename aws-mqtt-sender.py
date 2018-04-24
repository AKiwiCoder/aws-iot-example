# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from grovepi import *
from grove_rgb_lcd import *
from time import sleep
import datetime
import serial
import time
import smbus
import math
import RPi.GPIO as GPIO
import struct
import sys

#
# Global variables
#

# Connected PIN settings
led = 4
sound_sensor = 0
light_sensor = 1

# Temperature Sensor Connections
dht_sensor_port = 7
dht_sensor_type = 0

myMQTTClient = None


#
# Return the number of milli seconds between epoch and now
#
def now():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


#
# Send the JSON string on the MQTT queue
#
def publish_json(json):
    print json
    myMQTTClient.publish("data", json, 0)


#
# Collect and send the sound level readings
#
def send_sound_level_reading():
    try:
        sensor_value = analogRead(sound_sensor)
        if sensor_value > 0:
            publish_json("{ \"timestamp\":\"%d\", \"sound\":\"%d\" }" % (now(), sensor_value))
    except IOError:
        print ("Sound Sensor: Error")


#
# Collect and send the light level readings
#
def send_light_level_reading():
    try:
        sensor_value = analogRead(light_sensor)
        resistance = float(1023 - sensor_value) * 10 / sensor_value
        if resistance > 0:
            publish_json("{ \"timestamp\":\"%d\", \"light\":\"%f\" }" % (now(), resistance))
    except IOError:
        print ("Light Sensor: Error")


#
# Collect and send the temperature / humidity readings
#
def send_temperature_humidity_readings():
    try:
        [temp, hum] = dht(dht_sensor_port, dht_sensor_type)
        if not (math.isnan(temp) is True or math.isnan(hum) is True and temp > 0 and hum > 0):
            setText_norefresh(("Temp: %d C\nHumidity : %d %%" % (temp, hum)))
            publish_json("{ \"timestamp\":\"%d\", \"temperature\":\"%d\", \"humidity\":\"%d\" }" % (now(), temp, hum))
    except (IOError, TypeError) as e:
        print(str(e))
        setText("")


#
# Initialise the various sensors and MQTT connection
#
def initialise():
    # Set the screen background color
    setRGB(0, 255, 0)

    # Sent the various pin on the PI to input/output
    pinMode(sound_sensor, "INPUT")
    pinMode(light_sensor, "INPUT")
    pinMode(led, "OUTPUT")

    # Initialise the MQTT client
    global myMQTTClient
    myMQTTClient = AWSIoTMQTTClient("<AWS Thing ARN>")

    myMQTTClient.configureEndpoint("<AWS MQTT Server", 8883)
    myMQTTClient.configureCredentials("<Root CA File", "<Private Key File>", "<Certificate File>")

    myMQTTClient.configureOfflinePublishQueueing(-1)
    myMQTTClient.configureDrainingFrequency(2)
    myMQTTClient.configureConnectDisconnectTimeout(10)
    myMQTTClient.configureMQTTOperationTimeout(5)

    myMQTTClient.connect()


#
# Each second go around the loop sending data as appropriate.
# and blinking the LED each second
#
def loop():
    step = 0

    while True:
        # Each second send the sound readings
        send_sound_level_reading()

        # Every 3 seconds send the light readings
        if step % 3 == 0:
            send_light_level_reading()

        # Every 5 seconds send the temperature/humidity readings
        if step % 5 == 0:
            send_temperature_humidity_readings()

        step = step + 1
        digitalWrite(led, 1) # Turn LED on
        sleep(1)
        digitalWrite(led, 0) # Turn LED off


#
# Main Function
#
if __name__ == "__main__":
    initialise()
    loop()

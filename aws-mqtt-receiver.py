# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from blinkt import set_pixel, get_pixel, set_brightness, show, clear
from time import sleep


#
# Global Variables
#

# Status indicators for various message types
tick_led_on = False
sound_led_on = False
light_led_on = False
temp_led_on = False

myMQTTClient = None


#
# If the pixel is off, set it to the appropriate color, turn it off otherwise
#
def set_pixel_if_blank(led_index, red_on, green_on, blue_on, brightness_on):
    [red_current, green_current, blue_current, _] = get_pixel(led_index)
    if red_current == 0 and green_current == 0 and blue_current == 0:
        set_pixel(led_index, red_on, green_on, blue_on, brightness_on)


#
# Process a message from the MQTT server. We are using a crude
# detection method of looking for a string in the payload.
#
def message_received(_client, _userdata, message):
    global sound_led_on
    global light_led_on
    global temp_led_on

    if "sound" in message.payload:
        sound_led_on = not sound_led_on
    if "light" in message.payload:
        light_led_on = not light_led_on
    if "temperature" in message.payload:
        temp_led_on = not temp_led_on

    print("Received Message: ", message.payload)


#
# Toggle the various pixels on if we have received a message of the
# appropriate type
#
def update_pixels():
    print "Updating Pixels"
    clear()
    if tick_led_on:
        set_pixel_if_blank(0, 0, 0, 255, 1.0)
        set_pixel_if_blank(1, 0, 0, 255, 1.0)
    if sound_led_on:
        set_pixel_if_blank(2, 255, 0, 0, 1.0)
        set_pixel_if_blank(3, 255, 0, 0, 1.0)
    if light_led_on:
        set_pixel_if_blank(4, 255, 255, 0, 1.0)
        set_pixel_if_blank(5, 255, 255, 0, 1.0)
    if temp_led_on:
        set_pixel_if_blank(6, 0, 255, 0, 1.0)
        set_pixel_if_blank(7, 0, 255, 0, 1.0)
    show()


#
# Setup the MQTT client
#
def initialise():
    global myMQTTClient

    myMQTTClient = AWSIoTMQTTClient("<AWS Thing ARN>")

    myMQTTClient.configureEndpoint("<AWS MQTT Server", 8883)
    myMQTTClient.configureCredentials("<Root CA File", "<Private Key File>", "<Certificate File>")

    myMQTTClient.configureOfflinePublishQueueing(-1)
    myMQTTClient.configureDrainingFrequency(2)
    myMQTTClient.configureConnectDisconnectTimeout(10)
    myMQTTClient.configureMQTTOperationTimeout(5)

    myMQTTClient.connect()
    myMQTTClient.subscribe("data", 1, message_received)


#
# Update the pixels every 0.5 seconds, and toggle the tick led
# each second
#
def loop():
    global tick_led_on
    while True:
        update_pixels()
        sleep(0.5)
        update_pixels()
        sleep(0.5)
        tick_led_on = not tick_led_on


#
# Main Function
#
if __name__ == "__main__":
    initialise()
    loop()

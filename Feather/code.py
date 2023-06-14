# light up an led on the adafruit microcontroller
import board
import digitalio
import analogio
import time
import busio
import os
from sonar import GroveUltrasonicRanger
from groovelib import Grove4DigitDisplay
from webserver import SimpleWSGIApplication
import neopixel

# import socketpool
import ampule
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

try:
    import json as json_module
except ImportError:
    import ujson as json_module

print("ESP32 SPI simple web server test!")


recording_status_led = digitalio.DigitalInOut(board.D3)
recording_status_led.direction = digitalio.Direction.OUTPUT

wifi_led = digitalio.DigitalInOut(board.A0)
wifi_led.direction = digitalio.Direction.OUTPUT

input_button = digitalio.DigitalInOut(board.D9)
input_button.direction = digitalio.Direction.INPUT

sonar = GroveUltrasonicRanger(board.D5)
display = Grove4DigitDisplay(board.A2, board.A3)  # nRF52840 D9, D10, Grove D4

current_distance = "0000"
wifi_status = False

# FeatherWing ESP32 AirLift, nRF52840
cs = digitalio.DigitalInOut(board.D13)
rdy = digitalio.DigitalInOut(board.D11)
rst = digitalio.DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
wifi = adafruit_esp32spi.ESP_SPIcontrol(spi, cs, rdy, rst)

esp = adafruit_esp32spi.ESP_SPIcontrol(
    spi, cs, rdy, rst
)  # py

print("MAC addr:", [hex(i) for i in esp.MAC_address])
print("MAC addr actual:", [hex(i) for i in esp.MAC_address_actual])

status_light = neopixel.NeoPixel(
    board.NEOPIXEL, 1, brightness=0.2
)

wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
wifi.connect()


# ----------------------------------------------------------------------------------------
# Our HTTP Request handlers
def led_on(environ):  # pylint: disable=unused-argument
    print("led on!")
    status_light.fill((0, 0, 100))
    return web_app.serve_file("static/index.html")


def led_off(environ):  # pylint: disable=unused-argument
    print("led off!")
    status_light.fill(0)
    return web_app.serve_file("static/index.html")


def led_color(environ):  # pylint: disable=unused-argument
    json = json_module.loads(environ["wsgi.input"].getvalue())
    print(json)
    rgb_tuple = (json.get("r"), json.get("g"), json.get("b"))
    status_light.fill(rgb_tuple)
    return ("200 OK", [], [])


# Here we create our application, setting the static directory location
# and registering the above request_handlers for specific HTTP requests
# we want to listen and respond to.
static = "/static"
try:
    static_files = os.listdir(static)
    if "index.html" not in static_files:
        raise RuntimeError(
            """
            This example depends on an index.html, but it isn't present.
            Please add it to the {0} directory""".format(
                static
            )
        )
except OSError as e:
    raise RuntimeError(
        """
        This example depends on a static asset directory.
        Please create one named {0} in the root of the device filesystem.""".format(
            static
        )
    ) from e

web_app = SimpleWSGIApplication(static_dir=static)
web_app.on("GET", "/led_on", led_on)
web_app.on("GET", "/led_off", led_off)
web_app.on("POST", "/ajax/ledcolor", led_color)

# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print("open this IP in your browser: ", esp.pretty_ip(esp.ip_address))

# Start the server
wsgiServer.start()

while True:
    display.show(current_distance)
    recording_status_led.value = input_button.value
    current_distance = '{:0>4}'.format(int(sonar.get_distance()))
    time.sleep(0.1)

    try:
        wsgiServer.update_poll()
        # Could do any other background tasks here, like reading sensors
    except OSError as e:
        print("Failed to update server, restarting ESP32\n", e)
        wifi.reset()
        continue

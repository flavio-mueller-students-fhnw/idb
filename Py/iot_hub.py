from azure.iot.device import IoTHubDeviceClient, Message
import time
from grove.gpio import GPIO
from grove.grove_temperature_humidity_sensor import DHT

button = GPIO(5, GPIO.IN)
dht11 = DHT("11", 16)

# Connection string for your device
CONNECTION_STRING = "HostName=flavio-idb-test-sponsor.azure-devices.net;DeviceId=idb-raspberry;SharedAccessKey=tyJbuaeUEalsgbLsH0kItK1MpjLbNf4FmJFneSqcYl0="

client = None
cache = {}


def create_client():
    client = IoTHubDeviceClient.create_from_connection_string(
        CONNECTION_STRING)
    return client


def connect_to_azure(client):
    if client.connected:
        print("Already connected to Azure IoT Hub.")
    else:
        try:
            print("Connecting to Azure IoT Hub...")
            client.connect()
            print("Connected to Azure IoT Hub!")
        except Exception as e:
            print("Error connecting to Azure IoT Hub:", str(e))


def disconnect_from_azure(client):
    if client.connected:
        try:
            print("Disconnecting from Azure IoT Hub...")
            client.disconnect()
            print("Disconnected from Azure IoT Hub.")
        except Exception as e:
            print("Error disconnecting from Azure IoT Hub:", str(e))
    else:
        print("Already disconnected from Azure IoT Hub.")


def send_message(client, message):
    try:
        print("Sending message to Azure IoT Hub...")
        client.send_message(message)
        print("Message sent to Azure IoT Hub.")
    except Exception as e:
        print("Error sending message to Azure IoT Hub:", str(e))
        cache[time.time()] = message

    if len(cache) > 0 and client.connected:
        try:
            connect_to_azure(client)
        except Exception as e:
            print("Error connecting to Azure IoT Hub:", str(e))
            return
        for key in cache:
            try:
                print("Sending cached message to Azure IoT Hub...")
                client.send_message(cache[key])
                print("Cached message sent to Azure IoT Hub.")
                del cache[key]
            except Exception as e:
                print("Error sending cached message to Azure IoT Hub:", str(e))


client = create_client()
connect_to_azure(client)
send_message(client, "Hello from Raspberry Pi!")

while True:
    time.sleep(5)
    if button.read():
        send_message(client, "Button pressed!")
    else:
        send_message(client, "Button released!")

    send_message(client, "DHT:" + str(dht11.read))

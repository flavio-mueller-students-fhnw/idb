from azure.iot.device import IoTHubDeviceClient, Message

# Connection string for your device
CONNECTION_STRING = "HostName=flavio-idb-test-sponsor.azure-devices.net;DeviceId=idb-raspberry;SharedAccessKey=tyJbuaeUEalsgbLsH0kItK1MpjLbNf4FmJFneSqcYl0="

# Define the message payload
MESSAGE = "Hello, Azure IoT Hub!"


def send_message():
    try:
        print("Connecting to Azure IoT Hub...")

        # Create an IoT Hub client instance
        client = IoTHubDeviceClient.create_from_connection_string(
            CONNECTION_STRING)

        # Connect to the IoT Hub
        client.connect()
        print("Connected to Azure IoT Hub!")

        # Create a message object
        message = Message(MESSAGE)

        print("Sending message to Azure IoT Hub...")
        # Send the message to the IoT Hub
        client.send_message(message)
        print("Message sent successfully!")

        # Disconnect from the IoT Hub
        client.disconnect()
        print("Disconnected from Azure IoT Hub.")

    except Exception as e:
        print("Error sending message:", str(e))


# Call the function to send the message
send_message()

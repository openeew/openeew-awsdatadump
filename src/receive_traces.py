"""This script receives trace data from MQTT by subscribing to a topic"""
import json
from paho.mqtt.client import Client as MqttClient
import datetime
import os
import logging


class DataReceiver:
    """This class subscribes to the MQTT and receivces raw data"""

    log_format = "%(asctime)s - module:%(module)s - line:%(lineno)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)

    def __init__(self, df_holder, params) -> None:
        """
        Initializes the DataReceiver object

        MQTT variable in params (params["MQTT"]) define whether local, or IBM MQTT is used
        """
        super().__init__()
        self.df_holder = df_holder
        self.params = params

    def run(self):
        """Main method that parses command options and executes the rest of the script"""

        # create a client
        client = self.create_client(
            host=os.getenv("MQTT_HOST", "localhost"),
            port=int(os.getenv("MQTT_PORT", "1883")),
            clientid=os.getenv("MQTT_CLIENTID", "") + "_rec_aws",
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            cafile=os.getenv("MQTT_CERT"),
        )

        client.loop_forever()

    def create_client(self, host, port, username, password, clientid, cafile=None):
        """Creating an MQTT Client Object"""
        client = MqttClient(clientid)

        if username and password:
            client.username_pw_set(username=username, password=password)
        else:
            self.logger.warn("Proceeding without username and password")

        if cafile:
            client.tls_set(ca_certs=cafile)
        else:
            self.logger.warn("Proceeding without certificate file")

        try:
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.connect(host=host, port=port)
        except OSError as error:
            self.logger.error(error)

        return client

    def on_connect(self, client, userdata, flags, resultcode):
        """Upon connecting to an MQTT server, subscribe to the topic
        The production topic is 'iot-2/type/OpenEEW/id/+/evt/trace/fmt/json'"""

        topic = "iot-2/type/OpenEEW/id/+/evt/status/fmt/json"
        client.subscribe(topic)

        self.logger.info(f"✅ Subscribed to sensor data with result code {resultcode}")

    def on_message(self, client, userdata, message):
        """When a message is sent to a subscribed topic,
        decode the message and send it to another method"""
        try:
            decoded_message = str(message.payload.decode("utf-8", "ignore"))
            data = json.loads(decoded_message)

            # get timestamp for the received trace
            dt = datetime.datetime.now(datetime.timezone.utc)
            utc_time = dt.replace(tzinfo=datetime.timezone.utc)
            cloud_t = utc_time.timestamp()

            self.df_holder.update(data, cloud_t)

            # Print the current size of the data buffer
            # print(
            #     "▫️ Size of data in the buffer "
            #     + str(int(sys.getsizeof(self.df_holder.data) / 1e5) / 10)
            #     + " mb"
            # )
        except (ValueError, BaseException) as exception:
            self.logger.error(exception)

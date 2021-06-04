"""Simulates traces to an MQTT Server. Takes a .JSONL file and publishes each line to MQTT"""

import json
import glob
from paho.mqtt.client import Client as MqttClient

import pandas as pd
import time
import datetime
import os

def run():
    """Main method that creates client and executes the rest of the script"""

    # create a client
    client = create_client(
        host=os.environ["MQTT_HOST"],
        port=int(os.environ["MQTT_PORT"]),
        username=os.environ["MQTT_USERNAME"],
        password=os.environ["MQTT_PASSWORD"],
        clientid=os.environ["MQTT_CLIENTID"] + "_sim",
        cafile=os.environ["MQTT_CERT"],
    )

    topic = "iot-2/type/OpenEEW/id/000000000000/evt/status/fmt/json"

    publish_jsonl(datapath, client, topic)


def create_client(host, port, username, password, clientid, cafile):
    """Creating an MQTT Client Object"""
    client = MqttClient(clientid)

    if username and password:
        client.username_pw_set(username=username, password=password)

    try:
        client.tls_set(ca_certs=cafile)
    except:
        print("Proceeding without certificate file")

    client.connect(host=host, port=port)
    return client


def publish_jsonl(data_path, client, topic):
    """Publish each line of a jsonl given a directory"""

    # dataframe that will keep all data
    data = pd.DataFrame()

    # loop over all *.jsonl files in a folder
    for filepath in glob.iglob(data_path + "/*/*.jsonl"):

        # print("Processing:" + filepath)

        with open(filepath, "r") as json_file:
            json_array = list(json_file)
            data = data.append([json.loads(line) for line in json_array])

    # create a vector of 'deplays' that will make the data chunks come at the right time
    data.sort_values(by=["cloud_t"], inplace=True)
    timediff = data["cloud_t"].diff()
    timediff = timediff.iloc[1:].append(pd.Series([0])) / 1

    # loop over all json elements in the json array and publish to MQTT
    for i in range(len(data)):

        # get timestamp for the published trace
        dt = datetime.datetime.now(datetime.timezone.utc)
        utc_time = dt.replace(tzinfo=datetime.timezone.utc)
        cloud_t = utc_time.timestamp()

        d = data[["device_id", "x", "y", "z", "sr", "cloud_t"]].iloc[i]
        d["device_id"] = "mx" + d["device_id"]

        to_publish = {
            "traces": [{"x": d["x"], "y": d["y"], "z": d["z"]}],
            "sr": d["sr"],
            "device_id": d["device_id"],
            "cloud_t": cloud_t,
        }
        message = json.dumps(to_publish)

        client.publish(topic, message)

        time.sleep(timediff.iloc[i])

        print(
            datetime.datetime.utcfromtimestamp(data["cloud_t"].iloc[i]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )


hist_data_path = "../data/test_data"
run(hist_data_path)

time.sleep(200)

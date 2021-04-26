"""
Event module
"""

# Import modules
import numpy as np
import datetime
import math
import time
import json
from obspy import Stream, Trace, UTCDateTime
from glob import glob
import ast
from warnings import warn
import os

import logging
import boto3
from botocore.exceptions import ClientError


class AWSdump:
    """This class handles all the detection procedures"""

    def __init__(self, traces, params) -> None:
        super().__init__()
        self.traces = traces
        self.params = params

    def dump_data(self):

        # get timestamp for the received trace
        dt = datetime.datetime.now(datetime.timezone.utc)
        utc_time = dt.replace(tzinfo=datetime.timezone.utc)
        cloud_t = utc_time.timestamp()

        # get a list of unique devices
        try:
            devices = list(self.traces.data["device_id"].unique())
        except:
            devices = []

        # loop over all devices
        for device_id in devices:

            # get the last sample and find out how much time have passed
            last_sample = self.traces.data[self.traces.data["device_id"] == device_id][
                "cloud_t"
            ].iloc[-1]

            # if the last sample is older that max_gap
            if self.params["max_gap"] < (cloud_t - last_sample):

                # data to save
                trace = self.traces.data[self.traces.data["device_id"] == device_id]

                # get paths and filenames
                (
                    json_local_path,
                    mseed_local_path,
                    json_s3_path,
                    mseed_s3_path,
                ) = self.get_name_and_path(trace)

                a = time.time()
                if self.params["export_json"]:
                    print(device_id)
                    # save json file locally
                    self.save_to_jsonl(trace, json_local_path)
                    # save json to aws
                    self.upload_file_aws(json_local_path, json_s3_path)
                b = time.time()

                if self.params["export_mseed"]:
                    # convert json to mseed
                    self.json2mseed(json_local_path, mseed_local_path)
                    # save mseed to aws
                    self.upload_file_aws(mseed_local_path, mseed_s3_path)
                
                c = time.time()

                print((c-b, b-a))
                # DROP THE DATA FROM THE DATAFRAME
                self.traces.data = self.traces.data[
                    self.traces.data["device_id"] != device_id
                ]

    def get_name_and_path(self, trace):

        trace_start = trace["cloud_t"].min()
        timestamp = datetime.datetime.utcfromtimestamp(trace_start)

        year = str(timestamp.year)
        hour = str(timestamp.hour)
        minute = str(timestamp.minute)
        second = str(timestamp.second)
        jd = f"{timestamp.timetuple().tm_yday:03d}"
        device_id = trace["device_id"].iloc[0]

        json_filename = "hr" + hour + "_min" + minute + "_sec" + second + ".jsonl"
        mseed_filename = (
            self.params["network"]
            + "."
            + device_id
            + "."
            + timestamp.strftime("%Y.%j.%H.%M.%S")
            + ".MSEED"
        )

        json_local_path = "./tmp/jsonl/" + json_filename
        mseed_local_path = "./tmp/mseed/" + mseed_filename

        json_s3_path = (
            "test_traces/json/dev"
            + device_id
            + "/yr"
            + year
            + "/jd"
            + jd
            + "/"
            + json_filename
        )
        mseed_s3_path = "test_traces/mseed/" + mseed_filename

        return json_local_path, mseed_local_path, json_s3_path, mseed_s3_path

    def save_to_jsonl(self, df, json_local_path):

        with open(json_local_path, "w") as outfile:
            for _, entry in df.iterrows():
                json.dump(json.loads(entry.to_json()), outfile)
                outfile.write("\n")

    def json2mseed(self, json_local_path, mseed_local_path):

        misal_thresh = self.params["misal_thresh"]
        interp_samp = self.params["interp_samp"]
        network = self.params["network"]

        # create new empty data strem
        st = Stream()

        with open(json_local_path) as f:

            for entry in f:

                record = entry.strip()
                record = ast.literal_eval(record)

                tr = Trace()
                tr.stats.sampling_rate = record["sr"]
                tr.stats.starttime = (
                    UTCDateTime(record["cloud_t"])
                    - (len(record["x"]) - 1) / record["sr"]
                )
                tr.stats.station = record["device_id"]
                tr.stats.network = network

                if len(tr.stats.station) > 4:
                    warn(
                        "Station name for {} now {} to fit MSEED format".format(
                            tr.stats.station, tr.stats.station[0:4]
                        )
                    )
                    tr.stats.station = record["device_id"][0:4]

                for channel in ["x", "y", "z"]:

                    tr.data = np.array(record[channel])
                    tr.stats.channel = "EN" + channel.capitalize()
                    st += tr.copy()

        # align subsample shifts
        st.merge(method=-1, misalignment_threshold=misal_thresh)

        # close overlaps (either discarding or interpolating the overlapping samples)
        st.merge(method=1, fill_value=None, interpolation_samples=interp_samp)
        st = st.split()  # do not return a masked array

        st.write(mseed_local_path, format="MSEED")

    def upload_file_aws(self, local_path, s3_path):
        """Upload a file to an S3 bucket

        :return: True if file was uploaded, else False
        """

        try:

            s3_resource = boto3.resource(
                "s3",
                region_name=os.environ["AWS_REGION"],
                aws_access_key_id=os.environ["ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
            )

            s3_resource.Bucket(os.environ["BUCKET_NAME"]).put_object(
                Key=s3_path, Body=open(local_path, "rb")
            )

        except ClientError as e:
            logging.error(e)
            return False
        return True

    def run(self):
        # run loop indefinitely
        while True:
            self.dump_data()
            time.sleep(self.params["sleep_time"])

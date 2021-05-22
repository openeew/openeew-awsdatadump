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


class SaveTemp:
    """This class handles all the detection procedures"""

    def __init__(self, traces, todo, params) -> None:
        super().__init__()
        self.traces = traces
        self.params = params
        self.todo = todo

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

            # get the signal length
            num_of_sec = len(
                self.traces.data[self.traces.data["device_id"] == device_id]["cloud_t"]
            )

            # if the last sample is older that max_gap
            if (self.params["max_gap"] < (cloud_t - last_sample)) or (
                num_of_sec >= self.params["max_len"]
            ):

                # data to save
                trace = self.traces.data[self.traces.data["device_id"] == device_id]

                # for to-do list
                cloud_t_start = trace["cloud_t"].min()
                cloud_t_end = trace["cloud_t"].max()

                # get paths and filenames
                (
                    json_local_path,
                    mseed_local_path,
                    json_s3_path,
                    mseed_s3_path,
                    json_filename,
                    mseed_filename,
                ) = self.get_name_and_path(trace)

                # save json file locally
                self.save_to_jsonl(trace, json_local_path)

                if self.params["export_mseed"]:
                    # convert json to mseed
                    self.json2mseed(json_local_path, mseed_local_path)
                    # add to to-do list
                    self.todo.data = self.todo.data.append(
                        {
                            "s3_path": mseed_s3_path,
                            "local_path": mseed_local_path,
                            "file_name": mseed_filename,
                            "cloud_t_start": cloud_t_start,
                            "cloud_t_end": cloud_t_end,
                            "device_id": device_id,
                            "file_type": "mseed",
                        },
                        ignore_index=True,
                    )

                if self.params["export_json"]:
                    # add to to-do list
                    self.todo.data = self.todo.data.append(
                        {
                            "s3_path": json_s3_path,
                            "local_path": json_local_path,
                            "file_name": json_filename,
                            "cloud_t_start": cloud_t_start,
                            "cloud_t_end": cloud_t_end,
                            "device_id": device_id,
                            "file_type": "jsonl",
                        },
                        ignore_index=True,
                    )

                # DROP THE DATA FROM THE DATAFRAME
                self.traces.data = self.traces.data[
                    self.traces.data["device_id"] != device_id
                ]

    def get_name_and_path(self, trace):

        trace_start = trace["cloud_t"].min()
        timestamp = datetime.datetime.utcfromtimestamp(trace_start)

        year = str(timestamp.year)
        hour = str(timestamp.hour).zfill(2)
        minute = str(timestamp.minute).zfill(2)
        jd = f"{timestamp.timetuple().tm_yday:03d}".zfill(3)
        device_id = trace["device_id"].iloc[0]

        json_filename = "hr" + hour + "_min" + minute + ".jsonl"
        mseed_filename = (
            self.params["network"]
            + "."
            + device_id
            + "."
            + timestamp.strftime("%Y.%j.%H.%M.%S")
            + ".MSEED"
        )

        json_local_path = "./tmp/jsonl/" + device_id + "_" + json_filename
        mseed_local_path = "./tmp/mseed/" + device_id + "_" + mseed_filename

        json_s3_path = (
            self.params["s3_folder"]
            + "/json/dev"
            + device_id
            + "/yr"
            + year
            + "/jd"
            + jd
            + "/"
            + json_filename
        )
        mseed_s3_path = "test_traces/mseed/" + mseed_filename

        return (
            json_local_path,
            mseed_local_path,
            json_s3_path,
            mseed_s3_path,
            json_filename,
            mseed_filename,
        )

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

    def run(self):
        # run loop indefinitely
        while True:
            self.dump_data()
            time.sleep(self.params["sleep_time"])

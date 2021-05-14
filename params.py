"""
This file sets parameters used in data dump OpenEEW algorithm
"""

# NETWORK
network = "MX"

# MQTT
MQTT = "custom"  # local, custom or IBM

# PARAMETERS
max_gap = 10  # maximum gap in data
max_len = 600  # maximum signal length in seconds
sleep_time = 1  # the saving algorithm is goinng to sleep for this ammount of time

# EXPORT PARAMS
export_json = True
path_in_json = "./tmp/jsonl/"
export_mseed = False
path_in_mseed = "./tmp/mseed/"
interp_samp = 0  # 0: Do not interpolate, n: interpolate n samples, -1: interpolate ALL overlapping samples
misal_thresh = (
    0.5  # 0: do no align samples, 0.5: align all samples with sub-sample time shift​
)
traces_table_name = "openeew-traces"
s3_folder = "test_traces"


params = {
    "MQTT": MQTT,
    "max_gap": max_gap,
    "max_len": max_len,
    "sleep_time": sleep_time,
    "path_in_json": path_in_json,
    "path_in_mseed": path_in_mseed,
    "network": network,
    "interp_samp": interp_samp,
    "misal_thresh": misal_thresh,
    "export_json": export_json,
    "export_mseed": export_mseed,
    "traces_table_name": traces_table_name,
    "s3_folder": s3_folder,
}

"""
This file sets parameters used in data dump OpenEEW algorithm
"""

# PARAMETERS
max_gap = 10    # maximum gap in data
sleep_time = 1  # the saving algorithm is goinng to sleep for this ammount of time

# MSEED PARAMS
path_in_json = "./tmp/jsonl/"
path_in_mseed = "./tmp/mseed/"
network = "PR"
interp_samp = 0 # 0: Do not interpolate, n: interpolate n samples, -1: interpolate ALL overlapping samples
misal_thresh = 0.5 # 0: do no align samples, 0.5: align all samples with sub-sample time shift​


params = {
    "max_gap": max_gap,
    "sleep_time": sleep_time,
    "path_in_json": path_in_json, 
    "path_in_mseed": path_in_mseed,
    "network": network,
    "interp_samp": interp_samp,
    "misal_thresh": misal_thresh
}



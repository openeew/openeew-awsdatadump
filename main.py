"""
This is the main file that runs the OpenEEW code package
"""

# import modules
import time
from threading import Thread
import os

from params import params
from src import data_holders, receive_traces, aws

__author__ = "Vaclav Kuna"
__copyright__ = ""
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Vaclav Kuna"
__email__ = "kuna.vaclav@gmail.com"
__status__ = ""


def main():
    """Does everything"""

    # Create a dictionary of aws credentials from enviroment variables

    aws_cred = {
        "AWS_REGION": os.environ["AWS_REGION"],
        "ACCESS_KEY_ID": os.environ["ACCESS_KEY_ID"],
        "SECRET_ACCESS_KEY": os.environ["SECRET_ACCESS_KEY"],
        "BUCKET_NAME": os.environ["BUCKET_NAME"],
    }

    # Create a RawData DataFrame.
    traces = data_holders.Traces()

    # We create and start our traces update worker
    stream = receive_traces.DataReceiver(df_holder=traces, params=params)
    receive_data_process = Thread(target=stream.run)
    receive_data_process.start()

    # We create and start detection worker
    compute = aws.AWSdump(traces=traces, params=params)
    aws_process = Thread(target=compute.run)
    aws_process.start()

    # We join our Threads, i.e. we wait for them to finish before continuing
    receive_data_process.join()
    aws_process.join()


if __name__ == "__main__":

    main()

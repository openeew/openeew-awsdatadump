"""
This is the main file that runs the OpenEEW code package
"""

# import modules
import time
from threading import Thread
from dotenv import dotenv_values

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
    aws_cred = dotenv_values()  # take AWS S3 credentials from .env

    # Create a RawData DataFrame.
    traces = data_holders.Traces()

    # We create and start our traces update worker
    stream = receive_traces.DataReceiver(traces)
    receive_data_process = Thread(target=stream.run)
    receive_data_process.start()

    # We create and start detection worker
    compute = aws.AWSdump(traces=traces, params=params, aws_cred=aws_cred)
    aws_process = Thread(target=compute.run)
    aws_process.start()

    # We join our Threads, i.e. we wait for them to finish before continuing
    receive_data_process.join()
    aws_process.join()


if __name__ == "__main__":

    main()

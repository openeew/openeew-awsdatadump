"""
This is the main file that runs the OpenEEW code package
"""

# import modules
import time
from threading import Thread
import os

from params import params
from src import data_holders, receive_traces, save_temp, dump_aws_ibm

__author__ = "Vaclav Kuna"
__copyright__ = ""
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Vaclav Kuna"
__email__ = "kuna.vaclav@gmail.com"
__status__ = ""


def main():
    """Does everything"""

    # Create a RawData DataFrame.
    traces = data_holders.Traces()
    todo = data_holders.ToDo()

    # We create and start our traces update worker
    stream = receive_traces.DataReceiver(df_holder=traces, params=params)
    receive_data_process = Thread(target=stream.run)
    receive_data_process.start()

    # We create and start temporary save
    compute = save_temp.SaveTemp(traces=traces, todo=todo, params=params)
    tmp_process = Thread(target=compute.run)
    tmp_process.start()

    # We create and start dumper to AWS and IBM
    dump = dump_aws_ibm.Dump(todo=todo, params=params)
    dump_process = Thread(target=dump.run)
    dump_process.start()

    # We join our Threads, i.e. we wait for them to finish before continuing
    receive_data_process.join()
    tmp_process.join()
    dump_process.join()


if __name__ == "__main__":

    main()

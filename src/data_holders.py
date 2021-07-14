from dataclasses import dataclass
import pandas as pd
import logging


log_format = (
    "%(asctime)s - module:%(module)s - line:%(lineno)s - %(levelname)s - %(message)s"
)
logging.basicConfig(format=log_format)
logger = logging.getLogger(__name__)


@dataclass
class Traces:
    """This dataclass holds a reference to the RawData DF in memory."""

    data: pd.DataFrame = pd.DataFrame()

    logging.info("✅ Created empty dataframe for sensor data.")

    def update(self, data, cloud_t):

        device_id = data["device_id"]
        traces = [
            {
                "x": data["traces"][0]["x"],
                "y": data["traces"][0]["y"],
                "z": data["traces"][0]["z"],
            }
        ]
        sr = 31.25

        data = {
            "device_id": device_id,
            "traces": [traces],
            "sr": sr,
            "cloud_t": cloud_t,
        }

        # create a df
        df_new = pd.DataFrame(data)

        # append to the data
        self.data = self.data.append(df_new, ignore_index=True)


class ToDo:
    """This dataclass holds a reference to the RawData DF in memory."""

    data: pd.DataFrame = pd.DataFrame()

    logging.info("✅ Created empty to-do dataframe.")

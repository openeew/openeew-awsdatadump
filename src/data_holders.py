from dataclasses import dataclass
import pandas as pd
import json
import numpy as np
import datetime
import sys


@dataclass
class Traces:
    """This dataclass holds a reference to the RawData DF in memory."""

    data: pd.DataFrame = pd.DataFrame()

    print("✅ Created empty dataframe for sensor data.")

    def update(self, data, cloud_t):

        data = json.loads(data)
        data["cloud_t"] = cloud_t
        data["x"] = [data["x"]]
        data["y"] = [data["y"]]
        data["z"] = [data["z"]]

        # create a df
        df_new = pd.DataFrame(data)

        # append to the data
        self.data = self.data.append(df_new, ignore_index=True)

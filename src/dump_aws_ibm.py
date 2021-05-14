import logging
import boto3
from botocore.exceptions import ClientError

from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from cloudant.database import CloudantDatabase

import pandas as pd
import os
import time


class Dump:
    def __init__(self, todo, params):
        """Initiate the class with the to do list"""
        self.todo = todo
        self.params = params

        # initialize AWS
        self.s3_resource = boto3.resource(
            "s3",
            region_name=os.environ["AWS_REGION"],
            aws_access_key_id=os.environ["ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        )

        # initialize IBM
        self.client = Cloudant(
            os.environ["CLOUDANT_USERNAME"],
            os.environ["CLOUDANT_PASSWORD"],
            url=os.environ["CLOUDANT_URL"],
        )
        self.client.connect()
        self.ibm_db = self.client[self.params["traces_table_name"]]

    def dump_data(self):

        for _, row in self.todo.data.iterrows():

            print(row["local_path"])

            s3_path = row["s3_path"]
            local_path = row["local_path"]
            ibm_message = {
                "file_name": row["file_name"],
                "cloud_t_start": row["cloud_t_start"],
                "cloud_t_end": row["cloud_t_end"],
                "s3_path": row["s3_path"],
                "trace_length": row["cloud_t_end"] - row["cloud_t_start"],
                "device_id": row["device_id"],
                "file_type": row["file_type"],
            }

            self.s3_resource.Bucket(os.environ["BUCKET_NAME"]).put_object(
                Key=s3_path, Body=open(local_path, "rb")
            )
            self.ibm_db.create_document(ibm_message)

            os.remove(local_path)

            self.todo.data = self.todo.data[self.todo.data["local_path"] != local_path]

            print("✅ Dumped to ASW and IBM to the cloudant database.")

    def run(self):
        # run loop indefinitely
        while True:
            self.dump_data()
            time.sleep(self.params["sleep_time"])

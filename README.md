# OpenEEW seismological code

## Introduction

The algorithm subscribes to MQTT traces and saves them to AWS S3 storage.
There are currently 2 formats: JSONL and MSEED.

## Development

To run this project locally, you will need access to a local MQTT and AWS. The scripts will pick up
enviroment variables for your AWS buckets you can set them

```
export AWS_REGION=
export ACCESS_KEY_ID=
export SECRET_ACCESS_KEY=
export BUCKET_NAME=
```

This repository contains a Dockerfile that can be used for local development as well.

To build an aws-data-dump docker image, from the root directory run the following:

```
docker build --tag aws-data-dump:dev .
```

Create a .env file that contains details of your AWS bucket.

```
AWS_REGION=
ACCESS_KEY_ID=
SECRET_ACCESS_KEY=
BUCKET_NAME=
```

To then run this docker image execute the following command:

```
docker run \
  --interactive \
  --detach \
  --env-file .env \
  --name aws-data-dump \
  aws-data-dump:dev
```
## **Development**

This repository is written in Python and runs [Black](https://github.com/psf/black) on all Pull Request.

To install and run black linter:

```
pip install black
black /path/to/file
```

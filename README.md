# OpenEEW seismological code

## Introduction

The algorithm subscribes to MQTT traces and saves them to AWS S3 storage.
There are currently 2 formats: JSONL and MSEED.

## Development

This repository contains a Dockerfile that can be used for local development.

To build an aws-data-dump docker image, from the root directory run the following:

```
docker build --tag aws-data-dump:dev .
```

To then run this docker image execute the following command:

```
docker run \
  --interactive \
  --detach \
  --name aws-data-dump \
  aws-data-dump:dev
```

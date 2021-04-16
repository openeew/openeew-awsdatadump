# OpenEEW seismological code

## Introduction

The algorithm subscribes to MQTT traces and saves them to AWS S3 storage.
There are currently 2 formats: JSONL and MSEED.

## **Development**

This repository is written in Python and runs [Black](https://github.com/psf/black) on all Pull Request.

To install and run black linter:

```
pip install black
black /path/to/file
```

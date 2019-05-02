# Overview

This folder is used for generating a database of testable scenario
instances. You must have the following envrionment variables set to execute all
aspects:

- `MESSAGE_IX_CI_USER`
- `MESSAGE_IX_CI_PW`


The values for these variables can be found in the internal IIASA document
[here](https://iiasahub.sharepoint.com/:x:/s/ene/MESSAGEix/EQSb7ohzU2xCjltYjJs68SoBXOmIoovhezqfpFol1JOzGw?e=gvlXg2).

# Generate the Database

To generate and upload the database execute the follow files in order:

1. `fetch_scenarios.py`
2. `make_db.py`
3. `upload_db.sh`

## `upload_db.sh`

This command must be run by passing your ssh information, so either

```
./upload_db.sh <user>@data.ene.iiasa.ac.at
```

or

```
./upload_db.sh <ssh alias>
```

# Tests running on CI

These tests are designed to run on CI. To do so, one must download the test
database, generate the test file, and run `pytest`.

This can be done with one command

```
./run_on_ci.sh
```

## Individual Steps

Downloading the database is done with `download_db.py`.

Generating the test file is done with `generate_test_file.py`.

You can then run the test with

```
pytest test_scenarios.py
```

# Updating GAMS License File

These tests require a GAMS License file. To update the file on the IIASA server,
run

```
./upload_license.sh <ssh alias> </path/to/license_file.txt>
```

If you want to use your current GAMS license, this can be done with

```
./upload_license.sh <ssh alias> $(dirname $(which gams))/gamslice.txt
```

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches zipped file geodatabases from King County's FTP server
and organizes the contents.
"""

from ftplib import FTP
# import os
import sys
# import argparse

# These are the standard thematic geodatabases
# excluding the topographic contour lines.
# zip_list = [
#     'adminGDB.zip',
#     'censusGDB.zip',
#     'districtGDB.zip',
#     'enviroGDB.zip',
#     'hydroGDB.zip',
#     'natresGDB.zip',
#     'planningGDB.zip',
#     'politiclGDB.zip',
#     'propertyGDB.zip',
#     'pubsafeGDB.zip',
#     'recreatnGDB.zip',
#     'surveyGDB.zip',
#     'topoGDB.zip',
#     'transportationGDB.zip',
#     'utilityGDB.zip'
# ]

# TODO: this should read from a text file, like a simple config
# list all of the themes, and comment out the ones you don't
# want to download.

zip_list = ['districtGDB.zip']

# TODO: catch errors
ftp = FTP('ftp.kingcounty.gov')  # this also calls connect
ftp.login()  # anonymous login
ftp.cwd('gis-web/GISData/')


# Progress bar copied from here and very slightly modified:
# https://stackoverflow.com/questions/3160699/python-progress-bar
def update_progress(progress):
    barLength = 10  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done.\r\n"
    block = int(round(barLength * progress))
    text = "\rProgress: [{0}] {1:03.1f}% {2}".format(
        "#" * block + "-" * (barLength - block), progress * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()


# This is the callback function for the FTP retrieval.
def download_file(block):
    local_file.write(block)
    update_progress(local_file.tell() / totalSize)


for zipf in zip_list:
    try:
        totalSize = ftp.size(zipf)
        # sizeWritten = 0
        with open(zipf, 'wb') as local_file:
            ftp.retrbinary("RETR " + zipf, download_file)
            local_file.close()
    except Exception:
        print("whoops")

ftp.close()

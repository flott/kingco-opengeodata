#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches zipped file geodatabases from King County's FTP server
and organizes the contents.
"""

from ftplib import FTP
import os
import sys
import argparse

# These are the standard thematic geodatabases
# excluding the topographic contour lines.
themes = [
    'admin',
    'census',
    'district',
    'enviro',
    'hydro',
    'natres',
    'planning',
    'politicl',
    'property',
    'pubsafe',
    'recreatn',
    'survey',
    'topo',
    'transportation',
    'utility'
]

# parse the arguments from the command line
parser = argparse.ArgumentParser(
    description='Download and organize thematic file geodatabases.')

parser.add_argument(
    'out_dir', nargs='?', type=str, default=os.getcwd(),
    help='Destination directory')

parser.add_argument('--themes', nargs='+', choices=themes,
        metavar='theme1 theme2',
        help='List of themes to themes to download.' + \
                'Choose from ' + ', '.join(themes))

parser.add_argument('--theme-file', type=str,
                    help='file with list of themes to download')

args = parser.parse_args()

if args.themes:
    themes = args.themes

if args.theme_file:
    with open(args.theme_file) as f:
        tlist = f.read().splitlines()
        tlist_filtered = filter(None, [line for line in tlist if not(line.startswith('#'))])
    # make sure it's only themes that are actually available.
    themes = [t for t in tlist_filtered if t in themes]

# TODO: catch errors in FTP
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


for theme in themes:
    print('Downloading ' + theme)
    zipf = theme + 'GDB.zip'
    try:
        totalSize = ftp.size(zipf)
        print(totalSize)
        with open(os.join(args.out_dir,zipf), 'wb') as local_file:
            ftp.retrbinary("RETR " + zipf, download_file)
            local_file.close()
        pass
    except Exception:
        print("Error.")

ftp.close()

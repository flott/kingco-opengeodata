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
from zipfile import ZipFile
import shutil

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
    'out_dir', nargs='?', type=str, default='.',
    help='Destination directory')

parser.add_argument('--themes', nargs='+', choices=themes,
        metavar='THEME_NAME',
        help='List of themes to themes to download. ' + \
                'Choose from ' + ', '.join(themes))

parser.add_argument('--theme-file', type=str,
                    help='text file with list of themes to download')

args = parser.parse_args()

if args.themes:
    themes = args.themes

if args.theme_file:
    with open(args.theme_file) as f:
        tlist = f.read().splitlines()
        tlist_filtered = filter(None, [line for line in tlist if not(line.startswith('#'))])
    # make sure it's only themes that are actually available.
    themes = [t for t in tlist_filtered if t in themes]

# switch the working directory to the download location
out_dir = os.path.abspath(args.out_dir)
if not os.path.isdir(out_dir):
    os.makedirs(out_dir) 
os.chdir(out_dir)

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

# Make a zip folder if it doesn't exist. Move there
zip_dir = os.path.join(out_dir,'zip')
if not os.path.isdir(zip_dir):
    os.makedirs(zip_dir)

for theme in themes:
    print('Downloading ' + theme)
    zipf = theme + 'GDB.zip'
    try:
        totalSize = ftp.size(zipf)
        with open(os.path.join(zip_dir,theme + 'GDB.zip'), 'wb') as local_file:
            ftp.retrbinary("RETR " + zipf, download_file)
            local_file.close()
    except Exception:
        print("Error.")

ftp.close()

# Unzip and move files
gdb_dir = os.path.join(out_dir,'gdb')
if not os.path.isdir(gdb_dir):
    os.makedirs(gdb_dir)

for theme in themes:
    print('Extracting ' + theme)
    # zip file that was just downloaded
    zipf = os.path.join(zip_dir, theme + 'GDB.zip')
    # name of the GDB inside that zip file
    zip_gdb = 'KingCounty_GDB_' + theme + '.gdb/'
    # local destination for the GDB contents
    local_gdb = os.path.join(gdb_dir, theme + '.gdb/')

    if not os.path.isdir(local_gdb):
        os.makedirs(local_gdb)

    with ZipFile(zipf, 'r') as gdbzip:
        for f in gdbzip.namelist():
            if f.startswith(theme + 'GDB/' + zip_gdb):
                gdbf = os.path.split(f)
                # TODO: find better way to skip directory
                if gdbf[1]:
                    src = gdbzip.open(f)
                    with open(local_gdb + gdbf[1], 'wb') as dest:
                        shutil.copyfileobj(src,dest)

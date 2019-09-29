#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads a directory of geopackages and
merges all of the files into a single output geopackage.
"""

# Requires Python 3.5+
# This is just doing an ogr2ogr call again.
# It could be a shell script, but this is cross-platform.

# standard imports
import argparse
import os
import glob
import subprocess

# set some overall ogr2ogr options
opts_ogr2ogr = ["-progress",
                "-f", "GPKG",
                "-a_srs", "EPSG:2926",
                "-append"]

# geopackage driver options
opts_gpkg = ["-dsco", "VERSION=1.2",
             "-lco", "OVERWRITE=YES",
             "-gt", "65536"]


# parse the arguments from the command line
parser = argparse.ArgumentParser(
    description='Merge a directory of geopackages to a single output.')

parser.add_argument('src_dir', type=str,
                    help='Source directory of geopackages')

# this output should either be a directory or a PostgreSQL endpoint
parser.add_argument('dest_gpkg', type=str, help="""Path to output
                    geopackage file.
                    """)

args = parser.parse_args()

# clean this up so they're standardized
src = os.path.abspath(args.src_dir)
dest = os.path.abspath(args.dest_gpkg)

if not os.path.isdir(src):
    raise ValueError('Source directory does not exist.')

gpkg_paths = glob.glob(os.path.join(src, "*.gpkg"))
if not gpkg_paths:
    raise ValueError('No geopackages found in source directory.')

if os.path.exists(dest):
    print('Destination geopackage exists.')

for gpkg in gpkg_paths:
    subprocess.run(["ogr2ogr"] + opts_ogr2ogr + opts_gpkg
                    + [dest, gpkg])

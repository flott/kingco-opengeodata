#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads an Esri file geodatabase and writes the contents
to GeoPackage or PostGIS.
Input is the path to a source FileGDB.
Output is either a file or directory of GeoPackages or PostGIS tables.
"""

# standard imports
import argparse
import os
import glob
import fiona


# this will be the function for a single input and output feature
def convert_gdb(gdb, feature):
    """
    constructs the ogr2ogr command to convert a single feature.
    """
    c = fiona.open(gdb, layer=feature)
    print(c.schema['geometry'])
    if c.schema['geometry']:
        print(c.crs['init'])
    # clean close
    c.close()


# parse the arguments from the command line
parser = argparse.ArgumentParser(
    description='Convert a FileGDB to GeoPackage.')

# TODO: will check this with glob
parser.add_argument('in_gdb', type=str,
                    help='Source FileGDB file or directory')

# this output should either be a directory or a PostgreSQL endpoint
parser.add_argument(
    'out_dir', type=str, help='Destination directory for GeoPackages')

# expected behavior: make one geopackage per feature.
# if postgis, ignore? or don't import to a schema
# and prefix with the gdb name
parser.add_argument(
    '-s',
    '--splitgdb',
    action='store_true',
    help='Export each FileGDB feature class to a separate GeoPackage')

# might be a bad idea as an optional argument because
# of potential name conflicts
parser.add_argument(
    '-p',
    '--noprefix',
    action='store_true',
    help='Remove the source FileGDB name prefix on output gpkg')

args = parser.parse_args()

# Check paths to see if input is a directory or a single geodatabase.
# File geodatabases are directories on the file system.

# clean these up so they're standardized
in_gdb = os.path.abspath(args.in_gdb)
out_dir = os.path.abspath(args.out_dir)

# Make output directory if it doesn't exist
if not os.path.isdir(out_dir):
    raise ValueError("Output directory does not exist.")
    # print("Output directory does not exist. Creating it.")
    # os.mkdir(out_dir)

# Check the input location to see if it's a single gdb or a directory
if in_gdb.lower().endswith(".gdb"):
    gdb_list = [in_gdb]
else:
    # just search within the one directory. don't do a recursive search.
    gdb_list = glob.glob(os.path.join(in_gdb, "*.gdb"))
    if not gdb_list:
        raise ValueError('No file geodatabases found at this location.')

# loop through all features in all gdbs
for gdb in gdb_list:
    for layer in fiona.listlayers(gdb):
        print("processing", layer)
        convert_gdb(gdb, layer)

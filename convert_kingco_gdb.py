#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads an Esri file geodatabase and writes the contents
to GeoPackage or PostGIS.
Input is the path to a source FileGDB.
Output is either a file or directory of GeoPackages or PostGIS tables.
"""


# standard imports
import sys
import argparse
import os
import sys
import glob
import fiona

# parse the arguments from the command line
parser = argparse.ArgumentParser(
    description='Convert a FileGDB to GeoPackage.')

# TODO: will check this with glob
parser.add_argument('in_gdb', type=str, help='Input FileGDB file or directory')

# this output should either be a directory or a PostgreSQL endpoint
parser.add_argument(
    'out_dir', type=str, help='Output directory for GeoPackages')

# expected behavior: make one geopackage per feature.
# if postgis, ignore? or don't import to a schema and prefix with the gdb name
parser.add_argument(
    '-s',
    '--splitgdb',
    action='store_true',
    help='Export each FileGDB feature class to a separate GeoPackage')

# might be a bad idea as an optional argument because of potential name conflicts
parser.add_argument(
    '-p',
    '--noprefix',
    action='store_true',
    help='Remove the source FileGDB name prefix on output gpkg')

args = parser.parse_args()

# Check paths to see if input is a directory or a single geodatabase.
# File geodatabases are directories on the file system.

# clean these up so they're standardized
in_gdb = os.path.abspath(in_gdb)
out_dir = os.path.abspath(out_dir)

# Make output directory if it doesn't exist
if not os.path.isdir(out_dir):
    print("Output directory does not exist. Creating it.")
    os.mkdir(out_dir)

# Check the input location to see if it's a single gdb or a directory




if splitgdb:

    # Only need to load the ogr module if going feature by feature.

    # import OGR
    from osgeo import ogr

    # use OGR specific exceptions
    ogr.UseExceptions()

    # get the driver
    driver = ogr.GetDriverByName("OpenFileGDB")

    # opening the FileGDB
    try:
        gdb = driver.Open("./adminGDB/KingCounty_GDB_admin.gdb", 0)
    except Exception, e:
        print e
        sys.exit()

# list to store layers'names
featsClassList = []

# parsing layers by index
print "here come the features"
for featsClass_idx in range(gdb.GetLayerCount()):
    featsClass = gdb.GetLayerByIndex(featsClass_idx)
    print ogr.GeometryTypeToName(featsClass.GetGeomType())
    featsClassList.append(featsClass.GetName())

# sorting
featsClassList.sort()

# printing
for featsClass in featsClassList:
    print featsClass

# clean close
del gdb

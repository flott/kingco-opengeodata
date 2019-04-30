#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads an Esri file geodatabase and writes the contents
to GeoPackage or PostGIS.
Input is the path to a source FileGDB.
Output is either a file or directory of GeoPackages or PostGIS tables.
"""

# Goal is to assemble ogr2ogr commands.
# https://www.gdal.org/ogr2ogr.html
# https://www.gdal.org/ogr_utilities.html
#   This mentions general command line switches
#   --optfile file: Read the named file and substitute the contents into the
#   command line options list. Lines beginning with # will be ignored.
#   Multi-word arguments may be kept together with double quotes.
#
# https://www.gdal.org/drv_openfilegdb.html
# It can also read directly zipped .gdb directories (with .gdb.zip extension),
# provided they contain a .gdb directory at their first level.
# Alas, that's not how the KCGIS zip files are set up.
#
# https://www.gdal.org/drv_geopackage.html
#   Options: -dsco VERSION=1.2   # forget geopackage version 1.2
#            -lco OVERWRITE=YES  # overwrite existing layers w/the same name.
# https://www.gdal.org/drv_pg.html
# https://www.gdal.org/drv_pg_advanced.html
#
# These are the possible scenarios:
#
# 1. GPKG (single)
#    Just need the theme name.
#    ogr2ogr -f "GPKG" -progress -dsco VERSION=1.2 admin.gpkg admin.gdb
#    other potential options:
#    -lco OVERWRITE=YES  # to overwrite existing layers with the same name.
#
# 2. GPKG (multiple)
#    call this with the splitgdb option
#    need to use fiona to get the list of layers in the gdb.
#    output gpkg name is theme_layer.gpkg
#    gdb references is theme.gdb layer
#    ogr2ogr -f "GPKG" -progress -dsco VERSION=1.2
#       admin_address_point.gpkg admin.gdb address_point
#
# 3. PostGIS (single schema)
#    Behaves like the multiple gpkg option. Add theme prefix to table name.
#
# 4. PostGIS (multiple schema)
#    Create the schema ahead of time. Loop through themes, select schema,
#    export each layer to that schema. See below.
#
# SCHEMA: Set name of schema for new table. Using the same layer name in
# different schemas is supported, but not in the public schema and others.
# Note that using the -overwrite option of ogr2ogr and -lco SCHEMA= option
# at the same time will not work, as the ogr2ogr utility will not understand
# that the existing layer must be destroyed in the specified schema.
# Use the -nln option of ogr2ogr instead, or better the
# active_schema connection string. See below example.
# If you need to overwrite many tables located in a schema at once,
# the -nln option is not the more appropriate, so it might be more
# convenient to use the active_schema connection string
# (Starting with GDAL 1.7.0). The following example will overwrite,
# if necessary, all the PostgreSQL tables corresponding to a set of
# shapefiles inside the apt200810 directory :
# ogr2ogr -overwrite -f PostgreSQL "PG:dbname=warmerda
#   active_schema=apt200810" apt200810


# standard imports
import argparse
import os
import glob
import fiona


# this will be the function for a single input and output feature
def convert_gdb_feature(gdb, feature):
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
    description='Convert FileGDB data to GeoPackage or PostGIS format.')

parser.add_argument('in_gdb', type=str,
                    help='Source FileGDB file or directory')

parser.add_argument('format', type=str, choices=['gpkg', 'postgis'],
                    help='Output data format')

# this output should either be a directory or a PostgreSQL endpoint
parser.add_argument(
    'out_dir', type=str, help='Destination directory for GeoPackages')

# expected behavior: make one geopackage per feature.
# if postgis, ignore. it has to cycle through all layers regardless.
parser.add_argument(
    '-s',
    '--splitgdb',
    action='store_true',
    help='Export each FileGDB feature class to a separate GeoPackage')

# might be a bad idea as an optional argument because
# of potential name conflicts
# parser.add_argument(
#     '-p',
#     '--noprefix',
#     action='store_true',
#     help='Remove the source FileGDB thematic name prefix on output gpkg')

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
        convert_gdb_feature(gdb, layer)

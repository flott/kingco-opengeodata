#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads an Esri file geodatabase and writes the contents
to GeoPackage or PostGIS.
Input is the path to a source FileGDB.
Output is either a file or directory of GeoPackages or PostGIS tables.
"""
# Requires Python 3.5+

# Goal is to assemble ogr2ogr commands.
# ==== OGR2OGR ====
# https://www.gdal.org/ogr2ogr.html
# https://www.gdal.org/ogr_utilities.html
#   This mentions general command line switches
#   --optfile file: Read the named file and substitute the contents into the
#   command line options list. Lines beginning with # will be ignored.
#   Multi-word arguments may be kept together with double quotes.
#   Global ogr2ogr options for all scenarios:
#   [GLOBAL OPTIONS]
#   -progress
#   -a_srs EPSG:2926
#   -overwrite
#   -nlt CONVERT_TO_LINEAR
#
# https://www.gdal.org/drv_openfilegdb.html
#   It can also read directly zipped .gdb directories
#   (with .gdb.zip extension), provided they contain a .gdb
#   directory at their first level.
#   Alas, that's not how the KCGIS zip files are set up.
#
# ==== GEOPACKAGES ====
# https://www.gdal.org/drv_geopackage.html
#   [GPKG OPTIONS]
#   Options: -dsco VERSION=1.2   # force geopackage version 1.2
#            -lco OVERWRITE=YES  # overwrite existing layers w/the same name.
#            -gt 65536
#   from the docs: for SQLite, explicitly defining -gt 65536 ensures
#   optimal performance while populating some table containing many
#   hundreds of thousands or millions of rows.
#   However, note that -skipfailures overrides -gt
#   and sets the size of transactions to 1.
#
# ==== POSTGIS ====
# https://www.gdal.org/drv_pg.html
# https://www.gdal.org/drv_pg_advanced.html
#   [PG OPTIONS]
#   -lco SPATIAL_INDEX=YES
#   PG:"dbname=databasename host=addr port=5432
#       user=x password=y active_schema=public"
#   active_schema will be required for proper overwrite functionality
#   (see below), but will be set as 'public' if not entered.
#   Can save credentials in a ~/.pgpass file (preferred).
#   On Windows store it in %APPDATA%\postgresql\pgpass.conf
#   .pgpass must have 0600 or stricter permissions
#   hostname:port:database:username:password
#   Or set environment variables if you only connect to one thing.
#   See https://www.postgresql.org/docs/current/libpq-envars.html
#
# These are the possible scenarios (global options listed above):
#
# 1. GPKG (single)
#    Just need the theme name. Does a full convert without layer loop.
#    ogr2ogr -f GPKG [GLOBAL OPTIONS] [GPKG OPTIONS] admin.gpkg admin.gdb
#
# 2. GPKG (multiple)
#    Do this when --split==True
#    Need to use fiona to get the list of layers in the gdb.
#    Output gpkg name is LAYERNAME.gpkg
#    gdb references is theme.gdb layer
#    ogr2ogr -f GPKG [GLOBAL OPTIONS] [GPKG OPTIONS]
#       address_point.gpkg admin.gdb address_point
#
# 3. PostGIS (single schema)
#    Sends all GDB features to a single PostGIS db/schema
#    Will require the -nln flag to rename the output layer.
#    Probably not necessary unless there is a name conflict.
#    ogr2ogr -f PostgreSQL [GLOBAL OPTIONS] [PG OPTIONS]
#       admin.gdb
#
# 4. PostGIS (multiple schema)
#    Called when --split==True
#    Create the schemas ahead of time. (ex: CREATE SCHEMA yourschema;)
#    Loop through themes, set active_schema, export theme layers.
#    This will create a table with the same name as the input layer.
#    Can point this to a single GDB and it'll export everything
#    ogr2ogr -f PostgreSQL [GLOBAL OPTIONS] [PG OPTIONS]
#       admin.gdb
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
import re
import subprocess

# set some overall ogr2ogr options
opts_ogr2ogr = ["-progress", "-a_srs", "EPSG:2926",
                "-overwrite", "-nlt", "CONVERT_TO_LINEAR"]
# geopackage driver options
opts_gpkg = ["-dsco", "VERSION=1.2", "-lco", "OVERWRITE=YES", "-gt", "65536"]
# postgresql/postgis driver options
opts_pg = []  # ["-lco", "SPATIAL_INDEX=GIST"]


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

parser.add_argument('src', type=str,
                    help='Source FileGDB or directory of FileGDBs')

parser.add_argument('format', type=str, choices=['GPKG', 'PostgreSQL'],
                    help='Output data format')

# this output should either be a directory or a PostgreSQL endpoint
parser.add_argument('dest', type=str, help="""Output location. For GeoPackage,
                    this is a destination directory. For PostgreSQL this is
                    a connection string with the following form:
                    "PG:dbname=databasename host=addr port=5432
                    user=x password=y active_schema=public"
                    Double quotes around the connection string are required.
                    If --split is used, the active schema will be changed
                    for each source geodatabase.
                    """)

# expected behavior: make one geopackage per feature.
# if postgis, ignore. it has to cycle through all layers regardless.
parser.add_argument(
    '-s',
    '--split',
    action='store_true',
    help="""Split the output. For GeoPackage, create one gpkg per feature.
         For PostGIS, send contents of each thematic GDB to its own schema.
         The schema name must already exist and match the theme name
         (e.g. admin, hydro, politicl).
         """)

args = parser.parse_args()

# Check paths to see if input is a directory or a single geodatabase.
# File geodatabases are directories on the file system.

# clean this up so they're standardized
src = os.path.abspath(args.src)

# Make output directory if it doesn't exist
if args.format == 'GPKG':
    if not os.path.isdir(os.path.abspath(args.dest)):
        print("Output directory does not exist. Creating it.")
        os.mkdir(os.path.abspath(args.dest))
    dest_path = os.path.abspath(args.dest)

# Check the input location to see if it's a single gdb or a directory
if src.lower().endswith(".gdb"):
    gdb_paths = [src]
else:
    # just search within the one directory. don't do a recursive search.
    gdb_paths = glob.glob(os.path.join(src, "*.gdb"))
    if not gdb_paths:
        raise ValueError('No file geodatabases found at this location.')

# For all except gpkg+split, fiona is not needed.
for gdb in gdb_paths:
    theme = os.path.splitext(os.path.basename(gdb))[0]
    print("Converting {}".format(theme))

    # gdb to gpkg
    if args.format == 'GPKG' and not args.split:
        subprocess.run(["ogr2ogr", "-f", args.format]
                       + opts_ogr2ogr + opts_gpkg
                       + [os.path.join(dest_path, theme + ".gpkg")]
                       + [gdb])

    # gdb to multiple gpkgs
    elif args.format == 'GPKG' and args.split:
        for layer in fiona.listlayers(gdb):
            print("Extracting {}".format(layer))
            subprocess.run(["ogr2ogr", "-f", args.format]
                           + opts_ogr2ogr + opts_gpkg
                           + [os.path.join(dest_path, layer + ".gpkg")]
                           + [gdb] + [layer])

    # gdb to one postgres schema
    elif args.format == 'PostgreSQL' and not args.split:
        subprocess.run(["ogr2ogr", "-f", args.format]
                       + opts_ogr2ogr + opts_pg
                       + [args.dest]
                       + [gdb])

    # gdb to multiple postgres schemas
    elif args.format == 'PostgreSQL' and args.split:
        pgconn = re.sub(r"active_schema=(\w+)",
                        "active_schema=" + theme, args.dest)
        subprocess.run(["ogr2ogr", "-f", args.format]
                       + opts_ogr2ogr + opts_pg
                       + [pgconn]
                       + [gdb])

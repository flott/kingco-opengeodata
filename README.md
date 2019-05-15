# kingco-opengeodata

Tools for converting [King County's public GIS data](https://www5.kingcounty.gov/gisdataportal/) into modern open source formats. It's essentially a wrapper for `ogr2ogr` to loop over multiple file geodatabases.

Requires GDAL/OGR 2.2+, Python 3.5+, and [Fiona](https://github.com/Toblerity/Fiona).

## 0. Why
King County produces tons of GIS data, and makes it all publicly available. However, the only output formats are Esri FileGDBs, shapefiles, and KMZ. None of these are ideal for open source geospatial work. While shapefiles are fairly universal, some King County datasets are not available as shapefiles due to format restrictions.

I wanted to make it easier for someone to download and process all of these datasets, and avoid tedious file management and repetitive calls to ogr2ogr.

For local, file-based use, there is [GeoPackage](http://www.geopackage.org/) output ([why GeoPackage?](http://switchfromshapefile.org/#geopackage)). For the other database folks, there is [PostGIS](https://postgis.net/) output.

## 1. Downloading and organizing the data

`get_kingco_gdbs.py` will download any of the available [themes](http://www5.kingcounty.gov/sdc/addl_doc/SDCSubjectAreaDescriptions.htm).


A [list of the layers](layer_list.md) inside the thematic FileGDBs and metadata links are available in `layer_list.md`.

For more information, see the [KCGIS Metadata page](https://www.kingcounty.gov/services/gis/GISData/metadata.aspx).

| Theme name | Content | Layers | Uncompressed Size 
|---|---|---:|---:|
| admin | Administrative | 14 | 303 MB
| census | Census boundaries and tables | 285 | 920 MB
| district | District boundaries | 23 | 28 MB
| enviro | Environmental | 35 | 1389 MB
| hydro | Hydrography | 25 | 100 MB
| natres | Natural Resources | 11 | 11 MB
| planning | Planning | 22 | 121 MB
| politicl | Political boundaries | 5 | 5 MB
| property | Property | 12 | 789 MB
| pubsafe | Public Safety | 9 | 82 MB
| recreatn | Recreation | 6 | 17 MB
| survey | Survey | 30 | 1048 MB
| topo | Topography | 2 | 519 MB
| transportation | Transportation | 96 | 1102 MB
| utility | Utilities | 15 | 34 MB

The script requires an output directory, and has three download options:

`--all` downloads all available themes. This is about 2 GB of zip files (6 GB uncompressed).

`--themes` takes a list of themes (e.g. `--themes admin hydro recreatn`)

`--theme-file` allows you to specify a text file (see example `themes.txt`) with a list of themes that you would like to download.

### Examples
- Download everything to ~/kcgis: `get_kingco_gdbs.py ~/kcgis/ --all` 
- Download just the census and political data: `get_kingco_gdbs.py  ~/kcgis/ --themes politicl census`
- Download all the themes listed in a text file: `get_kingco_gdbs.py  ~/kcgis/ --theme-list themes.txt`

## 2. Converting the data
`convert_kingco_gdbs.py` is the converstion script. It requires the following arguments:

`src` : Either a folder containing file geodatabases, or a path to a single geodatabase.

`GPKG` or `PostgreSQL` (case sensitive): Output format

`dest`: Output location. For GeoPackage, this is a destination directory. For PostgreSQL this is a connection string with the following form:                `"PG:dbname=databasename host=addr port=5432 user=x password=y active_schema=public"` Double quotes around the connection string are required. If `--split` is used (see below), the active schema will be changed for each source geodatabase. If you want the default setting for `active_schema`, use `public`.

(Optional, GeoPackage mode only) `-s, --split`: Split the output. For GeoPackage, create one gpkg per feature (this isn't especially useful, but you may want to isolate layers to share).

### Examples
- Convert all FileGDBs in a directory to GeoPackages: `convert_kingco_gdbs.py ~/kcgis/gdb GPKG ~/kcgis/gpkg`
- Do the same as above, but export every layer to its own gpkg: `convert_kingco_gdbs.py ~/kcgis/gdb GPKG ~/kcgis/gpkg --split`
- Send all geodatabase contents to PostGIS: `convert_kingco_gdbs.py ~/kcdata/gdb PostgreSQL "PG:dbname=myplibrary host=SAMPLE.dbhost.com port=5432 user=fred active_schema=plibrary password=XXXXX"` (See [pgpass docs](https://www.postgresql.org/docs/11/libpq-pgpass.html) if you don't want to enter your password on the command line)

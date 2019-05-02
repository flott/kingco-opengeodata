# kingco-opengeodata

Tools for converting [King County's public GIS data](https://www5.kingcounty.gov/gisdataportal/) into modern open source formats. It's essentially a wrapper for `ogr2ogr` to loop over multiple file geodatabases.

Requires GDAL/OGR 2.2+, Python 3.5+, and [Fiona](https://github.com/Toblerity/Fiona).

## 0. Why
King County produces tons of GIS data, and makes it all publicly available. However, the only output formats are Esri FileGDBs, shapefiles, and KMZ. None of these are ideal for open source geospatial work. While shapefiles are fairly universal, some King County datasets are not available as shapefiles due to format restrictions.

I wanted to make it easier for someone to download and process all of these datasets, and avoid tedious file management and repetitive calls to ogr2ogr.

For local, file-based use, there is [GeoPackage](http://www.geopackage.org/) output ([why GeoPackage?](http://switchfromshapefile.org/#geopackage)). For the other database folks, there is [PostGIS](https://postgis.net/) output.

## 1. Downloading and organizing the data

`get_kingco_gdbs.py` will download any of the available themes. More information and a full layer list is available on King County's [Data Portal](https://www5.kingcounty.gov/gisdataportal/) or [Metadata pages](https://www.kingcounty.gov/services/gis/GISData/metadata.aspx).

| Theme name | Content |
|---|---|
| admin | Administrative |
| census | Census boundaries and tables |
| district | District boundaries |
| enviro | Environmental |
| hydro | Hydrography |
| natres | Natural Resources |
| planning | Planning |
| politicl | Political boundaries |
| property | Property |
| pubsafe | Public Safety |
| recreatn | Recreation |
| survey | Survey |
| topo | Topography |
| transportation | Transportation |
| utility | Utilities |

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

# kingco-opengeodata

**This isn't ready to use yet!!!**

Tools for converting [King County's public GIS data](https://www5.kingcounty.gov/gisdataportal/) into modern open source formats. It's essentially a wrapper for `ogr2ogr` to loop over multiple file geodatabases.

## Downloading and organizing the data

`fetch_gdbs.py` will download any of the available themes:

- admin
- census
- district
- enviro
- hydro
- natres
- planning
- politicl
- property
- pubsafe
- recreatn
- survey
- topo
- transportation
- utility

The script takes an output directory, and has two optional arguments:
`--themes` takes a list of themes (e.g. `--themes admin hydro recreatn`)
`--theme-file` allows you to specify a text file (see example `themes.txt`) with a list of themes that you would like to download.

## ogr2ogr examples for reference
sample command for a single conversion:

`ogr2ogr -f "GPKG" -progress -dsco VERSION=1.2 admin.gpkg KingCounty_GDB_admin.gdb`

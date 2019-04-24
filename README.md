# kingco-opengeodata

**This isn't ready to use yet!!!**

Tools for converting King County's public GIS data into modern open source formats

## Downloading and organizing the data

`mkdir zip && cd zip`

download all the gdbs using `wget -i gdb_urls.txt`

and unzip all of them with `unzip \*.zip`

This makes a ton of folders with geodatabases inside, along with metadata.



`mkdir gdb`

`mkdir gpkg`

- navigate to top level folder
- move all of the gdbs to a single directory: 

    `find ./zip -name '*.gdb' -prune -exec mv {} ./gdb \;`


Rename all those gdbs so they're just called the simple names like "admin" or "hydro"

`rename -n 's/KingCounty_GDB_//' *.gdb`

or

`rename -n 's/KingCounty_GDB_(\w+)/$1/' *.gdb`

sample command for a single conversion:
`ogr2ogr -f "GPKG" -progress -dsco VERSION=1.2 admin.gpkg KingCounty_GDB_admin.gdb`

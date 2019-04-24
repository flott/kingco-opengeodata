# kingco-opengeodata

**this isn't ready to use yet**

Tools for converting King County's public GIS data into modern open source formats
`mkdir zip`
download all the gdbs using `wget -i gdb_urls.txt`
and unzip all of them with `unzip \*.zip`

This makes a ton of folders with geodatabases inside, along with metadata.
move all of the gdbs to a single directory
navigate to top level folder

`mkdir gdb`

`mkdir gpkg`

`find . - find ./zip -name '*.gdb' -prune -exec mv {} ./gdb \;name '*.gdb' -exec mv {} ./gdb \;`

`rename -n 's/KingCounty_GDB_//' *.gdb`

or

`rename -n 's/KingCounty_GDB_(\w+)/$1/' *.gdb`

sample command for a single conversion:
`ogr2ogr -f "GPKG" -progress -dsco VERSION=1.2 admin.gpkg KingCounty_GDB_admin.gdb`

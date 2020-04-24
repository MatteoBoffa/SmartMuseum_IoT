# IoT_project
Smart Museum

Notes to run the project
- the Catalog needs to be run first
- the Sensors folder is made of files to use true sensors placed on a Raspberry Pi and files use to simulate the behavior of such sensors
- each entity must know from its config file the @IP of the catalog (all files are provided with a custom one that can be easily modified)
- two databases are required: instructions on their names and tables' composition can be found in the DBs folder
- the provided version works with five Estimote Beacons whose MAC addresses are inserted inside one of the databases; to add some more or change them, it is just needed to modify such data in the DB

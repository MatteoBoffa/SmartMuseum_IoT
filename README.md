# IoT project: Smart Museum

Project for the management of a Smart Museum, with services for the visitors and for the museum's curators.
To have a full description of the functionalities and the structure of the system, take a look at the videos linked below.

Notes to run the project:
- all the entities needed for the functioning of the system are included in folders Catalog, DB_server, Servers, Broker, Sensors, bot_telegram
- the Freeboard pages can be easily built importing the two dashboards present in the folder Freeboard
- the Sensors folder is made of files to use true sensors placed on a Raspberry Pi and files use to simulate the behavior of such sensors
- each entity must know from its config file the IP address of the catalog (all files are provided with a custom one that can be easily modified)
- two SQL databases are required: instructions on their names and tables' composition can be found in the DBs folder
- the provided version works with five Estimote Beacons whose MAC addresses are inserted inside one of the databases; to add some more or change them, just modify such data in the DB

Videos:
- PROMO: https://www.youtube.com/watch?v=YgoPoyFLknk
- DEMO: https://www.youtube.com/watch?v=mky62tQ42YM 

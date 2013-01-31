#MapRoulette#
MapRoulette is an extremely addictive OpenStreetMap bug fixing tool.   

##Dependencies##
The web front end is self-contained, some resources are loaded from the web.

The supplied service example is written in Python and tested only on Python 2.7. It depends on:

* [web.py](http://webpy.org) 0.37
* [psycopg2](http://pypi.python.org/pypi/psycopg2)
* [geojson](http://pypi.python.org/pypi/geojson)
* [simplejson](http://pypi.python.org/pypi/simplejson)

It runs as a WSGI script under Apache, so you will also need to have [mod_wsgi](http://code.google.com/p/modwsgi/) installed and enabled.

The supplied database example is tested on PostgreSQL 9.1 with PostGIS 2.0.
  
##Installation##
_These instructions assume a Ubuntu 12 system, you may need to adapt for a different distro._

First, check out the repo to a local `maproulette` directory. The instructions and the config file templates assume that this directory lives in your home directory.

```
git clone https://github.com/mvexel/remapatron maproulette
cd maproulette
```

###1. Web front end###
The web front end can live anywhere as long as the directory and the files in it are readable by your web server. If you are using Apache 2.x, there is a config file you can use in the `extras/apache-config` directory. You will need to adapt the path names to suit your local path and load this file as part of your Apache configuration. You can create a symlink to this file in `/etc/apache/conf.d/`. After this, restart apache.

```
sudo ln -s /home/mvexel/maproulette/extra/apache-config/maproulette.conf /etc/apache2/conf.d
sudo service apache2 restart
```

Next, open `client/js/config.js` and check the URLs for the service hooks:
 
```
        geojsonserviceurl: 'http://localhost/mrsvc/get/',
        storeresulturl: 'http://localhost/mrsvc/store/',
        counturl: 'http://localhost/mrsvc/count/',
```

If you are using the provided example web service (see below), these paths are good to go. Otherwise, revisit this after you configured the web services.

###2. Services ###

You have two options: either you use the supplied example web service and database schema, or you create your own backend. _Note that the example database relies on some poorly documented views and functions, so this setup is not likely to be very useful for a production environment where you want to load your own challenges._


If you want to use your own backend, you will need to supply a web service with three endpoints, as described below under `get *Craft Your Own*. 

If you want to use the supplied service, you will need to make sure your Python environment has all the required modules, see above. Then, read on under *Use The Example*.  

####Option 1: Use The Example####

To use the example backend including a small number of example connectivity issues, follow these steps:

__Step 1__ Prepare your PostgreSQL environment

You will need to have PostrgreSQL 9.0+ installed and running. Also make sure that...

1. A database named `maproulette` does not already exist.
1. A PostgreSQL superuser `osm` exists (`createuser -s osm`)



__Step 2__ Create the example database on your PostgreSQL instance and load the demonstration data:

```
psql -f database/database.sql
psql -d osm -f  demodata.sql
```
This assumes that psql connects to the local PostgreSQL instance as a superuser by default. Adjust if necessary.

__Step 2__ Configure the web service

Open `service/get.py` and look for these lines near the top:

```
db = {
  'host': 'localhost', 
  'dbname': 'maproulette', 
  'user': 'osm', 
  'password': 'osm'
}
```

Change these to match your database connection if necessary.

__Step 3__ Test

Point your browser to `http://localhost/mrsvc/get/`. Replace `localhost` with the path to your MapRoulette install. You should get a GeoJSON response containing one LineString and one Point geometry, like this:

```
{"type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[-101.5193522, 50.0795685], [-101.5196494, 50.0792779]]}, "type": "Feature", "properties": {"id": 190387057}, "id": null}, {"geometry": {"type": "Point", "coordinates": [-101.5193522, 50.0795685]}, "type": "Feature", "properties": {"id": 2010227030}, "id": null}]}
```

Never mind the `null` values in there, this is OK. 

You can test the `/count` endpoint in a similar fashion by pointing your browser to `http://localhost/mrsvc/count`, this should yield a Javascript array not unlike this one:

```
[67, 0, 0]
``` 

The first number is the total number of errors remaining, the second is the number fixed in the last day, and the third represents the number of fixes in the last hour.

If this is all peachy, you can test your fresh MapRoulette installation by going to `http://localhost/maproulette/`.

Good luck and don't hesitate to ask if something is not working!

####Option 2: Craft Your Own####

___To be continued...___


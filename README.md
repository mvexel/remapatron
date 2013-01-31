#MapRoulette#
MapRoulette is an extremely addictive OpenStreetMap bug fixing tool. It runs at <http://maproulette.org/>. If you are a MapRoulette user and have ideas for future challenges, improvements or a bug report, please file them right here under [issues](https://github.com/mvexel/remapatron/issues).

If you want to install your own instance of MapRoulette, read on.

##Introduction##

MapRoulette consists of a web front end or client, and a backend consisting of a database to store the OSM bugs you want to expose as well as usage metrics. Between the database and the web front end sits a simple web service layer.

![MapRoulette High Level Architecture](https://www.dropbox.com/s/4ngbfjcn5yeg2sg/MapRouletteArchitecture.png?dl=1 "Maproulette High Level Architecture")

This repository provides the client as well as a (bad) example of the service and database layers. Bad, because the web service uses direct database calls that rely on a poorly documented database schema. But if you just want to see how it works, it's a start.

##Dependencies##
The web front end is self-contained, some resources ([jQuery](http://jquery.org/), [Leaflet](http://leafletjs.com)) are loaded from the web.

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

If you want to use your own backend, you will need to supply a web service connecting to your own database that has three endpoints, as described in the next chapter: *Craft Your Own*. 

If you want to use the supplied service, you will need to make sure your Python environment has all the required modules, see above. Then, continue below.

####Setting up the example database and services####

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

__Step 3__ Configure the web service

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

__Step 4__ Test

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

##Craft Your Own##
So you want to set up your very own MapRoulette back end? Great - if you come up with something reusable and scalable, please consider submitting it to this repository. So whatever you do next, we encourage you to create your own fork of MapRoulette first.

You will need to design and implement a _database_ and the _service layer_. The database can be anything really, as long as your service layer can talk to it. A spatial database is probably most convenient, as you will be storing points and perhaps also linestrings, and in the future MapRoulette may support finding errors nearby so users can focus on specific regions. PostgreSQL + PostGIS is an obvious choice.

###Database###

The database needs to store two things: the bugs and the user activity. 

####Bugs####
MapRoulette support two types of bugs at this time. The simplest bug type is represented by a single point, corresponding to the affected OSM node. The bug table should contain at least the point geometry (or lon / lat in separate columns) and the OSM ID. You may also want to store the OSM tags, MapRoulette will support [popups](http://leafletjs.com/reference.html#popup) soon that would display any attributes attached to the bug.

The other type of bug currently supported has two geometries: one linestring and one point. This is useful for bugs that affect a particular node along a way. In that case, both geometries (point and line) as well as both OSM IDs need to be in the table.

This table needs to be updated regularly from the main OSM database, otherwise errors that have long been fixed will keep showing up. In the main MapRoulette instance, the table is updated every four hours.

####User Activity####
MapRoulette stores the various types of user activity for two reasons. The first is metrics: MapRoulette displays counts in its own interface, and longer term metrics may be derived from the database. The second is to flag errors as fixed between table updates. This feedback is stored as a fix flag, which is an integer value. The value increments as an error is more likely to no longer exist. There are six user activity that affect the fix flag, as set in `client/js/config.js`:

```
  fixflag: {
		fixed: 100,
		notfixed: 0,
		someonebeatme: 100,
		noerrorafterall: 100,
		falsepositive: 1,
		skip: -1   
	}
```

The idea is that you would select the next bug for the user to fix out of the current table with the condition that the fix flag is smaller than a certain threshold. In the main MapRoulette instance, this threshold is 3. _This is an underdeveloped concept in MapRoulette, we would love to see ideas for how to improve on it._

###Service Endpoints###

The MapRoulette client accesses the database through three service endpoints as described below.

####/get####
`HTTP HEAD`
`No parameters`

This parameterless endpoint gets the next bug. It returns the object as GeoJSON in the following form:

```
{"type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[-101.5193522, 50.0795685], [-101.5196494, 50.0792779]]}, "type": "Feature", "properties": {"id": 190387057}, "id": null}, {"geometry": {"type": "Point", "coordinates": [-101.5193522, 50.0795685]}, "type": "Feature", "properties": {"id": 2010227030}, "id": null}]}
```

This example assumes a challenge that incorporates a linestring and a point. For point-only challenges, you would return a FeatureCollection with only one single Point geometry. 

It is up to you how you determine what the 'next' challenge is. You may pick a random record from the database, but `ORDER BY RANDOM()` in PostgreSQL is notoriously slow with larger tables as it needs to perform a sequential scan of the table. You will need to make sure that no two parallel users are presented with the same bug to fix, as this may lead to editing conflicts in the OSM database and general confusion.

####/count#####
`HTTP HEAD`
`No parameters`

This endpoint gets the counts to update the client UI and returns a JS Array of the following form:

`[total_remaining, fixed_last24h, fixed_lasthour]`

####/store####
`HTTP PUT`
`Parameters: OSM ID, fix flag increment`

This endpoint stores the user activity when any of the six user activity types occur in the client. It takes the OSM ID of the current bug in the client as well as the increment (which could be negative) in the fix flag. This should trigger a database insert or update.

Example:

`http://localhost/mrsvc/store/168894038/1` 

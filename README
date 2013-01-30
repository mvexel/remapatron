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
First, check out the repo to a local `maproulette` directory. The instructions and the config file templates assume that this directory lives in your home directory.

`git clone https://github.com/mvexel/remapatron maproulette`

###1. Web front end###
The web front end can live anywhere as long as the directory and the files in it are readable by your web server. If you are using Apache 2.x, there is a config file you can use in the `extras/apache-config` directory. You will need to adapt the path names to suit your local path and load this file as part of your Apache configuration. If you are on Ubuntu, you can create a symlink to this file in `/etc/apache/conf.d/`. 

Next, you will want to open `client/js/config.js` and check the paths to the service hooks:
 
```
        geojsonserviceurl: 'http://localhost/mrsvc/get/',
        storeresulturl: 'http://localhost/mrsvc/store/',
        counturl: 'http://localhost/mrsvc/count/',
```

If you are using the provided example web service (see below), these paths are good to go. Otherwise, revisit this after you configured the web services.

###2. Services ###

You have two options: either you use the supplied example web service and database schema, or you create your own backend. 

If you want to use your own backend, you will need to supply a web service with three endpoints, as described below under `get *Craft Your Own*. 

If you want to use the supplied service, you will need to make sure your Python environment has all the required modules, see above. Then, read on under *Use The Example*.  

####Use The Example####
The apache configuration file mentioned before takes care 

####Craft Your Own####
 

###3. Database ###
If you want to use the example database, you will need PostrgreSQL 9.1+ and PostGIS 2.0+ installed. 

Everything needed to create the demo database (except for data) is in `database/database.sql` which you can just load using psql. There are two prerequisites:

1. A database named `maproulette` must not already exist.
1. A PostgreSQL superuser `osm` must exist (`createuser -s osm`)


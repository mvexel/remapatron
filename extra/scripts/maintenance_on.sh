#!/bin/sh
mv /osm/software/remapping-microtask/webapp/index.html /osm/software/remapping-microtask/webapp/index0.html
mv /osm/software/remapping-microtask/webapp/index-maintenance.html /osm/software/remapping-microtask/webapp/index.html
psql -U osm -d deletedways -c 'SELECT update_remapping_status()' >> /osm/software/remapping-microtask/log.txt

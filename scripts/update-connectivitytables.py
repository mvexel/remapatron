#!/usr/bin/python
import os
import sys
import shutil
from datetime import datetime
import subprocess
from time import gmtime, strftime
import argparse

appath = '/home/ubuntu/mr-conn/client'
indexname = 'index.html'
tempindexname = 'index_t.html'
maintindexname = 'index_m.html'
workpath = '/mnt/mr_data'
frequency = 3600 # seconds, every hour
psql = 'psql'
pghost = 'localhost'
pgrestore = 'pg_restore'
pguser = 'osm'
pgdb = 'maproulette'
pgpass = 'osm'
tables = {'tnav_connectivity_errors': 'osm_planet.dump', 'tnav_ways_no_lanes': 'ways_no_lanes.dump'}
pgrestorecommand = '%s -h %s -U %s -d %s -a' % (pgrestore, pghost, pguser, pgdb)
psqlcommand = '%s -h %s -U %s -d %s -c' % (psql, pghost, pguser, pgdb)

parser = argparse.ArgumentParser()
parser.add_argument('--force', help='force execution regardless time passed', action='store_true')
args = parser.parse_args()

def logline(txt):
    print '%s\t%s' % (strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()), txt)

def maint_on():
    logline('putting maproulette into maintenance mode...')
    shutil.move(os.path.join(appath,indexname), os.path.join(appath,tempindexname))
    shutil.move(os.path.join(appath,maintindexname), os.path.join(appath,indexname))

def maint_off():
    # exit maintenance mode
    logline('restoring maproulette pages...')
    shutil.move(os.path.join(appath, indexname), os.path.join(appath,maintindexname))
    shutil.move(os.path.join(appath, tempindexname), os.path.join(appath,indexname))

t = 0.0
files = os.listdir(workpath)

# first check if the index and index_m html files exist
if not (os.path.exists(os.path.join(appath,indexname)) and os.path.exists(os.path.join(appath,maintindexname))):
    logline('index and maintenance index do not exist, script probably exited in incomplete state previously')
    sys.exit(1)

# get the timestamp for the latest postgres dump file
for f in files:
    if f.endswith('.dump'):
        t = max(t, os.path.getmtime(os.path.join(workpath, f)))

# if the timstamp is longer go than the frequency, process.
if (datetime.now() - datetime.fromtimestamp(t)).seconds < frequency or args.force:
    # put maproulette into maintenance mode
    maint_on()
    # truncate table
    try:
        logline('truncating tables...')
        for tablename, dumpname in tables.iteritems():
            if not os.path.exists(os.path.join(workpath,dumpname)):
                logline('dump file %s not found, exiting' % (dumpname))
                maint_off()
            logline('truncating %s' % (tablename))
            subprocess.call(psqlcommand.split() + ['TRUNCATE %s' % (tablename)])
            # load new data
            logline('loading new data...')
            subprocess.call(pgrestorecommand.split() + [os.path.join(workpath, dumpname)])
            sys.stdout.flush()
    finally:
        logline('done.')
        maint_off()
        sys.stdout.flush()
else:
    logline('no newer files.')

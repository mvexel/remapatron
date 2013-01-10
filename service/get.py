import sys
import web
import psycopg2
import geojson
import simplejson as json
from datetime import datetime

pg_host = 'localhost'
pg_dbname = 'maproulette'
pg_user = 'osm'
pg_password = 'osm'

pg_connstr = "host=%s dbname=%s user=%s password=%s" % (pg_host, pg_dbname, pg_user, pg_password)

urls = (
    '/count/', 'getcount',
    '/store/(.*)/(-*\d+)', 'storeresult',
    '/get/', 'getcandidate'
)

sys.stdout = sys.stderr

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

class getcandidate:        
    def GET(self):
        conn = psycopg2.connect(pg_connstr)
        cur = conn.cursor()
        cur.execute("SELECT * FROM mr_getsomenolaneways()")
        recs = cur.fetchall()
        features = []
        for rec in recs:
          (osmid,gj) = rec
          features.append(geojson.Feature(osmid, geojson.loads(gj), {'id':osmid}))
          cur.execute("SELECT mr_setlocked(%s, %s)", (datetime.now(), osmid,))
        conn.commit()
        cur.close()
        return geojson.dumps(geojson.FeatureCollection(features))

class storeresult:        
    def PUT(self,osmid,amt):
        conn = psycopg2.connect(pg_connstr)
        cur = conn.cursor()
        if not osmid:
            return web.badrequest();
        try:
            cur.execute("SELECT mr_upsert(%s,%s)", (amt,osmid,))
            cur.execute("SELECT mr_setlocked(%s, %s)", (datetime.now(), osmid,))
            conn.commit()
        except Exception, e:
            print e
            return web.badrequest()
        finally:
            cur.close()
        return True

class getcount:
    def GET(self):
        result = []
        conn = psycopg2.connect(pg_connstr)
        cur = conn.cursor()
        cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from mr_currentchallenge WHERE type = 'motorway' AND fixflag < 3))")
        conn.commit()
        cur.execute("select * from remapathonresults order by tstamp desc limit 1")
        rec = cur.fetchone()
        result.append(rec[1])
        cur.execute("select mr_donesince(1)")
        result.append(cur.fetchone()[0])
        cur.execute("select mr_donesince(24)")
        result.append(cur.fetchone()[0])
        cur.close()
        return json.dumps(result)
        
if __name__ == "__main__":
    app.run()

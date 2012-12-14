import sys
import web
import psycopg2
import geojson
import simplejson as json

urls = (
    '/count/', 'getcount',
    '/store/(.*)/(-*\d+)', 'storeresult',
    '/get/(.*)', 'getcandidate'
)

sys.stdout = sys.stderr

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

class getcandidate:        
    def GET(self,osmid):
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        if osmid:
            cur.execute("SELECT ST_AsGeoJSON(geom), osmid FROM mr_currentchallenge WHERE osmid = %s", (osmid,))
        else:
            cur.execute("SELECT ST_AsGeoJSON(geom), osmid FROM mr_untaggedwayschallenge WHERE fixflag < 3 ORDER BY RANDOM() LIMIT 1")
        recs = cur.fetchall()
        (way,wayid) = recs[0]
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid})])
        return geojson.dumps(out)

class storeresult:        
    def PUT(self,osmid,amt):
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        if not osmid:
            return web.badrequest();
        try:
            cur.execute("SELECT mr_upsert(%s,%s)", (amt,osmid,))
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
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from mr_currentchallenge WHERE fixflag < 3))")
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

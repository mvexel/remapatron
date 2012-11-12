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
            cur.execute("SELECT ST_AsGeoJSON(geom_way), osmid_way, ST_AsGeoJSON(geom), osmid FROM mr_currentchallenge WHERE osmid = %s", (osmid,))
        else:
            cur.execute("SELECT ST_AsGeoJSON(geom_way), osmid_way, ST_AsGeoJSON(geom), osmid FROM mr_currentchallenge WHERE fixflag < 3 ORDER BY RANDOM() LIMIT 1")
        recs = cur.fetchall()
        (way,wayid,point,nodeid) = recs[0]
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid}),geojson.Feature(geometry=geojson.loads(point),properties={"id": nodeid})])
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
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from mr_currentchallenge WHERE fixflag < 3))")
        conn.commit()
        cur.execute("select * from remapathonresults order by tstamp desc limit 1")
        rec = cur.fetchone()
        cur.close()
        return json.dumps(rec[1:])
        
if __name__ == "__main__":
    app.run()

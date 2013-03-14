import sys
import web
import psycopg2
import geojson
import simplejson as json

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
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        cur.execute("SELECT ST_AsGeoJSON(linestring), id  FROM mr_ways_no_lanes_challenge WHERE NOT done AND (current_timestamp - donetime) > '1 hour' LIMIT 1")
        recs = cur.fetchall()
        (way,wayid) = recs[0]
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid})])
        return geojson.dumps(out)

class storeresult:        
    def PUT(self,osmid,done):
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        if not osmid:
            return web.badrequest();
        try:
            cur.execute("SELECT mr_upsert(%s::boolean,%s)", (done,osmid))
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
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        #cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from mr_currentchallenge WHERE fixflag < 3), 1)")
        #conn.commit()
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 hour' and done")
        result.append(cur.fetchone()[0])
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 day' and done")
        result.append(cur.fetchone()[0])
        cur.close()
        return json.dumps(result)
        
if __name__ == "__main__":
    app.run()

import sys
import web
import psycopg2
import geojson

urls = (
    '/(.*)/(-*\d)', 'getcandidate',
    '/count', 'getcount',
    '/(.*)', 'getcandidate'
)

sys.stdout = sys.stderr

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

class getcandidate:        
    def GET(self,wayid):
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        if wayid:
            cur.execute("SELECT ST_AsGeoJSON(linestring), id, tags->'highway' FROM deletedways WHERE id = %s", (wayid))
        else:
            cur.execute("SELECT ST_AsGeoJSON(linestring), id, tags->'highway' FROM deletedways WHERE likelyremapped = false AND tags->'highway' IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary') AND remappedflag < 3 ORDER BY RANDOM() LIMIT 1")
        recs = cur.fetchall()
        (gj,wayid,waytype) = recs[0]
        out = geojson.Feature(geometry=geojson.loads(gj),properties={"id": wayid, "type": waytype})        
        return geojson.dumps(out)

    def PUT(self,wayid,amt):
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        if not wayid:
            return web.badrequest();
        try:
            print "UPDATE deletedways SET remappedflag = remappedflag + %s WHERE id = %s" % (amt,wayid)
            cur.execute("UPDATE deletedways SET remappedflag = remappedflag + %s WHERE id = %s", (amt,wayid,))
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
        cur.execute("SELECT count(1) FROM deletedways WHERE likelyremapped = false AND tags->'highway' IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary') AND remappedflag < 3");
        rec = cur.fetchone()
        cur.close()
        return rec[0]
        
if __name__ == "__main__":
    app.run()

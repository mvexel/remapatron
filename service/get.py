import sys
import web
import psycopg2
import geojson
import simplejson as json

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
            cur.execute("SELECT ST_AsGeoJSON(linestring), id, tags->'highway' FROM foldingways WHERE id = %s", (wayid,))
        else:
            cur.execute("SELECT ST_AsGeoJSON(linestring), id, tags->'highway', ST_AsGeoJSON(foldpoint) FROM foldingways WHERE tags->'highway' IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','road','residential') AND fixflag < 3 ORDER BY RANDOM() LIMIT 1")
        recs = cur.fetchall()
        (gj,wayid,waytype,fp) = recs[0]
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(gj),properties={"id": wayid, "type": waytype}),geojson.Feature(geometry=geojson.loads(fp))])        
        return geojson.dumps(out)

    def PUT(self,wayid,amt):
        conn = psycopg2.connect("host=localhost dbname=deletedways user=osm password=osm")
        cur = conn.cursor()
        if not wayid:
            return web.badrequest();
        try:
            print "UPDATE foldingways SET fixflag = fixflag + %s WHERE id = %s" % (amt,wayid)
            if amt < 3:
                cur.execute("UPDATE foldingways SET fixflag = fixflag + %s WHERE id = %s", (amt,wayid,))
            else:
                cur.execute("UPDATE foldingways SET fixflag = %s WHERE id = %s", (amt,wayid,))                
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
        cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from foldingways WHERE tags->'highway' IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','road','residential') AND fixflag < 3), (select count(1) from foldingways WHERE tags->'highway' IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary', 'residential') AND fixflag < 3), (select count(1) from foldingways WHERE tags?'highway' AND fixflag < 3), (select count(1) from foldingways WHERE fixflag < 3));")
        conn.commit()
        cur.execute("select * from remapathonresults order by tstamp desc limit 1");
        rec = cur.fetchone()
        cur.close()
        return json.dumps(rec[1:])
        
if __name__ == "__main__":
    app.run()

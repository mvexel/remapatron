import sys
import web
import psycopg2
import geojson
import simplejson as json

db = {
  'host': 'localhost', 
  'dbname': 'maproulette', 
  'user': 'osm', 
  'password': 'osm'
}

connstr = "host=%s dbname=%s user=%s password=%s" % (
    db['host'], db['dbname'], db['user'], db['password'])

urls = (
    '/count/', 'getcount',
    '/store/(.*)/(-*\d+)', 'storeresult',
    '/get/(.*)', 'getcandidate'
)

sys.stdout = sys.stderr

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

# this class handles the /get service hook
class getcandidate:        
    def GET(self,osmid):
        conn = psycopg2.connect(connstr)
        cur = conn.cursor()
        if osmid:                                                            
            cur.execute("SELECT ST_AsGeoJSON(geom_way), osmid_way, ST_AsGeoJSON(geom), osmid FROM mr_currentchallenge WHERE osmid_way = %(osmid)s",
                        {'osmid': osmid})
            
        else:
            cur.execute("SELECT ST_AsGeoJSON(geom_way), osmid_way, ST_AsGeoJSON(geom), osmid FROM mr_currentchallenge WHERE fixflag < 3 ORDER BY RANDOM() LIMIT 1")
        recs = cur.fetchall()
        print recs[0]
        (way,wayid,point,nodeid) = recs[0]
        if point is not None:
            out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid}),geojson.Feature(geometry=geojson.loads(point),properties={"id": nodeid})])
        else:
            out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid})])
        return geojson.dumps(out)

# this class handles the /store service hook
class storeresult:        
    def PUT(self,osmid,amt):
        conn = psycopg2.connect(connstr)
        cur = conn.cursor()
        if not osmid:
            return web.badrequest();
        try:
#FIXME hardcoded challenge ID
            cur.execute("SELECT mr_upsert(%(amt)s::integer,%(osmid)s::bigint,1::integer)", {'amt': amt, 'osmid': osmid})
            conn.commit()
        except Exception, e:
            print e
            return web.badrequest()
        finally:
            cur.close()
        return True

# this class handles the /count service hook
class getcount:
    def GET(self):
        result = []
        conn = psycopg2.connect(connstr)
        cur = conn.cursor()
        cur.execute("insert into remapathonresults values (current_timestamp, (select count(1) from mr_currentchallenge WHERE fixflag < 3), 1)")
        conn.commit()
#FIXME hardcoded challenge id
        cur.execute("select * from remapathonresults WHERE challengeid = 1 order by tstamp desc limit 1")
        rec = cur.fetchone()
        result.append(rec[1])
#FIXME hardcoded chalenge ID as second parameter
        cur.execute("select mr_donesince(1)")
        result.append(cur.fetchone()[0])
#FIXME hardcoded challenge id as second parameter
        cur.execute("select mr_donesince(24)")
        result.append(cur.fetchone()[0])
        cur.close()
        return json.dumps(result)
        
if __name__ == "__main__":
    app.run()

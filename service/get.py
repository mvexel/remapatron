import sys
import web
import psycopg2
import geojson
import simplejson as json
import logging 

CHALLENGE_ID = 10
SKIP_THRESHOLD = 2 # number of times a task must have been marked before
# it is no longer served up
DISTANCE_THRESHOLD = 1 # degrees 
logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/maproulette/maproulette.log',level=logging.DEBUG)

urls = (
    '/count/', 'getcount',
    '/store/(.*)/(-*\d+)', 'storeresult',
    '/get/', 'getcandidate',
    '/getgeo/(-*\d+\.*\d*)/(-*\d+\.*\d*)/(\d*\.*\d*)', 'getcandidategeo'
)

sys.stdout = sys.stderr

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

class getcandidate:        
    def GET(self):
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        sql = """SELECT ST_AsGeoJSON(linestring), id  FROM 
                mr_ways_no_lanes_challenge 
                WHERE NOT done AND (type = 'motorway' or type = 'trunk') AND (current_timestamp - donetime) > '1 hour'
                AND skipflag <= %s
                ORDER BY random LIMIT 1""" % (SKIP_THRESHOLD)
        logging.debug(sql)
        cur.execute(sql)
        recs = cur.fetchall()
        (way,wayid) = recs[0]
#lock the way
        cur2 = conn.cursor()
        sql = cur2.mogrify("SELECT mr_upsert(%s,%s)", (0,wayid))
        logging.debug(sql)
        cur2.execute("SELECT mr_upsert(%s,%s)", (0,wayid))
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid})])
        conn.commit();
        cur2.close()
        cur.close()
        return geojson.dumps(out)

class getcandidategeo:        
    def GET(self, lon, lat, dist):
        if not (lon and lat):
            return web.badrequest()
        lon = float(lon)
        lat = float(lat)
        if dist:
            dist = float(dist)
        else:
            dist = DISTANCE_THRESHOLD
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        sql = """SELECT ST_AsGeoJSON(linestring), id  FROM 
                mr_ways_no_lanes_challenge 
                WHERE NOT done AND (type = 'motorway' or type = 'trunk') AND (current_timestamp - donetime) > '1 hour'
                AND skipflag <= %s
                AND linestring <-> ST_MakePoint(%f, %f) < %f
                ORDER BY random LIMIT 1""" % (SKIP_THRESHOLD, lon, lat, dist)
        logging.debug(sql)
        cur.execute(sql)
        recs = cur.fetchall()
        if len(recs) == 0:
            return web.notfound('no task near here')
        (way,wayid) = recs[0]
#lock the way
        cur2 = conn.cursor()
        sql = cur2.mogrify("SELECT mr_upsert(%s,%s)", (0,wayid))
        logging.debug(sql)
        cur2.execute("SELECT mr_upsert(%s,%s)", (0,wayid))
        out = geojson.FeatureCollection([geojson.Feature(geometry=geojson.loads(way),properties={"id": wayid})])
        conn.commit();
        cur2.close()
        cur.close()
        return geojson.dumps(out)


class storeresult:        
    def PUT(self,osmid,done):
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        if not osmid:
            return web.badrequest();
        try:
            if (done == '2'):
                return True
            cur.execute("SELECT mr_upsert(%s,%s)", (done,osmid))
            conn.commit()
        except Exception, e:
            print e
            return web.badrequest()
        finally:
            cur.close()
        return True

class getcount:
    """returns a list containing total count remaining, fixed in last hour, fixed in last day, seen in last hour, seen in last day"""
    def GET(self):
        result = []
        conn = psycopg2.connect("host=localhost dbname=osm user=osm password=osm")
        cur = conn.cursor()
        cur.execute("select count(1) from mr_ways_no_lanes_challenge where (type = 'motorway' or type = 'trunk') and not done and skipflag <= %s;", (SKIP_THRESHOLD,))
        result.append(cur.fetchone()[0])
        cur.execute("insert into remapathonresults values (now(), %s, %s)", (result[0], CHALLENGE_ID,))
        conn.commit()
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 hour' and done")
        result.append(cur.fetchone()[0])
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 day' and done")
        result.append(cur.fetchone()[0])
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 hour'")
        result.append(cur.fetchone()[0])
        cur.execute("select count(1) FROM tnav_ways_no_lanes_mrstatus WHERE now() - donetime < interval '1 day'")
        result.append(cur.fetchone()[0])
        cur.close()
        return json.dumps(result)
        
if __name__ == "__main__":
    app.run()

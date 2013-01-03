-- Function: mr_getsomenolaneways()

-- DROP FUNCTION mr_getsomenolaneways();

CREATE OR REPLACE FUNCTION mr_getsomenolaneways()
  RETURNS TABLE(osmid bigint, geojson text) AS
$BODY$ 
DECLARE 
BEGIN  
  RETURN QUERY
    WITH 
      initialq 
    AS ( 
      SELECT 
        mr_currentchallenge.osmid,
        ST_AsText(mr_currentchallenge.geom) as gtxt
      FROM 
        mr_currentchallenge 
      WHERE 
        type = 'motorway' AND 
        fixflag < 3 AND 
        (EXTRACT(EPOCH FROM now() - locked) / 3600) < 0 
      LIMIT 1
    ) 
    SELECT 
      mr_currentchallenge.osmid, 
      ST_AsGeoJSON(mr_currentchallenge.geom)
    FROM 
      mr_currentchallenge, initialq
    WHERE
--      ABS(initialq.osmid - mr_currentchallenge.osmid) < 20;
--    AND 
        ST_GeomFromText(initialq.gtxt) <#> mr_currentchallenge.geom < 0.01;
  RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION mr_getsomenolaneways()
  OWNER TO osm;

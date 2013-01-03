-- Function: mr_setlocked(timestamp without time zone, bigint)

-- DROP FUNCTION mr_setlocked(timestamp without time zone, bigint);

CREATE OR REPLACE FUNCTION mr_setlocked(in_t timestamp without time zone, in_osmid bigint)
  RETURNS void AS
$BODY$ 
DECLARE 
BEGIN 
    UPDATE maproulette SET locked = in_t WHERE osmid = in_osmid; 
    IF NOT FOUND THEN 
    INSERT INTO maproulette (osmid, locked) values (in_osmid, in_t); 
    END IF; 
END; 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION mr_setlocked(timestamp without time zone, bigint)
  OWNER TO osm;


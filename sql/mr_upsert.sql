-- Function: mr_upsert(integer, bigint)

-- DROP FUNCTION mr_upsert(integer, bigint);

CREATE OR REPLACE FUNCTION mr_upsert(in_fixflag integer, in_osmid bigint)
  RETURNS void AS
$BODY$ 
DECLARE 
BEGIN 
    UPDATE maproulette SET fixflag = in_fixflag WHERE osmid = in_osmid; 
    IF NOT FOUND THEN 
    INSERT INTO maproulette (osmid, fixflag) values (in_osmid, in_fixflag); 
    END IF; 
END; 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION mr_upsert(integer, bigint)
  OWNER TO osm;

-- Function: mr_donesince(integer)

-- DROP FUNCTION mr_donesince(integer);

CREATE OR REPLACE FUNCTION mr_donesince(in_interval integer)
  RETURNS integer AS
$BODY$
  DECLARE 
	cmd text;
	result integer;
BEGIN
	cmd := 'SELECT 
		(SELECT mainroads FROM remapathonresults ORDER BY tstamp DESC LIMIT 1) - 
		(SELECT mainroads FROM remapathonresults WHERE tstamp < NOW() - INTERVAL ''' 
		|| in_interval || 
		'HOUR'' ORDER BY tstamp DESC LIMIT 1);';
	EXECUTE cmd INTO result;
	RETURN -result;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION mr_donesince(integer)
  OWNER TO osm;

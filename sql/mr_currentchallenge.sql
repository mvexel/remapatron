-- View: mr_currentchallenge

-- DROP VIEW mr_currentchallenge;

CREATE OR REPLACE VIEW mr_currentchallenge AS 
 SELECT a.deadend_node_id AS osmid, a.the_geom AS geom, a.deadend_way_id AS osmid_way, a.deadend_geom AS geom_way, a.distance_min, a.closeest_way_id AS secondary_osmid, a.closest_way_geom AS secondary_geom, COALESCE(b.fixflag, 0) AS fixflag
   FROM tnav_connectivity_errors a
   LEFT JOIN maproulette b ON a.deadend_way_id = b.osmid;

ALTER TABLE mr_currentchallenge
  OWNER TO osm;


-- Table: tnav_connectivity_errors

-- DROP TABLE tnav_connectivity_errors;

CREATE TABLE tnav_connectivity_errors
(
  deadend_node_id bigint,
  the_geom geometry,
  deadend_way_id bigint,
  deadend_geom geometry,
  distance_min double precision,
  closeest_way_id bigint,
  closest_way_geom geometry
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tnav_connectivity_errors
  OWNER TO postgres;

-- Index: idx_osmid

-- DROP INDEX idx_osmid;

CREATE INDEX idx_osmid
  ON tnav_connectivity_errors
  USING btree
  (deadend_node_id );


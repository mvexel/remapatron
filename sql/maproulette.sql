-- Table: maproulette

-- DROP TABLE maproulette;

CREATE TABLE maproulette
(
  osmid bigint NOT NULL,
  fixflag integer,
  CONSTRAINT pkey_osmid PRIMARY KEY (osmid )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE maproulette
  OWNER TO osm;
